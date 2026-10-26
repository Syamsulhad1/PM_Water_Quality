// Konfigurasi URL Backend FastAPI (Menyesuaikan prefiks /api/v1 dari main.py)
const API_BASE_URL = "http://localhost:8000/api/v1";

// 1. Update Jam Real-time di Header
function updateClock() {
    const now = new Date();
    document.getElementById('live-clock').innerHTML = `<i class="fa-regular fa-clock"></i> ${now.toLocaleDateString('id-ID')} ${now.toLocaleTimeString('id-ID')} WIB`;
}
setInterval(updateClock, 1000);
updateClock();

// 2. Inisialisasi Grafik Tren Parameter (Chart.js)
const ctx = document.getElementById('trendChart').getContext('2d');
const trendChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [], // Diisi dinamis dari backend
        datasets: [
            {
                label: 'Kekeruhan (NTU)',
                data: [],
                borderColor: '#e11d48',
                backgroundColor: 'rgba(225, 29, 72, 0.05)',
                tension: 0.3,
                fill: true
            },
            {
                label: 'pH',
                data: [],
                borderColor: '#2563eb',
                tension: 0.3
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
        },
        scales: {
            y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
            x: { grid: { display: false } }
        }
    }
});

// 3. Fungsi Utama untuk Menarik Data dari Backend API FastAPI
async function fetchBackendData() {
    try {
        // A. Ambil data status stasiun dari endpoint /api/v1/status
        const responseStatus = await fetch(`${API_BASE_URL}/status`);
        if (responseStatus.ok) {
            const statusData = await responseStatus.json();
            updateStatusCards(statusData);
        }

        // B. Ambil data pembacaan sensor terbaru untuk grafik dari /api/v1/readings/latest
        const responseReadings = await fetch(`${API_BASE_URL}/readings/latest`);
        if (responseReadings.ok) {
            const readingsData = await responseReadings.json();
            updateChartData(readingsData);
        }

    } catch (error) {
        console.warn("Menunggu server backend FastAPI aktif di port 8000...", error);
    }
}

// Render Kartu Status secara Dinamis berdasarkan respons endpoint /status
function updateStatusCards(statusData) {
    const container = document.getElementById('sensor-cards-container');
    if (!container) return;
    
    if (!statusData || statusData.length === 0) {
        container.innerHTML = `<div class="bg-white p-4 rounded-xl shadow-sm border-l-4 border-gray-300 text-center text-slate-500 text-xs col-span-4">Belum ada data stasiun atau titik pantau.</div>`;
        return;
    }

    container.innerHTML = '';

    statusData.forEach(item => {
        // item struktur dari api.py: { station: nama, id_titik, status, latest: {suhu, ph, kekeruhan, ...} }
        let badgeColor = 'bg-emerald-100 text-emerald-800 border-emerald-500';
        if (item.status === 'Waspada') badgeColor = 'bg-amber-100 text-amber-800 border-amber-500';
        if (item.status === 'Indikasi Anomali' || item.status === 'Tercemar') badgeColor = 'bg-rose-100 text-rose-800 border-rose-500';
        if (item.status === 'Belum ada data') badgeColor = 'bg-gray-100 text-gray-600 border-gray-400';

        const suhu = item.latest ? `${item.latest.suhu}°C` : '-';
        const ph = item.latest ? item.latest.ph : '-';
        const turbidity = item.latest ? `${item.latest.kekeruhan} NTU` : '-';

        const cardHTML = `
            <div class="bg-white p-4 rounded-xl shadow-sm border-l-4 ${badgeColor.split(' ')[2]}">
                <div class="flex justify-between items-start">
                    <h3 class="font-bold text-slate-700 text-sm">${item.station}</h3>
                    <span class="${badgeColor.split(' ').slice(0,2).join(' ')} text-xs px-2 py-0.5 rounded font-semibold">${item.status}</span>
                </div>
                <div class="mt-3 grid grid-cols-3 gap-2 text-center text-xs">
                    <div class="bg-gray-50 p-2 rounded"><span class="block text-gray-400">pH</span><span class="font-bold text-slate-700">${ph}</span></div>
                    <div class="bg-gray-50 p-2 rounded"><span class="block text-gray-400">Suhu</span><span class="font-bold text-slate-700">${suhu}</span></div>
                    <div class="bg-gray-50 p-2 rounded"><span class="block text-gray-400">Turbidity</span><span class="font-bold text-slate-700">${turbidity}</span></div>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', cardHTML);
    });
}

// Perbarui Grafik Tren dengan data dari /readings/latest
function updateChartData(readings) {
    if (!readings || readings.length === 0) return;
    
    // Ambil beberapa data terakhir dan balik urutannya agar kronologis dari kiri ke kanan
    const recentReadings = readings.slice(0, 8).reverse();
    
    const labels = recentReadings.map(r => {
        const date = new Date(r.waktu_baca);
        return date.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
    });
    
    const turbidityValues = recentReadings.map(r => r.kekeruhan);
    const phValues = recentReadings.map(r => r.ph);

    trendChart.data.labels = labels;
    trendChart.data.datasets[0].data = turbidityValues;
    trendChart.data.datasets[1].data = phValues;
    trendChart.update();
}

// Jalankan saat pertama kali halaman dimuat, lalu perbarui secara berkala setiap 15 detik
fetchBackendData();
setInterval(fetchBackendData, 15000);