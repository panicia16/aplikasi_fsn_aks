# halaman data penjualan
import streamlit as st

from utils import judul, pesan_belum_ada_data, tabel_transaksi


def halaman_penjualan():
    judul("DATA PENJUALAN")
    data = st.session_state["data"]
    if data is None:
        pesan_belum_ada_data()
        return

    # tabel riwayat penjualan semua obat
    tabel_transaksi(data, "penjualan", "jumlah_terjual", "Jumlah Terjual")
