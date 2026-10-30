# halaman detail sku
import html

import altair as alt
import pandas as pd
import streamlit as st

from komponen.tabel_data import tampilkan_tabel
from utils import (
    KODE_WARNA_BARIS, TINDAK_LANJUT, WARNA_MUDA, WARNA_TUA,
    angka, angka_atau_kosong, daftar_periode_data, judul, label_bulan, pindah_halaman, rekap_bulanan,
)


# tampilan untuk halaman detail sku
GAYA_DETAIL = """
<style>
.st-key-wadah_kembali { align-items: flex-end; }
.kartu-putih { background-color: #ffffff; border-radius: 12px; padding: 20px 24px; margin-bottom: 16px; }
.judul-kartu { font-weight: 700; font-size: 1.05rem; margin-bottom: 12px; }

/* informasi obat dalam dua kolom (6 baris di kiri, 6 baris di kanan): nama, titik dua, isi */
.isi-informasi { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); grid-template-rows: repeat(6, auto); grid-auto-flow: column; column-gap: 32px; }
.baris-informasi { display: grid; grid-template-columns: 190px 16px 1fr; padding: 6px 0; border-bottom: 1px solid #eef5f3; }
.baris-informasi span:first-child { font-weight: 600; color: #52514e; }

/* kotak hasil klasifikasi, bentuknya sama dengan kotak di dashboard */
.kotak-klasifikasi { border-radius: 12px; padding: 20px 24px; margin-bottom: 16px; }
.nama-kategori { font-size: 2.4rem; font-weight: 800; letter-spacing: 1px; line-height: 1.2; }
.catatan { display: flex; gap: 12px; align-items: flex-start; margin-top: 14px; padding: 12px 16px; background-color: #ffffff; border-radius: 10px; }
.tanda-seru {
    flex: none; width: 24px; height: 24px; border-radius: 50%; background-color: #e34948; color: #ffffff;
    font-weight: 800; display: flex; align-items: center; justify-content: center;
}

.st-key-kartu_grafik { background-color: #ffffff; border-radius: 12px; padding: 20px 24px; }
#vg-tooltip-element td.key { text-align: left; }

/* layar sedang: informasi obat menjadi satu kolom */
@media (max-width: 900px) {
    .isi-informasi { grid-template-columns: 1fr; grid-template-rows: none; grid-auto-flow: row; }
}

/* layar ponsel: jarak dan tulisan lebih kecil */
@media (max-width: 640px) {
    .kartu-putih, .kotak-klasifikasi, .st-key-kartu_grafik { padding: 14px 16px; }
    .baris-informasi { grid-template-columns: 130px 12px 1fr; font-size: 0.9rem; }
    .nama-kategori { font-size: 1.7rem; }
}
</style>
"""

# tanggal terakhir masuk, kalau kosong berarti pembelian terakhir sebelum periode data
def teks_tanggal_masuk(tanggal):
    if pd.isna(tanggal):
        return "Sebelum periode data"
    return f"{tanggal:%d-%m-%Y}"

# tanggal terakhir keluar, kalau kosong berarti tidak ada penjualan -> dibuat jadi '-' 
def teks_tanggal_keluar(tanggal):
    if pd.isna(tanggal):
        return "-"
    return f"{tanggal:%d-%m-%Y}"

# angka stok, kalau kosong ditulis tanda "-"
def teks_angka(nilai):
    if pd.isna(nilai):
        return "-"
    return angka(nilai)


# kartu putih berisi informasi obat, dibuat jdi dua kolom (6 baris di kiri, 6 baris di kanan)
def kartu_informasi(sku, kode):
    # peletakan enam informasi pertama di kolom kiri, enam berikutnya di kolom kanan
    daftar_informasi = [
        ("Nama Obat", sku["nama_obat"]),
        ("Kode Obat", kode),
        ("Kategori", sku["kategori"]),
        ("Golongan", sku["golongan"]),
        ("Stok Awal", teks_angka(sku["stok_awal"])),
        ("Sisa Stok", teks_angka(sku["stok_akhir"])),
        ("Total Masuk", angka(sku["total_masuk"])),
        ("Total Keluar", angka(sku["total_keluar"])),
        ("Frekuensi Transaksi", angka(sku["frekuensi_transaksi"])),
        ("Active Months", sku["active_months"]),
        ("Tanggal Terakhir Masuk", teks_tanggal_masuk(sku["tanggal_terakhir_masuk"])),
        ("Tanggal Terakhir Keluar", teks_tanggal_keluar(sku["tanggal_terakhir_keluar"])),
    ]

    semua_baris = ""
    for nama, isi in daftar_informasi:
        semua_baris += f'<div class="baris-informasi"><span>{nama}</span><span>:</span><span>{html.escape(str(isi))}</span></div>'

    st.markdown(
        f'<div class="kartu-putih"><div class="judul-kartu">Informasi Obat</div><div class="isi-informasi">{semua_baris}</div></div>',
        unsafe_allow_html=True,
    )


