# halaman data & hasil klasifikasi sku
import pandas as pd
import streamlit as st

from komponen.tabel_data import tampilkan_tabel
from utils import KODE_WARNA_BARIS, URUTAN_FSN, angka_atau_kosong, judul, pesan_belum_ada_data, pindah_halaman


# susunan kolom tabel hasil klasifikasi
KOLOM_TABEL_SKU = [
    {"kunci": "no", "judul": "No", "lebar": "4%", "rata": "kanan", "jenis": "nomor"},
    {"kunci": "kode_obat", "judul": "Kode SKU", "lebar": "12%", "jenis": "kode"},
    {"kunci": "nama_obat", "judul": "Nama Obat", "lebar": "19%"},
    {"kunci": "kategori", "judul": "Kategori", "lebar": "14%", "filter": "pilihan"},
    {"kunci": "golongan", "judul": "Golongan", "lebar": "12%", "filter": "pilihan"},
    {"kunci": "stok_awal", "judul": "Stok Awal", "lebar": "8%", "rata": "kanan", "jenis": "angka", "filter": "rentang"},
    {"kunci": "stok_akhir", "judul": "Sisa Stok", "lebar": "8%", "rata": "kanan", "jenis": "angka", "filter": "rentang"},
    {"kunci": "hasil_klasifikasi", "judul": "Hasil Klasifikasi", "lebar": "11%", "jenis": "kelas", "filter": "pilihan"},
    {"kunci": "aksi", "judul": "Aksi", "lebar": "12%", "rata": "tengah", "jenis": "tombol",
     "teks_tombol": "Lihat Detail", "kunci_nilai": "kode_obat"},
]


# mengubah nilai kosong menjadi None dan nilai lain menjadi tulisan
def teks_atau_kosong(nilai):
    if pd.isna(nilai):
        return None
    return str(nilai)


# menyiapkan isi tabel hasil klasifikasi
def pengaturan_tabel_sku(data_sku, ringkasan):
    daftar_baris = []
    for sku in data_sku.itertuples():
        daftar_baris.append({
            "kode_obat": teks_atau_kosong(sku.kode_obat),
            "nama_obat": teks_atau_kosong(sku.nama_obat),
            "kategori": teks_atau_kosong(sku.kategori),
            "golongan": teks_atau_kosong(sku.golongan),
            "stok_awal": angka_atau_kosong(sku.stok_awal),
            "stok_akhir": angka_atau_kosong(sku.stok_akhir),
            "hasil_klasifikasi": teks_atau_kosong(sku.hasil_klasifikasi),
            "warna_baris": KODE_WARNA_BARIS.get(sku.hasil_klasifikasi, ""),
        })

    # pilihan untuk filter kategori dan golongan, diurutkan sesuai abjad
    pilihan_kategori = sorted(data_sku["kategori"].dropna().astype(str).unique())
    pilihan_golongan = sorted(data_sku["golongan"].dropna().astype(str).unique())

    # pengaturan nilai tertinggi untuk filter rentang stok
    stok_awal_tertinggi = data_sku["stok_awal"].max()
    sisa_stok_tertinggi = data_sku["stok_akhir"].max()

    return {
        "nama_penyimpanan": "filter_tabel_sku",
        # penanda data, filter akan dikosongkan lagi jika dataset diganti
        "versi": f"{ringkasan['tanggal_awal']}_{ringkasan['tanggal_akhir']}_{ringkasan['jumlah_sku']}_{ringkasan['jumlah_baris_diproses']}",
        "kolom": KOLOM_TABEL_SKU,
        "baris": daftar_baris,
        "pilihan": {
            "kategori": list(pilihan_kategori),
            "golongan": list(pilihan_golongan),
            "hasil_klasifikasi": URUTAN_FSN,
        },
        "maksimal": {
            "stok_awal": 0 if pd.isna(stok_awal_tertinggi) else float(stok_awal_tertinggi),
            "stok_akhir": 0 if pd.isna(sisa_stok_tertinggi) else float(sisa_stok_tertinggi),
        },
        "cari": {"petunjuk": "Cari kode atau nama obat", "kolom": ["kode_obat", "nama_obat"]},
        "ekspor": {"nama_file": "hasil_klasifikasi_sku.xlsx", "nama_lembar": "Hasil Klasifikasi"},
        "baris_per_halaman": 25,
        "lebar_minimal": 980,
        "satuan": "SKU",
        "teks_kosong": "Tidak ada SKU yang sesuai dengan pencarian atau filter.",
    }


def halaman_klasifikasi():
    judul("DATA & HASIL KLASIFIKASI SKU")
    data = st.session_state["data"]
    if data is None:
        pesan_belum_ada_data()
        return

    # menampilkan tabel dan membaca kode obat dari tombol lihat detail yang diklik
    kode_dipilih = tampilkan_tabel("tabel_sku", pengaturan_tabel_sku(data["sku"], data["ringkasan"]))

    # membuka halaman detail untuk obat yang dipilih
    if kode_dipilih:
        st.session_state["kode_detail"] = kode_dipilih
        st.query_params["kode"] = str(kode_dipilih)
        pindah_halaman("detail_sku")
