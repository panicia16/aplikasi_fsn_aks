# membuat laporan penjualan dan laporan pembelian dalam bentuk pdf
from datetime import datetime, timedelta, timezone
from io import BytesIO

import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

import pandas as pd

from utils import angka, label_bulan, rekap_bulanan


# pilihan periode 10 obat teratas, sama dengan pilihan di halaman
SELURUH_PERIODE = "Seluruh periode"

# warna yang sama dengan tampilan aplikasi
HIJAU_TUA = colors.HexColor("#07706e")
HIJAU_MUDA = colors.HexColor("#f2fbf9")
GARIS = colors.HexColor("#cfe9e4")

# jam laporan dicetak memakai Waktu Indonesia Barat
WIB = timezone(timedelta(hours=7))

# gaya tulisan pada laporan
GAYA_APOTEK = ParagraphStyle("apotek", fontName="Helvetica-Bold", fontSize=11, textColor=HIJAU_TUA, alignment=TA_CENTER)
GAYA_JUDUL = ParagraphStyle("judul", fontName="Helvetica-Bold", fontSize=16, leading=20, alignment=TA_CENTER, spaceBefore=4)
GAYA_KETERANGAN = ParagraphStyle("keterangan", fontName="Helvetica", fontSize=9, leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#52514e"))
GAYA_SUBJUDUL = ParagraphStyle("subjudul", fontName="Helvetica-Bold", fontSize=12, textColor=HIJAU_TUA, spaceBefore=14, spaceAfter=6)
GAYA_ISI = ParagraphStyle("isi", fontName="Helvetica", fontSize=9, leading=11)
GAYA_ISI_KECIL = ParagraphStyle("isi_kecil", fontName="Helvetica", fontSize=7.5, leading=9)

# tulisan yang berbeda untuk laporan penjualan dan laporan pembelian
TEKS_LAPORAN = {
    "penjualan": {"judul": "LAPORAN PENJUALAN", "nama": "Penjualan", "kata": "terjual", "warna": "#2a78d6", "teratas": "10 Obat Terlaris"},
    "pembelian": {"judul": "LAPORAN PEMBELIAN", "nama": "Pembelian", "kata": "dibeli", "warna": "#07706e", "teratas": "10 Obat Pembelian Terbanyak"},
}


# angka pada sumbu grafik memakai titik sebagai pemisah ribuan
FORMAT_ANGKA = FuncFormatter(lambda nilai, posisi: angka(nilai))


# grafik matplotlib diubah menjadi gambar untuk dimasukkan ke pdf
def gambar_grafik(fig, lebar_cm):
    berkas = BytesIO()
    fig.savefig(berkas, format="png", dpi=200, bbox_inches="tight")
    berkas.seek(0)
    lebar_asli, tinggi_asli = fig.get_size_inches()
    return Image(berkas, width=lebar_cm * cm, height=lebar_cm * cm * tinggi_asli / lebar_asli)

# grafik batang jumlah obat per bulan
def grafik_bulanan(rekap, teks):
    fig = Figure(figsize=(8, 3.2))
    ax = fig.subplots()
    batang = ax.bar(rekap["bulan"], rekap["jumlah"], color=teks["warna"])
    ax.bar_label(batang, labels=[angka(nilai) for nilai in rekap["jumlah"]], fontsize=7, padding=2)
    ax.set_ylabel(f"Jumlah obat {teks['kata']}", fontsize=8)
    ax.tick_params(axis="x", labelsize=7, rotation=45)
    ax.tick_params(axis="y", labelsize=7)
    ax.yaxis.set_major_formatter(FORMAT_ANGKA)
    ax.spines[["top", "right"]].set_visible(False)
    ax.margins(y=0.12)
    return gambar_grafik(fig, 17)

# jumlah obat setiap hari, hari tanpa transaksi diisi 0
def hitung_harian(transaksi):
    jumlah_per_hari = transaksi.groupby(transaksi["tanggal"].dt.normalize())["jumlah"].sum()
    semua_hari = pd.date_range(jumlah_per_hari.index.min(), jumlah_per_hari.index.max(), freq="D")
    return jumlah_per_hari.reindex(semua_hari, fill_value=0)

# grafik batang jumlah obat per hari, dipakai jika periode data hanya satu bulan
def grafik_harian(jumlah_per_hari, teks):
    semua_hari = jumlah_per_hari.index
    fig = Figure(figsize=(8, 3.2))
    ax = fig.subplots()
    ax.bar([f"{hari:%d}" for hari in jumlah_per_hari.index], jumlah_per_hari.values, color=teks["warna"])
    ax.set_xlabel(f"Tanggal ({label_bulan(semua_hari[0].to_period('M'))})", fontsize=8)
    ax.set_ylabel(f"Jumlah obat {teks['kata']}", fontsize=8)
    ax.tick_params(axis="both", labelsize=7)
    ax.yaxis.set_major_formatter(FORMAT_ANGKA)
    ax.spines[["top", "right"]].set_visible(False)
    return gambar_grafik(fig, 17)

# grafik batang sepuluh obat teratas
def grafik_teratas(teratas, teks):
    fig = Figure(figsize=(8, 3.6))
    ax = fig.subplots()
    data_grafik = teratas.iloc[::-1]
    nama = [nama if len(nama) <= 40 else nama[:38] + "..." for nama in data_grafik["nama_obat"]]
    batang = ax.barh(nama, data_grafik["jumlah"], color=teks["warna"])
    ax.bar_label(batang, labels=[angka(nilai) for nilai in data_grafik["jumlah"]], fontsize=7, padding=3)
    ax.set_xlabel(f"Jumlah obat {teks['kata']}", fontsize=8)
    ax.tick_params(axis="both", labelsize=7)
    ax.xaxis.set_major_formatter(FORMAT_ANGKA)
    ax.spines[["top", "right"]].set_visible(False)
    ax.margins(x=0.1)
    return gambar_grafik(fig, 17)

# tabel dengan baris judul hijau dan garis tipis
def tabel_laporan(isi, lebar_kolom, kolom_kanan, ukuran_huruf=8.5):
    tabel = Table(isi, colWidths=[lebar * cm for lebar in lebar_kolom], repeatRows=1)
    tabel.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HIJAU_TUA),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), ukuran_huruf),
        ("GRID", (0, 0), (-1, -1), 0.5, GARIS),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, HIJAU_MUDA]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (kolom_kanan, 0), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return tabel

