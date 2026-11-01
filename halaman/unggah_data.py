# halaman unggah dataset
import pandas as pd
import streamlit as st

from prapemrosesan.prapemrosesan import FITUR_MODEL, proses_kartu_stok, validasi_format
from utils import LOKASI_MODEL, angka, hapus_data, judul, muat_model, pindah_halaman, simpan_data


# tampilan khusus halaman unggah dataset
GAYA_UNGGAH = """
<style>
/* panel putih tempat unggah file */
.st-key-panel_unggah { background-color: #ffffff; border-radius: 12px; padding: 28px 32px; }
.st-key-panel_unggah [data-testid="stMarkdownContainer"] { text-align: center; }

/* kotak tarik dan lepas file */
.st-key-panel_unggah [data-testid="stFileUploaderDropzone"] {
    flex-direction: column; align-items: center; justify-content: center; text-align: center;
    gap: 12px; padding: 32px 16px; background-color: #f5fdfb; border: 2px dashed #2bb39c;
}
.st-key-panel_unggah [data-testid="stFileUploaderDropzone"]:has([data-testid="stFileUploaderDropzoneInstructions"])::before {
    content: "Drag & drop file dataset di sini\\A atau klik di sini untuk memilih file"; white-space: pre-line; color: #52514e; font-weight: 600;
    padding-top: 52px; background-repeat: no-repeat; background-position: top center; background-size: 42px 42px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%230b0b0b'%3E%3Cpath d='M19 15v4H5v-4H3v6h18v-6zM11 5.83V16h2V5.83l3.09 3.08L17.5 7.5 12 2 6.5 7.5l1.41 1.41z'/%3E%3C/svg%3E");
}
.st-key-panel_unggah [data-testid="stFileUploaderDropzone"]:has([data-testid="stFileUploaderDropzoneInstructions"]) button { display: none; }
.st-key-panel_unggah [data-testid="stFileUploaderDropzoneInstructions"] { flex: none; justify-content: center; text-align: center; }
[data-testid="stFileUploader"] button[aria-label="Add files"] { display: none; }

/* setelah file dipilih, kotak tidak bisa diklik lagi kecuali tombol hapus file */
.st-key-panel_unggah [data-testid="stFileUploaderDropzone"]:not(:has([data-testid="stFileUploaderDropzoneInstructions"])) { pointer-events: none; cursor: default; }
.st-key-panel_unggah [data-testid="stFileUploaderDropzone"]:not(:has([data-testid="stFileUploaderDropzoneInstructions"])) button { pointer-events: auto; cursor: pointer; }

/* pesan gagal dan animasi saat data diproses */
.pesan-gagal { color: #e34948; font-weight: 800; font-size: 1.3rem; padding-top: 24px; }
.memuat { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 12px 0; color: #07706e; font-weight: 600; }
.lingkaran { width: 42px; height: 42px; border: 5px solid #c9efe8; border-top-color: #07706e; border-radius: 50%; animation: putar 0.9s linear infinite; }
.titik::after { content: ""; animation: titik 1.2s steps(1) infinite; }
@keyframes putar { to { transform: rotate(360deg); } }
@keyframes titik { 0% { content: ""; } 25% { content: "."; } 50% { content: ".."; } 75% { content: "..."; } }

/* angka ringkasan dan judulnya dibuat rata tengah */
.st-key-panel_unggah [data-testid="stMetric"] { text-align: center; }
.st-key-panel_unggah [data-testid="stMetricLabel"],
.st-key-panel_unggah [data-testid="stMetricValue"] { justify-content: center; text-align: center; width: 100%; }

/* tiga tombol (lihat data, unggah lagi, hapus data) dibuat sama besar */
.st-key-tombol_lihat button,
.st-key-tombol_hapus button,
.st-key-wadah_unggah_lagi [data-testid="stFileUploaderDropzone"] button {
    width: 100%; min-height: 44px; border-radius: 22px; padding: 0 16px;
}
.st-key-tombol_lihat button p,
.st-key-tombol_hapus button p { font-size: 0.95rem; font-weight: 600; }
.st-key-wadah_unggah_lagi [data-testid="stFileUploader"] { width: 100%; }
.st-key-wadah_unggah_lagi [data-testid="stFileUploaderDropzone"] { align-items: stretch; }

/* saat file dipilih lewat tombol unggah lagi, nama file tidak ditampilkan di tombol,
   tombol hanya bertuliskan "Memuat file..." sampai halaman berpindah ke kotak unggah */
.st-key-panel_unggah .st-key-wadah_unggah_lagi [data-testid="stFileUploaderDropzone"]:not(:has([data-testid="stFileUploaderDropzoneInstructions"])) {
    position: relative; min-height: 44px; padding: 0; border: 1px solid #07706e; border-radius: 22px; background-color: #ffffff;
}
.st-key-panel_unggah .st-key-wadah_unggah_lagi [data-testid="stFileUploaderDropzone"]:not(:has([data-testid="stFileUploaderDropzoneInstructions"])) > * { display: none; }
.st-key-panel_unggah .st-key-wadah_unggah_lagi [data-testid="stFileUploaderDropzone"]:not(:has([data-testid="stFileUploaderDropzoneInstructions"]))::after {
    content: "Memuat file..."; position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
    color: #07706e; font-size: 0.95rem; font-weight: 600;
}
.st-key-wadah_unggah_lagi [data-testid="stFileUploaderFile"] { display: none; }

/* warna tombol lihat data (hijau), unggah lagi (putih), dan hapus data (merah) */
.st-key-tombol_lihat button { border: 1px solid #07706e; color: #ffffff; background-color: #07706e; }
.st-key-tombol_lihat button:hover { border-color: #1f9884; color: #ffffff; background-color: #1f9884; }
.st-key-tombol_hapus button { border: 1px solid #e34948; color: #e34948; background-color: #ffffff; }
.st-key-tombol_hapus button:hover { border-color: #e34948; color: #ffffff; background-color: #e34948; }
.st-key-tombol_yakin_hapus button { border: none; color: #ffffff; background-color: #e34948; }
.st-key-tombol_yakin_hapus button:hover { color: #ffffff; background-color: #c0302f; }

/* tampilan ponsel: jarak di dalam panel lebih kecil */
@media (max-width: 640px) {
    .st-key-panel_unggah { padding: 16px; }
    .st-key-panel_unggah [data-testid="stFileUploaderDropzone"] { padding: 24px 8px; }
    .pesan-gagal { font-size: 1.1rem; padding-top: 12px; }
}
</style>
"""

