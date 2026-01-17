# LeuitLog 🌾
**Lightweight SIEM & Syslog Recorder**

![LeuitLog Architecture](./docs/WorkFlow%20LeuitLog.png)

LeuitLog adalah solusi **Lightweight SIEM** yang dirancang untuk **ISP, Data Center, dan infrastruktur Linux**.  
Mengadopsi filosofi *Leuit* (lumbung padi), LeuitLog berfungsi sebagai **lumbung digital** untuk menyimpan, menjaga, dan menganalisis log jaringan secara **mandiri & berdaulat**.

---

## 🚧 Status Proyek

> **Under Development (Active Development)**

- ❌ Belum siap untuk production
- 🔄 Arsitektur & fitur masih dapat berubah
- 🧪 Digunakan untuk eksplorasi desain & pengembangan internal

---

## 🧭 Gambaran Sistem (High-Level)

LeuitLog mengumpulkan **syslog dari berbagai sumber** melalui **UDP 514**, lalu memprosesnya menggunakan **Sentinel Engine** untuk membedakan:

- Aktivitas normal
- Serangan brute force (multi sumber)
- Perubahan konfigurasi sah oleh NOC (audit)

---

## 🧱 Arsitektur & Alur Kerja (Berdasarkan Diagram)

### 👤 Source / Actor Layer
- 🟢 **Normal User** — login sukses
- 🔴 **Attacker #1** — `192.168.111.111` (SSH gagal x7)
- 🟠 **Attacker #2** — `192.168.222.222` (MikroTik gagal x12)
- 🔵 **NOC Engineer** — perubahan konfigurasi (authorized)

> Semua aktivitas menghasilkan **Syslog UDP 514**

---

### 🌐 Device & Service Layer
- **Linux Server**
  - SSH Service
- **MikroTik Router**
  - Winbox / API / CLI

---

### 🛡️ LeuitLog — Sentinel Engine

**1) Async Syslog Receiver**
- UDP 514
- Non-blocking, real-time

**2) Log Parser**
- Vendor detection: Linux / MikroTik
- Kategori:
  - `auth`
  - `system`
  - `config`

**3) Security Analyzer**
- Counter brute force **per IP**
- Threshold **hanya berlaku untuk auth failure**
- Config change **tidak memicu alert**

---

### 🗄️ Penyimpanan Log
- `logs`
  - auth / system / config
- `security_incidents`
  - IP attacker
  - Jumlah attempt
  - Target device

---

### 📊 Dashboard Web
Berbasis **Nginx + FastAPI**, menyediakan:
- Log viewer & audit trail
- Alert brute force
- Ringkasan attacker

Contoh:
- `192.168.222.222` (MikroTik) → **12 attempts**
- `192.168.111.111` (Linux) → **7 attempts**

---

## 🔔 Perilaku Sistem (Ringkas)

| Aktivitas | Respon LeuitLog |
|---|---|
| Login sukses | Disimpan sebagai log |
| Gagal login < threshold | Disimpan sebagai log |
| Gagal login > threshold | Incident + Alert |
| Config change (NOC) | Audit log (tanpa alert) |

---

## 🛡️ Filosofi

> **Setiap log adalah padi.**  
> **Setiap serangan adalah hama.**  
> **Setiap data adalah marwah.**

LeuitLog tidak hanya menyimpan log, tetapi **menjaga kedaulatan dan ketahanan data jaringan**.

---

## 📌 Catatan Penting
Repository ini **belum direkomendasikan untuk production**.  
Dokumentasi teknis & panduan instalasi akan menyusul pada rilis stabil.

---

🌾 Terima kasih telah tertarik dengan **LeuitLog**
