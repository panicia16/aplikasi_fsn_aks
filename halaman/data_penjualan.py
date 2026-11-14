# halaman data penjualan
import streamlit as st

from grafik import WARNA_JUAL, grafik_bulanan, isi_ringkasan_jual, kartu_teratas, kotak_ringkasan, tulisan_periode
from utils import daftar_periode_data, judul, pesan_belum_ada_data, rekap_bulanan, tabel_transaksi


def halaman_penjualan():
    judul("DATA PENJUALAN")
    data = st.session_state["data"]
    if data is None:
        pesan_belum_ada_data()
        return

    tulisan_periode(data["ringkasan"])

    # jumlah penjualan setiap bulan, sama seperti di dashboard
    daftar_periode = daftar_periode_data(data)
    rekap_jual = rekap_bulanan(data["penjualan"], "jumlah_terjual", daftar_periode)

    # ringkasan penjualan dan grafik penjualan per bulan sebelahan
    kiri, kanan = st.columns([1, 2])
    with kiri.container(key="kartu_ringkasan_jual"):
        st.subheader("Ringkasan Penjualan")
        kotak_ringkasan(isi_ringkasan_jual(rekap_jual), jumlah_kolom=1)
    with kanan.container(key="kartu_statistik_jual"):
        st.subheader("Statistik Penjualan")
        st.altair_chart(grafik_bulanan(rekap_jual, WARNA_JUAL, "Jumlah obat terjual"), use_container_width=True)

    # 10 obat teratas untuk seluruh periode atau satu bulan tertentu
    kartu_teratas(data, "penjualan", rekap_jual, daftar_periode)

    # tabel riwayat penjualan, bisa diekspor ke excel atau pdf
    st.subheader("Riwayat Penjualan")
    tabel_transaksi(data, "penjualan", "jumlah_terjual", "Jumlah Terjual")