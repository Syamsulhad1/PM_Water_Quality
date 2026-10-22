
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.models import Reading, Threshold, Analysis, Notification


def turbidity_level(ntu: float) -> int:
    """Konversi nilai kekeruhan ke level 1–10."""
    return min(10, max(1, int(ntu // 2) + 1))


def classify(db: Session, reading: Reading):
    """
    Mengklasifikasikan pembacaan sensor dan menyimpan hasil analisis
    jika kondisi indikasi anomali terpenuhi.

    Catatan:
    - Waspada bukan bukti pencemaran.
    - Indikasi Anomali memerlukan persistensi dan validasi silang.
    - Pengiriman notifikasi dilakukan terpisah dari transaksi analisis.
    """
    cfg = db.get(Threshold, reading.id_titik)

    if cfg is None:
        cfg = Threshold(id_titik=reading.id_titik)
        db.add(cfg)
        db.flush()

    # Ambil pembacaan sebelumnya, bukan pembacaan yang sedang diproses.
    prev = db.scalars(
        select(Reading)
        .where(
            Reading.id_titik == reading.id_titik,
            Reading.id_baca != reading.id_baca,
        )
        .order_by(desc(Reading.waktu_baca), desc(Reading.id_baca))
        .limit(1)
    ).first()

    # Status awal berdasarkan level kekeruhan.
    if reading.level_kekeruhan <= 3:
        status = "Normal"
    else:
        status = "Waspada"

    # Ambil sejumlah siklus terbaru, termasuk pembacaan sekarang.
    rows = list(
    db.scalars(
        select(Reading)
        .where(Reading.id_titik == reading.id_titik)
        .order_by(desc(Reading.id_baca))
        .limit(max(1, cfg.jumlah_siklus_persistensi))
    ).all()
)
    print(
    "DEBUG ROWS:",
    [(r.id_baca, r.waktu_baca, r.level_kekeruhan) for r in rows]
)

    required_cycles = max(1, cfg.jumlah_siklus_persistensi)

    # Persistensi: seluruh siklus harus memenuhi level anomali.
    persistent = (
        len(rows) >= required_cycles
        and all(
            r.level_kekeruhan >= cfg.batas_level_anomali
            for r in rows
        )
    )

    print("DEBUG required_cycles:", required_cycles)
    print("DEBUG levels:", [r.level_kekeruhan for r in rows])
    print("DEBUG persistent:", persistent)

    # Indikator silang sensor.
    ph_out = reading.ph < cfg.ph_min or reading.ph > cfg.ph_max

    delta_temp = (
        abs(reading.suhu - prev.suhu)
        if prev is not None
        else 0.0
    )
    temp_change = (
        prev is not None
        and delta_temp >= cfg.ambang_perubahan_suhu
    )

    cross = []

    if ph_out:
        cross.append(
            f"pH di luar rentang {cfg.ph_min}-{cfg.ph_max}"
        )

    if temp_change:
        cross.append(
            f"perubahan suhu {delta_temp:.2f} C"
        )

    # Indikasi anomali memerlukan persistensi dan minimal
    # satu indikator silang sensor.
    final = persistent and bool(cross)

    # Simpan status pada pembacaan.
    reading.status = (
        "Indikasi Anomali"
        if final
        else status
    )

    result_id = None

    if final:
        # Cegah pembuatan hasil analisis duplikat untuk pembacaan
        # dan titik pantau yang sama.
        existing_analysis = db.scalars(
            select(Analysis)
            .where(
                Analysis.id_titik == reading.id_titik,
                Analysis.waktu_analisis == reading.waktu_baca,
            )
        ).first()

        if existing_analysis is None:
            result = Analysis(
                id_titik=reading.id_titik,
                waktu_analisis=reading.waktu_baca,
                jenis_analisis="deteksi",
                tingkat_risiko="Tinggi",
                estimasi_waktu=(
                    reading.waktu_baca
                    + timedelta(hours=2)
                ),
                jumlah_siklus_persistensi=len(rows),
                aturan_crosssensor="; ".join(cross),
                keterangan=(
                    "Indikasi berbasis sensor; "
                    "memerlukan validasi lapangan."
                ),
            )
            db.add(result)
            db.flush()
            result_id = result.id_hasil
        else:
            result_id = existing_analysis.id_hasil

        # Buat satu catatan notifikasi per hasil analisis.
        notification = db.scalars(
            select(Notification)
            .where(Notification.id_hasil == result_id)
        ).first()

        if notification is None:
            db.add(
                Notification(
                    id_titik=reading.id_titik,
                    id_hasil=result_id,
                    kanal="web",
                    isi=(
                        "Indikasi Anomali pada titik "
                        f"{reading.id_titik}. "
                        f"pH={reading.ph}, "
                        f"suhu={reading.suhu} C, "
                        f"kekeruhan={reading.kekeruhan} NTU. "
                        "Memerlukan validasi lapangan."
                    ),
                    status_kirim="pending",
                )
            )

    return {
        "status": reading.status,
        "alert": final,
        "cross_sensor": cross,
        "persistensi": len(rows),
        "hasil_analisis_id": result_id,
        "label": {
            "Normal": "Tidak Terdeteksi Anomali",
            "Waspada": "Perlu Pemantauan",
            "Indikasi Anomali": "Memerlukan Validasi Lapangan",
        }[reading.status],
    }
