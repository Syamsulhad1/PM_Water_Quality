# Issue 04 – Analisis Kebutuhan Backend dan Database

## Tujuan Pekerjaan

Mengidentifikasi data yang perlu dikelola, struktur entitas database, kebutuhan API, dan mekanisme autentikasi agar backend dapat menerima data sensor dari ESP32, menyimpan data, menyediakan data untuk modul AI dan dashboard, serta mengelola akses pengguna.

## Keputusan Rancangan

- **Status AI:** `Normal`, `Waspada`, `Indikasi Anomali`.
- **Protokol perangkat ke backend:** MQTT melalui broker.
- **Validasi anomali:** mempertimbangkan validasi antar-sensor dan persistensi empat siklus pengukuran dengan interval 15 menit.
- **Database:** mempertahankan tiga entitas inti proposal (`TITIK_PANTAU`, `PEMBACAAN_SENSOR`, `HASIL_ANALISIS`) dan menambahkan entitas pengguna untuk autentikasi.
- **Interpretasi anomali:** `Indikasi Anomali` merupakan indikasi awal yang membutuhkan validasi lapangan, bukan bukti pasti pencemaran.

---

## 1. Identifikasi Data Sensor

Data sensor merupakan data utama yang dikirimkan ESP32 dari titik pemantauan. Backend menerima, memvalidasi, dan menyimpan data agar dapat digunakan oleh modul AI serta ditampilkan pada dashboard.

### 1.1 Data yang Dibutuhkan

| Data | Tipe Data yang Disarankan | Keterangan |
|---|---|---|
| `id_baca` | Integer / UUID | Identitas unik setiap pembacaan |
| `id_titik` | Integer / UUID | Identitas titik pemantauan asal data |
| `waktu_baca` | Timestamp | Waktu pengukuran dilakukan |
| `suhu` | Decimal | Suhu air dalam °C |
| `ph` | Decimal | Nilai pH air |
| `kekeruhan` | Decimal | Tingkat kekeruhan air dalam NTU, jika kalibrasi sensor mendukung satuan tersebut |
| `status` | Enum / Varchar | Status kualitas air jika hasil klasifikasi disimpan bersama pembacaan |

`id_baca` membedakan setiap pembacaan, sedangkan `id_titik` menghubungkan pembacaan dengan titik pemantauan yang benar.

### 1.2 Kebutuhan Pengelolaan Data Sensor

- ESP32 membaca suhu, pH, dan kekeruhan setiap 15 menit.
- ESP32 mengirimkan data ke backend melalui MQTT.
- Backend memvalidasi kelengkapan data, tipe data, waktu pengukuran, dan identitas titik pemantauan sebelum menyimpan data.
- Data yang tidak valid tidak boleh langsung digunakan untuk analisis AI.
- Backend menyimpan riwayat pembacaan agar dashboard dapat menampilkan data terkini maupun historis.
- Data sensor yang diterima disediakan untuk modul AI melalui proses backend yang terdefinisi.

**Catatan rancangan:** status AI akhir sebaiknya disimpan pada `HASIL_ANALISIS` agar data mentah sensor tidak tercampur dengan hasil analisis. Kolom `status` pada `PEMBACAAN_SENSOR` bersifat opsional jika tim memilih menyimpan hasil klasifikasi per pembacaan.

## 2. Identifikasi Data Monitoring Point

Monitoring point adalah lokasi atau titik tempat sensor dipasang dan digunakan untuk memantau kualitas air.

### 2.1 Data yang Dibutuhkan

| Data | Tipe Data yang Disarankan | Keterangan |
|---|---|---|
| `id_titik` | Integer / UUID | Identitas unik titik pemantauan |
| `nama` | Varchar | Nama atau label titik pemantauan |
| `koordinat` | Decimal / JSON / kolom koordinat terpisah | Lokasi geografis titik pemantauan |
| `tanggal_pasang` | Date | Tanggal pemasangan perangkat |
| `status_aktif` | Boolean / Enum (opsional) | Menandakan titik masih beroperasi atau sudah tidak aktif |

