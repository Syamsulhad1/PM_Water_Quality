from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base
def now_utc(): return datetime.now(timezone.utc)
class Station(Base):
    __tablename__="titik_pantau"
    id_titik: Mapped[int]=mapped_column(primary_key=True)
    nama: Mapped[str]=mapped_column(String(120), unique=True)
    lat: Mapped[float]=mapped_column(Float)
    lng: Mapped[float]=mapped_column(Float)
    tanggal_pasang: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now_utc)
    aktif: Mapped[bool]=mapped_column(Boolean, default=True)
    readings=relationship("Reading", back_populates="station", cascade="all, delete-orphan")
class Reading(Base):
    __tablename__="pembacaan_sensor"
    __table_args__=(UniqueConstraint("id_titik","waktu_baca",name="uq_reading_station_timestamp"), CheckConstraint("ph >= 0 AND ph <= 14","ck_ph_range"), CheckConstraint("kekeruhan >= 0","ck_turbidity_nonnegative"), CheckConstraint("suhu >= -5 AND suhu <= 70","ck_temp_range"), Index("ix_reading_station_time","id_titik","waktu_baca"))
    id_baca: Mapped[int]=mapped_column(primary_key=True)
    id_titik: Mapped[int]=mapped_column(ForeignKey("titik_pantau.id_titik", ondelete="CASCADE"), index=True)
    waktu_baca: Mapped[datetime]=mapped_column(DateTime(timezone=True), index=True)
    suhu: Mapped[float]=mapped_column(Float)
    ph: Mapped[float]=mapped_column(Float)
    kekeruhan: Mapped[float]=mapped_column(Float)
    level_kekeruhan: Mapped[int]=mapped_column(Integer)
    status: Mapped[str]=mapped_column(String(40), default="Normal")
    station=relationship("Station", back_populates="readings")
class Analysis(Base):
    __tablename__="hasil_analisis"
    id_hasil: Mapped[int]=mapped_column(primary_key=True)
    id_titik: Mapped[int]=mapped_column(ForeignKey("titik_pantau.id_titik", ondelete="CASCADE"), index=True)
    waktu_analisis: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now_utc)
    jenis_analisis: Mapped[str]=mapped_column(String(40), default="deteksi")
    tingkat_risiko: Mapped[str]=mapped_column(String(40))
    estimasi_waktu: Mapped[datetime|None]=mapped_column(DateTime(timezone=True), nullable=True)
    jumlah_siklus_persistensi: Mapped[int]=mapped_column(Integer, default=0)
    aturan_crosssensor: Mapped[str]=mapped_column(Text, default="")
    keterangan: Mapped[str]=mapped_column(Text, default="")
class User(Base):
    __tablename__="pengguna"
    id: Mapped[int]=mapped_column(primary_key=True)
    username: Mapped[str]=mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str]=mapped_column(String(255))
    role: Mapped[str]=mapped_column(String(20))
    telegram_chat_id: Mapped[str|None]=mapped_column(String(80), nullable=True)
    aktif: Mapped[bool]=mapped_column(Boolean, default=True)
    __table_args__=(CheckConstraint("role IN ('admin','petugas')","ck_user_role"),)
class Threshold(Base):
    __tablename__="konfigurasi_ambang"
    id_titik: Mapped[int]=mapped_column(ForeignKey("titik_pantau.id_titik", ondelete="CASCADE"), primary_key=True)
    batas_level_anomali: Mapped[int]=mapped_column(Integer, default=8)
    jumlah_siklus_persistensi: Mapped[int]=mapped_column(Integer, default=4)
    kenaikan_level_min: Mapped[int]=mapped_column(Integer, default=3)
    ph_min: Mapped[float]=mapped_column(Float, default=6.5)
    ph_max: Mapped[float]=mapped_column(Float, default=8.5)
    ambang_perubahan_suhu: Mapped[float]=mapped_column(Float, default=2.0)
    interval_menit: Mapped[int]=mapped_column(Integer, default=15)
class Notification(Base):
    __tablename__="notifikasi_log"
    id: Mapped[int]=mapped_column(primary_key=True)
    id_titik: Mapped[int]=mapped_column(ForeignKey("titik_pantau.id_titik", ondelete="CASCADE"), index=True)
    id_hasil: Mapped[int|None]=mapped_column(ForeignKey("hasil_analisis.id_hasil", ondelete="SET NULL"), nullable=True)
    waktu_kirim: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now_utc)
    kanal: Mapped[str]=mapped_column(String(30), default="telegram")
    isi: Mapped[str]=mapped_column(Text)
    status_kirim: Mapped[str]=mapped_column(String(30), default="pending")
class Device(Base):
    __tablename__="perangkat"
    id_titik: Mapped[int]=mapped_column(ForeignKey("titik_pantau.id_titik", ondelete="CASCADE"), primary_key=True)
    api_key_hash: Mapped[str]=mapped_column(String(64))
    last_seen: Mapped[datetime|None]=mapped_column(DateTime(timezone=True), nullable=True)
