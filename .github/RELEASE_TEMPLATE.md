## 🌾 LeuitLog v.0.2.1

> Lightweight SIEM & Syslog Recorder  
> Release Type: **Post-Foundation / Engineering Baseline**

---

# 🇮🇩 Bahasa Indonesia

## 📌 Ringkasan Rilis

Rilis ini merupakan **tonggak pengembangan fungsional** dari LeuitLog.

Versi ini melanjutkan **fondasi dan identitas proyek** yang telah dibangun
pada rilis awal, serta mulai menghadirkan **komponen sistem yang dapat dijalankan**
tanpa mengorbankan filosofi dan arah desain awal.

⚠️ **Rilis ini belum direkomendasikan untuk penggunaan produksi.**

---

## 🎯 Tujuan Rilis

- Mewujudkan desain arsitektur menjadi sistem yang berjalan
- Menetapkan struktur core yang stabil untuk pengembangan lanjutan
- Memvalidasi konsep penerimaan syslog dan deteksi berbasis aturan
- Menjadi sarana pembelajaran dan eksplorasi desain SIEM

---

## 📦 Cakupan Rilis

### 🧱 Sistem Inti
- Syslog receiver (UDP port 514)
- Parsing RFC3164 & RFC5424
- Penyimpanan berbasis SQLite
- Detection engine berbasis rule (YAML)

### 🧭 Deteksi & Perilaku
- Deteksi brute force (threshold & time window)
- Deteksi perubahan konfigurasi (audit-oriented)
- Klasifikasi severity: INFO / WARNING / CRITICAL

### 🧰 Operasional
- Web dashboard ringan (ringkasan)
- CLI untuk kebutuhan operator
- Kerangka systemd service

### 📄 Repository & OSS Hygiene
- Filosofi dan identitas proyek tetap dipertahankan
- README diperbarui sesuai kondisi sistem
- Keberlanjutan CHANGELOG dari versi sebelumnya
- ROADMAP dan CONTRIBUTING selaras dengan arah proyek

---

## 🚧 Status Saat Ini

- ⚠️ Belum direkomendasikan untuk produksi
- 🧱 Arsitektur core relatif stabil
- 🔧 Logika deteksi dapat dikonfigurasi dan diperluas
- 🧪 Cocok untuk lab SOC, pembelajaran, dan tooling internal

---

## 🛣️ Rencana Selanjutnya

Pengembangan yang direncanakan:
- Autentikasi dan pemisahan peran (RBAC)
- Korelasi event
- Enrichment alert
- Hardening deployment

---

## ⚠️ Keterbatasan yang Diketahui

- Belum ada mekanisme autentikasi
- Belum mendukung high availability
- Aturan deteksi dibuat sederhana secara sengaja
- Skema dan API masih dapat berubah

---

## 📄 Lisensi

Rilis ini dipublikasikan di bawah **MIT License**.

---

# 🇬🇧 English Version

## 📌 Release Overview

This release represents the **first functional milestone** of LeuitLog.

It builds upon the **foundation and identity established in earlier releases**
and introduces **working, executable components** while preserving the original
philosophy and architectural intent.

⚠️ **This release is not recommended for production use.**

---

## 🎯 Purpose of This Release

- Transform architectural designs into working components
- Establish a stable core structure for future development
- Validate syslog ingestion and rule-based detection concepts
- Serve as a learning and experimentation platform for SIEM design

---

## 📦 Included in This Release

### 🧱 Core System
- Syslog receiver (UDP port 514)
- RFC3164 & RFC5424 parsing
- SQLite-based storage
- Rule-based detection engine (YAML-driven)

### 🧭 Detection & Behavior
- Brute force detection (threshold & time window)
- Configuration change detection (audit-oriented)
- Severity classification: INFO / WARNING / CRITICAL

### 🧰 Operations
- Lightweight web dashboard (summary view)
- CLI for basic operational visibility
- systemd service skeleton

### 📄 Repository & OSS Hygiene
- Preserved project philosophy and identity
- README updated to reflect system capabilities
- Continuous CHANGELOG from previous versions
- ROADMAP and CONTRIBUTING aligned with project direction

---

## 🚧 Current Status

- ⚠️ Not recommended for production use
- 🧱 Core architecture is relatively stable
- 🔧 Detection logic is configurable and extensible
- 🧪 Intended for SOC labs, learning, and internal tooling

---

## 🛣️ What Comes Next

Planned future development:
- Authentication and role-based access control (RBAC)
- Event correlation
- Alert enrichment
- Deployment hardening

---

## ⚠️ Known Limitations

- No authentication or authorization mechanisms
- No high availability support
- Detection rules are intentionally simple
- Schema and APIs may evolve

---

## 📄 License

This release is published under the **MIT License**.

---

🌾 *LeuitLog — storing logs with dignity, guarding systems with intent.*