# kotak hasil klasifikasi berwarna sesuai kategorinya
def kotak_klasifikasi(kategori):
    warna_latar = WARNA_MUDA.get(kategori, "#ffffff")
    warna_tulisan = WARNA_TUA.get(kategori, "#07706e")
    nama_kategori = kategori.replace("-", " ").upper()
    st.markdown(
        f'<div class="kotak-klasifikasi" style="background-color:{warna_latar}">'
        f'<div class="judul-kartu">Hasil Klasifikasi</div>'
        f'<div class="nama-kategori" style="color:{warna_tulisan}">{nama_kategori}</div>'
        f'<div class="catatan"><div class="tanda-seru">!</div><div>{TINDAK_LANJUT.get(kategori, "-")}</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# grafik batang penjualan dan pembelian tiap bulannya
def grafik_transaksi(jual_obat, beli_obat, daftar_periode):
    rekap_jual = rekap_bulanan(jual_obat, "jumlah_terjual", daftar_periode)
    rekap_beli = rekap_bulanan(beli_obat, "jumlah_dibeli", daftar_periode)
    urutan_bulan = list(rekap_jual["bulan"])

    # data grafik yang berisi bulan, jenis transaksi, dan jumlah
    rekap_jual["Jenis"] = "Penjualan"
    rekap_beli["Jenis"] = "Pembelian"
    data_grafik = pd.concat([rekap_jual, rekap_beli])[["bulan", "Jenis", "jumlah"]]
    data_grafik = data_grafik.rename(columns={"bulan": "Bulan", "jumlah": "Jumlah"})

    # diagram batang penjualan dan pembelian sampingan
    warna = alt.Scale(domain=["Penjualan", "Pembelian"], range=["#2a78d6", "#07706e"])
    dasar = alt.Chart(data_grafik).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X("Bulan:N", sort=urutan_bulan, title=None, axis=alt.Axis(labelAngle=0)),
        xOffset=alt.XOffset("Jenis:N", sort=["Penjualan", "Pembelian"]),
        y=alt.Y("Jumlah:Q", title="Jumlah obat", axis=alt.Axis(titlePadding=14, labelPadding=6)),
        color=alt.Color("Jenis:N", scale=warna, legend=alt.Legend(title=None, orient="bottom")),
    )

    # tulisan saat kursor diarahkan dibedakan untuk penjualan dan pembelian
    batang_jual = dasar.transform_filter(alt.datum.Jenis == "Penjualan").encode(
        tooltip=[alt.Tooltip("Bulan:N"), alt.Tooltip("Jenis:N"), alt.Tooltip("Jumlah:Q", title="Jumlah Terjual", format=",.0f")]
    )
    batang_beli = dasar.transform_filter(alt.datum.Jenis == "Pembelian").encode(
        tooltip=[alt.Tooltip("Bulan:N"), alt.Tooltip("Jenis:N"), alt.Tooltip("Jumlah:Q", title="Jumlah Dibeli", format=",.0f")]
    )
    return alt.layer(batang_jual, batang_beli).properties(height=300, padding={"left": 16, "top": 20, "right": 16, "bottom": 8})


