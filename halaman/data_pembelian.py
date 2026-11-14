# halaman data pembelian
import streamlit as st

from grafik import WARNA_BELI, grafik_bulanan, isi_ringkasan_beli, kartu_teratas, kotak_ringkasan, tulisan_periode
from utils import daftar_periode_data, judul, pesan_belum_ada_data, rekap_bulanan, tabel_transaksi


def halaman_pembelian():
    judul("DATA PEMBELIAN")
    data = st.session_state["data"]
    if data is None:
        pesan_belum_ada_data()
        return

    tulisan_periode(data["ringkasan"])

    # jumlah pembelian setiap bulan, sama seperti di dashboard
    daftar_periode = daftar_periode_data(data)
    rekap_beli = rekap_bulanan(data["pembelian"], "jumlah_dibeli", daftar_periode)

    # ringkasan pembelian dan grafik pembelian per bulan sebelahan
    kiri, kanan = st.columns([1, 2])
    with kiri.container(key="kartu_ringkasan_beli"):
        st.subheader("Ringkasan Pembelian")
        kotak_ringkasan(isi_ringkasan_beli(rekap_beli), jumlah_kolom=1)
    with kanan.container(key="kartu_statistik_beli"):
        st.subheader("Statistik Pembelian")
        st.altair_chart(grafik_bulanan(rekap_beli, WARNA_BELI, "Jumlah obat dibeli"), use_container_width=True)

    # 10 obat teratas untuk seluruh periode atau satu bulan tertentu
    kartu_teratas(data, "pembelian", rekap_beli, daftar_periode)

    # tabel riwayat pembelian, bisa diekspor ke excel atau pdf
    st.subheader("Riwayat Pembelian")
    tabel_transaksi(data, "pembelian", "jumlah_dibeli", "Jumlah Dibeli")