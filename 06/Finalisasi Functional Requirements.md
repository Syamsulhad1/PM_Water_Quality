# Issue 06 — Finalisasi Functional Requirements
 
**Tujuan:** Menetapkan kebutuhan fungsional sebagai acuan implementasi dan pengujian. Dokumen ini adalah draf untuk ditinjau dan disepakati seluruh anggota; jangan menyatakan sudah disepakati sebelum konfirmasi tim dilakukan.

## 1. Ruang Lingkup

Sistem memantau suhu, pH, dan kekeruhan air melalui node IoT, menampilkan data pada dashboard web, melakukan klasifikasi kondisi dan deteksi indikasi anomali, menerbitkan peringatan dini sesuai aturan validasi dan persistensi, mengelola akses pengguna dan titik pemantauan, serta mencatat log anomali.

Label kondisi:
- **Normal** — Tidak Terdeteksi Anomali.
- **Waspada** — Perlu Pemantauan.
- **Indikasi Anomali** — Memerlukan Validasi Lapangan; bukan bukti pasti pencemaran.

Interval pengukuran direncanakan setiap 15 menit. Peringatan dini baru diterbitkan setelah validasi antarsensor dan persistence check terpenuhi.

## 2. Aktor Sistem

| Aktor | Peran |
|---|---|
| Masyarakat umum | Melihat status kualitas air pada dashboard tanpa login. |
| Petugas/instansi pengelola | Memantau kondisi dan tren kualitas air serta menerima peringatan dini. |
| Admin | Mengelola titik pemantauan, ambang batas notifikasi, pengguna, dan konfigurasi sistem. |
| Node IoT | Mengukur suhu, pH, dan kekeruhan secara berkala serta mengirimkan data ke sistem. |

## 3. Kebutuhan Fungsional

### FR-01 — Akuisisi Data Sensor
**Kebutuhan:** Sistem harus menerima data suhu dari DS18B20 Waterproof, pH dari PH-4502C, dan kekeruhan dari sensor turbidity yang terhubung ke ESP32 secara berkala, dengan interval yang direncanakan setiap 15 menit.

**Kriteria penerimaan**
- Data memuat nilai suhu, pH, kekeruhan, waktu pembacaan, dan identitas titik pemantauan/node.
- Data yang diterima dapat disimpan untuk ditampilkan dan dianalisis.
- Data yang tidak lengkap/tidak valid tidak dianggap sebagai pembacaan sah tanpa penandaan.

**Prioritas:** Tinggi.

### FR-02 — Dashboard Real-time dan Historis
**Kebutuhan:** Sistem harus menyediakan dashboard web yang menampilkan status kualitas air terkini, nilai suhu/pH/kekeruhan, grafik tren setiap parameter, dan riwayat pembacaan berdasarkan rentang waktu.

**Kriteria penerimaan**
- Dashboard menampilkan nilai terbaru ketiga parameter dan label kondisi.
- Grafik tren suhu, pH, dan kekeruhan serta riwayat berdasarkan rentang waktu dapat ditampilkan.
- Data sensor tampil maksimal 30 detik setelah diterima server, sesuai kebutuhan non-fungsional proposal.
- Masyarakat umum dapat melihat status tanpa login.

**Prioritas:** Tinggi.

### FR-03 — Klasifikasi Kualitas Air
**Kebutuhan:** Sistem harus mengklasifikasikan kondisi kualitas air menggunakan model AI berdasarkan data suhu, pH, dan kekeruhan ke kategori **Normal**, **Waspada**, atau **Indikasi Anomali**.

**Kriteria penerimaan**
- Hasil klasifikasi menggunakan salah satu dari tiga label tersebut.
- Hasil dikaitkan dengan data pembacaan dan waktu analisis.
- Indikasi Anomali dijelaskan sebagai indikasi yang memerlukan validasi lapangan.
- Akurasi model tidak diklaim sebelum evaluasi dengan data uji yang sesuai.

**Prioritas:** Tinggi.

### FR-04 — Deteksi Anomali
**Kebutuhan:** Sistem harus mendeteksi indikasi anomali kualitas air berdasarkan perubahan atau pola data suhu, pH, dan kekeruhan yang menyimpang dari kondisi yang diharapkan.

**Kriteria penerimaan**
- Sistem menganalisis data sensor untuk mengenali kondisi berpotensi menyimpang.
- Hasil deteksi mencatat waktu kejadian, titik pemantauan, dan data sensor terkait yang tersedia.
- Deteksi tidak otomatis dianggap bukti pencemaran dan diproses lebih lanjut melalui FR-08 dan FR-09 sebelum peringatan dini.

**Prioritas:** Tinggi.

### FR-05 — Peringatan Dini
**Kebutuhan:** Sistem harus menghasilkan peringatan dini dan ringkasan kondisi ketika indikasi anomali memenuhi aturan validasi antarsensor dan pemeriksaan persistensi.

