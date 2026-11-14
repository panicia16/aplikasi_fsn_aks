# halaman dashboard
import altair as alt
import pandas as pd
import streamlit as st

from grafik import (
    WARNA_BELI, WARNA_JUAL, grafik_bulanan, isi_ringkasan_beli, isi_ringkasan_jual,
    kartu_teratas, kotak_ringkasan, tulisan_periode,
)
from utils import (
    TINDAK_LANJUT, URUTAN_FSN, WARNA_FSN, WARNA_MUDA, WARNA_TUA,
    angka, daftar_periode_data, judul, pesan_belum_ada_data, rekap_bulanan,
)


# tampilan khusus halaman dashboard
GAYA_DASHBOARD = """
<style>
/* empat kotak jumlah sku */
.baris-kotak { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin-bottom: 16px; }
.kotak-jumlah { position: relative; border-radius: 12px; padding: 16px 20px; }
.kotak-jumlah.ada-keterangan { cursor: help; }
.kotak-judul { font-weight: 700; font-size: 0.95rem; }
.kotak-angka { font-size: 2.2rem; font-weight: 800; line-height: 1.2; }
.kotak-persen { font-size: 0.85rem; color: #52514e; }

/* keterangan tindak lanjut yang muncul saat kursor diarahkan ke kotak */
.kotak-keterangan {
    display: none; position: absolute; left: 0; right: 0; top: calc(100% + 8px); z-index: 20;
    background-color: #ffffff; border: 1px solid #cfe9e4; border-radius: 10px; padding: 10px 14px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12); font-size: 0.85rem; color: #0b0b0b;
}
.kotak-jumlah:hover .kotak-keterangan { display: block; }

/* grafik donat dan ringkasan transaksi dibuat sama tinggi */
.st-key-kartu_distribusi, .st-key-kartu_ringkasan { min-height: 440px; }

/* layar sedang: kotak jumlah sku menjadi 2 kolom */
@media (max-width: 900px) {
    .baris-kotak { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

/* layar ponsel: ukuran tulisan dan jarak dibuat lebih kecil */
@media (max-width: 640px) {
    .baris-kotak { gap: 10px; }
    .kotak-jumlah { padding: 12px 14px; }
    .kotak-angka { font-size: 1.6rem; }
    .st-key-kartu_distribusi, .st-key-kartu_ringkasan { min-height: 0; }
}
</style>
"""


# empat kotak jumlah sku dengan warna sesuai kategorinya
def kotak_jumlah_sku(data_sku):
    jumlah_per_kategori = data_sku["hasil_klasifikasi"].value_counts()
    total_sku = len(data_sku)

    # isi kotaknya total sku setiap kategori
    isi_kotak = [("Total SKU", total_sku)]
    for kategori in URUTAN_FSN:
        isi_kotak.append((kategori, int(jumlah_per_kategori.get(kategori, 0))))

    semua_kotak = ""
    for nama, jumlah in isi_kotak:
        if nama == "Total SKU":
            tulisan_bawah = "Seluruh obat non konsinyasi"
        else:
            persen = jumlah / max(total_sku, 1) * 100
            tulisan_bawah = f"{persen:.1f}% dari total SKU".replace(".", ",")

        # keterangan tindak lanjut pada kotak kategorinya 
        keterangan = TINDAK_LANJUT.get(nama)
        if keterangan:
            kelas_kotak = "kotak-jumlah ada-keterangan"
            kotak_keterangan = f'<div class="kotak-keterangan">{keterangan}</div>'
        else:
            kelas_kotak = "kotak-jumlah"
            kotak_keterangan = ""

        semua_kotak += (
            f'<div class="{kelas_kotak}" style="background-color:{WARNA_MUDA[nama]}">'
            f'<div class="kotak-judul">{nama.replace("-", " ")}</div>'
            f'<div class="kotak-angka" style="color:{WARNA_TUA[nama]}">{angka(jumlah)}</div>'
            f'<div class="kotak-persen">{tulisan_bawah}</div>{kotak_keterangan}</div>'
        )
    st.markdown(f'<div class="baris-kotak">{semua_kotak}</div>', unsafe_allow_html=True)


