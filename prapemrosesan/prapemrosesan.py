# pengolahan data kartu stok mengikuti notebook eda dan prapemrosesan
import re

import numpy as np
import pandas as pd


# kolom wajib pada file kartu stok yang diunggah
KOLOM_WAJIB = [
    "No.", "Tanggal", "Gudang", "Kode Obat", "Nama Obat", "No. Bukti", "Keterangan",
    "Stok Awal", "Masuk", "Keluar", "Sisa Stok", "Golongan", "Kategori", "Jenis Obat", "Status"
]

# fitur masukan model sesuai urutan saat pelatihan
FITUR_MODEL = [
    "golongan", "kategori", "total_masuk", "total_keluar", "frekuensi_transaksi", "active_months"
]


# memeriksa kelengkapan kolom dan isi dataset
def validasi_format(df_mentah):
    kesalahan = []
    kolom_tersedia = [str(kolom).strip() for kolom in df_mentah.columns]

    # mencari kolom wajib yang tidak ada
    kolom_hilang = [kolom for kolom in KOLOM_WAJIB if kolom not in kolom_tersedia]
    if kolom_hilang:
        kesalahan.append("Kolom tidak ditemukan: " + ", ".join(kolom_hilang))

    # memeriksa dataset kosong
    if len(df_mentah) == 0:
        kesalahan.append("Dataset tidak memiliki baris data.")

    return kesalahan


# mengubah nilai stok menjadi angka
def ambil_nilai_numerik(nilai):
    # nilai kosong dikembalikan sebagai NaN
    if pd.isna(nilai):
        return np.nan

    # mengubah nilai menjadi teks agar dapat dibaca secara konsisten
    teks = str(nilai).strip()

    # mengambil bagian angka termasuk tanda negatif dan pemisah angka
    hasil = re.search(r"-?\d[\d.,]*", teks)

    if hasil is None:
        return np.nan

    angka = hasil.group()

    # titik sebagai pemisah ribuan
    if "." in angka and "," not in angka:
        bagian = angka.split(".")
        if len(bagian) > 1 and all(len(x) == 3 for x in bagian[1:]):
            angka = angka.replace(".", "")

    # koma sebagai pemisah ribuan atau desimal
    elif "," in angka and "." not in angka:
        bagian = angka.split(",")
        if len(bagian) > 1 and all(len(x) == 3 for x in bagian[1:]):
            angka = angka.replace(",", "")
        else:
            angka = angka.replace(",", ".")

    # jika titik dan koma muncul bersamaan maka tanda terakhir dianggap desimal
    elif "." in angka and "," in angka:
        if angka.rfind(".") > angka.rfind(","):
            angka = angka.replace(",", "")
        else:
            angka = angka.replace(".", "").replace(",", ".")

    return float(angka)


# mengambil nomor faktur asli dari teks keterangan
def ambil_faktur(teks):
    if pd.isna(teks):
        return pd.NA

    hasil = re.search(
        r"faktur\s*:\s*(.*?)(?:\s+telah\s+di\s+hapus)?$",
        str(teks),
        flags=re.IGNORECASE
    )

    return hasil.group(1).strip() if hasil else pd.NA