Struktur ini mempertahankan entitas `TITIK_PANTAU` dari proposal. `status_aktif` merupakan usulan tambahan yang dapat diterapkan jika dibutuhkan.

### 2.2 Kebutuhan Pengelolaan Monitoring Point

- Admin dapat menambahkan dan memperbarui informasi titik pemantauan.
- Setiap pembacaan sensor harus terhubung ke satu titik pemantauan.
- Dashboard dapat menampilkan data berdasarkan titik pemantauan.
- Sistem mendukung pencarian riwayat data berdasarkan titik dan rentang waktu.
- Titik yang sudah tidak digunakan sebaiknya dinonaktifkan, bukan langsung dihapus, agar riwayat pembacaan dan analisis tetap terjaga.

## 3. Identifikasi Data User

Data pengguna diperlukan untuk mengelola akun, melakukan autentikasi, dan membatasi akses berdasarkan peran pengguna. Entitas pengguna ditambahkan untuk melengkapi tiga entitas inti proposal.

### 3.1 Data yang Dibutuhkan

| Data | Tipe Data yang Disarankan | Keterangan |
|---|---|---|
| `id_user` | Integer / UUID | Identitas unik pengguna |
| `nama` | Varchar | Nama pengguna |
| `email` | Varchar | Email untuk identitas akun dan login |
| `password_hash` | Varchar | Password yang sudah di-hash, bukan password asli |
| `role` | Enum / Varchar | Peran pengguna dalam sistem |
| `status_akun` | Boolean / Enum | Menandakan akun aktif atau nonaktif |
| `created_at` | Timestamp | Waktu akun dibuat |
| `updated_at` | Timestamp | Waktu terakhir data akun diperbarui |

Email harus unik agar satu alamat email tidak digunakan oleh beberapa akun. Password tidak boleh disimpan dalam bentuk teks biasa.

### 3.2 Peran Pengguna

| Role | Hak Akses |
|---|---|
| `masyarakat` | Melihat dashboard dan informasi kualitas air yang tersedia untuk publik |
| `petugas` | Melihat data sensor, riwayat pengukuran, dan hasil analisis untuk pemantauan |
| `admin` | Mengelola titik pemantauan, akun pengguna, dan ambang batas sesuai kewenangannya |

Pembagian tersebut menggunakan konsep *Role-Based Access Control* (RBAC). Hak akses setiap endpoint harus diterapkan di backend, bukan hanya dengan menyembunyikan menu di dashboard.

## 4. Identifikasi Data Anomali

Data anomali digunakan untuk menyimpan hasil analisis kualitas air yang dihasilkan modul AI atau mekanisme deteksi anomali backend. Struktur ini mempertahankan entitas inti proposal, yaitu `HASIL_ANALISIS`.

### 4.1 Data yang Dibutuhkan

| Data | Tipe Data yang Disarankan | Keterangan |
|---|---|---|
| `id_hasil` | Integer / UUID | Identitas unik hasil analisis |
| `id_titik` | Integer / UUID | Titik pemantauan terkait |
| `waktu_analisis` | Timestamp | Waktu analisis dilakukan |
| `jenis` | Varchar / Enum | Jenis analisis, misalnya klasifikasi atau deteksi anomali |
| `tingkat_risiko` | Enum / Varchar | Status: `Normal`, `Waspada`, atau `Indikasi Anomali` |
| `estimasi_waktu` | Timestamp / Nullable | Waktu estimasi jika fitur prediksi benar-benar diterapkan |
| `keterangan` | Text | Penjelasan hasil analisis |
| `jumlah_siklus_persistensi` | Integer | Jumlah siklus berturut-turut yang memenuhi kondisi |
| `aturan_cross_sensor` | Text / JSON | Informasi validasi antar-sensor yang digunakan |

