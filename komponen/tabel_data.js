// menulis angka dengan titik ribuan, contoh 1250 menjadi 1.250
function tulisAngka(nilai) {
    if (nilai === null || nilai === undefined) return "-";
    return Number(nilai).toLocaleString("id-ID");
}

// membuat elemen html serta nama kelas dan tulisannya
function buatElemen(jenisElemen, namaKelas, tulisan) {
    const elemen = document.createElement(jenisElemen);
    if (namaKelas) elemen.className = namaKelas;
    if (tulisan !== undefined) elemen.textContent = tulisan;
    return elemen;
}

// membaca filter yang pernah disimpan di browser
function bacaFilterTersimpan(namaPenyimpanan) {
    try {
        return JSON.parse(sessionStorage.getItem(namaPenyimpanan));
    } catch (kesalahan) {
        return null;
    }
}

// menyimpan filter di browser supaya tidak hilang saat pindah halaman
function simpanFilter(namaPenyimpanan, filter) {
    try {
        sessionStorage.setItem(namaPenyimpanan, JSON.stringify(filter));
    } catch (kesalahan) {
        // kalau browser tidak mengizinkan, filter hanya berlaku sementara
    }
}

// nama data yang dipakai untuk memfilter suatu kolom
function kunciFilter(kolom) {
    return kolom.kunci_filter || kolom.kunci;
}

// filter awal yang menampilkan semua data
function buatFilterAwal(pengaturan) {
    const filter = { versi: pengaturan.versi, cari: "", halaman: 1, urut: pengaturan.urut_awal || null };
    for (const kolom of pengaturan.kolom) {
        if (kolom.filter === "pilihan") filter[kunciFilter(kolom)] = [...pengaturan.pilihan[kunciFilter(kolom)]];
        if (kolom.filter === "rentang") filter[kolom.kunci] = [null, null];
    }
    return filter;
}

// mengecek apakah filter suatu kolom sedang dipakai
function filterDipakai(filter, pengaturan, kolom) {
    if (kolom.filter === "pilihan") {
        return filter[kunciFilter(kolom)].length !== pengaturan.pilihan[kunciFilter(kolom)].length;
    }
    const [minimal, maksimal] = filter[kolom.kunci];
    return (minimal !== null && minimal > 0) || maksimal !== null;
}

// menyaring baris sesuai pencarian dan filter, lalu mengurutkannya
function saringBaris(semuaBaris, pengaturan, filter) {
    const kataCari = filter.cari.trim().toLowerCase();

    const hasil = semuaBaris.filter((baris) => {
        // pencarian kata harus ada di salah satu kolom pencarian
        if (kataCari && pengaturan.cari) {
            const cocok = pengaturan.cari.kolom.some((kunci) => String(baris[kunci] ?? "").toLowerCase().includes(kataCari));
            if (!cocok) return false;
        }

        // filter setiap kolom
        for (const kolom of pengaturan.kolom) {
            if (!kolom.filter || !filterDipakai(filter, pengaturan, kolom)) continue;

            if (kolom.filter === "pilihan" && !filter[kunciFilter(kolom)].includes(baris[kunciFilter(kolom)])) return false;

            if (kolom.filter === "rentang") {
                const nilai = baris[kolom.kunci];
                const [minimal, maksimal] = filter[kolom.kunci];
                if (nilai === null) return false;
                if (minimal !== null && nilai < minimal) return false;
                if (maksimal !== null && nilai > maksimal) return false;
            }
        }
        return true;
    });

    // mengurutkan dari yang terkecil ke terbesar atau dari terbesar ke terkecil
    if (filter.urut) {
        const { kunci, arah } = filter.urut;
        const pengali = arah === "naik" ? 1 : -1;
        hasil.sort((a, b) => {
            if (a[kunci] < b[kunci]) return -1 * pengali;
            if (a[kunci] > b[kunci]) return 1 * pengali;
            return 0;
        });
    }
    return hasil;
}