# menyiapkan isi tabel riwayat transaksi satu obat
def pengaturan_riwayat(data_transaksi, jenis, kolom_bukti, judul_bukti, kolom_jumlah, judul_jumlah, kategori, versi):
    # transaksi terbaru ditaruh paling atas
    data_transaksi = data_transaksi.sort_values("tanggal", ascending=False)
    data_transaksi = data_transaksi.rename(columns={kolom_bukti: "bukti", kolom_jumlah: "jumlah"})

    daftar_baris = []
    for transaksi in data_transaksi.itertuples():
        ada_tanggal = pd.notna(transaksi.tanggal)
        daftar_baris.append({
            "tanggal": f"{transaksi.tanggal:%d-%m-%Y %H:%M}" if ada_tanggal else "-",
            "tanggal_urut": transaksi.tanggal.isoformat() if ada_tanggal else "",
            "bulan": label_bulan(transaksi.tanggal.to_period("M")) if ada_tanggal else "-",
            "bukti": str(transaksi.bukti),
            "jumlah": angka_atau_kosong(transaksi.jumlah),
            "sisa_stok": angka_atau_kosong(transaksi.sisa_stok),
            "warna_baris": KODE_WARNA_BARIS.get(kategori, ""),
        })

    # pilihan bulan untuk filter dan nilai tertinggi untuk filter angka
    daftar_bulan = sorted(data_transaksi["tanggal"].dropna().dt.to_period("M").unique())
    jumlah_tertinggi = data_transaksi["jumlah"].max()
    sisa_tertinggi = data_transaksi["sisa_stok"].max()

    return {
        "nama_penyimpanan": f"filter_riwayat_{jenis}",
        "versi": versi,
        "kolom": [
            {"kunci": "tanggal", "judul": "Tanggal", "lebar": "28%", "filter": "pilihan", "kunci_filter": "bulan",
             "urut": {"kunci": "tanggal_urut", "naik": "Terlama", "turun": "Terbaru"}},
            {"kunci": "bukti", "judul": judul_bukti, "lebar": "28%", "jenis": "kode"},
            {"kunci": "jumlah", "judul": judul_jumlah, "lebar": "22%", "rata": "kanan", "jenis": "angka", "filter": "rentang"},
            {"kunci": "sisa_stok", "judul": "Sisa Stok", "lebar": "22%", "rata": "kanan", "jenis": "angka", "filter": "rentang"},
        ],
        "baris": daftar_baris,
        "urut_awal": {"kunci": "tanggal_urut", "arah": "turun"},
        "pilihan": {"bulan": [label_bulan(periode) for periode in daftar_bulan]},
        "maksimal": {
            "jumlah": 0 if pd.isna(jumlah_tertinggi) else float(jumlah_tertinggi),
            "sisa_stok": 0 if pd.isna(sisa_tertinggi) else float(sisa_tertinggi),
        },
        "cari": None,
        "ekspor": None,
        "baris_per_halaman": 10,
        "lebar_minimal": 560,
        "satuan": "transaksi",
        "teks_kosong": f"Tidak terdapat transaksi {jenis} untuk obat ini pada periode data.",
    }


def halaman_detail():
    st.markdown(GAYA_DETAIL, unsafe_allow_html=True)
    data = st.session_state["data"]
    kode = st.session_state["kode_detail"]

    # kembali ke tabel kalau data atau kode obat tidak ditemukan
    if data is None or kode is None or not (data["sku"]["kode_obat"] == kode).any():
        pindah_halaman("data_klasifikasi")
        return

    # judul di tengah dan tombol kembali di kanan
    kiri, tengah, kanan = st.columns([1, 4, 1], vertical_alignment="center")
    with tengah:
        judul("DETAIL SKU")
    with kanan.container(key="wadah_kembali"):
        if st.button("Kembali", icon=":material/arrow_back:"):
            pindah_halaman("data_klasifikasi")

    # data obat yang dipilih
    sku = data["sku"].set_index("kode_obat").loc[kode]
    kategori = sku["hasil_klasifikasi"]

    kartu_informasi(sku, kode)
    kotak_klasifikasi(kategori)

    # transaksi obat yang dipilih
    daftar_periode = daftar_periode_data(data)
    jual_obat = data["penjualan"][data["penjualan"]["kode_obat"] == kode]
    beli_obat = data["pembelian"][data["pembelian"]["kode_obat"] == kode]

    # grafik penjualan dan pembelian per bulan
    with st.container(key="kartu_grafik"):
        st.subheader("Penjualan dan Pembelian per Bulan")
        st.altair_chart(grafik_transaksi(jual_obat, beli_obat, daftar_periode), use_container_width=True)

    # riwayat transaksi dibuat dua tab
    st.subheader("Riwayat Transaksi")
    tab_jual, tab_beli = st.tabs([f"Penjualan ({len(jual_obat)})", f"Pembelian ({len(beli_obat)})"])
    versi = f"{data['ringkasan']['tanggal_awal']}_{data['ringkasan']['jumlah_sku']}_{kode}"
    with tab_jual:
        tampilkan_tabel("riwayat_penjualan", pengaturan_riwayat(
            jual_obat, "penjualan", "no_bukti", "No. Bukti", "jumlah_terjual", "Jumlah Terjual", kategori, versi))
    with tab_beli:
        tampilkan_tabel("riwayat_pembelian", pengaturan_riwayat(
            beli_obat, "pembelian", "no_faktur", "No. Faktur", "jumlah_dibeli", "Jumlah Dibeli", kategori, versi))
