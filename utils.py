# fungsi dan pengaturan yang dipakai bersama oleh semua halaman
import os

import joblib
import pandas as pd
import streamlit as st

from komponen.tabel_data import tampilkan_tabel


# letak folder aplikasi, file model, dan file data yang tersimpan
FOLDER_APLIKASI = os.path.dirname(os.path.abspath(__file__))
LOKASI_MODEL = os.path.join(FOLDER_APLIKASI, "model", "random_forest_final.joblib")
LOKASI_DATA = os.path.join(FOLDER_APLIKASI, "penyimpanan", "data_terakhir.joblib")

# urutan kategori pergerakan obat
URUTAN_FSN = ["Fast-Moving", "Slow-Moving", "Non-Moving"]

# warna utama setiap kategori
WARNA_FSN = {"Fast-Moving": "#1baf7a", "Slow-Moving": "#eda100", "Non-Moving": "#e34948"}

# warna latar muda untuk kotak setiap kategori
WARNA_MUDA = {"Total SKU": "#d6f0ec", "Fast-Moving": "#d3f2e6", "Slow-Moving": "#fcecc5", "Non-Moving": "#f9d9d8"}

# warna tulisan tua untuk kotak setiap kategori
WARNA_TUA = {"Total SKU": "#07706e", "Fast-Moving": "#128a5f", "Slow-Moving": "#b07800", "Non-Moving": "#c0302f"}

# nama singkat kategori untuk memberi warna baris tabel
KODE_WARNA_BARIS = {"Fast-Moving": "fast", "Slow-Moving": "slow", "Non-Moving": "non"}

# keterangan tindak lanjut untuk setiap kategori
TINDAK_LANJUT = {
    "Fast-Moving": (
        "Obat dengan kategori Fast Moving memiliki tingkat pergerakan yang tinggi. "
        "Perhatikan ketersediaan persediaan obat agar tidak terjadi kekosongan stok."
    ),
    "Slow-Moving": (
        "Obat dengan kategori Slow Moving memiliki tingkat pergerakan yang lambat. "
        "Perlu evaluasi jumlah persediaan agar tidak berlebih, serta pertimbangkan promosi "
        "untuk meningkatkan penjualan."
    ),
    "Non-Moving": (
        "Obat dengan kategori Non-Moving hampir atau tidak mengalami pergerakan selama periode data. "
        "Perlu evaluasi kebutuhan obat ini serta pemeriksaan risiko kedaluwarsa pada persediaan."
    ),
}

# nama bulan singkat untuk grafik dan filter
NAMA_BULAN = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun",
    7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des",
}


# pindah ke halaman lain
def pindah_halaman(nama_halaman):
    st.session_state["halaman"] = nama_halaman
    # nama halaman disimpan di alamat web supaya tidak hilang saat di-refresh
    st.query_params["halaman"] = nama_halaman
    if nama_halaman != "detail_sku" and "kode" in st.query_params:
        del st.query_params["kode"]
    st.rerun()


# membuka file model sekali saja lalu disimpan di memori
@st.cache_resource(show_spinner=False)
def muat_model():
    return joblib.load(LOKASI_MODEL)


# menyimpan hasil unggahan terakhir ke folder penyimpanan
def simpan_data(data):
    os.makedirs(os.path.dirname(LOKASI_DATA), exist_ok=True)
    joblib.dump(data, LOKASI_DATA)


# membuka hasil unggahan terakhir kalau filenya ada
def muat_data_tersimpan():
    if os.path.exists(LOKASI_DATA):
        return joblib.load(LOKASI_DATA)
    return None


# menghapus data yang tersimpan sehingga aplikasi kembali kosong
def hapus_data():
    if os.path.exists(LOKASI_DATA):
        os.remove(LOKASI_DATA)
    st.session_state["data"] = None
    st.session_state["status_unggah"] = None
    st.session_state["kode_detail"] = None
    st.session_state["pesan_gagal"] = None
    st.session_state["kunci_uploader"] += 1
    if "kode" in st.query_params:
        del st.query_params["kode"]


# menulis angka dengan titik sebagai pemisah ribuan, contoh 1250 menjadi 1.250
def angka(nilai):
    return f"{nilai:,.0f}".replace(",", ".")


# mengubah nilai kosong menjadi None dan nilai lain menjadi angka desimal
def angka_atau_kosong(nilai):
    if pd.isna(nilai):
        return None
    return float(nilai)


# menampilkan judul halaman di tengah
def judul(teks):
    st.markdown(f'<div class="judul-halaman">{teks}</div>', unsafe_allow_html=True)


# mengubah periode bulan menjadi tulisan, contoh 2022-01 menjadi Jan 2022
def label_bulan(periode):
    return f"{NAMA_BULAN[periode.month]} {periode.year}"


# daftar bulan dari tanggal awal sampai tanggal akhir data
def daftar_periode_data(data):
    ringkasan = data["ringkasan"]
    return pd.period_range(ringkasan["tanggal_awal"], ringkasan["tanggal_akhir"], freq="M")


