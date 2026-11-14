# grafik dan kotak ringkasan yang dipakai di dashboard, data penjualan, dan data pembelian
import altair as alt
import streamlit as st

from utils import angka


# pilihan untuk melihat obat terlaris selama seluruh periode
SELURUH_PERIODE = "Seluruh periode"

# warna batang grafik penjualan dan pembelian
WARNA_JUAL = "#2a78d6"
WARNA_BELI = "#07706e"


# tulisan periode data di kanan atas halaman
def tulisan_periode(ringkasan):
    st.markdown(
        f'<div class="periode-data">Periode data: {ringkasan["tanggal_awal"]:%d-%m-%Y} s.d. {ringkasan["tanggal_akhir"]:%d-%m-%Y}</div>',
        unsafe_allow_html=True,
    )

# bulan dengan jumlah obat paling banyak
def bulan_terbanyak(rekap):
    return rekap.loc[rekap["jumlah"].idxmax()]

# kotak kecil ringkasan, isi_kotak berisi (judul, nilai, catatan)
def kotak_ringkasan(isi_kotak, jumlah_kolom=2):
    semua_kotak = ""
    for nama, nilai, catatan in isi_kotak:
        semua_kotak += (
            f'<div class="kotak-ringkasan"><div class="ringkasan-judul">{nama}</div>'
            f'<div class="ringkasan-angka">{nilai}</div><div class="ringkasan-catatan">{catatan}</div></div>'
        )
    gaya_kolom = f"grid-template-columns: repeat({jumlah_kolom}, minmax(0, 1fr));"
    st.markdown(f'<div class="isi-ringkasan" style="{gaya_kolom}">{semua_kotak}</div>', unsafe_allow_html=True)

# isi kotak ringkasan penjualan
def isi_ringkasan_jual(rekap_jual):
    terbanyak = bulan_terbanyak(rekap_jual)
    return [
        ("Total obat terjual", angka(rekap_jual["jumlah"].sum()), "selama periode data"),
        ("Bulan penjualan terbanyak", terbanyak["bulan"], f"{angka(terbanyak['jumlah'])} obat terjual"),
    ]

# isi kotak ringkasan pembelian
def isi_ringkasan_beli(rekap_beli):
    terbanyak = bulan_terbanyak(rekap_beli)
    return [
        ("Total obat dibeli", angka(rekap_beli["jumlah"].sum()), "selama periode data"),
        ("Bulan pembelian terbanyak", terbanyak["bulan"], f"{angka(terbanyak['jumlah'])} obat dibeli"),
    ]


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

# pengaturan 10 obat teratas untuk penjualan dan pembelian
JENIS_TERATAS = {
    "penjualan": {
        "judul": "10 Obat Terlaris",
        "kolom": "jumlah_terjual",
        "label": "Jumlah Terjual",
        "sumbu": "Jumlah obat terjual",
        "warna": WARNA_JUAL,
        "kosong": "Tidak ada penjualan pada {}.",
    },
    "pembelian": {
        "judul": "10 Obat Pembelian Terbanyak",
        "kolom": "jumlah_dibeli",
        "label": "Jumlah Dibeli",
        "sumbu": "Jumlah obat dibeli",
        "warna": WARNA_BELI,
        "kosong": "Tidak ada pembelian pada {}.",
    },
}


# sepuluh obat dengan jumlah terbanyak pada periode yang dipilih
def hitung_teratas(data, jenis, periode_dipilih, pilihan_periode, daftar_periode):
    kolom = JENIS_TERATAS[jenis]["kolom"]
    data_transaksi = data[jenis]
    if periode_dipilih != SELURUH_PERIODE:
        bulan_dipilih = daftar_periode[pilihan_periode.index(periode_dipilih) - 1]
        data_transaksi = data_transaksi[data_transaksi["tanggal"].dt.to_period("M") == bulan_dipilih]

    teratas = data_transaksi.groupby(["kode_obat", "nama_obat"], as_index=False)[kolom].sum()
    teratas = teratas.sort_values(kolom, ascending=False).head(10)
    return teratas.rename(columns={kolom: "jumlah"})

# grafik batang sepuluh obat teratas
def grafik_teratas(teratas, jenis):
    pengaturan = JENIS_TERATAS[jenis]
    label = pengaturan["label"]
    data_grafik = teratas.rename(columns={"kode_obat": "Kode SKU", "nama_obat": "Nama Obat", "jumlah": label})
    batang = (
        alt.Chart(data_grafik)
        .mark_bar(color=pengaturan["warna"], cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
        .encode(
            x=alt.X(f"{label}:Q", title=pengaturan["sumbu"], axis=alt.Axis(titlePadding=10)),
            y=alt.Y("Nama Obat:N", sort="-x", title=None, axis=alt.Axis(labelLimit=180, labelPadding=8)),
            tooltip=[alt.Tooltip("Kode SKU:N"), alt.Tooltip("Nama Obat:N"), alt.Tooltip(f"{label}:Q", format=",.0f")],
        )
    )
    # jumlahnya ditulis di ujung tiap batang
    tulisan_angka = batang.mark_text(align="left", dx=4, color="#0b0b0b").encode(
        text=alt.Text(f"{label}:Q", format=",.0f")
    )
    return (batang + tulisan_angka).properties(height=360, padding={"left": 8, "top": 12, "right": 24, "bottom": 8})

# kartu 10 obat teratas untuk seluruh periode atau satu bulan tertentu
# mengembalikan periode yang dipilih dan tabelnya, dipakai juga untuk laporan pdf
def kartu_teratas(data, jenis, rekap, daftar_periode):
    pengaturan = JENIS_TERATAS[jenis]
    with st.container(key=f"kartu_teratas_{jenis}"):
        st.subheader(pengaturan["judul"])
        pilihan_periode = [SELURUH_PERIODE] + list(rekap["bulan"])
        periode_dipilih = st.selectbox("Pilih periode", pilihan_periode, index=0, key=f"periode_{jenis}")

        teratas = hitung_teratas(data, jenis, periode_dipilih, pilihan_periode, daftar_periode)
        if teratas.empty:
            st.info(pengaturan["kosong"].format(periode_dipilih))
        else:
            st.altair_chart(grafik_teratas(teratas, jenis), use_container_width=True)
    return periode_dipilih, teratas