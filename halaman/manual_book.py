# halaman manual book
import base64
import io
import os

import pypdfium2
import streamlit as st

from utils import FOLDER_APLIKASI, judul


# letak file manual book
LOKASI_MANUAL = os.path.join(FOLDER_APLIKASI, "dokumen", "manual_book.pdf")


# setiap halaman pdf diubah menjadi gambar jpg dalam bentuk teks base64
# hasilnya disimpan supaya tidak diulang, dan dibuat ulang jika file manual book diganti (waktu_ubah)
@st.cache_data(show_spinner="Memuat manual book...")
def ubah_pdf_jadi_gambar(lokasi_file, waktu_ubah):
    dokumen = pypdfium2.PdfDocument(lokasi_file)
    daftar_gambar = []
    for halaman in dokumen:
        gambar = halaman.render(scale=2).to_pil().convert("RGB")
        isi_gambar = io.BytesIO()
        gambar.save(isi_gambar, format="JPEG", quality=80)
        daftar_gambar.append(base64.b64encode(isi_gambar.getvalue()).decode())
    dokumen.close()
    return daftar_gambar


# halaman html penampil: toolbar zoom di atas, halaman pdf di bawahnya
def buat_penampil(daftar_gambar):
    semua_halaman = "".join(
        f'<img class="halaman" src="data:image/jpeg;base64,{gambar}" alt="Halaman {nomor}">'
        for nomor, gambar in enumerate(daftar_gambar, start=1)
    )
    return f"""
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* {{ box-sizing: border-box; }}
html, body {{ height: 100%; }}
body {{ margin: 0; display: flex; flex-direction: column; font-family: "Source Sans Pro", Arial, sans-serif; }}
.toolbar {{
    position: sticky; top: 0; z-index: 2; display: flex; align-items: center; justify-content: center;
    gap: 8px; padding: 8px 12px; background-color: #07706e; color: #ffffff; flex-wrap: wrap;
}}
.toolbar button {{
    border: none; border-radius: 6px; background-color: #1f9884; color: #ffffff;
    font-size: 15px; font-weight: 600; min-width: 36px; height: 32px; padding: 0 10px; cursor: pointer;
}}
.toolbar button:hover {{ background-color: #2bb39c; }}
.persen {{ min-width: 52px; text-align: center; font-weight: 600; }}
.nomor {{ margin-left: 12px; font-size: 14px; }}
.isi {{ flex: 1; overflow: auto; background-color: #e3e7e6; padding: 16px 0; }}
.halaman {{
    display: block; margin: 0 auto 16px auto; background-color: #ffffff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
}}
</style>
</head>
<body>
<div class="toolbar">
    <button onclick="ubahZoom(-0.25)" title="Perkecil">&minus;</button>
    <span class="persen" id="persen">100%</span>
    <button onclick="ubahZoom(0.25)" title="Perbesar">+</button>
    <button onclick="aturZoom(1)" title="Sesuaikan lebar">Sesuaikan Lebar</button>
    <span class="nomor" id="nomor">Halaman 1 dari {len(daftar_gambar)}</span>
</div>
<div class="isi" id="isi">{semua_halaman}</div>
<script>
const isi = document.getElementById("isi");
const semuaHalaman = document.querySelectorAll(".halaman");
let zoom = 1;

// lebar halaman pada zoom 100% mengikuti lebar penampil, paling lebar 750 piksel
function lebarDasar() {{
    return Math.min(isi.clientWidth - 32, 750);
}}

function aturZoom(nilai) {{
    zoom = Math.min(3, Math.max(0.5, nilai));
    semuaHalaman.forEach((halaman) => {{ halaman.style.width = (lebarDasar() * zoom) + "px"; }});
    document.getElementById("persen").textContent = Math.round(zoom * 100) + "%";
}}

function ubahZoom(selisih) {{
    aturZoom(zoom + selisih);
}}

// nomor halaman yang sedang dilihat diperbarui saat di-scroll
isi.addEventListener("scroll", () => {{
    let nomor = 1;
    semuaHalaman.forEach((halaman, urutan) => {{
        if (halaman.offsetTop - isi.offsetTop <= isi.scrollTop + isi.clientHeight / 3) {{ nomor = urutan + 1; }}
    }});
    document.getElementById("nomor").textContent = "Halaman " + nomor + " dari " + semuaHalaman.length;
}});

window.addEventListener("resize", () => aturZoom(zoom));
aturZoom(1);
</script>
</body>
</html>
"""


def halaman_manual():
    judul("MANUAL BOOK")

    if not os.path.exists(LOKASI_MANUAL):
        st.error(f"File manual book '{LOKASI_MANUAL}' tidak ditemukan. Letakkan file manual book di dalam folder dokumen.")
        return

    with open(LOKASI_MANUAL, "rb") as file_manual:
        isi_manual = file_manual.read()

    # tombol unduh manual book
    st.download_button(
        "Unduh Manual Book",
        data=isi_manual,
        file_name="Manual Book Aplikasi Klasifikasi FSN.pdf",
        mime="application/pdf",
        icon=":material/download:",
        on_click="ignore",
    )

    # manual book ditampilkan di penampil dengan tombol zoom, bisa dibuka juga di hp
    daftar_gambar = ubah_pdf_jadi_gambar(LOKASI_MANUAL, os.path.getmtime(LOKASI_MANUAL))
    st.iframe(buat_penampil(daftar_gambar), height=850)