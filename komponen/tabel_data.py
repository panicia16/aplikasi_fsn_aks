# tabel interaktif (pencarian, filter, halaman, serta ekspor excel dan pdf) yang dipakai di beberapa halaman
import base64
import time
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st


# folder tempat file tabel_data.css dan tabel_data.js berada
FOLDER_KOMPONEN = Path(__file__).parent

# mendaftarkan tampilan tabel (css) dan cara kerjanya di browser (js) ke streamlit
KOMPONEN_TABEL = st.components.v2.component(
    "tabel_data",
    css=(FOLDER_KOMPONEN / "tabel_data.css").read_text(encoding="utf-8"),
    js=(FOLDER_KOMPONEN / "tabel_data.js").read_text(encoding="utf-8"),
)


# membuat file excel dari baris yang sedang tampil di tabel
def buat_file_excel(pengaturan_tabel, nomor_baris_tampil):
    # kolom nomor dan kolom tombol tidak ikut diekspor
    kolom_ekspor = [kolom for kolom in pengaturan_tabel["kolom"] if kolom.get("jenis") not in ("nomor", "tombol")]

    isi_excel = []
    for urutan, nomor_baris in enumerate(nomor_baris_tampil, start=1):
        baris = pengaturan_tabel["baris"][nomor_baris]
        satu_baris = {"No": urutan}
        for kolom in kolom_ekspor:
            satu_baris[kolom["judul"]] = baris.get(kolom["kunci"])
        isi_excel.append(satu_baris)

    nama_kolom = ["No"] + [kolom["judul"] for kolom in kolom_ekspor]
    tabel_excel = pd.DataFrame(isi_excel, columns=nama_kolom)

    # tabel ditulis ke file excel di memori, bukan ke folder
    berkas = BytesIO()
    tabel_excel.to_excel(berkas, index=False, sheet_name=pengaturan_tabel["ekspor"]["nama_lembar"])
    return berkas.getvalue()


# jenis file yang dikirim ke browser
TIPE_EXCEL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
TIPE_PDF = "application/pdf"


# menampilkan tabel, lalu mengembalikan isi tombol yang diklik di baris tabel (misalnya kode obat)
# buat_pdf diisi fungsi pembuat pdf jika tabel juga bisa diekspor ke pdf
def tampilkan_tabel(kunci, pengaturan_tabel, buat_pdf=None):
    pengaturan_tabel = dict(pengaturan_tabel)
    if pengaturan_tabel.get("ekspor"):
        pengaturan_tabel["ekspor"] = {**pengaturan_tabel["ekspor"], "pdf": buat_pdf is not None}

    # kalau file sudah disiapkan, file dikirim ke browser untuk diunduh
    unduhan = st.session_state.pop(f"unduhan_{kunci}", None)
    if unduhan is not None:
        isi_file, nama_file, tipe_file = unduhan
        pengaturan_tabel["unduhan"] = {
            "isi": base64.b64encode(isi_file).decode(),
            "nama_file": nama_file,
            "tipe": tipe_file,
            "tanda": str(time.time()),
        }

    hasil = KOMPONEN_TABEL(
        key=kunci,
        data=pengaturan_tabel,
        on_tombol_change=lambda: None,
        on_ekspor_change=lambda: None,
        on_ekspor_pdf_change=lambda: None,
    )

    # tombol ekspor excel diklik: buat file excel lalu muat ulang halaman supaya file terkirim
    if hasil.ekspor is not None:
        isi_excel = buat_file_excel(pengaturan_tabel, hasil.ekspor)
        st.session_state[f"unduhan_{kunci}"] = (isi_excel, pengaturan_tabel["ekspor"]["nama_file"], TIPE_EXCEL)
        st.rerun()

    # tombol ekspor pdf diklik: buat file pdf dari baris yang sedang tampil
    if buat_pdf is not None and getattr(hasil, "ekspor_pdf", None) is not None:
        isi_pdf = buat_pdf(hasil.ekspor_pdf)
        st.session_state[f"unduhan_{kunci}"] = (isi_pdf, pengaturan_tabel["ekspor"]["nama_file_pdf"], TIPE_PDF)
        st.rerun()

    return hasil.tombol