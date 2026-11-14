# halaman login
import hashlib

import streamlit as st
import streamlit.components.v1 as components


# akun untuk masuk ke aplikasi
USERNAME = st.secrets["login"]["username"]
PASSWORD = st.secrets["login"]["password"]

# cookie login: jika "ingat saya" dicentang disimpan 30 hari, jika tidak hilang saat browser ditutup
NAMA_COOKIE = "fsn_login"
LAMA_INGAT = 30 * 24 * 60 * 60
NAMA_PARAMETER = "masuk"

# isi cookie dibuat dari username dan password, jadi cookie tidak berlaku lagi jika password diganti
TOKEN_INGAT = hashlib.sha256(f"{USERNAME}:{PASSWORD}:apotek-kreator".encode()).hexdigest()

# tampilan khusus halaman login
GAYA_LOGIN = """
<style>
.st-key-kartu_login { margin-top: 8vh; }
.judul-login { text-align: center; color: #07706e; font-weight: 800; font-size: 1.6rem; line-height: 1.25; }
.subjudul-login { text-align: center; color: #52514e; font-size: 0.9rem; margin: 6px 0 18px 0; }
.st-key-kartu_login [data-testid="stForm"] { border: none; padding: 0; }

/* tulisan "Press Enter to submit form" disembunyikan */
.st-key-kartu_login [data-testid="InputInstructions"] { display: none; }

/* kotak isian selalu punya garis tepi, tidak hanya saat diklik */
.st-key-kartu_login [data-testid="stTextInputRootElement"] {
    border: 1px solid #9fd8cd !important; border-radius: 8px; background-color: #f2fbf9;
}
.st-key-kartu_login [data-testid="stTextInputRootElement"]:focus-within { border-color: #07706e !important; }
.st-key-kartu_login [data-testid="stTextInputRootElement"] * { background-color: transparent; }
</style>
"""


# mengecek apakah pengguna masih login saat aplikasi dibuka atau di-refresh
def login_diingat():
    # di komputer sendiri, cookie bisa langsung dibaca oleh server
    if st.context.cookies.get(NAMA_COOKIE) == TOKEN_INGAT:
        st.query_params[NAMA_PARAMETER] = TOKEN_INGAT
        return True

    # di Streamlit Cloud, tanda login dibaca dari alamat halaman
    token = st.query_params.get(NAMA_PARAMETER)
    if token == TOKEN_INGAT:
        return True

    # tanda login lama sudah tidak berlaku (misalnya password diganti), jadi dihapus
    if token is not None:
        del st.query_params[NAMA_PARAMETER]
        st.session_state["aksi_cookie"] = "hapus"
    return False


# menyimpan atau menghapus tanda login di browser
def jalankan_skrip_cookie():
    if st.session_state.pop("aksi_cookie", None) == "hapus":
        # keluar dari aplikasi: cookie dan "ingat saya" dihapus
        skrip = f"""
        window.parent.document.cookie = "{NAMA_COOKIE}=; max-age=0; path=/";
        localStorage.removeItem("{NAMA_COOKIE}");
        """
        # tanda supaya halaman login tidak membaca "ingat saya" lagi
        st.session_state["login_dihapus"] = True
    elif st.session_state.get("sudah_login") and st.session_state.get("ingat_saya") is True:
        # "ingat saya" dicentang: disimpan 30 hari, tetap ada walaupun tab atau browser ditutup
        skrip = f"""
        window.parent.document.cookie = "{NAMA_COOKIE}={TOKEN_INGAT}; max-age={LAMA_INGAT}; path=/; SameSite=Lax";
        localStorage.setItem("{NAMA_COOKIE}", "{TOKEN_INGAT}");
        """
    elif st.session_state.get("sudah_login") and st.session_state.get("ingat_saya") is False:
        # "ingat saya" tidak dicentang: cookie hilang saat browser ditutup, "ingat saya" lama dihapus
        skrip = f"""
        window.parent.document.cookie = "{NAMA_COOKIE}={TOKEN_INGAT}; path=/; SameSite=Lax";
        localStorage.removeItem("{NAMA_COOKIE}");
        """
    else:
        return

    components.html(f"<script>{skrip}</script>", height=0)


# membaca "ingat saya" yang tersimpan di browser, lalu membuka ulang aplikasi dengan tanda login di alamat halaman
def baca_ingat_saya():
    components.html(
        f"""<script>
        let jendela = window.parent;
        try {{ if (window.top.location.href) {{ jendela = window.top; }} }} catch (e) {{}}
        const token = localStorage.getItem("{NAMA_COOKIE}");
        const alamat = new URL(jendela.location.href);
        if (token && !alamat.searchParams.has("{NAMA_PARAMETER}")) {{
            alamat.searchParams.set("{NAMA_PARAMETER}", token);
            jendela.location.replace(alamat.toString());
        }}
        </script>""",
        height=0,
    )


def halaman_login():
    st.markdown(GAYA_LOGIN, unsafe_allow_html=True)

    # jika "ingat saya" pernah dicentang, pengguna langsung masuk kembali
    if not st.session_state.get("login_dihapus"):
        baca_ingat_saya()

    # kotak login di tengah layar
    _, tengah, _ = st.columns([1, 1.2, 1])
    with tengah.container(key="kartu_login"):
        st.markdown('<div class="judul-login">APOTEK KREATOR KESEHATAN</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="subjudul-login">Aplikasi Klasifikasi Tingkat Pergerakan Persediaan Obat</div>',
            unsafe_allow_html=True,
        )

        with st.form("form_login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            ingat_saya = st.checkbox("Ingat saya")
            tombol_masuk = st.form_submit_button("Masuk", type="primary", width="stretch")

        if tombol_masuk:
            if username == "" or password == "":
                st.error("Username dan password wajib diisi.")
            elif username == USERNAME and password == PASSWORD:
                # tanda sudah login disimpan selama aplikasi dibuka
                st.session_state["sudah_login"] = True
                # tanda login disimpan di alamat halaman supaya tidak keluar saat di-refresh
                st.query_params[NAMA_PARAMETER] = TOKEN_INGAT
                # pilihan "ingat saya" disimpan, lalu dipakai oleh jalankan_skrip_cookie
                st.session_state["ingat_saya"] = ingat_saya
                st.rerun()
            else:
                st.error("Username atau password salah.")