`jumlah_siklus_persistensi` dan `aturan_cross_sensor` merupakan usulan pelengkapan untuk mendokumentasikan aturan deteksi. Jika menggunakan JSON, struktur dan format isinya perlu ditetapkan oleh tim.

### 4.2 Aturan Penentuan Status

Status yang digunakan sistem harus konsisten dengan proposal:

- **Normal:** data yang tersedia tidak menunjukkan kondisi yang memenuhi kriteria peringatan sistem.
- **Waspada:** terdapat kondisi yang perlu dipantau lebih lanjut, tetapi kriteria `Indikasi Anomali` belum terpenuhi.
- **Indikasi Anomali:** terdapat pola data yang memenuhi aturan deteksi, termasuk validasi antar-sensor dan persistensi yang ditetapkan.

### 4.3 Validasi Antar-Sensor dan Persistensi

Aturan deteksi harus mempertimbangkan dua hal berikut.

**A. Validasi antar-sensor**

Backend atau modul AI mengevaluasi data suhu, pH, dan kekeruhan secara bersama-sama berdasarkan aturan yang ditentukan dari studi literatur dan rancangan sistem. Satu pembacaan yang menyimpang tidak otomatis membuktikan pencemaran.

**B. Persistensi empat siklus**

Kondisi yang memenuhi aturan perlu bertahan selama empat siklus pengukuran berturut-turut. Dengan interval 15 menit, empat hasil pembacaan yang berjarak 15 menit mencakup waktu dari pembacaan pertama hingga keempat selama 45 menit. Aturan ini menghitung empat pembacaan, bukan empat interval penuh setelah pembacaan pertama.

**Alur penanganan indikasi:**

1. ESP32 mengirimkan hasil pengukuran melalui MQTT.
2. Backend memvalidasi dan menyimpan data sensor.
3. Data dievaluasi berdasarkan aturan antar-sensor.
4. Sistem memeriksa apakah kondisi yang memenuhi kriteria bertahan selama empat siklus pengukuran berturut-turut.
5. Hasil analisis disimpan pada `HASIL_ANALISIS` dan status diperbarui sesuai aturan sistem.
6. Jika statusnya `Indikasi Anomali`, dashboard menampilkan indikasi beserta waktu dan keterangannya.

**Batasan interpretasi:** `Indikasi Anomali` merupakan indikasi awal yang memerlukan validasi lapangan, bukan bukti pasti pencemaran. Ambang batas, aturan kombinasi sensor, dan penanganan data hilang perlu ditetapkan serta diuji sebelum sistem diimplementasikan.

## 5. Identifikasi Kebutuhan API

API menghubungkan backend, database, dashboard, dan modul AI. Komunikasi data sensor dari ESP32 menggunakan MQTT sesuai keputusan tim, sedangkan REST API digunakan dashboard dan klien lain untuk mengakses fungsi backend melalui HTTP.

### 5.1 Daftar Endpoint yang Dibutuhkan

| Method | Endpoint | Fungsi | Akses |
|---|---|---|---|
| `POST` | `/api/auth/login` | Memverifikasi kredensial pengguna dan memberikan token autentikasi | Publik |
| `GET` | `/api/titik` | Mengambil daftar titik pemantauan | Publik |
| `POST` | `/api/titik` | Menambahkan titik pemantauan | Admin |
| `PUT` | `/api/titik/{id}` | Memperbarui informasi titik pemantauan | Admin |
| `GET` | `/api/pembacaan` | Mengambil data sensor berdasarkan titik dan rentang waktu | Publik / Petugas sesuai kebijakan data |
| `GET` | `/api/analisis` | Mengambil hasil klasifikasi dan deteksi anomali | Publik / Petugas sesuai kebijakan data |
| `PUT` | `/api/ambang` | Mengelola ambang batas kualitas air | Admin |

