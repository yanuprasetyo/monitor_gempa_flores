# Monitor Berita Gempa Flores & Maumere 2026

Dashboard sederhana untuk memantau pemberitaan media tentang gempa M7,7
Flores/Maumere (15 Agustus 2026), dikelompokkan per fase penanganan bencana:

- Gempa & Gempa Susulan (Umum)
- Tanggap Darurat & Evakuasi
- Korban & Kerusakan
- Rehabilitasi & Rekonstruksi
- Pemulihan & Bantuan Sosial

Cara kerjanya sama seperti dashboard "Monitor Berita Pascabencana Banjir
Sumatera" yang sudah pernah dibuat sebelumnya: setiap 6 jam, sebuah program
otomatis (bukan Anda yang menjalankan) mengambil berita terbaru dari Google
News, lalu halaman web ini menampilkannya dalam bentuk daftar, grafik, dan
kalender.

## Apa saja isi folder ini

| Bagian | Fungsi |
|---|---|
| `index.html` | Halaman web dashboard yang akan dilihat orang (tidak perlu diedit) |
| `data/news.json` | "Gudang data" berita — otomatis diperbarui, jangan diedit manual |
| `scripts/fetch_news.py` | Program pengambil berita — tidak perlu diedit |
| `.github/workflows/update-news.yml` | Jadwal otomatis "ambil berita tiap 6 jam" |

## Langkah menampilkan dashboard ini secara online (GitHub Pages)

Anda tidak perlu paham coding untuk langkah-langkah ini — hanya klik dan isi form.

1. **Buat repository baru** di GitHub (github.com → tombol hijau "New").
   Beri nama misalnya `monitor_gempa_flores`. Pilih "Public" (harus public
   supaya GitHub Pages gratis bisa dipakai).

2. **Unggah semua file** di folder ini ke repository tersebut. Caranya:
   buka halaman repo yang baru dibuat → klik "Add file" → "Upload files" →
   seret (drag-and-drop) seluruh isi folder ini, termasuk folder
   `.github` dan `data` (pastikan strukturnya tetap sama, jangan hanya
   file-nya saja tanpa folder).

   *Catatan:* folder `.github` kadang tersembunyi di file explorer komputer
   Anda. Jika upload lewat browser tidak menyertakan folder tersembunyi,
   beri tahu saya — saya bisa bantu siapkan lewat cara lain.

3. **Aktifkan GitHub Pages**: di repo → Settings → Pages (menu kiri) →
   pada "Branch" pilih `main` dan folder `/ (root)` → Save. Setelah
   beberapa menit, dashboard akan bisa diakses di alamat seperti:
   `https://<nama-akun-anda>.github.io/monitor_gempa_flores/`

4. **Nyalakan pengambilan berita otomatis**: di repo → tab "Actions" →
   akan muncul workflow bernama "Perbarui Berita Gempa Flores" → klik →
   klik tombol "Run workflow" (di kanan) untuk menjalankan pertama kali
   secara manual. Setelah itu, ia akan berjalan sendiri setiap 6 jam.

5. Refresh halaman dashboard setelah workflow pertama selesai (biasanya
   1–2 menit) — data berita akan mulai muncul.

## Menyesuaikan cakupan pemantauan

Kalau suatu saat ingin menambah kata kunci pencarian (misalnya menyertakan
"gempa NTB" karena ada wilayah lain yang ikut terdampak), tinggal beri tahu
saya — saya bisa update bagian `SEARCH_QUERIES` di `scripts/fetch_news.py`
tanpa Anda perlu mengedit kode sendiri.

## Catatan sumber

Semua berita diambil dari Google News RSS (judul & tautan asli media,
tidak diubah). Dashboard ini hanya untuk keperluan pemantauan/riset —
selalu buka tautan aslinya untuk membaca berita lengkap.
