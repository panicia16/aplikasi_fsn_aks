# halaman login
import hashlib

import streamlit as st


# akun untuk masuk ke aplikasi
USERNAME = st.secrets["login"]["username"]
PASSWORD = st.secrets["login"]["password"]

# cookie login: jika "ingat saya" dicentang disimpan 30 hari, jika tidak hilang saat browser ditutup
NAMA_COOKIE = "fsn_login"
LAMA_INGAT = 30 * 24 * 60 * 60

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


# mengecek apakah browser menyimpan cookie login yang benar
def login_diingat():
    return st.context.cookies.get(NAMA_COOKIE) == TOKEN_INGAT


# menyimpan atau menghapus cookie di browser, dijalankan sekali setelah login atau keluar
def jalankan_skrip_cookie():
    aksi = st.session_state.pop("aksi_cookie", None)
    if aksi == "ingat":
        # disimpan 30 hari, tetap ada walaupun browser ditutup
        isi_cookie = f"{NAMA_COOKIE}={TOKEN_INGAT}; max-age={LAMA_INGAT}"
    elif aksi == "sesi":
        # tanpa lama simpan, tetap ada saat refresh tetapi hilang saat browser ditutup
        isi_cookie = f"{NAMA_COOKIE}={TOKEN_INGAT}"
    elif aksi == "hapus":
        isi_cookie = f"{NAMA_COOKIE}=; max-age=0"
    else:
        return

    with st.container(key="wadah_cookie"):
        st.html(
            f'<script>document.cookie = "{isi_cookie}; path=/; SameSite=Lax" + '
            f'(location.protocol === "https:" ? "; Secure" : "");</script>',
            unsafe_allow_javascript=True,
        )


def halaman_login():
    st.markdown(GAYA_LOGIN, unsafe_allow_html=True)

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
                # cookie login disimpan, lama simpannya tergantung "ingat saya"
                st.session_state["aksi_cookie"] = "ingat" if ingat_saya else "sesi"
                st.rerun()
            else:
                st.error("Username atau password salah.")