# cetakan gaya untuk mengubah kotak unggah menjadi sebuah tombol
CETAKAN_TOMBOL_UNGGAH = """
<style>
.st-key-panel_unggah .st-key-NAMA_WADAH [data-testid="stFileUploaderDropzone"] { border: none; background-color: transparent; padding: 0; min-height: 0; }
.st-key-panel_unggah .st-key-NAMA_WADAH [data-testid="stFileUploaderDropzone"]:has([data-testid="stFileUploaderDropzoneInstructions"])::before { content: none; }
.st-key-panel_unggah .st-key-NAMA_WADAH [data-testid="stFileUploaderDropzoneInstructions"] { display: none; }
.st-key-panel_unggah .st-key-NAMA_WADAH [data-testid="stFileUploaderDropzone"]:has([data-testid="stFileUploaderDropzoneInstructions"]) button {
    display: inline-flex; align-items: center; justify-content: center; width: LEBAR_TOMBOL; min-height: 44px; border-radius: 22px;
    border: 1px solid #07706e; background-color: WARNA_LATAR; padding: 0 36px;
}
.st-key-panel_unggah .st-key-NAMA_WADAH [data-testid="stFileUploaderDropzone"]:has([data-testid="stFileUploaderDropzoneInstructions"]) button > * { display: none; }
.st-key-panel_unggah .st-key-NAMA_WADAH [data-testid="stFileUploaderDropzone"]:has([data-testid="stFileUploaderDropzoneInstructions"]) button::after {
    content: "TULISAN_TOMBOL"; color: WARNA_TULISAN; font-size: 0.95rem; font-weight: 600;
}
</style>
"""

# label tempat unggah file (tidak ditampilkan), dipakai sama pada kotak unggah utama dan tombol unggah lagi
LABEL_UPLOADER = "Unggah file dataset"

# animasi lingkaran berputar saat data diproses
ANIMASI_MEMUAT = '<div class="memuat"><div class="lingkaran"></div><div>Memproses data<span class="titik"></span></div></div>'

# mengisi cetakan gaya tombol unggah sesuai wadah, tulisan, dan warnanya
def gaya_tombol_unggah(nama_wadah, tulisan, warna_latar, warna_tulisan, lebar):
    gaya = CETAKAN_TOMBOL_UNGGAH.replace("NAMA_WADAH", nama_wadah)
    gaya = gaya.replace("TULISAN_TOMBOL", tulisan)
    gaya = gaya.replace("WARNA_LATAR", warna_latar)
    gaya = gaya.replace("WARNA_TULISAN", warna_tulisan)
    gaya = gaya.replace("LEBAR_TOMBOL", lebar)
    return gaya