# menjumlahkan transaksi per bulan, bulan tanpa transaksi diisi 0
def rekap_bulanan(data_transaksi, kolom_jumlah, daftar_periode):
    bulan_transaksi = data_transaksi["tanggal"].dt.to_period("M")
    jumlah_per_bulan = data_transaksi.groupby(bulan_transaksi)[kolom_jumlah].sum()
    jumlah_per_bulan = jumlah_per_bulan.reindex(daftar_periode, fill_value=0)

    rekap = pd.DataFrame({"periode": jumlah_per_bulan.index, "jumlah": jumlah_per_bulan.values})
    rekap["bulan"] = rekap["periode"].apply(label_bulan)
    return rekap


# pesan kalau belum ada data yang diunggah
def pesan_belum_ada_data():
    st.info("Belum ada data yang diproses. Silakan unggah dataset kartu stok pada menu **Unggah Dataset**.")
    if st.button("Ke Unggah Dataset"):
        pindah_halaman("unggah_data")


# menampilkan tabel transaksi di halaman data penjualan dan data pembelian
def tabel_transaksi(data, jenis, kolom_jumlah, label_jumlah):
    # transaksi terbaru ditaruh paling atas
    data_transaksi = data[jenis].sort_values("tanggal", ascending=False)
    data_transaksi = data_transaksi.rename(columns={kolom_jumlah: "jumlah"})

    # isi setiap baris tabel
    daftar_baris = []
    for transaksi in data_transaksi.itertuples():
        ada_tanggal = pd.notna(transaksi.tanggal)
        daftar_baris.append({
            "tanggal": f"{transaksi.tanggal:%d-%m-%Y %H:%M}" if ada_tanggal else "-",
            "tanggal_urut": transaksi.tanggal.isoformat() if ada_tanggal else "",
            "bulan": label_bulan(transaksi.tanggal.to_period("M")) if ada_tanggal else "-",
            "kode_obat": str(transaksi.kode_obat),
            "nama_obat": str(transaksi.nama_obat),
            "jumlah": angka_atau_kosong(transaksi.jumlah),
            "sisa_stok": angka_atau_kosong(transaksi.sisa_stok),
            "warna_baris": "netral",
        })

    # pilihan bulan untuk filter, dari bulan paling awal
    daftar_bulan = sorted(data_transaksi["tanggal"].dropna().dt.to_period("M").unique())

    # nilai tertinggi untuk filter rentang angka
    jumlah_tertinggi = data_transaksi["jumlah"].max()
    sisa_tertinggi = data_transaksi["sisa_stok"].max()

    ringkasan = data["ringkasan"]
    pengaturan_tabel = {
        "nama_penyimpanan": f"filter_data_{jenis}",
        "versi": f"{ringkasan['tanggal_awal']}_{ringkasan['tanggal_akhir']}_{ringkasan['jumlah_baris_diproses']}",
        "kolom": [
            {"kunci": "no", "judul": "No", "lebar": "5%", "rata": "kanan", "jenis": "nomor"},
            {"kunci": "tanggal", "judul": "Tanggal", "lebar": "15%", "filter": "pilihan", "kunci_filter": "bulan",
             "urut": {"kunci": "tanggal_urut", "naik": "Terlama", "turun": "Terbaru"}},
            {"kunci": "kode_obat", "judul": "Kode SKU", "lebar": "13%", "jenis": "kode"},
            {"kunci": "nama_obat", "judul": "Nama Obat", "lebar": "37%"},
            {"kunci": "jumlah", "judul": label_jumlah, "lebar": "15%", "rata": "kanan", "jenis": "angka", "filter": "rentang"},
            {"kunci": "sisa_stok", "judul": "Sisa Stok", "lebar": "15%", "rata": "kanan", "jenis": "angka", "filter": "rentang"},
        ],
        "baris": daftar_baris,
        "urut_awal": {"kunci": "tanggal_urut", "arah": "turun"},
        "pilihan": {"bulan": [label_bulan(periode) for periode in daftar_bulan]},
        "maksimal": {
            "jumlah": 0 if pd.isna(jumlah_tertinggi) else float(jumlah_tertinggi),
            "sisa_stok": 0 if pd.isna(sisa_tertinggi) else float(sisa_tertinggi),
        },
        "cari": {"petunjuk": "Cari kode atau nama obat", "kolom": ["kode_obat", "nama_obat"]},
        "ekspor": {"nama_file": f"data_{jenis}.xlsx", "nama_lembar": f"Data {jenis.capitalize()}"},
        "baris_per_halaman": 25,
        "lebar_minimal": 900,
        "satuan": "transaksi",
        "teks_kosong": "Tidak ada transaksi yang sesuai dengan pencarian atau filter.",
    }
    tampilkan_tabel(f"tabel_{jenis}", pengaturan_tabel)
