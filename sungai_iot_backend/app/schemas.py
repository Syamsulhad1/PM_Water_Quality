from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
class ReadingIn(BaseModel):
    id_titik: int
    suhu: float = Field(ge=-5, le=70)
    ph: float = Field(ge=0, le=14)
    kekeruhan: float = Field(ge=0, le=100000)
    timestamp: datetime
class StationIn(BaseModel):
    nama: str
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    aktif: bool = True
class ThresholdIn(BaseModel):
    batas_level_anomali: int = Field(default=8, ge=1, le=10)
    jumlah_siklus_persistensi: int = Field(default=4, ge=1, le=100)
    kenaikan_level_min: int = Field(default=3, ge=1, le=10)
    ph_min: float = Field(default=6.5, ge=0, le=14)
    ph_max: float = Field(default=8.5, ge=0, le=14)
    ambang_perubahan_suhu: float = Field(default=2.0, ge=0, le=50)
    interval_menit: int = Field(default=15, ge=1, le=1440)
class UserIn(BaseModel):
    username: str
    password: str
    role: str
    telegram_chat_id: str|None = None
    aktif: bool = True
class LoginIn(BaseModel):
    username: str
    password: str
class ReadingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_baca: int
    id_titik: int
    waktu_baca: datetime
    suhu: float
    ph: float
    kekeruhan: float
    level_kekeruhan: int
    status: str
