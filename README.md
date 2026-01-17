<p align="center">
  <img src="./docs/Leuitloglogonobg.png" alt="LeuitLog Logo" width="180"/>
</p>

<h1 align="center">LeuitLog 🌾</h1>

<p align="center">
  <b>Lightweight SIEM & Syslog Recorder</b><br/>
  <i>Menyimpan Marwah • Menjaga Kedaulatan • Menjamin Ketahanan</i><br/>
  <i>Store with dignity • Guard with sovereignty • Build resilience</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-under%20development-orange"/>
  <img src="https://img.shields.io/badge/category-SIEM-blue"/>
  <img src="https://img.shields.io/badge/syslog-UDP%20514-green"/>
  <img src="https://img.shields.io/badge/platform-Linux-lightgrey"/>
  <img src="https://img.shields.io/badge/license-TBD-red"/>
</p>

---

![LeuitLog Architecture](./docs/WorkFlow%20LeuitLog.png)

---

## 🇮🇩 Bahasa Indonesia

### 🚧 Status Proyek
**LeuitLog masih dalam tahap pengembangan aktif.**

- ❌ Belum siap untuk production
- 🔄 Arsitektur dan fitur masih dapat berubah
- 🧪 Digunakan untuk eksplorasi desain dan pengembangan internal

---

### 🌾 Apa itu LeuitLog?
LeuitLog adalah **Lightweight SIEM & Syslog Recorder** yang dirancang untuk **ISP, Data Center, dan infrastruktur Linux**.

Terinspirasi dari konsep *Leuit* (lumbung padi), LeuitLog berfungsi sebagai **lumbung digital**:
- Log diperlakukan sebagai aset berharga
- Serangan dipantau secara aktif
- Kedaulatan data dijaga sepenuhnya (on-premise, tanpa vendor lock-in)

---

### 🧭 Gambaran Sistem
LeuitLog mengumpulkan **syslog melalui UDP port 514** dan memprosesnya menggunakan **Sentinel Engine** untuk membedakan:

- Aktivitas normal  
- Serangan brute force  
- Perubahan konfigurasi sah oleh NOC  

---

### 🔔 Perilaku Sistem
| Aktivitas | Respon |
|----------|--------|
| Login sukses | Disimpan sebagai log |
| Gagal login < threshold | Disimpan sebagai log |
| Gagal login > threshold | Incident + Alert |
| Config change (NOC) | Audit log (tanpa alert) |

---

## 🇬🇧 English Version

### 🚧 Project Status
**LeuitLog is under active development.**

- ❌ Not production-ready
- 🔄 Architecture and features may change
- 🧪 Intended for design exploration and internal development

---

### 🌾 What is LeuitLog?
LeuitLog is a **Lightweight SIEM & Syslog Recorder** designed for **ISP, Data Centers, and Linux infrastructures**.

Inspired by the traditional *Leuit* (granary), LeuitLog acts as a **digital granary**:
- Logs are treated as valuable assets
- Security threats are actively monitored
- Full data sovereignty is maintained (on-premise, no vendor lock-in)

---

### 🧭 System Overview
LeuitLog collects **syslog via UDP port 514** and processes it using a **Sentinel Engine** to distinguish between:

- Normal activity  
- Brute force attacks  
- Authorized configuration changes by NOC engineers  

---

### 🔔 System Behavior
| Activity | Response |
|--------|----------|
| Successful login | Stored as log |
| Failed login < threshold | Stored as log |
| Failed login > threshold | Incident + Alert |
| NOC config change | Audit log (no alert) |

---

## 🛡️ Philosophy / Filosofi

> **Every log is grain.  
> Setiap log adalah padi.**  
>
> **Every attack is a pest.  
> Setiap serangan adalah hama.**  
>
> **Every datum is sovereignty.  
> Setiap data adalah marwah.**

---

## 📌 Important Notice / Catatan Penting
Repository ini **belum direkomendasikan untuk penggunaan produksi**.  
This repository is **not recommended for production use** at this stage.

---

🌾 **LeuitLog — Secure Your Logs, Secure Your Network**
