# halaman dashboard
import altair as alt
import pandas as pd
import streamlit as st

from utils import (
    TINDAK_LANJUT, URUTAN_FSN, WARNA_FSN, WARNA_MUDA, WARNA_TUA,
    angka, daftar_periode_data, judul, pesan_belum_ada_data, rekap_bulanan,
)


# pilihan untuk melihat obat terlaris selama seluruh periode
SELURUH_PERIODE = "Seluruh periode"

# tampilan untuk halaman dashboard
GAYA_DASHBOARD = """
<style>
.periode-data { text-align: right; color: #52514e; font-size: 0.9rem; margin-bottom: 12px; }

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

/* kartu putih untuk grafik dan ringkasan */
.st-key-kartu_distribusi, .st-key-kartu_ringkasan, .st-key-kartu_jual, .st-key-kartu_beli, .st-key-kartu_terlaris {
    background-color: #ffffff; border-radius: 12px; padding: 20px 24px;
}
.st-key-kartu_distribusi, .st-key-kartu_ringkasan { min-height: 440px; }

/* empat kotak kecil ringkasan transaksi */
.isi-ringkasan { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.kotak-ringkasan {
    background-color: #f2fbf9; border-radius: 10px; padding: 14px 16px; min-height: 150px;
    display: flex; flex-direction: column; justify-content: center;
}
.ringkasan-judul { color: #52514e; font-size: 0.85rem; font-weight: 600; }
.ringkasan-angka { font-size: 1.5rem; font-weight: 800; color: #07706e; line-height: 1.3; }
.ringkasan-catatan { color: #52514e; font-size: 0.8rem; }

/* kotak pilihan periode obat terlaris */
.st-key-kartu_terlaris [data-testid="stSelectbox"] [role="group"] { background-color: #f2fbf9; border-color: #9fd8cd; }
#vg-tooltip-element td.key { text-align: left; }

/* layar sedang: kotak jumlah sku menjadi 2 kolom */
@media (max-width: 900px) {
    .baris-kotak { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

/* layar ponsel: ukuran tulisan dan jarak dibuat lebih kecil */
@media (max-width: 640px) {
    .periode-data { text-align: center; }
    .baris-kotak { gap: 10px; }
    .kotak-jumlah { padding: 12px 14px; }
    .kotak-angka { font-size: 1.6rem; }
    .st-key-kartu_distribusi, .st-key-kartu_ringkasan, .st-key-kartu_jual, .st-key-kartu_beli, .st-key-kartu_terlaris {
        padding: 14px 16px;
    }
    .st-key-kartu_distribusi, .st-key-kartu_ringkasan { min-height: 0; }
    .kotak-ringkasan { min-height: 110px; }
    .ringkasan-angka { font-size: 1.25rem; }
}
</style>
"""


# empat kotak jumlah sku dengan warna sesuai kategorinya
def kotak_jumlah_sku(data_sku):
    jumlah_per_kategori = data_sku["hasil_klasifikasi"].value_counts()
    total_sku = len(data_sku)

    # isi kotaknya total sku lalu setiap kategori
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

# empat kotak kecil pada ringkasan transaksi
def kotak_ringkasan(rekap_jual, rekap_beli):
    bulan_jual_terbanyak = rekap_jual.loc[rekap_jual["jumlah"].idxmax()]
    bulan_beli_terbanyak = rekap_beli.loc[rekap_beli["jumlah"].idxmax()]

    isi_kotak = [
        ("Total obat terjual", angka(rekap_jual["jumlah"].sum()), "selama periode data"),
        ("Total obat dibeli", angka(rekap_beli["jumlah"].sum()), "selama periode data"),
        ("Bulan penjualan terbanyak", bulan_jual_terbanyak["bulan"], f"{angka(bulan_jual_terbanyak['jumlah'])} obat terjual"),
        ("Bulan pembelian terbanyak", bulan_beli_terbanyak["bulan"], f"{angka(bulan_beli_terbanyak['jumlah'])} obat dibeli"),
    ]

    semua_kotak = ""
    for nama, nilai, catatan in isi_kotak:
        semua_kotak += (
            f'<div class="kotak-ringkasan"><div class="ringkasan-judul">{nama}</div>'
            f'<div class="ringkasan-angka">{nilai}</div><div class="ringkasan-catatan">{catatan}</div></div>'
        )
    st.markdown(f'<div class="isi-ringkasan">{semua_kotak}</div>', unsafe_allow_html=True)