Daftar ini merupakan rancangan endpoint awal berdasarkan kebutuhan SRS. Endpoint tambahan dapat dibuat jika diperlukan pada tahap implementasi.

### 5.2 Penerimaan Data Melalui MQTT

Karena tim memilih MQTT, jalur utama pengiriman data sensor tidak menggunakan `POST /api/ingest`. Alur yang dirancang adalah:

1. **ESP32 + sensor:** mengukur suhu, pH, dan kekeruhan.
2. **MQTT broker:** menerima pesan dari perangkat yang terautentikasi.
3. **Backend subscriber:** membaca pesan dan memvalidasi payload, identitas titik, waktu, serta nilai sensor.
4. **Database dan modul AI:** menyimpan data, mengevaluasi kondisi, dan menyimpan hasil analisis.
5. **REST API dan dashboard:** menyajikan data sensor dan hasil analisis kepada pengguna sesuai hak akses.

### 5.3 Kebutuhan Fungsional API

- Menerima pesan MQTT dari ESP32 dengan format data yang telah ditentukan.
- Memvalidasi data sebelum menyimpan ke database.
- Menolak atau mencatat data yang tidak valid tanpa mengacaukan riwayat pembacaan.
- Menyimpan pembacaan sensor dan menghubungkannya dengan `TITIK_PANTAU`.
- Menyediakan data historis berdasarkan titik pemantauan dan rentang waktu.
- Menyediakan hasil analisis dengan status `Normal`, `Waspada`, atau `Indikasi Anomali`.
- Membatasi fungsi pengelolaan titik dan ambang batas berdasarkan peran pengguna.
- Memberikan respons API dengan kode status dan format data yang konsisten.

### 5.4 Contoh Payload MQTT

Berikut contoh rancangan payload yang dikirim ESP32 ke topik MQTT. Format ini belum merupakan format final implementasi.

```json
{
  "id_titik": 1,
  "waktu_baca": "2026-10-16T08:00:00+07:00",
  "suhu": 28.5,
  "ph": 7.2,
  "kekeruhan": 12.4
}
```

Nama topik MQTT, format identitas perangkat, satuan, dan aturan validasi payload perlu diseragamkan oleh tim sebelum implementasi. Timestamp pada contoh hanya ilustrasi.

## 6. Identifikasi Kebutuhan Autentikasi

Autentikasi memastikan hanya pengguna dan perangkat terdaftar yang dapat mengakses fungsi sistem sesuai kewenangannya.

### 6.1 Autentikasi Pengguna

- Pengguna login menggunakan email dan password.
- Backend memverifikasi password terhadap `password_hash` yang tersimpan.
- Setelah login berhasil, backend memberikan token autentikasi.
- Endpoint yang dilindungi memverifikasi token sebelum menjalankan permintaan.
- Hak akses diperiksa berdasarkan peran `masyarakat`, `petugas`, atau `admin`.
- Akun nonaktif tidak boleh digunakan untuk mengakses fungsi yang memerlukan autentikasi.
- Password disimpan menggunakan algoritma hashing password yang sesuai, bukan enkripsi yang dapat dibalik atau teks biasa.

### 6.2 Autentikasi Perangkat ESP32

ESP32 juga membutuhkan mekanisme autentikasi tersendiri saat terhubung ke broker MQTT.

- Setiap perangkat menggunakan kredensial atau identitas perangkat yang terdaftar.
- Broker membatasi perangkat agar hanya dapat melakukan publish ke topik yang diizinkan.
- Kredensial perangkat tidak boleh disamakan dengan akun pengguna dashboard.
- Koneksi MQTT sebaiknya dilindungi TLS jika didukung broker dan perangkat.
- Backend tetap memvalidasi isi pesan karena autentikasi perangkat saja tidak menjamin bahwa data sensor benar.

### 6.3 Kebutuhan Keamanan