**Kriteria penerimaan**
- Peringatan hanya diterbitkan setelah FR-08 dan FR-09 terpenuhi.
- Peringatan memuat informasi yang tersedia tentang waktu, titik pemantauan, status, dan parameter terkait.
- Peringatan dapat dilihat petugas/instansi pengelola melalui sistem.
- Satu pembacaan yang belum memenuhi aturan tidak memicu peringatan final.

**Prioritas:** Tinggi.

### FR-06 — Authentication dan Role
**Kebutuhan:** Sistem harus menyediakan autentikasi dan pembatasan hak akses berdasarkan peran. Masyarakat umum dapat melihat dashboard tanpa login; petugas memantau dan menerima peringatan; admin mengelola konfigurasi.

**Kriteria penerimaan**
- Pengguna berakun dapat login.
- Hak akses dibedakan berdasarkan peran.
- Admin dapat mengelola pengguna dan konfigurasi sistem.
- Petugas dapat mengakses fungsi pemantauan/peringatan sesuai kewenangannya.
- Masyarakat umum dapat mengakses dashboard publik tanpa login.
- Pengguna tidak dapat menjalankan fungsi yang tidak diizinkan untuk perannya.

**Prioritas:** Sedang.

### FR-07 — Monitoring Point dan Threshold
**Kebutuhan:** Sistem harus menyediakan fungsi bagi admin untuk mengelola titik pemantauan serta ambang batas notifikasi.

**Kriteria penerimaan**
- Admin dapat menambah, melihat, memperbarui, dan mengelola informasi titik pemantauan sesuai rancangan.
- Pembacaan dan hasil analisis terhubung ke titik pemantauan yang benar.
- Admin dapat mengatur dan memperbarui ambang notifikasi.
- Perubahan ambang batas hanya dilakukan oleh peran berwenang.
- Angka ambang batas harus mengikuti acuan teknis yang disepakati tim; dokumen ini tidak menetapkan angka baru yang tidak dinyatakan dalam proposal.

**Prioritas:** Sedang.

### FR-08 — Cross-sensor Validation
**Kebutuhan:** Sistem harus membandingkan pola atau perubahan pada data kekeruhan, pH, dan suhu sebelum menetapkan indikasi anomali yang dapat memicu peringatan dini.

**Kriteria penerimaan**
- Validasi mempertimbangkan data ketiga parameter sensor yang tersedia.
- Hasil validasi mencatat parameter yang mendukung/tidak mendukung indikasi sejauh dapat ditentukan aturan sistem.
- Jika bukti lintas sensor belum memenuhi aturan, peringatan final tidak diterbitkan dan kondisi dapat dipantau lebih lanjut.
- Aturan validasi terdokumentasi dan dapat diuji dengan skenario data.

**Prioritas:** Tinggi.

### FR-09 — Persistence Check
**Kebutuhan:** Sistem harus memeriksa apakah indikasi anomali bertahan minimal empat siklus pengukuran berturut-turut, dengan interval 15 menit, sebelum peringatan dini diterbitkan.

**Kriteria penerimaan**
- Persistensi dihitung berdasarkan siklus pembacaan berturut-turut.
- Empat siklus × 15 menit setara sekitar satu jam.
- Peringatan final tidak diterbitkan sebelum syarat persistensi terpenuhi.
- Perilaku ketika indikasi terputus, data hilang, atau pembacaan tidak valid harus ditentukan dan didokumentasikan secara konsisten oleh tim.

**Prioritas:** Tinggi.

### FR-10 — Laporan Log Anomali
**Kebutuhan:** Sistem harus menghasilkan log anomali digital yang berisi data dan konteks kejadian untuk membantu peninjauan dan validasi lapangan.

**Kriteria penerimaan**
- Log menyimpan informasi yang tersedia, sekurang-kurangnya waktu kejadian, titik pemantauan, nilai suhu/pH/kekeruhan terkait, status/jenis indikasi, dan hasil validasi/persistensi yang relevan.
- Pengguna berwenang dapat melihat log anomali.
- Log dapat ditelusuri untuk pemeriksaan kejadian sebelumnya.
- Antarmuka menyediakan tombol **Generate Laporan Anomali** sebagaimana disebutkan dalam proposal. Format keluaran laporan perlu disepakati tim.

**Prioritas:** Sedang.

## 4. Hubungan Antar-Requirement

| Requirement | Hubungan |
|---|---|
| FR-01 | Menyediakan data untuk FR-02, FR-03, FR-04, FR-08, FR-09, dan FR-10. |
| FR-02 | Menampilkan data sensor, hasil klasifikasi, dan informasi pemantauan yang relevan. |
| FR-03 | Menggunakan data dari FR-01. |
| FR-04 | Menghasilkan indikasi yang ditinjau melalui FR-08 dan FR-09. |
| FR-05 | Dijalankan setelah FR-08 dan FR-09 terpenuhi. |
| FR-06 | Membatasi akses berdasarkan peran. |
| FR-07 | Mengelola titik pemantauan dan ambang notifikasi. |
| FR-08 | Memvalidasi indikasi berdasarkan pola antarsensor. |
| FR-09 | Memastikan indikasi bertahan empat siklus berturut-turut. |
| FR-10 | Mendokumentasikan kejadian untuk pemeriksaan selanjutnya. |
