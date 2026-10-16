# Issue 05 – Analisis Kebutuhan UI/UX

## Tujuan Pekerjaan

Menganalisis kebutuhan tampilan dan pengalaman pengguna (*User Interface/User Experience* atau UI/UX) untuk website monitoring kualitas air. Analisis mencakup dashboard monitoring, informasi sensor, grafik historis, status kualitas air, tampilan peringatan, halaman login, serta halaman administrasi.

Dokumen ini merupakan analisis kebutuhan dan rancangan awal UI/UX. Dokumen belum menetapkan desain visual final dan belum merupakan implementasi antarmuka.

## Keputusan dan Konteks Rancangan

- Sensor yang ditampilkan: suhu air, pH, dan kekeruhan.
- Interval pembacaan yang direncanakan: setiap 15 menit.
- Status kualitas air: `Normal`, `Waspada`, dan `Indikasi Anomali`.
- Penentuan `Indikasi Anomali` harus mempertimbangkan validasi antar-sensor dan persistensi empat siklus pengukuran berturut-turut.
- `Indikasi Anomali` adalah indikasi awal yang membutuhkan validasi lapangan, bukan bukti pasti pencemaran.
- Peran pengguna: `masyarakat`, `petugas`, dan `admin`.
- Data perangkat dikirim melalui MQTT ke backend, sedangkan website mengambil data melalui REST API.

---

## 1. Identifikasi Kebutuhan Dashboard

Dashboard merupakan halaman utama website yang menyajikan kondisi kualitas air secara ringkas dan mudah dipahami. Pengguna harus dapat mengetahui kondisi terkini, melihat nilai sensor, memeriksa tren historis, dan memahami apakah ada peringatan yang perlu ditindaklanjuti.

### 1.1 Informasi Utama Dashboard

Dashboard perlu menampilkan:

1. **Ringkasan status kualitas air**
   - Status terbaru: `Normal`, `Waspada`, atau `Indikasi Anomali`.
   - Waktu pembaruan atau waktu pengukuran terakhir.
   - Titik pemantauan yang sedang ditampilkan.
   - Keterangan singkat mengenai status tersebut.

2. **Kartu ringkasan sensor**
   - Suhu air dalam °C.
   - Nilai pH.
   - Kekeruhan dalam NTU jika satuan tersebut didukung oleh hasil kalibrasi sensor.
   - Waktu pembacaan terakhir untuk setiap nilai.
   - Indikator data tersedia, terlambat, atau tidak tersedia.

3. **Grafik historis**
   - Tren perubahan suhu, pH, dan kekeruhan.
   - Rentang waktu yang dapat dipilih.
   - Penanda waktu agar pengguna dapat memahami kapan perubahan terjadi.

4. **Bagian peringatan**
   - Peringatan aktif jika ada.
   - Waktu peringatan dibuat atau diperbarui.
   - Status kualitas air yang memicu peringatan.
   - Keterangan dan saran tindak lanjut yang sesuai dengan hasil analisis.

5. **Informasi titik pemantauan**
   - Nama atau identitas titik.
   - Lokasi atau koordinat jika tersedia.
   - Status operasional titik jika informasi tersebut dikelola oleh sistem.

### 1.2 Kebutuhan Pengalaman Pengguna

- Informasi terpenting, yaitu status kualitas air dan waktu pengukuran terakhir, mudah ditemukan.
- Nilai sensor menggunakan satuan yang jelas.
- Informasi disajikan dalam bahasa yang mudah dipahami, bukan hanya istilah teknis.
- Pengguna dapat berpindah dari ringkasan ke grafik atau detail peringatan tanpa alur yang membingungkan.
- Tampilan dapat digunakan pada komputer maupun perangkat seluler.
- Jika data belum tersedia, website menampilkan pesan yang jelas dan bukan nilai nol yang menyesatkan.
- Waktu pembaruan data harus terlihat agar pengguna tidak mengira data lama sebagai data terbaru.

### 1.3 Susunan Informasi Dashboard

Susunan awal yang disarankan:

1. Header: nama sistem, titik pemantauan aktif, dan menu pengguna.
2. Ringkasan status kualitas air dan waktu pengukuran terakhir.
3. Kartu nilai suhu, pH, dan kekeruhan.
4. Grafik historis dengan filter waktu.
5. Daftar peringatan dan detail hasil analisis.
6. Informasi titik pemantauan dan status data.