# grafik donat distribusi hasil klasifikasi
def grafik_distribusi(data_sku):
    jumlah_per_kategori = data_sku["hasil_klasifikasi"].value_counts()
    total_sku = max(len(data_sku), 1)

    jumlah = [int(jumlah_per_kategori.get(kategori, 0)) for kategori in URUTAN_FSN]
    persen = [f"{nilai / total_sku * 100:.1f}%".replace(".", ",") for nilai in jumlah]
    data_grafik = pd.DataFrame({"Klasifikasi": URUTAN_FSN, "Jumlah SKU": jumlah, "Persentase": persen})

    warna = alt.Scale(domain=URUTAN_FSN, range=[WARNA_FSN[kategori] for kategori in URUTAN_FSN])
    return (
        alt.Chart(data_grafik)
        .mark_arc(innerRadius=70, stroke="#ffffff", strokeWidth=2)
        .encode(
            theta=alt.Theta("Jumlah SKU:Q"),
            color=alt.Color("Klasifikasi:N", scale=warna, legend=alt.Legend(title=None, orient="bottom")),
            tooltip=[alt.Tooltip("Klasifikasi:N"), alt.Tooltip("Jumlah SKU:Q"), alt.Tooltip("Persentase:N")],
        )
        .properties(height=280, padding={"left": 8, "top": 8, "right": 8, "bottom": 8})
    )


def halaman_dashboard():
    st.markdown(GAYA_DASHBOARD, unsafe_allow_html=True)
    judul("DASHBOARD")

    data = st.session_state["data"]
    if data is None:
        pesan_belum_ada_data()
        return

    tulisan_periode(data["ringkasan"])
    kotak_jumlah_sku(data["sku"])

    # jumlah penjualan dan pembelian setiap bulan
    daftar_periode = daftar_periode_data(data)
    rekap_jual = rekap_bulanan(data["penjualan"], "jumlah_terjual", daftar_periode)
    rekap_beli = rekap_bulanan(data["pembelian"], "jumlah_dibeli", daftar_periode)

    # grafik donat dan ringkasan transaksi sebelahan
    kiri, kanan = st.columns(2)
    with kiri.container(key="kartu_distribusi"):
        st.subheader("Distribusi Hasil Klasifikasi")
        st.altair_chart(grafik_distribusi(data["sku"]), use_container_width=True)
    with kanan.container(key="kartu_ringkasan"):
        st.subheader("Ringkasan Transaksi")
        # urutan kotak: total terjual, total dibeli, bulan jual terbanyak, bulan beli terbanyak
        jual = isi_ringkasan_jual(rekap_jual)
        beli = isi_ringkasan_beli(rekap_beli)
        kotak_ringkasan([jual[0], beli[0], jual[1], beli[1]], jumlah_kolom=2)

    # grafik penjualan dan pembelian per bulan
    kiri, kanan = st.columns(2)
    with kiri.container(key="kartu_jual"):
        st.subheader("Statistik Penjualan")
        st.altair_chart(grafik_bulanan(rekap_jual, WARNA_JUAL, "Jumlah obat terjual"), use_container_width=True)
    with kanan.container(key="kartu_beli"):
        st.subheader("Statistik Pembelian")
        st.altair_chart(grafik_bulanan(rekap_beli, WARNA_BELI, "Jumlah obat dibeli"), use_container_width=True)

    # 10 obat terlaris dan 10 obat pembelian terbanyak sebelahan
    kiri, kanan = st.columns(2)
    with kiri:
        kartu_teratas(data, "penjualan", rekap_jual, daftar_periode)
    with kanan:
        kartu_teratas(data, "pembelian", rekap_beli, daftar_periode)