// mengunduh file excel yang dikirim dari python
function unduhFileExcel(unduhan) {
    const isiFile = Uint8Array.from(atob(unduhan.isi), (huruf) => huruf.charCodeAt(0));
    const file = new Blob([isiFile], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
    const tautan = document.createElement("a");
    tautan.href = URL.createObjectURL(file);
    tautan.download = unduhan.nama_file;
    document.body.appendChild(tautan);
    tautan.click();
    tautan.remove();
    setTimeout(() => URL.revokeObjectURL(tautan.href), 1000);
}

export default function (komponen) {
    // data = pengaturan tabel dari python, parentElement = tempat tabel digambar,
    // setTriggerValue = cara mengirim nilai ke python
    const { data, parentElement, setTriggerValue } = komponen;
    const pengaturan = data;
    const tempatTabel = parentElement;

    // menghapus tampilan lama kalau tabel digambar ulang
    if (tempatTabel.hapusTampilanLama) tempatTabel.hapusTampilanLama();

    // setiap baris diberi nomor asli supaya python tahu baris mana yang diekspor
    const semuaBaris = pengaturan.baris.map((baris, nomor) => ({ ...baris, nomor_baris: nomor }));

    // memakai filter tersimpan kalau datanya masih sama, kalau tidak memakai filter awal
    let filter = bacaFilterTersimpan(pengaturan.nama_penyimpanan);
    if (!filter || filter.versi !== pengaturan.versi) filter = buatFilterAwal(pengaturan);

    // file excel dari python langsung diunduh (sekali saja untuk setiap file)
    if (pengaturan.unduhan && tempatTabel.tandaUnduhanTerakhir !== pengaturan.unduhan.tanda) {
        tempatTabel.tandaUnduhanTerakhir = pengaturan.unduhan.tanda;
        unduhFileExcel(pengaturan.unduhan);
    }

    // wadah utama tabel
    const wadah = buatElemen("div", "wadah");

    // kotak pencarian di atas tabel
    const kotakCari = buatElemen("input", "cari");
    if (pengaturan.cari) {
        const barisAtas = buatElemen("div", "atas");
        kotakCari.placeholder = pengaturan.cari.petunjuk;
        kotakCari.value = filter.cari;
        barisAtas.append(kotakCari);
        wadah.append(barisAtas);
    }

    // tombol filter khusus layar kecil, karena judul kolom disembunyikan kalau di hp
    const filterPonsel = buatElemen("div", "filter-ponsel");
    for (const kolom of pengaturan.kolom) {
        if (!kolom.filter) continue;
        const tombol = buatElemen("button", "judul-filter", kolom.judul);
        tombol.dataset.kolom = kolom.kunci;
        tombol.append(buatElemen("span", "panah"));
        filterPonsel.append(tombol);
    }
    if (filterPonsel.children.length > 0) wadah.append(filterPonsel);

    // tabel-> lebar kolom, judul kolom, dan isi
    const pembungkus = buatElemen("div", "pembungkus");
    const tabel = buatElemen("table");
    tabel.style.setProperty("--lebar-minimal", `${pengaturan.lebar_minimal}px`);
    const aturanLebar = buatElemen("colgroup");
    const barisJudul = buatElemen("tr");
    for (const kolom of pengaturan.kolom) {
        const lebar = buatElemen("col");
        lebar.style.width = kolom.lebar;
        aturanLebar.append(lebar);

        const selJudul = buatElemen("th", kolom.rata || "");
        if (kolom.filter) {
            const tombol = buatElemen("button", "judul-filter", kolom.judul);
            tombol.dataset.kolom = kolom.kunci;
            tombol.append(buatElemen("span", "panah"));
            selJudul.append(tombol);
        } else {
            selJudul.textContent = kolom.judul;
        }
        barisJudul.append(selJudul);
    }
    const bagianJudul = buatElemen("thead");
    bagianJudul.append(barisJudul);
    const bagianIsi = buatElemen("tbody");
    tabel.append(aturanLebar, bagianJudul, bagianIsi);
    pembungkus.append(tabel);

    // keterangan jumlah data dan tombol pindah halaman tabel
    const barisBawah = buatElemen("div", "bawah");
    const keterangan = buatElemen("div", "keterangan");
    const navigasi = buatElemen("div", "halaman");
    const tombolSebelumnya = buatElemen("button", "", "Sebelumnya");
    const tulisanHalaman = buatElemen("span");
    const tombolSelanjutnya = buatElemen("button", "", "Selanjutnya");
    navigasi.append(tombolSebelumnya, tulisanHalaman, tombolSelanjutnya);
    barisBawah.append(keterangan, navigasi);
    const areaEkspor = buatElemen("div", "area-ekspor");
    const tombolEkspor = buatElemen("button", "ekspor", "Ekspor ke Excel");
    areaEkspor.append(tombolEkspor);

    // panel filter yang muncul saat judul kolom diklik
    const panel = buatElemen("div", "panel");
    panel.hidden = true;

    wadah.append(pembungkus, barisBawah);
    if (pengaturan.ekspor) wadah.append(areaEkspor);
    wadah.append(panel);
    tempatTabel.append(wadah);

    // membuat satu sel tabel sesuai jenis kolomnya
    function buatSel(kolom, baris, nomorUrut) {
        let sel;
        if (kolom.jenis === "nomor") {
            sel = buatElemen("td", kolom.rata, String(nomorUrut));
        } else if (kolom.jenis === "angka") {
            sel = buatElemen("td", kolom.rata, tulisAngka(baris[kolom.kunci]));
        } else if (kolom.jenis === "tombol") {
            sel = buatElemen("td", kolom.rata);
            const tombol = buatElemen("button", "tombol-baris", kolom.teks_tombol);
            tombol.onclick = () => setTriggerValue("tombol", baris[kolom.kunci_nilai]);
            sel.append(tombol);
        } else {
            const namaKelas = [kolom.rata || "", kolom.jenis === "kelas" ? "kelas" : "", kolom.jenis === "kode" ? "kode" : ""].join(" ").trim();
            sel = buatElemen("td", namaKelas, baris[kolom.kunci] ?? "-");
        }
        // nama kolom ditulis di samping isi sel saat tampil di ponsel
        sel.dataset.label = kolom.judul;
        return sel;
    }

    // menggambar isi tabel sesuai pencarian, filter, dan halaman yang sedang dibuka
    let barisTampil = [];
    function gambarTabel() {
        barisTampil = saringBaris(semuaBaris, pengaturan, filter);
        const jumlahHalaman = Math.max(Math.ceil(barisTampil.length / pengaturan.baris_per_halaman), 1);
        filter.halaman = Math.min(Math.max(filter.halaman, 1), jumlahHalaman);
        simpanFilter(pengaturan.nama_penyimpanan, filter);

        // menampilkan pesan kalau tidak ada data
        bagianIsi.replaceChildren();
        if (barisTampil.length === 0) {
            const baris = buatElemen("tr");
            const sel = buatElemen("td", "kosong", pengaturan.teks_kosong);
            sel.colSpan = pengaturan.kolom.length;
            baris.append(sel);
            bagianIsi.append(baris);
        }

        // hanya baris di halaman ini yang digambar
        const awal = (filter.halaman - 1) * pengaturan.baris_per_halaman;
        const barisHalamanIni = barisTampil.slice(awal, awal + pengaturan.baris_per_halaman);
        barisHalamanIni.forEach((dataBaris, urutan) => {
            const baris = buatElemen("tr", dataBaris.warna_baris || "");
            for (const kolom of pengaturan.kolom) baris.append(buatSel(kolom, dataBaris, awal + urutan + 1));
            bagianIsi.append(baris);
        });

        keterangan.textContent = `Menampilkan ${tulisAngka(barisTampil.length)} dari ${tulisAngka(semuaBaris.length)} ${pengaturan.satuan}`;
        tulisanHalaman.textContent = `Halaman ${filter.halaman} dari ${jumlahHalaman}`;
        tombolSebelumnya.disabled = filter.halaman <= 1;
        tombolSelanjutnya.disabled = filter.halaman >= jumlahHalaman;

        // judul kolom yang sedang difilter diberi tanda
        wadah.querySelectorAll(".judul-filter").forEach((tombol) => {
            const kolom = pengaturan.kolom.find((k) => k.kunci === tombol.dataset.kolom);
            tombol.classList.toggle("aktif", filterDipakai(filter, pengaturan, kolom));
        });
    }

    // mengubah filter lalu kembali ke halaman pertama
    function ubahFilter(perubahan) {
        perubahan();
        filter.halaman = 1;
        gambarTabel();
    }

    // isi panel untuk mengurutkan data (misalnya terlama atau terbaru)
    function isiPanelUrut(kolom) {
        const bagianUrut = buatElemen("div", "urut");
        for (const [arah, tulisan] of [["naik", kolom.urut.naik], ["turun", kolom.urut.turun]]) {
            const tombol = buatElemen("button", "", tulisan);
            const sedangDipakai = filter.urut && filter.urut.kunci === kolom.urut.kunci && filter.urut.arah === arah;
            tombol.classList.toggle("aktif", Boolean(sedangDipakai));
            tombol.onclick = () => {
                ubahFilter(() => { filter.urut = { kunci: kolom.urut.kunci, arah: arah }; });
                bagianUrut.querySelectorAll("button").forEach((b) => b.classList.toggle("aktif", b === tombol));
            };
            bagianUrut.append(tombol);
        }
        panel.append(bagianUrut);
    }

    // isi panel untuk filter berupa daftar centang
    function isiPanelPilihan(kunci) {
        const semuaPilihan = pengaturan.pilihan[kunci];
        const daftar = buatElemen("div", "daftar");

        // kotak cari kecil kalau pilihannya banyak
        if (semuaPilihan.length > 8) {
            const cariPilihan = buatElemen("input", "cari-pilihan");
            cariPilihan.placeholder = "Cari di daftar";
            cariPilihan.oninput = () => {
                const kata = cariPilihan.value.toLowerCase();
                daftar.querySelectorAll("label[data-nilai]").forEach((label) => {
                    label.hidden = !label.dataset.nilai.toLowerCase().includes(kata);
                });
            };
            panel.append(cariPilihan);
        }

        // centang "pilih semua"
        const labelSemua = buatElemen("label", "semua");
        const centangSemua = buatElemen("input");
        centangSemua.type = "checkbox";
        labelSemua.append(centangSemua, document.createTextNode("Pilih semua"));
        daftar.append(labelSemua);

        // satu centang untuk setiap pilihan
        const daftarCentang = semuaPilihan.map((nilai) => {
            const label = buatElemen("label");
            label.dataset.nilai = nilai;
            const centang = buatElemen("input");
            centang.type = "checkbox";
            centang.checked = filter[kunci].includes(nilai);
            centang.dataset.nilai = nilai;
            centang.onchange = () => ubahFilter(() => {
                filter[kunci] = daftarCentang.filter((c) => c.checked).map((c) => c.dataset.nilai);
                centangSemua.checked = filter[kunci].length === semuaPilihan.length;
            });
            label.append(centang, document.createTextNode(nilai));
            daftar.append(label);
            return centang;
        });

        centangSemua.checked = filter[kunci].length === semuaPilihan.length;
        centangSemua.onchange = () => ubahFilter(() => {
            daftarCentang.forEach((centang) => { centang.checked = centangSemua.checked; });
            filter[kunci] = centangSemua.checked ? [...semuaPilihan] : [];
        });
        panel.append(daftar);
    }

    // isi panel untuk filter rentang angka (minimal dan maksimal)
    function isiPanelRentang(kunci) {
        const nilaiTertinggi = pengaturan.maksimal[kunci];
        const rentang = buatElemen("div", "rentang");
        const kotakAngka = filter[kunci].map((nilai, urutan) => {
            const masukan = buatElemen("input");
            masukan.type = "number";
            masukan.min = "0";
            masukan.max = String(nilaiTertinggi);
            masukan.placeholder = "0";
            masukan.value = nilai === null ? "" : nilai;
            rentang.append(buatElemen("span", "", urutan === 0 ? "Minimal" : "Maksimal"), masukan);
            return masukan;
        });

        // angka yang diketik dijaga supaya tetap di antara 0 dan nilai tertinggi
        const terapkan = () => ubahFilter(() => {
            filter[kunci] = kotakAngka.map((masukan) => {
                if (masukan.value === "") return null;
                const nilai = Math.min(Math.max(Number(masukan.value), 0), nilaiTertinggi);
                if (Number(masukan.value) !== nilai) masukan.value = nilai;
                return nilai;
            });
        });
        kotakAngka.forEach((masukan) => { masukan.oninput = terapkan; });
        panel.append(rentang, buatElemen("div", "batas", `Rentang data: 0 sampai ${tulisAngka(nilaiTertinggi)}`));
    }

    // membuka panel filter di bawah tombol yang diklik
    let tombolTerbuka = null;
    function bukaPanel(tombol) {
        // klik tombol yang sama sekali lagi berarti menutup panel
        if (tombolTerbuka === tombol && !panel.hidden) return tutupPanel();

        const kolom = pengaturan.kolom.find((k) => k.kunci === tombol.dataset.kolom);
        panel.replaceChildren();
        if (kolom.urut) isiPanelUrut(kolom);
        if (kolom.filter === "pilihan") isiPanelPilihan(kunciFilter(kolom));
        else isiPanelRentang(kolom.kunci);

        // tombol untuk mengembalikan filter kolom ini seperti semula
        const tombolAturUlang = buatElemen("button", "ulang", "Atur ulang");
        tombolAturUlang.onclick = () => {
            const kunci = kolom.filter === "pilihan" ? kunciFilter(kolom) : kolom.kunci;
            ubahFilter(() => { filter[kunci] = buatFilterAwal(pengaturan)[kunci]; });
            tombolTerbuka = null;
            bukaPanel(tombol);
        };
        panel.append(tombolAturUlang);

        panel.hidden = false;
        tombolTerbuka = tombol;
        aturPosisiPanel();
    }

    // panel diletakkan tepat di bawah tombol dan tidak keluar dari layar
    function aturPosisiPanel() {
        const posisi = tombolTerbuka.getBoundingClientRect();
        const kiriTerjauh = window.innerWidth - panel.offsetWidth - 8;
        panel.style.left = `${Math.max(Math.min(posisi.left, kiriTerjauh), 8)}px`;
        panel.style.top = `${posisi.bottom + 8}px`;
    }

    // menutup panel filter
    function tutupPanel() {
        panel.hidden = true;
        tombolTerbuka = null;
    }

    // menghubungkan tombol-tombol dengan tugasnya
    kotakCari.oninput = () => ubahFilter(() => { filter.cari = kotakCari.value; });
    tombolSebelumnya.onclick = () => { filter.halaman -= 1; gambarTabel(); };
    tombolSelanjutnya.onclick = () => { filter.halaman += 1; gambarTabel(); };
    wadah.querySelectorAll(".judul-filter").forEach((tombol) => {
        tombol.onclick = () => bukaPanel(tombol);
    });

    // tombol ekspor mengirim nomor baris yang sedang tampil ke python
    tombolEkspor.onclick = () => {
        tombolEkspor.disabled = true;
        tombolEkspor.textContent = "Menyiapkan file...";
        setTriggerValue("ekspor", barisTampil.map((baris) => baris.nomor_baris));
    };

    // panel ditutup saat klik di luar panel, dan ikut bergeser saat halaman digulir
    const klikDiLuarPanel = (kejadian) => {
        const jalurKlik = kejadian.composedPath();
        const kenaPanel = jalurKlik.includes(panel);
        const kenaTombolFilter = jalurKlik.some((elemen) => elemen.classList && elemen.classList.contains("judul-filter"));
        if (!panel.hidden && !kenaPanel && !kenaTombolFilter) tutupPanel();
    };
    const saatDigulir = (kejadian) => {
        if (!panel.hidden && !kejadian.composedPath().includes(panel)) aturPosisiPanel();
    };
    document.addEventListener("click", klikDiLuarPanel);
    document.addEventListener("scroll", saatDigulir, true);

    gambarTabel();

    // membersihkan tabel saat digambar ulang atau saat pindah halaman
    const hapusTampilan = () => {
        document.removeEventListener("click", klikDiLuarPanel);
        document.removeEventListener("scroll", saatDigulir, true);
        wadah.remove();
        tempatTabel.hapusTampilanLama = null;
    };
    tempatTabel.hapusTampilanLama = hapusTampilan;
    return hapusTampilan;
}