# grafik batang jumlah obat per bulan
def grafik_bulanan(rekap, warna, judul_sumbu):
    data_grafik = rekap[["bulan", "jumlah"]].rename(columns={"bulan": "Bulan", "jumlah": judul_sumbu})
    return (
        alt.Chart(data_grafik)
        .mark_bar(color=warna, cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("Bulan:N", sort=list(data_grafik["Bulan"]), title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y(f"{judul_sumbu}:Q", title=judul_sumbu, axis=alt.Axis(titlePadding=14, labelPadding=6)),
            tooltip=[alt.Tooltip("Bulan:N"), alt.Tooltip(f"{judul_sumbu}:Q", format=",.0f")],
        )
        .properties(height=280, padding={"left": 16, "top": 20, "right": 16, "bottom": 8})
    )

# grafik sepuluh obat yang paling banyak terjual
def grafik_terlaris(terlaris):
    data_grafik = terlaris.rename(columns={"kode_obat": "Kode SKU", "nama_obat": "Nama Obat", "jumlah_terjual": "Jumlah Terjual"})
    batang = (
        alt.Chart(data_grafik)
        .mark_bar(color="#2a78d6", cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
        .encode(
            x=alt.X("Jumlah Terjual:Q", title="Jumlah obat terjual", axis=alt.Axis(titlePadding=10)),
            y=alt.Y("Nama Obat:N", sort="-x", title=None, axis=alt.Axis(labelLimit=200, labelPadding=8)),
            tooltip=[alt.Tooltip("Kode SKU:N"), alt.Tooltip("Nama Obat:N"), alt.Tooltip("Jumlah Terjual:Q", format=",.0f")],
        )
    )
    # total jumlah terjual ditulis di ujung tiap batangnya
    tulisan_angka = batang.mark_text(align="left", dx=4, color="#0b0b0b").encode(
        text=alt.Text("Jumlah Terjual:Q", format=",.0f")
    )
    return (batang + tulisan_angka).properties(height=360, padding={"left": 8, "top": 12, "right": 24, "bottom": 8})


def halaman_dashboard():
    st.markdown(GAYA_DASHBOARD, unsafe_allow_html=True)
    judul("DASHBOARD")

    data = st.session_state["data"]
    if data is None:
        pesan_belum_ada_data()
        return

    data_sku = data["sku"]
    ringkasan = data["ringkasan"]

    # periode data
    st.markdown(
        f'<div class="periode-data">Periode data: {ringkasan["tanggal_awal"]:%d-%m-%Y} s.d. {ringkasan["tanggal_akhir"]:%d-%m-%Y}</div>',
        unsafe_allow_html=True,
    )

    kotak_jumlah_sku(data_sku)

    # jumlah penjualan dan pembelian setiap bulan
    daftar_periode = daftar_periode_data(data)
    rekap_jual = rekap_bulanan(data["penjualan"], "jumlah_terjual", daftar_periode)
    rekap_beli = rekap_bulanan(data["pembelian"], "jumlah_dibeli", daftar_periode)

    # grafik donat dan ringkasan transaksi sebelahan
    kiri, kanan = st.columns(2)
    with kiri.container(key="kartu_distribusi"):
        st.subheader("Distribusi Hasil Klasifikasi")
        st.altair_chart(grafik_distribusi(data_sku), use_container_width=True)
    with kanan.container(key="kartu_ringkasan"):
        st.subheader("Ringkasan Transaksi")
        kotak_ringkasan(rekap_jual, rekap_beli)

    # grafik penjualan dan pembelian per bulan
    kiri, kanan = st.columns(2)
    with kiri.container(key="kartu_jual"):
        st.subheader("Statistik Penjualan")
        st.altair_chart(grafik_bulanan(rekap_jual, "#2a78d6", "Jumlah obat terjual"), use_container_width=True)
    with kanan.container(key="kartu_beli"):
        st.subheader("Statistik Pembelian")
        st.altair_chart(grafik_bulanan(rekap_beli, "#07706e", "Jumlah obat dibeli"), use_container_width=True)

    # obat terlaris untuk seluruh periode atau satu bulan tertentu
    with st.container(key="kartu_terlaris"):
        st.subheader("10 Obat Terlaris")
        pilihan_periode = [SELURUH_PERIODE] + list(rekap_jual["bulan"])
        periode_dipilih = st.selectbox("Pilih periode", pilihan_periode, index=0)

        data_jual = data["penjualan"]
        if periode_dipilih != SELURUH_PERIODE:
            bulan_dipilih = daftar_periode[pilihan_periode.index(periode_dipilih) - 1]
            data_jual = data_jual[data_jual["tanggal"].dt.to_period("M") == bulan_dipilih]

        terlaris = data_jual.groupby(["kode_obat", "nama_obat"], as_index=False)["jumlah_terjual"].sum()
        terlaris = terlaris.sort_values("jumlah_terjual", ascending=False).head(10)

        if terlaris.empty:
            st.info(f"Tidak ada penjualan pada {periode_dipilih}.")
        else:
            st.altair_chart(grafik_terlaris(terlaris), use_container_width=True)