# tombol yang diletakkan di tengah panel
def tombol_tengah(tulisan, kunci):
    kolom_tengah = st.columns([1, 1, 1])[1]
    return kolom_tengah.button(tulisan, key=kunci, type="primary", width="stretch")

# menyimpan pesan gagal, mengosongkan pilihan file, lalu memuat ulang halaman
def unggah_gagal(daftar_pesan):
    st.session_state["pesan_gagal"] = daftar_pesan
    st.session_state["kunci_uploader"] += 1
    st.rerun()

# dijalankan sebelum halaman digambar ulang, supaya langsung kembali ke ringkasan dataset tanpa berkedip
def kembali_ke_data_sebelumnya():
    st.session_state["pesan_gagal"] = None
    st.session_state["status_unggah"] = "selesai"

# jendela konfirmasi sebelum data dihapus
@st.dialog("Hapus Data")
def konfirmasi_hapus():
    st.write("Seluruh data yang sudah diunggah beserta hasil klasifikasinya akan dihapus dari aplikasi. Lanjutkan?")
    kiri, kanan = st.columns(2)
    if kiri.button("Batal", width="stretch"):
        st.rerun()
    with kanan.container(key="tombol_yakin_hapus"):
        if st.button("Hapus", width="stretch"):
            hapus_data()
            st.rerun()

# tampilan setelah dataset selesai diproses
def tampilan_selesai():
    ringkasan = st.session_state["data"]["ringkasan"]
    with st.container(border=True, key="panel_unggah"):
        st.success("Dataset telah selesai diproses.")

        # ringkasan hasil pengolahan
        kolom_1, kolom_2, kolom_3 = st.columns(3)
        kolom_1.metric("Baris data", angka(ringkasan["jumlah_baris_diunggah"]))
        kolom_2.metric("Baris diproses", angka(ringkasan["jumlah_baris_diproses"]))
        kolom_3.metric("Jumlah SKU", angka(ringkasan["jumlah_sku"]))
        st.write(f"Periode data: **{ringkasan['tanggal_awal']:%d-%m-%Y}** s.d. **{ringkasan['tanggal_akhir']:%d-%m-%Y}**")
        if ringkasan.get("peringatan_periode"):
            st.warning(ringkasan["peringatan_periode"])
        # tiga tombol sejajar dengan lebar yang sama: lihat data, unggah lagi, hapus data
        st.markdown(gaya_tombol_unggah("wadah_unggah_lagi", "Unggah Lagi", "#ffffff", "#07706e", "100%"), unsafe_allow_html=True)
        _, kolom_lihat, kolom_unggah, kolom_hapus, _ = st.columns([1, 2, 2, 2, 1], vertical_alignment="center")

        with kolom_lihat.container(key="tombol_lihat"):
            if st.button("Lihat Data", width="stretch"):
                pindah_halaman("data_klasifikasi")

        # tombol unggah lagi langsung membuka pilihan file
        # label dan kuncinya sama dengan kotak unggah utama, supaya file yang dipilih langsung tampil di kotak tersebut
        with kolom_unggah.container(key="wadah_unggah_lagi"):
            file_baru = st.file_uploader(
                LABEL_UPLOADER, type=["xlsx"], key=f"uploader_{st.session_state['kunci_uploader']}",
                label_visibility="collapsed",
            )

        with kolom_hapus.container(key="tombol_hapus"):
            if st.button("Hapus Data", width="stretch"):
                konfirmasi_hapus()

        # kalau file baru dipilih, kembali ke tampilan unggah
        if file_baru is not None:
            st.session_state["status_unggah"] = None
            st.rerun()

