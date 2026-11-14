# aplikasi klasifikasi tingkat pergerakan persediaan obat apotek kreator kesehatan
import streamlit as st

# pengaturan halaman harus ditulis paling awal
st.set_page_config(page_title="Apotek Kreator Kesehatan", layout="wide")

from utils import muat_data_tersimpan, pindah_halaman
from halaman.login import halaman_login, jalankan_skrip_cookie, login_diingat
from halaman.dashboard import halaman_dashboard
from halaman.unggah_data import halaman_unggah
from halaman.data_klasifikasi import halaman_klasifikasi
from halaman.detail_sku import halaman_detail
from halaman.data_penjualan import halaman_penjualan
from halaman.data_pembelian import halaman_pembelian
from halaman.tentang_aplikasi import halaman_tentang
from halaman.manual_book import halaman_manual


# menu di sidebar: nama halaman, tulisan menu, dan ikon
DAFTAR_MENU = [
    ("dashboard", "Dashboard", ":material/pie_chart:"),
    ("unggah_data", "Unggah Dataset", ":material/upload:"),
    ("data_klasifikasi", "Data & Hasil Klasifikasi SKU", ":material/folder:"),
    ("data_penjualan", "Data Penjualan", ":material/show_chart:"),
    ("data_pembelian", "Data Pembelian", ":material/description:"),
    ("tentang_aplikasi", "Tentang Aplikasi", ":material/info:"),
    ("manual_book", "Manual Book", ":material/menu_book:"),
]

# fungsi yang dijalankan untuk setiap halaman
DAFTAR_HALAMAN = {
    "dashboard": halaman_dashboard,
    "unggah_data": halaman_unggah,
    "data_klasifikasi": halaman_klasifikasi,
    "detail_sku": halaman_detail,
    "data_penjualan": halaman_penjualan,
    "data_pembelian": halaman_pembelian,
    "tentang_aplikasi": halaman_tentang,
    "manual_book": halaman_manual,
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
.garis-sidebar { border-top: 1px solid rgba(255, 255, 255, 0.45); margin: 14px 0 6px 0; }

/* tempat skrip cookie tidak perlu terlihat */
.st-key-wadah_cookie { display: none; }

/* judul halaman dan tombol */
.judul-halaman { text-align: center; color: #07706e; font-weight: 800; font-size: 2.1rem; margin-bottom: 0.5rem; }
.stButton button, .stDownloadButton button { border-radius: 20px; }

/* tulisan periode data di kanan atas */
.periode-data { text-align: right; color: #52514e; font-size: 0.9rem; margin-bottom: 12px; }

/* kartu putih untuk grafik, ringkasan, dan isi halaman */
[class*="st-key-kartu_"] { background-color: #ffffff; border-radius: 12px; padding: 20px 24px; }

/* ringkasan dan grafik di data penjualan dan data pembelian dibuat sama tinggi */
.st-key-kartu_ringkasan_jual, .st-key-kartu_statistik_jual,
.st-key-kartu_ringkasan_beli, .st-key-kartu_statistik_beli { min-height: 420px; }

/* kotak kecil ringkasan transaksi */
.isi-ringkasan { display: grid; gap: 12px; }
.kotak-ringkasan {
    background-color: #f2fbf9; border-radius: 10px; padding: 14px 16px; min-height: 150px;
    display: flex; flex-direction: column; justify-content: center;
}
.ringkasan-judul { color: #52514e; font-size: 0.85rem; font-weight: 600; }
.ringkasan-angka { font-size: 1.5rem; font-weight: 800; color: #07706e; line-height: 1.3; }
.ringkasan-catatan { color: #52514e; font-size: 0.8rem; }

/* kotak pilihan periode 10 obat teratas */
[class*="st-key-kartu_teratas"] [data-testid="stSelectbox"] [role="group"] { background-color: #f2fbf9; border-color: #9fd8cd; }
#vg-tooltip-element td.key { text-align: left; }

/* tampilan ponsel: judul lebih kecil dan jarak tepi lebih sempit */
@media (max-width: 640px) {
    .judul-halaman { font-size: 1.5rem; }
    [data-testid="stMainBlockContainer"] { padding-left: 1rem; padding-right: 1rem; }
    .periode-data { text-align: center; }
    [class*="st-key-kartu_"] { padding: 14px 16px; }
    .st-key-kartu_ringkasan_jual, .st-key-kartu_statistik_jual,
    .st-key-kartu_ringkasan_beli, .st-key-kartu_statistik_beli { min-height: 0; }
    .kotak-ringkasan { min-height: 110px; }
    .ringkasan-angka { font-size: 1.25rem; }
}
</style>
"""
st.markdown(GAYA_UMUM, unsafe_allow_html=True)


# nilai awal yang disimpan selama aplikasi dibuka
if "sudah_login" not in st.session_state:
    # jika browser menyimpan cookie "ingat saya", pengguna langsung dianggap sudah login
    st.session_state["sudah_login"] = login_diingat()
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


# menyimpan cookie setelah login atau menghapusnya setelah keluar
jalankan_skrip_cookie()

# kalau belum login, hanya halaman login yang ditampilkan
if not st.session_state["sudah_login"]:
    halaman_login()
    st.stop()


# keluar dari aplikasi lalu kembali ke halaman login
def keluar():
    st.session_state["sudah_login"] = False
    st.session_state["aksi_cookie"] = "hapus"
    st.session_state["halaman"] = "dashboard"
    st.session_state["kode_detail"] = None
    st.query_params.clear()
    st.rerun()


# jendela konfirmasi sebelum keluar
@st.dialog("Keluar dari Aplikasi")
def konfirmasi_keluar():
    st.write("Yakin ingin keluar dari aplikasi?")
    kiri, kanan = st.columns(2)
    if kiri.button("Batal", key="batal_keluar", width="stretch"):
        st.rerun()
    if kanan.button("Ya, Keluar", key="yakin_keluar", type="primary", width="stretch"):
        keluar()


# sidebar berisi nama apotek, menu, dan tombol keluar
with st.sidebar:
    st.markdown('<div class="judul-sidebar">APOTEK<br>KREATOR<br>KESEHATAN</div>', unsafe_allow_html=True)
    halaman_aktif = st.session_state["halaman"]
    for nama_halaman, tulisan_menu, ikon_menu in DAFTAR_MENU:
        # halaman detail sku masih termasuk menu data & hasil klasifikasi sku
        menu_aktif = halaman_aktif == nama_halaman or (halaman_aktif == "detail_sku" and nama_halaman == "data_klasifikasi")
        jenis_tombol = "primary" if menu_aktif else "secondary"
        if st.button(tulisan_menu, key=f"menu_{nama_halaman}", icon=ikon_menu, width="stretch", type=jenis_tombol):
            pindah_halaman(nama_halaman)

    st.markdown('<div class="garis-sidebar"></div>', unsafe_allow_html=True)
    if st.button("Keluar", key="tombol_keluar", icon=":material/logout:", width="stretch"):
        konfirmasi_keluar()


# menjalankan halaman yang sedang dibuka
fungsi_halaman = DAFTAR_HALAMAN.get(st.session_state["halaman"], halaman_dashboard)
fungsi_halaman()