Susunan ini merupakan rancangan konseptual dan dapat disesuaikan setelah evaluasi kebutuhan pengguna.

## 2. Identifikasi Informasi Sensor

Website menampilkan data sensor yang diterima backend dari ESP32. Nilai yang ditampilkan harus sesuai dengan data yang benar-benar tersedia di database.

### 2.1 Informasi Sensor yang Ditampilkan

| Sensor / Parameter | Informasi pada UI | Satuan / Format |
|---|---|---|
| DS18B20 Waterproof | Suhu air | °C |
| PH-4502C | Nilai pH air | Skala pH |
| Turbidity Sensor Module | Tingkat kekeruhan air | NTU jika hasil kalibrasi mendukung satuan tersebut |

### 2.2 Elemen pada Setiap Kartu Sensor

Setiap kartu sensor sebaiknya menampilkan:

- Nama parameter.
- Nilai pembacaan terakhir.
- Satuan pengukuran.
- Waktu pembacaan terakhir.
- Tren sederhana dibandingkan pembacaan sebelumnya jika data pembanding tersedia.
- Indikator status data, misalnya tersedia, terlambat, atau tidak tersedia.

UI tidak boleh menyatakan sensor normal atau rusak hanya berdasarkan dugaan. Status perangkat sebaiknya didasarkan pada waktu data terakhir diterima dan aturan ketersediaan data yang ditetapkan tim.

### 2.3 Penanganan Data Tidak Tersedia

- Jika pembacaan belum pernah diterima, tampilkan `Belum ada data`.
- Jika data terakhir sudah melewati batas keterlambatan yang ditetapkan, tampilkan `Data terlambat` beserta waktu pembacaan terakhir.
- Jika nilai tidak valid, jangan menampilkannya seolah-olah sebagai pengukuran yang sah.
- Jangan mengganti data kosong dengan angka `0`, karena angka tersebut dapat disalahartikan sebagai hasil sensor.

Batas keterlambatan data perlu ditentukan pada tahap implementasi dan disesuaikan dengan interval pengukuran 15 menit serta kondisi komunikasi perangkat.

## 3. Identifikasi Kebutuhan Grafik

Grafik membantu pengguna memahami perubahan kualitas air dari waktu ke waktu, bukan hanya melihat satu nilai terbaru.

### 3.1 Grafik yang Dibutuhkan

| Grafik | Data | Tujuan |
|---|---|---|
| Grafik suhu | Suhu terhadap waktu | Melihat tren perubahan suhu air |
| Grafik pH | pH terhadap waktu | Melihat perubahan tingkat keasaman atau kebasaan |
| Grafik kekeruhan | Kekeruhan terhadap waktu | Melihat perubahan tingkat kekeruhan |
| Grafik gabungan (opsional) | Beberapa parameter dalam satu tampilan | Membandingkan pola perubahan jika skala dan satuannya tetap mudah dipahami |

Grafik terpisah menjadi pilihan awal yang lebih mudah dibaca karena suhu, pH, dan kekeruhan memiliki satuan serta rentang nilai berbeda.

### 3.2 Filter dan Kontrol Grafik

Pengguna sebaiknya dapat:

- Memilih titik pemantauan.
- Memilih rentang waktu, misalnya 24 jam terakhir, 7 hari terakhir, atau rentang tanggal tertentu.
- Melihat nilai dan waktu pengukuran melalui tooltip atau detail titik data.
- Melihat pesan jika data pada rentang waktu yang dipilih tidak tersedia.
- Memuat ulang data grafik melalui mekanisme pembaruan yang ditentukan aplikasi.

Pilihan rentang waktu di atas merupakan usulan UI dan dapat disesuaikan dengan kapasitas penyimpanan serta kebutuhan pengguna.

### 3.3 Aturan Penyajian Grafik

- Sumbu waktu harus menampilkan tanggal atau waktu secara jelas.
- Setiap grafik harus menampilkan nama parameter dan satuannya.
- Data yang tidak valid atau hilang tidak boleh digambar seolah-olah merupakan pembacaan valid.
- Jika ada celah data, UI perlu menampilkannya secara jujur dan tidak membuat tren palsu dengan menghubungkan data yang tidak berdekatan tanpa penjelasan.
- Grafik historis harus bersumber dari data yang tersimpan, bukan data contoh yang terlihat seperti data operasional.