| Kebutuhan | Penerapan yang Direncanakan |
|---|---|
| Kerahasiaan komunikasi | HTTPS untuk REST API dan TLS untuk MQTT jika tersedia |
| Keamanan password | Simpan dalam bentuk hash password |
| Kontrol akses | RBAC untuk endpoint dan fungsi sistem |
| Keamanan perangkat | Autentikasi klien MQTT dan pembatasan akses topik |
| Validasi masukan | Periksa tipe, kelengkapan, rentang nilai, dan identitas titik |
| Pengelolaan akun | Admin dapat mengelola atau menonaktifkan akun sesuai kewenangan |
| Audit aktivitas | Pertimbangkan pencatatan login dan aktivitas administratif |

## 7. Rancangan Entitas Database

Tiga entitas inti proposal dipertahankan dan dilengkapi dengan entitas `USERS`.

### 7.1 `TITIK_PANTAU`

| Kolom | Keterangan |
|---|---|
| `id_titik` (PK) | Identitas titik pemantauan |
| `nama` | Nama titik pemantauan |
| `koordinat` | Lokasi geografis |
| `tanggal_pasang` | Tanggal pemasangan perangkat |
| `status_aktif` (opsional) | Status operasional titik |

### 7.2 `PEMBACAAN_SENSOR`

| Kolom | Keterangan |
|---|---|
| `id_baca` (PK) | Identitas pembacaan |
| `id_titik` (FK) | Referensi ke `TITIK_PANTAU.id_titik` |
| `waktu_baca` | Waktu pengukuran |
| `suhu` | Suhu air dalam °C |
| `ph` | Nilai pH |
| `kekeruhan` | Nilai kekeruhan sesuai kalibrasi |
| `status` (opsional) | Status jika klasifikasi per pembacaan disimpan |

### 7.3 `HASIL_ANALISIS`

| Kolom | Keterangan |
|---|---|
| `id_hasil` (PK) | Identitas hasil analisis |
| `id_titik` (FK) | Referensi ke `TITIK_PANTAU.id_titik` |
| `waktu_analisis` | Waktu analisis dilakukan |
| `jenis` | Jenis analisis |
| `tingkat_risiko` | `Normal`, `Waspada`, atau `Indikasi Anomali` |
| `estimasi_waktu` (opsional) | Digunakan jika fitur prediksi diterapkan |
| `keterangan` | Penjelasan hasil analisis |
| `jumlah_siklus_persistensi` (usulan) | Jumlah siklus yang memenuhi kondisi |
| `aturan_cross_sensor` (usulan) | Catatan atau struktur aturan validasi antar-sensor |

### 7.4 `USERS`

| Kolom | Keterangan |
|---|---|
| `id_user` (PK) | Identitas pengguna |
| `nama` | Nama pengguna |
| `email` (unik) | Email untuk login |
| `password_hash` | Hash password |
| `role` | `masyarakat`, `petugas`, atau `admin` |
| `status_akun` | Status aktif/nonaktif |
| `created_at` | Waktu pembuatan akun |
| `updated_at` | Waktu pembaruan akun |

### 7.5 Relasi Antar-Entitas

- Satu `TITIK_PANTAU` dapat memiliki banyak `PEMBACAAN_SENSOR`.
- Satu `TITIK_PANTAU` dapat memiliki banyak `HASIL_ANALISIS`.
- `PEMBACAAN_SENSOR.id_titik` menjadi foreign key yang mengacu ke `TITIK_PANTAU.id_titik`.
- `HASIL_ANALISIS.id_titik` menjadi foreign key yang mengacu ke `TITIK_PANTAU.id_titik`.
- `USERS` menjadi entitas tambahan untuk autentikasi dan pengelolaan hak akses. Tidak semua hasil analisis harus memiliki relasi langsung ke akun pengguna karena hasil analisis berasal dari data sensor dan proses sistem.

**Catatan:** rancangan ini bersifat konseptual. Tipe data final, indeks, constraint, dan detail fisik database ditetapkan ketika tahap implementasi dimulai.