# mengolah kartu stok menjadi data per sku, data penjualan, data pembelian, dan ringkasan
def proses_kartu_stok(df_mentah):
    df = df_mentah.copy()

    # penyeragaman nama kolom
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )

    # penyesuaian tipe data tanggal dan stok
    df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")

    kolom_stok = ["stok_awal", "masuk", "keluar", "sisa_stok"]
    for kolom in kolom_stok:
        df[kolom] = df[kolom].apply(ambil_nilai_numerik)

    # penyeragaman data teks
    kolom_teks = ["nama_obat", "gudang", "no_bukti", "keterangan",
                  "golongan", "kategori", "jenis_obat", "status"]
    for kolom in kolom_teks:
        df[kolom] = (
            df[kolom]
            .astype("string")
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
            .str.lower()
        )

    df["kode_obat"] = df["kode_obat"].astype("string").str.strip()

    # penyaringan data non konsinyasi
    df_non_konsinyasi = df[
        df["jenis_obat"].astype("string").str.strip() == "non konsinyasi"
    ].copy()

    # pembersihan keterangan transaksi
    df_non_konsinyasi["keterangan_cek"] = (
        df_non_konsinyasi["keterangan"]
        .astype("string")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .str.lower()
    )

    # identifikasi jenis aktivitas transaksi
    keterangan = df_non_konsinyasi["keterangan_cek"]

    is_penjualan = keterangan.str.contains(r"^penjualan.*faktur", case=False, regex=True, na=False)

    is_pembelian = (
        keterangan.str.contains(r"^pembelian.*faktur", case=False, regex=True, na=False)
        & ~keterangan.str.contains(r"telah\s+di\s+hapus|telah\s+dihapus", case=False, regex=True, na=False)
        & ~keterangan.str.contains(r"^retur\s+pembelian", case=False, regex=True, na=False)
    )

    is_hapus_penjualan = keterangan.str.fullmatch(r"hapus\s+penjualan", case=False, na=False)

    is_hapus_pembelian = keterangan.str.contains(
        r"^pembelian.*telah\s+di\s+hapus$|^pembelian.*telah\s+dihapus$", case=False, regex=True, na=False
    )

    is_retur_pembelian = (
        keterangan.str.contains(r"^retur\s+pembelian", case=False, regex=True, na=False)
        & ~keterangan.str.contains(r"telah\s+di\s+hapus|telah\s+dihapus", case=False, regex=True, na=False)
    )

    is_hapus_retur_pembelian = keterangan.str.contains(
        r"^retur\s+pembelian.*telah\s+di\s+hapus$|^retur\s+pembelian.*telah\s+dihapus$",
        case=False, regex=True, na=False
    )

    # pembentukan penjualan bersih
    data_penjualan = df_non_konsinyasi[is_penjualan | is_hapus_penjualan].copy()
    data_penjualan["keluar_bersih"] = 0.0

    idx_penjualan = is_penjualan.loc[data_penjualan.index]
    data_penjualan.loc[idx_penjualan, "keluar_bersih"] = data_penjualan.loc[idx_penjualan, "keluar"]

    idx_hapus_penjualan = is_hapus_penjualan.loc[data_penjualan.index]
    data_penjualan.loc[idx_hapus_penjualan, "keluar_bersih"] = -data_penjualan.loc[idx_hapus_penjualan, "masuk"]

    penjualan_bersih = (
        data_penjualan
        .groupby(["no_bukti", "kode_obat"], as_index=False)
        .agg(total_keluar=("keluar_bersih", "sum"))
    )

    # pembentukan pembelian bersih
    data_pembelian = df_non_konsinyasi.copy()
    data_pembelian["no_faktur_asli"] = data_pembelian["keterangan_cek"].astype("string").apply(ambil_faktur)

    data_pembelian = data_pembelian[
        is_pembelian | is_retur_pembelian | is_hapus_pembelian | is_hapus_retur_pembelian
    ].copy()

    data_pembelian["efek_masuk"] = 0.0

    idx_pembelian = is_pembelian.loc[data_pembelian.index]
    idx_retur = is_retur_pembelian.loc[data_pembelian.index]
    idx_hapus_pembelian = is_hapus_pembelian.loc[data_pembelian.index]
    idx_hapus_retur = is_hapus_retur_pembelian.loc[data_pembelian.index]

    data_pembelian.loc[idx_pembelian, "efek_masuk"] = data_pembelian.loc[idx_pembelian, "masuk"]
    data_pembelian.loc[idx_retur, "efek_masuk"] = -data_pembelian.loc[idx_retur, "keluar"]
    data_pembelian.loc[idx_hapus_retur, "efek_masuk"] = data_pembelian.loc[idx_hapus_retur, "masuk"]
    data_pembelian.loc[idx_hapus_pembelian, "efek_masuk"] = -data_pembelian.loc[idx_hapus_pembelian, "keluar"]

    pembelian_bersih = (
        data_pembelian
        .groupby(["no_faktur_asli", "kode_obat"], as_index=False)
        .agg(total_masuk=("efek_masuk", "sum"))
    )

    # perhitungan total masuk, total keluar, dan identitas sku
    total_keluar = penjualan_bersih.groupby("kode_obat", as_index=False)["total_keluar"].sum()
    total_masuk = pembelian_bersih.groupby("kode_obat", as_index=False)["total_masuk"].sum()

    kode_obat = (
        df_non_konsinyasi[["kode_obat", "nama_obat", "golongan", "kategori", "jenis_obat"]]
        .dropna(subset=["kode_obat"])
        .drop_duplicates(subset=["kode_obat"])
        .copy()
    )

    data_agregat = (
        kode_obat
        .merge(total_masuk, on="kode_obat", how="left")
        .merge(total_keluar, on="kode_obat", how="left")
    )
    data_agregat[["total_masuk", "total_keluar"]] = data_agregat[["total_masuk", "total_keluar"]].fillna(0)

    # perhitungan frekuensi transaksi
    penjualan_valid = (
        df_non_konsinyasi[is_penjualan]
        .groupby(["no_bukti", "kode_obat"], as_index=False)
        .agg(total_keluar=("keluar", "sum"))
    )

    hapus_penjualan = (
        df_non_konsinyasi[is_hapus_penjualan]
        .groupby(["no_bukti", "kode_obat"], as_index=False)
        .agg(total_hapus=("masuk", "sum"))
    )

    penjualan_valid = penjualan_valid.merge(hapus_penjualan, on=["no_bukti", "kode_obat"], how="left")
    penjualan_valid["total_hapus"] = penjualan_valid["total_hapus"].fillna(0)
    penjualan_valid["keluar_bersih"] = penjualan_valid["total_keluar"] - penjualan_valid["total_hapus"]

    # penjualan valid 
    penjualan_valid = penjualan_valid[penjualan_valid["keluar_bersih"] > 0]

    # pembelian valid 
    pembelian_valid = pembelian_bersih[pembelian_bersih["total_masuk"] > 0].copy()

    frekuensi_penjualan = penjualan_valid.groupby("kode_obat").size().rename("frekuensi_penjualan")
    frekuensi_pembelian = pembelian_valid.groupby("kode_obat").size().rename("frekuensi_pembelian")

    frekuensi_transaksi = pd.concat([frekuensi_penjualan, frekuensi_pembelian], axis=1).fillna(0)
    frekuensi_transaksi["frekuensi_transaksi"] = (
        frekuensi_transaksi["frekuensi_penjualan"] + frekuensi_transaksi["frekuensi_pembelian"]
    ).astype(int)
    frekuensi_transaksi = frekuensi_transaksi[["frekuensi_transaksi"]].reset_index()

    data_agregat = data_agregat.merge(frekuensi_transaksi, on="kode_obat", how="left")
    data_agregat["frekuensi_transaksi"] = data_agregat["frekuensi_transaksi"].fillna(0).astype(int)

    # baris penjualan valid juga dipakai untuk halaman data penjualan
    baris_penjualan_valid = df_non_konsinyasi[is_penjualan].merge(
        penjualan_valid[["no_bukti", "kode_obat"]],
        on=["no_bukti", "kode_obat"],
        how="inner"
    )

    # baris pembelian valid juga dipakai untuk halaman data pembelian
    baris_pembelian_valid = data_pembelian[is_pembelian.loc[data_pembelian.index]].merge(
        pembelian_valid[["no_faktur_asli", "kode_obat"]],
        on=["no_faktur_asli", "kode_obat"],
        how="inner"
    )

    # perhitungan active months dari transaksi valid
    data_transaksi_valid = pd.concat(
        [baris_penjualan_valid[["tanggal", "kode_obat"]], baris_pembelian_valid[["tanggal", "kode_obat"]]],
        ignore_index=True
    )
    data_transaksi_valid["bulan"] = data_transaksi_valid["tanggal"].dt.to_period("M")

    active_months = (
        data_transaksi_valid
        .dropna(subset=["bulan"])
        .groupby("kode_obat")["bulan"]
        .nunique()
        .rename("active_months")
    )

    data_agregat = data_agregat.merge(active_months, on="kode_obat", how="left")
    data_agregat["active_months"] = data_agregat["active_months"].fillna(0).astype(int)

    # tanggal terakhir masuk dan keluar dari transaksi valid
    tanggal_terakhir_masuk = (
        baris_pembelian_valid
        .groupby("kode_obat")["tanggal"].max().rename("tanggal_terakhir_masuk")
    )
    tanggal_terakhir_keluar = (
        baris_penjualan_valid.groupby("kode_obat")["tanggal"].max().rename("tanggal_terakhir_keluar")
    )

    data_agregat = (
        data_agregat
        .merge(tanggal_terakhir_masuk, on="kode_obat", how="left")
        .merge(tanggal_terakhir_keluar, on="kode_obat", how="left")
    )
    data_agregat["tanggal_terakhir_masuk"] = pd.to_datetime(data_agregat["tanggal_terakhir_masuk"], errors="coerce")
    data_agregat["tanggal_terakhir_keluar"] = pd.to_datetime(data_agregat["tanggal_terakhir_keluar"], errors="coerce")

    # stok awal dan stok akhir
    data_stok = df_non_konsinyasi.sort_values(["kode_obat", "tanggal"]).copy()

    stok_awal = data_stok.drop_duplicates(subset="kode_obat", keep="first")[["kode_obat", "stok_awal"]].copy()
    stok_akhir = (
        data_stok.drop_duplicates(subset="kode_obat", keep="last")[["kode_obat", "sisa_stok"]]
        .rename(columns={"sisa_stok": "stok_akhir"})
        .copy()
    )

    data_agregat = data_agregat.merge(stok_awal, on="kode_obat", how="left")
    data_agregat = data_agregat.merge(stok_akhir, on="kode_obat", how="left")

    # tabel transaksi untuk halaman data penjualan dan data pembelian
    df_penjualan = (
        baris_penjualan_valid[["tanggal", "no_bukti", "kode_obat", "nama_obat", "keluar", "sisa_stok"]]
        .rename(columns={"keluar": "jumlah_terjual"})
        .sort_values("tanggal")
        .reset_index(drop=True)
    )
    df_pembelian = (
        baris_pembelian_valid[["tanggal", "no_faktur_asli", "kode_obat", "nama_obat", "masuk", "sisa_stok"]]
        .rename(columns={"masuk": "jumlah_dibeli", "no_faktur_asli": "no_faktur"})
        .sort_values("tanggal")
        .reset_index(drop=True)
    )

    # ringkasan jumlah baris dan periode data
    ringkasan = {
        "jumlah_baris_diunggah": len(df),
        "jumlah_baris_konsinyasi_dibuang": len(df) - len(df_non_konsinyasi),
        "jumlah_baris_diproses": len(df_non_konsinyasi),
        "jumlah_sku": data_agregat["kode_obat"].nunique(),
        "tanggal_awal": df_non_konsinyasi["tanggal"].min(),
        "tanggal_akhir": df_non_konsinyasi["tanggal"].max(),
    }

    return {
        "sku": data_agregat,
        "penjualan": df_penjualan,
        "pembelian": df_pembelian,
        "ringkasan": ringkasan,
    }
