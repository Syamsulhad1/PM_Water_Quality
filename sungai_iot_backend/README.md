# Backend Deteksi Anomali Kualitas Air Sungai

## Menjalankan dengan XAMPP (MariaDB)

Proyek ini dikonfigurasi untuk menggunakan database MariaDB bawaan XAMPP, bukan PostgreSQL.

### 1. Siapkan database
1. Buka XAMPP Control Panel, lalu klik **Start** pada **MySQL** (XAMPP sebenarnya menjalankan MariaDB).
2. Buka `http://localhost/phpmyadmin`.
3. Pilih tab **Databases**, buat database bernama `sungai_db` dengan collation `utf8mb4_unicode_ci`.
4. Pada instalasi XAMPP standar, user database biasanya `root` dan password kosong. Jika Anda sudah memberi password pada user `root`, sesuaikan `DATABASE_URL` di langkah berikutnya.

### 2. Siapkan backend di Windows
Buka terminal di folder `sungai_iot_backend`, lalu jalankan:

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Buka file `.env` dan pastikan URL database sesuai pengaturan XAMPP:

```env
DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/sungai_db
MQTT_HOST=127.0.0.1
MQTT_ENABLED=false
```

Jika root memakai password, formatnya `mysql+pymysql://root:PASSWORD@127.0.0.1:3306/sungai_db` (karakter khusus di password perlu URL-encoding).

### 3. Jalankan API
Pastikan **MySQL** di XAMPP masih berstatus Running, lalu dari folder backend jalankan:

```powershell
uvicorn app.main:app --reload
```

Buka dokumentasi API di `http://127.0.0.1:8000/docs` dan pemeriksaan status di `http://127.0.0.1:8000/health`. Tabel database dibuat otomatis saat API pertama kali dijalankan.

### 4. Catatan
- Cara paling mudah untuk pemula adalah menjalankan backend langsung di Windows seperti langkah di atas; tidak perlu `docker compose`.
- `docker-compose.yml` disediakan sebagai opsi jika Docker sudah terpasang. Untuk opsi itu, XAMPP harus aktif dan database `sungai_db` sudah dibuat; container API mengakses host Windows melalui `host.docker.internal`.
- Seed default: admin / `Admin123!Change`, petugas / `Petugas123!Change`. Ganti sebelum digunakan bersama.
- Tes lokal: `pytest -q`.

## Contoh HTTP
```bash
curl -X POST http://localhost:8000/api/v1/readings -H 'Content-Type: application/json' -H 'X-API-Key: demo-node-key-change-me' -d '{"id_titik":1,"suhu":27,"ph":7.2,"kekeruhan":3,"timestamp":"2026-10-18T10:00:00Z"}'
```
Skenario simulator:
```bash
python scripts/simulator.py --mode normal
python scripts/simulator.py --mode persistent --count 8
python scripts/simulator.py --mode sediment --count 8
python scripts/simulator.py --mode brief --count 8
python scripts/simulator.py --mode replay --count 8
python scripts/simulator.py --transport mqtt --mode persistent
```

## Endpoint utama
- Publik: `GET /api/v1/stations`, `/status`, `/readings/latest`, `/readings`, `/analysis`, `/alerts`
- Ingest node: `POST /api/v1/readings` (X-API-Key; body satu object atau batch array)
- Auth: `POST /api/v1/auth/login`, `GET /api/v1/auth/me`
- Petugas/admin: `GET /api/v1/notifications`, `POST /api/v1/reports/anomaly?id_hasil=1`
- Admin: `POST/PUT/DELETE /api/v1/stations`, `GET/PUT /api/v1/config/thresholds/{id_titik}`, `GET/POST/DELETE /api/v1/users`
- WebSocket: `ws://localhost:8000/ws/live`

## Catatan implementasi dan asumsi
- `# ASUMSI:` timestamp naive dianggap UTC; batas suhu wajar -5..70 C; fallback API key global hanya untuk bootstrap demo; cooldown alarm 4 jam.
- Level NTU memakai rentang 2 NTU per level sebagaimana aturan, level 10 terbuka ke atas.
- Label indikasi bukan penetapan pencemaran final; validasi lapangan wajib.
- Alembic migration awal memakai metadata SQLAlchemy untuk membuat seluruh tabel.
- Untuk produksi: matikan anonymous MQTT, aktifkan TLS/auth MQTT, HTTPS reverse proxy, secret manager, rotasi JWT/API key, dan worker async terpisah untuk Telegram.