# nomor halaman di bagian bawah setiap halaman
def nomor_halaman(kanvas, dokumen):
    kanvas.setFont("Helvetica", 8)
    kanvas.setFillColor(colors.HexColor("#52514e"))
    kanvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Halaman {dokumen.page}")
    kanvas.drawString(2 * cm, 1.2 * cm, "Apotek Kreator Kesehatan")


# sepuluh obat dengan jumlah terbanyak, sama seperti kartu 10 obat teratas di halaman
# jika periode_teratas berisi nama bulan, hanya transaksi pada bulan itu yang dihitung
def hitung_teratas(transaksi, periode_teratas):
    if periode_teratas != SELURUH_PERIODE:
        bulan_transaksi = transaksi["tanggal"].dt.to_period("M").map(lambda bulan: label_bulan(bulan) if pd.notna(bulan) else "")
        transaksi = transaksi[bulan_transaksi == periode_teratas]
    teratas = transaksi.groupby(["kode_obat", "nama_obat"], as_index=False)["jumlah"].sum()
    return teratas.sort_values("jumlah", ascending=False).head(10)


# membuat file pdf laporan penjualan atau pembelian
# ringkasan, grafik, dan 10 obat teratas dihitung dari seluruh transaksi, sama seperti di halaman
# tabel riwayat di bagian bawah berisi baris yang sedang tampil di tabel (mengikuti pencarian dan filter)
# periode_teratas mengikuti pilihan periode pada kartu 10 obat teratas di halaman
def buat_laporan_pdf(ringkasan, jenis, semua_transaksi, transaksi_tabel, periode_teratas=SELURUH_PERIODE):
    teks = TEKS_LAPORAN[jenis]
    kata = teks["kata"]
    waktu_cetak = datetime.now(WIB)

    keterangan = (
        f"Periode data: {ringkasan['tanggal_awal']:%d-%m-%Y} s.d. {ringkasan['tanggal_akhir']:%d-%m-%Y}<br/>"
        f"Dicetak: {waktu_cetak:%d-%m-%Y %H:%M} WIB"
    )
    isi = [
        Paragraph("APOTEK KREATOR KESEHATAN", GAYA_APOTEK),
        Paragraph(teks["judul"], GAYA_JUDUL),
        Paragraph(keterangan, GAYA_KETERANGAN),
        Spacer(1, 8),
    ]

    if len(semua_transaksi) == 0:
        isi.append(Paragraph(f"Belum ada data {jenis}.", GAYA_ISI))
    else:
        # jumlah obat setiap bulan selama periode data, sama seperti grafik di halaman
        daftar_periode = pd.period_range(ringkasan["tanggal_awal"], ringkasan["tanggal_akhir"], freq="M")
        rekap = rekap_bulanan(semua_transaksi, "jumlah", daftar_periode)
        terbanyak = rekap.loc[rekap["jumlah"].idxmax()]

        # ringkasan
        isi.append(Paragraph(f"Ringkasan {teks['nama']} (Seluruh Data)", GAYA_SUBJUDUL))
        isi.append(tabel_laporan(
            [
                ["Keterangan", "Nilai"],
                ["Jumlah transaksi", angka(len(semua_transaksi))],
                [f"Total obat {kata}", angka(semua_transaksi["jumlah"].sum())],
                [f"Bulan {jenis} terbanyak", f"{terbanyak['bulan']} ({angka(terbanyak['jumlah'])} obat {kata})"],
            ],
            [8, 9], 1,
        ))

        # grafik jumlah obat per bulan, atau per hari jika periode data hanya satu bulan
        # judul dan grafik dijaga tetap di halaman yang sama
        # di bawah grafik ada tabel angkanya, sama seperti bagian 10 obat teratas
        judul_jumlah = f"Jumlah Obat {kata.capitalize()}"
        if len(daftar_periode) == 1:
            jumlah_per_hari = hitung_harian(semua_transaksi)
            judul_grafik = f"Statistik {teks['nama']} per Hari (Seluruh Data)"
            gambar = grafik_harian(jumlah_per_hari, teks)
            baris_jumlah = [["No", "Tanggal", judul_jumlah]]
            for nomor, (hari, jumlah) in enumerate(jumlah_per_hari.items(), start=1):
                baris_jumlah.append([nomor, f"{hari:%d-%m-%Y}", angka(jumlah)])
        else:
            judul_grafik = f"Statistik {teks['nama']} per Bulan (Seluruh Data)"
            gambar = grafik_bulanan(rekap, teks)
            baris_jumlah = [["No", "Bulan", judul_jumlah]]
            for nomor, baris in enumerate(rekap.itertuples(), start=1):
                baris_jumlah.append([nomor, baris.bulan, angka(baris.jumlah)])
        isi.append(KeepTogether([Paragraph(judul_grafik, GAYA_SUBJUDUL), gambar]))
        isi.append(Spacer(1, 6))
        tabel_jumlah = tabel_laporan(baris_jumlah, [1.2, 9.3, 6.5], 2)
        # tabel per bulan pendek sehingga tidak dipotong, tabel per hari boleh berlanjut ke halaman berikutnya
        isi.append(tabel_jumlah if len(daftar_periode) == 1 else KeepTogether([tabel_jumlah]))

        # grafik dan tabel sepuluh obat teratas sesuai periode yang dipilih
        teratas = hitung_teratas(semua_transaksi, periode_teratas)
        judul_teratas = f"{teks['teratas']} ({periode_teratas})"
        if teratas.empty:
            isi.append(Paragraph(judul_teratas, GAYA_SUBJUDUL))
            isi.append(Paragraph(f"Tidak ada obat {kata} pada {periode_teratas}.", GAYA_ISI))
        else:
            isi.append(KeepTogether([Paragraph(judul_teratas, GAYA_SUBJUDUL), grafik_teratas(teratas, teks)]))
            isi.append(Spacer(1, 6))
            baris_teratas = [["No", "Kode SKU", "Nama Obat", f"Jumlah {kata.capitalize()}"]]
            for nomor, baris in enumerate(teratas.itertuples(), start=1):
                baris_teratas.append([nomor, baris.kode_obat, Paragraph(str(baris.nama_obat), GAYA_ISI), angka(baris.jumlah)])
            # tabel 10 obat teratas tidak dipotong ke halaman berikutnya
            isi.append(KeepTogether([tabel_laporan(baris_teratas, [1.2, 3.3, 9, 3.5], 3)]))

    # tabel riwayat transaksi di bagian paling bawah, berisi baris yang tampil di tabel aplikasi
    # jika tabel di aplikasi dicari atau difilter, judulnya diberi tanda dan ada catatan di bawahnya
    ada_filter = len(transaksi_tabel) < len(semua_transaksi)
    if ada_filter:
        isi.append(Paragraph(f"Riwayat {teks['nama']} (Sesuai Pencarian atau Filter)", GAYA_SUBJUDUL))
        isi.append(Paragraph(
            f"<b>Catatan:</b> ringkasan, statistik, dan {teks['teratas'].lower()} di atas dihitung dari seluruh data "
            f"{jenis}. Tabel di bawah ini hanya berisi {angka(len(transaksi_tabel))} dari "
            f"{angka(len(semua_transaksi))} transaksi, sesuai pencarian atau filter pada tabel "
            f"Riwayat {teks['nama']} di aplikasi.",
            GAYA_ISI,
        ))
        isi.append(Spacer(1, 6))
    else:
        isi.append(Paragraph(f"Riwayat {teks['nama']} (Seluruh Data)", GAYA_SUBJUDUL))

    if len(transaksi_tabel) == 0:
        isi.append(Paragraph("Tidak ada transaksi yang sesuai dengan pencarian atau filter.", GAYA_ISI))
    else:
        baris_data = [["No", "Tanggal", "Kode SKU", "Nama Obat", f"Jumlah {kata.capitalize()}", "Sisa Stok"]]
        for nomor, baris in enumerate(transaksi_tabel.itertuples(), start=1):
            baris_data.append([
                nomor,
                f"{baris.tanggal:%d-%m-%Y %H:%M}" if pd.notna(baris.tanggal) else "-",
                baris.kode_obat,
                Paragraph(str(baris.nama_obat), GAYA_ISI_KECIL),
                angka(baris.jumlah),
                angka(baris.sisa_stok) if pd.notna(baris.sisa_stok) else "-",
            ])
        isi.append(tabel_laporan(baris_data, [1.1, 2.6, 2.8, 6.2, 2.3, 2.0], 4, ukuran_huruf=7.5))

    berkas = BytesIO()
    dokumen = SimpleDocTemplate(
        berkas, pagesize=A4, title=teks["judul"].title(), author="Apotek Kreator Kesehatan",
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2 * cm,
    )
    dokumen.build(isi, onFirstPage=nomor_halaman, onLaterPages=nomor_halaman)
    return berkas.getvalue()