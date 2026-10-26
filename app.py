# aplikasi klasifikasi tingkat pergerakan persediaan obat apotek kreator kesehatan
import streamlit as st

# pengaturan halaman harus ditulis paling awal
st.set_page_config(page_title="Apotek Kreator Kesehatan", layout="wide")

from utils import muat_data_tersimpan, pindah_halaman
from halaman.dashboard import halaman_dashboard
from halaman.unggah_data import halaman_unggah
from halaman.data_klasifikasi import halaman_klasifikasi
from halaman.detail_sku import halaman_detail
from halaman.data_penjualan import halaman_penjualan
from halaman.data_pembelian import halaman_pembelian


# menu di sidebar: nama halaman, tulisan menu, dan ikon
DAFTAR_MENU = [
    ("dashboard", "Dashboard", ":material/pie_chart:"),
    ("unggah_data", "Unggah Dataset", ":material/upload:"),
    ("data_klasifikasi", "Data & Hasil Klasifikasi SKU", ":material/folder:"),
    ("data_penjualan", "Data Penjualan", ":material/show_chart:"),
    ("data_pembelian", "Data Pembelian", ":material/description:"),
]

# fungsi yang dijalankan untuk setiap halaman
DAFTAR_HALAMAN = {
    "dashboard": halaman_dashboard,
    "unggah_data": halaman_unggah,
    "data_klasifikasi": halaman_klasifikasi,
    "detail_sku": halaman_detail,
    "data_penjualan": halaman_penjualan,
    "data_pembelian": halaman_pembelian,
}

# warna dan bentuk tampilan yang dipakai di semua halaman
GAYA_UMUM = """
<style>
.stApp { background-color: #e6fbf7; }

/* sidebar */
[data-testid="stSidebar"] { background-color: #2bb39c; }
[data-testid="stSidebar"] * { color: #ffffff; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 6px; }
.judul-sidebar { font-weight: 800; font-size: 1.4rem; line-height: 1.2; margin-bottom: 1.2rem; }
[data-testid="stSidebar"] .stButton button {
    justify-content: flex-start; text-align: left; border: none; border-radius: 8px;
    padding: 10px 14px; background-color: transparent; font-weight: 600;
}
[data-testid="stSidebar"] .stButton button > div,
[data-testid="stSidebar"] .stButton button span { justify-content: flex-start; }
[data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-primary"] { background-color: #07706e; }
[data-testid="stSidebar"] .stButton button:hover { background-color: #1f9884; }

/* judul halaman dan tombol */
.judul-halaman { text-align: center; color: #07706e; font-weight: 800; font-size: 2.1rem; margin-bottom: 0.5rem; }
.stButton button, .stDownloadButton button { border-radius: 20px; }

/* tampilan ponsel: judul lebih kecil dan jarak tepi lebih sempit */
@media (max-width: 640px) {
    .judul-halaman { font-size: 1.5rem; }
    [data-testid="stMainBlockContainer"] { padding-left: 1rem; padding-right: 1rem; }
}
</style>
"""
st.markdown(GAYA_UMUM, unsafe_allow_html=True)


# nilai awal yang disimpan selama aplikasi dibuka
if "halaman" not in st.session_state:
    st.session_state["halaman"] = st.query_params.get("halaman", "dashboard")
if "data" not in st.session_state:
    st.session_state["data"] = muat_data_tersimpan()
if "kode_detail" not in st.session_state:
    st.session_state["kode_detail"] = st.query_params.get("kode")
if "kunci_uploader" not in st.session_state:
    st.session_state["kunci_uploader"] = 0
if "status_unggah" not in st.session_state:
    st.session_state["status_unggah"] = "selesai" if st.session_state["data"] is not None else None


# sidebar berisi nama apotek dan menu
with st.sidebar:
    st.markdown('<div class="judul-sidebar">APOTEK<br>KREATOR<br>KESEHATAN</div>', unsafe_allow_html=True)
    halaman_aktif = st.session_state["halaman"]
    for nama_halaman, tulisan_menu, ikon_menu in DAFTAR_MENU:
        # halaman detail sku masih termasuk menu data & hasil klasifikasi sku
        menu_aktif = halaman_aktif == nama_halaman or (halaman_aktif == "detail_sku" and nama_halaman == "data_klasifikasi")
        jenis_tombol = "primary" if menu_aktif else "secondary"
        if st.button(tulisan_menu, key=f"menu_{nama_halaman}", icon=ikon_menu, width="stretch", type=jenis_tombol):
            pindah_halaman(nama_halaman)


# menjalankan halaman yang sedang dibuka
fungsi_halaman = DAFTAR_HALAMAN.get(st.session_state["halaman"], halaman_dashboard)
fungsi_halaman()