## 4. Identifikasi Status Kualitas Air

Dashboard menggunakan tiga status yang telah ditetapkan dalam rancangan sistem.

| Status | Makna pada UI | Penyajian yang Disarankan |
|---|---|---|
| `Normal` | Berdasarkan data yang tersedia, kondisi belum memenuhi kriteria peringatan sistem | Label status dan ringkasan kondisi |
| `Waspada` | Ada kondisi yang perlu diperhatikan atau dipantau lebih lanjut | Label status, penjelasan singkat, dan hal yang perlu dipantau |
| `Indikasi Anomali` | Pola data memenuhi aturan deteksi dan memerlukan tindak lanjut serta validasi lapangan | Label status yang jelas, waktu kejadian, alasan indikasi, dan anjuran validasi lapangan |

### 4.1 Prinsip Tampilan Status

- Gunakan label teks secara eksplisit; jangan mengandalkan warna saja.
- Gunakan ikon atau warna sebagai pendukung, bukan satu-satunya penanda.
- Terapkan gaya visual yang konsisten untuk status yang sama di seluruh halaman.
- Tampilkan waktu analisis atau waktu pembaruan status.
- Jika status belum tersedia, tampilkan `Belum ada hasil analisis`.
- Hindari klaim bahwa sistem telah membuktikan pencemaran.

### 4.2 Informasi Pendukung Status

Jika tersedia dari backend, detail status dapat menampilkan:

- Parameter yang berkontribusi terhadap hasil analisis.
- Waktu pengukuran yang digunakan.
- Ringkasan aturan validasi antar-sensor.
- Jumlah siklus berturut-turut yang memenuhi kondisi.
- Penjelasan bahwa `Indikasi Anomali` membutuhkan validasi lapangan.

UI tidak boleh menampilkan rincian yang tidak dikirim atau tidak didukung oleh backend.

## 5. Identifikasi Tampilan Warning

Bagian warning atau peringatan digunakan untuk menarik perhatian pengguna ketika status `Waspada` atau `Indikasi Anomali` muncul. Peringatan harus informatif, proporsional, dan tidak menimbulkan kesimpulan yang lebih kuat daripada data yang tersedia.

### 5.1 Informasi pada Peringatan

Setiap peringatan sebaiknya menampilkan:

- Status peringatan.
- Titik pemantauan terkait.
- Waktu peringatan atau waktu analisis.
- Ringkasan alasan peringatan.
- Parameter sensor yang terkait, jika tersedia.
- Status validasi atau jumlah siklus persistensi, jika disediakan backend.
- Saran tindak lanjut yang tidak mengklaim adanya pencemaran pasti.

### 5.2 Perilaku Tampilan Warning

- Peringatan aktif terlihat jelas pada dashboard.
- Pengguna dapat membuka detail peringatan untuk membaca informasi lebih lengkap.
- Peringatan disusun berdasarkan waktu terbaru atau prioritas yang ditetapkan.
- Perubahan status harus mengikuti hasil backend, bukan hanya perubahan warna di antarmuka.
- Jika data pendukung belum lengkap, tampilkan bahwa informasi masih terbatas.
- Jika status kembali berubah, riwayat hasil analisis sebaiknya tetap dapat ditinjau sesuai data yang disimpan.

### 5.3 Aturan Peringatan Indikasi Anomali

Sebelum sistem menampilkan `Indikasi Anomali`, proses backend atau modul AI harus menerapkan validasi antar-sensor dan persistensi empat siklus pengukuran berturut-turut dengan interval 15 menit. UI menampilkan hasil dan alasan yang tersedia dari backend; UI tidak menggantikan proses validasi tersebut.

`Indikasi Anomali` harus dijelaskan sebagai indikasi awal yang memerlukan pemeriksaan atau validasi lapangan, bukan bukti pasti pencemaran.

## 6. Identifikasi Kebutuhan Halaman Admin

Halaman admin digunakan oleh pengguna dengan role `admin` untuk mengelola konfigurasi yang menjadi kewenangannya. Menu admin harus dilindungi autentikasi dan pemeriksaan role di backend.