# membaca, memeriksa, mengolah, dan mengklasifikasikan file yang diunggah
def proses_file(file_unggahan):
    # animasi memuat selama data diproses
    tempat_memuat = st.empty()
    tempat_memuat.markdown(ANIMASI_MEMUAT, unsafe_allow_html=True)

    # membaca sheet pertama file excel
    try:
        data_mentah = pd.read_excel(file_unggahan, sheet_name=0)
    except Exception:
        unggah_gagal(["File tidak dapat dibaca sebagai file Excel."])
        return

    # memeriksa kolom yang wajib ada
    kesalahan = validasi_format(data_mentah)
    if kesalahan:
        unggah_gagal(kesalahan)
        return

    # membuka model
    try:
        model = muat_model()
    except FileNotFoundError:
        tempat_memuat.empty()
        st.error(f"File model '{LOKASI_MODEL}' tidak ditemukan. Letakkan file model di dalam folder model.")
        return

    # mengolah kartu stok menjadi data per sku
    try:
        hasil = proses_kartu_stok(data_mentah)
    except Exception as kesalahan_proses:
        unggah_gagal([f"Data tidak dapat diproses: {kesalahan_proses}"])
        return

    if hasil["sku"].empty:
        tempat_memuat.empty()
        st.error("Tidak ada data obat non-konsinyasi yang dapat diproses.")
        return

    # klasifikasi setiap sku dengan model random forest
    hasil["sku"]["hasil_klasifikasi"] = model.predict(hasil["sku"][FITUR_MODEL])

    # peringatan kalau periode data kurang dari satu tahun, karena model dibuat dari data satu tahun
    ringkasan = hasil["ringkasan"]
    lama_hari = (ringkasan["tanggal_akhir"] - ringkasan["tanggal_awal"]).days + 1
    if lama_hari < 330:
        ringkasan["peringatan_periode"] = (
            f"Periode data hanya {lama_hari} hari. Model dibangun dengan data satu tahun, "
            "sehingga hasil klasifikasi untuk periode yang lebih pendek perlu ditafsirkan dengan hati-hati."
        )

    # hasil disimpan ke file supaya tetap ada saat aplikasi dibuka lagi
    simpan_data(hasil)

    # hasil juga disimpan di memori aplikasi
    st.session_state["data"] = hasil
    st.session_state["status_unggah"] = "selesai"
    st.session_state["kode_detail"] = None
    st.session_state["kunci_uploader"] += 1
    st.rerun()


def halaman_unggah():
    st.markdown(GAYA_UNGGAH, unsafe_allow_html=True)
    judul("UNGGAH DATASET")

    # file yang sedang dipilih diperiksa sebelum halaman digambar, supaya halaman tidak berkedip
    # saat berpindah antara ringkasan dataset dan kotak unggah
    file_terpilih = st.session_state.get(f"uploader_{st.session_state['kunci_uploader']}")
    if st.session_state["data"] is not None and not st.session_state.get("pesan_gagal"):
        # ada file baru yang dipilih: tampilkan kotak unggah, tidak ada file: tampilkan ringkasan dataset
        st.session_state["status_unggah"] = None if file_terpilih is not None else "selesai"

    # kalau dataset sudah selesai diproses, tampilkan ringkasannya
    if st.session_state["status_unggah"] == "selesai" and st.session_state["data"] is not None:
        tampilan_selesai()
        return

    pesan_gagal = st.session_state.get("pesan_gagal")
    with st.container(border=True, key="panel_unggah"):
        # pesan format tidak sesuai atau petunjuk unggah
        if pesan_gagal:
            st.markdown(gaya_tombol_unggah("wadah_uploader", "Pilih File", "#07706e", "#ffffff", "auto"), unsafe_allow_html=True)
            st.markdown("<style>.st-key-wadah_uploader { width: fit-content; margin: 0 auto; }</style>", unsafe_allow_html=True)
            st.markdown('<div class="pesan-gagal">Format File Tidak Sesuai!</div>', unsafe_allow_html=True)
            for pesan in pesan_gagal:
                st.write(pesan)
        else:
            st.markdown("Unggah file kartu stok dalam format **Excel (.xlsx)** dengan periode data **satu tahun**.")

        # tempat memilih file (tampil sebagai tombol pilih file kalau format sebelumnya salah)
        with st.container(key="wadah_uploader"):
            file_unggahan = st.file_uploader(
                LABEL_UPLOADER, type=["xlsx"], key=f"uploader_{st.session_state['kunci_uploader']}",
                label_visibility="collapsed",
            )

        if file_unggahan is None:
            # dataset sebelumnya masih tersimpan, jadi pengguna bisa kembali ke ringkasannya
            if st.session_state["data"] is not None:
                # file baru dibatalkan (tombol x) sebelum diproses, langsung kembali ke ringkasan dataset sebelumnya
                if not pesan_gagal:
                    st.session_state["status_unggah"] = "selesai"
                    st.rerun()
                # file baru gagal diproses, pengguna bisa memilih file lain atau kembali ke dataset sebelumnya
                kolom_tengah = st.columns([1, 1, 1])[1]
                kolom_tengah.button(
                    "Kembali ke Data Sebelumnya", key="tombol_kembali", type="primary", width="stretch",
                    on_click=kembali_ke_data_sebelumnya,
                )
            return

        # pesan gagal dihapus setelah file baru dipilih
        if pesan_gagal:
            st.session_state["pesan_gagal"] = None
            st.rerun()

        st.write(f"File berhasil diunggah: **{file_unggahan.name}**")
        if tombol_tengah("Unggah dan Proses", "tombol_proses"):
            proses_file(file_unggahan)