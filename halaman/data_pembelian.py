# halaman data pembelian
import streamlit as st

from utils import judul, pesan_belum_ada_data, tabel_transaksi


def halaman_pembelian():
    judul("DATA PEMBELIAN")
    data = st.session_state["data"]
    if data is None:
        pesan_belum_ada_data()
        return

    # tabel riwayat pembelian semua obat
    tabel_transaksi(data, "pembelian", "jumlah_dibeli", "Jumlah Dibeli")
