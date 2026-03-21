# Panduan AI_OS

Panduan ini menjelaskan cara install, menjalankan, dan mengecek aplikasi `AI_OS` dari awal.

## 1) Prasyarat

- OS: Windows (tested)
- Python: 3.10+
- Ollama: sudah terpasang dan berjalan
- Koneksi internet (untuk install dependency dan model Ollama)

## 2) Struktur Singkat

- `backend/` -> API FastAPI
- `frontend/index.html` -> UI bawaan (served oleh backend)
- `ai_versions/` -> logika AI per versi (`v1`, `v2`, `v3`)
- `memory/` -> vector store memory
- `config/` -> konfigurasi version/model aktif
- `logs/ai_os.log` -> log aplikasi

## 3) Install Dependency

Jalankan dari root project:

```powershell
python -m pip install -r requirements.txt
```

## 4) Konfigurasi Environment

Jika belum ada `.env`, salin dari `.env.example`:

```powershell
copy .env.example .env
```

Contoh isi penting:

- `OLLAMA_URL=http://localhost:11434`
- `API_HOST=0.0.0.0`
- `API_PORT=8000`

## 5) Siapkan Model Ollama

Cek model yang sudah terpasang:

```powershell
ollama list
```

Jika belum ada model, pull minimal satu model (contoh ringan):

```powershell
ollama pull gemma3:1b
```

Catatan:
- UI sekarang membaca model terpasang langsung dari Ollama.
- Pilih model yang memang ada di mesin agar chat berfungsi.

## 6) Menjalankan Aplikasi

Jalankan backend dari root project:

```powershell
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Setelah jalan:

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- UI: `http://127.0.0.1:8000/ui`

## 7) Alur Pakai UI

1. Buka `http://127.0.0.1:8000/ui`
2. Cek status global (backend + Ollama)
3. Di panel **Konfigurasi**, pilih:
   - Version (`v1/v2/v3`)
   - Model (yang tersedia dari Ollama)
4. Klik simpan model/version
5. Uji chat di panel **Chat**
6. Gunakan panel **Memory** untuk store/search/count/clear

## 8) Endpoint Penting

- `GET /` -> health check
- `GET /version`, `POST /version`
- `GET /model`, `POST /model`
- `POST /chat`
- `GET /stats`
- `GET /ollama/status`
- `GET /memory/count`
- `POST /memory/store`
- `GET /memory/search`
- `DELETE /memory/clear`
- `GET /logs/tail`

## 9) Testing Cepat (Smoke Test)

### Cek health

```powershell
python -c "import requests; print(requests.get('http://127.0.0.1:8000/').text)"
```

### Cek model + version aktif

```powershell
python -c "import requests; print(requests.get('http://127.0.0.1:8000/model').text); print(requests.get('http://127.0.0.1:8000/version').text)"
```

### Uji chat

```powershell
python -c "import requests; r=requests.post('http://127.0.0.1:8000/chat', json={'message':'Halo'}); print(r.text)"
```

## 10) Troubleshooting

### A) Chat gagal / error model not found

Penyebab umum: model aktif tidak ada di Ollama lokal.

Solusi:

1. Cek `ollama list`
2. Pull model yang dibutuhkan (mis. `ollama pull gemma3:1b`)
3. Pilih model itu di UI panel konfigurasi

### B) Endpoint memory pertama kali lambat

Penyebab: download model embedding Chroma pertama kali.  
Ini normal; request berikutnya biasanya lebih cepat.

### C) UI tidak kebuka

1. Pastikan backend aktif di port 8000
2. Buka `http://127.0.0.1:8000/ui`
3. Jika tetap gagal, cek log di `logs/ai_os.log`

### D) Port 8000 sudah dipakai

Jalankan di port lain:

```powershell
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8010
```

Lalu akses:

- `http://127.0.0.1:8010/ui`

## 11) Log dan Monitoring

- File log utama: `logs/ai_os.log`
- Dari API:
  - `GET /logs/tail?n=50`

## 12) Saran Operasional

- Untuk stabilitas awal, gunakan:
  - Version: `v1`
  - Model: yang paling ringan dan tersedia (mis. `gemma3:1b`)
- Naik ke `v2/v3` setelah chat dasar stabil
- Hindari gonta-ganti model besar jika RAM terbatas

---

Jika dibutuhkan, tambahkan bagian deploy (Docker/service) di versi berikutnya.
