# tabel interaktif (pencarian, filter, halaman, dan ekspor excel) yang dipakai di beberapa halaman
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


# menampilkan tabel, lalu mengembalikan isi tombol yang diklik di baris tabel (misalnya kode obat)
def tampilkan_tabel(kunci, pengaturan_tabel):
    # kalau file excel sudah disiapkan, file dikirim ke browser untuk diunduh
    file_excel = st.session_state.pop(f"excel_{kunci}", None)
    if file_excel is not None:
        pengaturan_tabel = dict(pengaturan_tabel)
        pengaturan_tabel["unduhan"] = {
            "isi": base64.b64encode(file_excel).decode(),
            "nama_file": pengaturan_tabel["ekspor"]["nama_file"],
            "tanda": str(time.time()),
        }

    hasil = KOMPONEN_TABEL(
        key=kunci,
        data=pengaturan_tabel,
        on_tombol_change=lambda: None,
        on_ekspor_change=lambda: None,
    )

    # tombol ekspor diklik: buat file excel lalu muat ulang halaman supaya file terkirim
    if hasil.ekspor is not None:
        st.session_state[f"excel_{kunci}"] = buat_file_excel(pengaturan_tabel, hasil.ekspor)
        st.rerun()

    return hasil.tombol
