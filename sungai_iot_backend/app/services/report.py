from io import BytesIO
from datetime import timedelta
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy import select, desc
from app.models import Analysis, Station, Reading, Notification
def make_report(db,id_hasil):
    a=db.get(Analysis,id_hasil)
    if not a: raise ValueError("Hasil analisis tidak ditemukan")
    s=db.get(Station,a.id_titik)
    rows=list(db.scalars(select(Reading).where(Reading.id_titik==a.id_titik,Reading.waktu_baca>=a.waktu_analisis-timedelta(hours=24)).order_by(Reading.waktu_baca)))
    buf=BytesIO(); doc=SimpleDocTemplate(buf,pagesize=A4); styles=getSampleStyleSheet(); story=[]
    story += [Paragraph("Laporan Indikasi Anomali Kualitas Air Sungai",styles["Title"]),Paragraph(f"Waktu analisis: {a.waktu_analisis}",styles["Normal"]),Paragraph(f"Lokasi: {s.nama} ({s.lat}, {s.lng})",styles["Normal"]),Spacer(1,10)]
    data=[["Waktu","Suhu C","pH","Kekeruhan NTU","Level","Status"]]
    data += [[str(r.waktu_baca),f"{r.suhu:.2f}",f"{r.ph:.2f}",f"{r.kekeruhan:.2f}",str(r.level_kekeruhan),r.status] for r in rows[-30:]]
    table=Table(data,repeatRows=1); table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.lightgrey),("GRID",(0,0),(-1,-1),0.3,colors.grey),("FONTSIZE",(0,0),(-1,-1),7)])); story.append(table)
    if rows:
        img=BytesIO(); fig,ax=plt.subplots(); ax.plot([r.waktu_baca for r in rows],[r.kekeruhan for r in rows],marker="."); ax.set_title("Tren kekeruhan 24 jam"); ax.set_ylabel("NTU"); fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(img,format="png"); plt.close(fig); img.seek(0); story += [Spacer(1,10),Image(img,width=450,height=180)]
    story += [Spacer(1,10),Paragraph(f"Hasil deteksi: Indikasi Anomali — {a.keterangan}",styles["Normal"]),Paragraph(f"Tingkat risiko: {a.tingkat_risiko}",styles["Normal"]),Paragraph(f"Cross-sensor: {a.aturan_crosssensor or 'Tidak ada aturan yang terpenuhi'}",styles["Normal"]),Paragraph(f"Durasi persistensi: {a.jumlah_siklus_persistensi} siklus",styles["Normal"]),Paragraph("Riwayat notifikasi:",styles["Heading2"])]
    for n in db.scalars(select(Notification).where(Notification.id_hasil==id_hasil)):
        story.append(Paragraph(f"{n.waktu_kirim} | {n.kanal} | {n.status_kirim} | {n.isi}",styles["Normal"]))
    story += [Spacer(1,20),Paragraph("Validasi lapangan: __________________________________________________________",styles["Normal"]),Paragraph("Catatan: hasil ini merupakan indikasi berbasis sensor, bukan bukti hukum atau penetapan pencemaran final.",styles["Italic"])]
    doc.build(story); return buf.getvalue()
