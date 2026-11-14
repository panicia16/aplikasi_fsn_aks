# halaman tentang aplikasi
import streamlit as st

from utils import URUTAN_FSN, WARNA_MUDA, WARNA_TUA, judul


# penjelasan singkat setiap kategori
PENJELASAN_FSN = {
    "Fast-Moving": "Obat dengan tingkat pergerakan yang tinggi.",
    "Slow-Moving": "Obat dengan tingkat pergerakan yang lambat.",
    "Non-Moving": "Obat yang hampir atau tidak mengalami pergerakan selama periode data.",
}

# tampilan khusus halaman tentang aplikasi
GAYA_TENTANG = """
<style>
.st-key-kartu_tentang p, .st-key-kartu_tentang li { line-height: 1.6; }
.baris-kategori { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin: 4px 0 12px 0; }
.kotak-kategori { border-radius: 10px; padding: 12px 16px; }
.kategori-nama { font-weight: 700; }
.kategori-isi { font-size: 0.9rem; color: #2f2e2b; }
@media (max-width: 640px) {
    .baris-kategori { grid-template-columns: 1fr; }
}
</style>
"""


# tiga kotak kategori dengan warna sesuai kategorinya
def kotak_kategori():
    semua_kotak = ""
    for kategori in URUTAN_FSN:
        semua_kotak += (
            f'<div class="kotak-kategori" style="background-color:{WARNA_MUDA[kategori]}">'
            f'<div class="kategori-nama" style="color:{WARNA_TUA[kategori]}">{kategori.replace("-", " ")}</div>'
            f'<div class="kategori-isi">{PENJELASAN_FSN[kategori]}</div></div>'
        )
    st.markdown(f'<div class="baris-kategori">{semua_kotak}</div>', unsafe_allow_html=True)


def halaman_tentang():
    st.markdown(GAYA_TENTANG, unsafe_allow_html=True)
    judul("TENTANG APLIKASI")

    with st.container(key="kartu_tentang"):
        st.subheader("Tujuan Aplikasi")
        st.markdown(
            "Aplikasi ini digunakan untuk mengklasifikasikan tingkat pergerakan persediaan obat "
            "di Apotek Kreator Kesehatan. Hasil klasifikasi disajikan sebagai informasi pendukung "
            "dalam pengelolaan persediaan obat."
        )

        st.subheader("Kategori Pergerakan Obat")
        st.markdown("Setiap obat (SKU) dikelompokkan ke dalam tiga kategori berikut.")
        kotak_kategori()

        st.subheader("Model Klasifikasi")
        st.markdown(
            "Klasifikasi dilakukan dengan algoritma *Random Forest*. Model dilatih menggunakan "
            "Data Kartu Stok Obat Apotek Kreator Kesehatan periode Januari hingga Desember 2022. "
        )
        st.markdown(
            "Fitur yang digunakan model adalah Golongan, Kategori, Total Masuk, Total Keluar, "
            "Frekuensi Transaksi, dan *Active Months*."
        )

        st.subheader("Penggunaan Model pada Data Baru")
        st.markdown(
            "- Model tidak dilatih ulang setiap kali data baru diunggah. Aplikasi selalu memakai model yang dilatih dari data tahun 2022.\n"
            "- Model membaca karakteristik obat, bukan kode atau nama obat. Karena itu, data periode lain dan obat baru tetap dapat diklasifikasikan.\n"
            "- Data yang diunggah sebaiknya mencakup satu tahun, sama seperti data yang dipakai saat pelatihan model.\n"
            "- Jika pola penjualan apotek berubah besar, model perlu dilatih ulang dengan data dan label yang baru."
        )

        st.subheader("Pengembang Aplikasi")
        st.markdown(
            "Aplikasi ini kembangkan oleh **Panicia** (NIM 535230059), Program Studi Teknik Informatika, "
            "Fakultas Teknologi Informasi, Universitas Tarumanagara, sebagai bagian dari skripsi "
            "dengan dosen pembimbing Lely Hiryanto, S.T., M.Sc., Ph.D."
        )