### 6.1 Fitur Halaman Admin

| Fitur | Kebutuhan |
|---|---|
| Ringkasan administrasi | Menampilkan ringkasan titik pemantauan dan informasi sistem yang tersedia |
| Pengelolaan titik pemantauan | Menambah dan memperbarui nama, koordinat, serta informasi pemasangan titik |
| Status titik | Melihat status operasional dan menonaktifkan titik jika fitur ini diterapkan |
| Pengelolaan pengguna | Melihat, menambahkan, memperbarui, atau menonaktifkan akun sesuai kebijakan sistem |
| Pengaturan ambang batas | Mengelola ambang batas kualitas air sesuai rancangan dan kewenangan admin |
| Informasi sistem | Melihat status data terakhir atau informasi operasional yang disediakan backend |

Fitur yang belum didukung oleh SRS atau backend harus diperlakukan sebagai usulan dan dikonfirmasi sebelum implementasi.

### 6.2 Formulir Admin

Formulir pengelolaan data perlu:

- Memiliki label yang jelas untuk setiap kolom.
- Memvalidasi kolom wajib sebelum data dikirim.
- Menampilkan pesan kesalahan yang menjelaskan cara memperbaiki input.
- Meminta konfirmasi sebelum tindakan penting, seperti menonaktifkan akun atau titik pemantauan.
- Menampilkan pesan berhasil atau gagal setelah permintaan diproses backend.
- Tidak menampilkan password asli pengguna.

### 6.3 Hak Akses

- `masyarakat`: hanya mengakses halaman dan informasi publik.
- `petugas`: mengakses informasi pemantauan sesuai kewenangannya.
- `admin`: mengakses halaman administrasi sesuai hak yang ditentukan.

Pembatasan harus diterapkan di backend. Menyembunyikan menu admin di frontend saja tidak cukup untuk melindungi data dan fungsi administrasi.

## 7. Identifikasi Kebutuhan Halaman Login

Halaman login diperlukan untuk mengautentikasi pengguna yang mengakses fitur terlindungi.

Elemen halaman login:

- Kolom email.
- Kolom password.
- Tombol masuk.
- Validasi kolom wajib.
- Pesan kesalahan jika kredensial tidak valid.
- Indikator proses ketika permintaan login sedang berjalan.
- Penanganan akun nonaktif atau akses yang ditolak dengan pesan yang sesuai.

Setelah login berhasil, pengguna diarahkan ke halaman sesuai role dan kebijakan akses. Token autentikasi harus ditangani dengan aman; password tidak boleh disimpan atau ditampilkan kembali oleh UI.

## 8. Kebutuhan Responsif dan Aksesibilitas

- Website harus dapat digunakan pada desktop, tablet, dan perangkat seluler.
- Kartu sensor dan grafik harus menyesuaikan lebar layar.
- Teks, label, dan tombol harus mudah dibaca dan digunakan.
- Warna status harus memiliki kontras yang memadai.
- Informasi status harus disampaikan melalui teks, bukan warna saja.
- Formulir harus memiliki label yang jelas dan pesan validasi yang mudah dipahami.
- Tabel pada halaman admin perlu tetap dapat digunakan pada layar kecil, misalnya dengan tata letak responsif atau area gulir horizontal yang jelas.

## 9. Ringkasan Kebutuhan Halaman

| Halaman | Pengguna | Informasi / Fungsi Utama |
|---|---|---|
| Dashboard | Masyarakat, petugas, admin sesuai hak akses | Status kualitas air, kartu sensor, grafik historis, dan peringatan |
| Detail pemantauan | Masyarakat / Petugas sesuai kebijakan | Data sensor dan hasil analisis berdasarkan titik serta rentang waktu |
| Detail peringatan | Masyarakat / Petugas sesuai kebijakan | Status, waktu, alasan, parameter terkait, dan catatan validasi |
| Login | Pengguna terdaftar | Autentikasi email dan password |
| Administrasi titik | Admin | Menambah dan memperbarui titik pemantauan |
| Administrasi pengguna | Admin | Mengelola akun dan role sesuai kewenangan |
| Pengaturan ambang batas | Admin | Mengelola ambang batas jika fitur diterapkan |

