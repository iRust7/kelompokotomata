# HealthBuddy

> Asisten edukasi kesehatan berbasis Finite State Machine. Dibuat untuk Tugas Akhir mata kuliah Teori Bahasa & Otomata.

Anggap saja ini bot kesehatan yang nggak coba jadi dokter beneran. Dia cuma kebagian tugas mendengarkan keluhan ringan, mengenali gejala, lalu kasih saran perawatan mandiri yang sumbernya bisa lo telusuri. Semuanya berjalan di atas FSM klasik tanpa nyentuh API LLM apapun. Sangat akademis, sangat *teori bahasa otomata*.

## Kenapa proyek ini ada

Tugas mata kuliah, jelas. Tapi kalau cuma demo "halo" "halo balik" rasanya kurang seru. Jadi kami coba bikin sesuatu yang fungsional: chatbot kesehatan yang bisa dipakai konsultasi gejala ringan, baca-baca definisi istilah medis, atau cek panduan P3K. Cocok buat orang yang panik tengah malam dan lupa apakah luka bakar harus disiram air dingin atau ditempel pasta gigi (jawabannya: bukan keduanya — air mengalir suhu ruang, 15-20 menit).

Aturannya satu: **dilarang pakai API AI eksternal**. Jadi semua "kepintaran" bot ini pure dari aturan yang kami tulis tangan. Murni Python, FSM, regex, plus dua library NLP ringan untuk stemming Bahasa Indonesia.

## Yang dipakai

- **Python 3.11+**
- **Streamlit** untuk antarmuka
- **Sastrawi** untuk stemming Bahasa Indonesia, biar variasi kata seperti "menyakitkan", "disakiti", "sakit-sakit" tetap dikenali sebagai akar kata yang sama
- **RapidFuzz** untuk toleransi typo, biar "batok" tetap dikenali sebagai "batuk"

Itu saja. Tidak ada model machine learning yang di-load, tidak ada panggilan keluar ke API manapun.

## Cara menjalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

Browser akan otomatis terbuka di `http://localhost:8501`. Kalau tidak, klik link yang muncul di terminal.

Kalau cuma mau lihat FSM-nya jalan tanpa UI:

```bash
python smoke_test.py
```

Skrip ini menyimulasikan delapan skenario percakapan: greeting, triage multi-turn, definisi istilah, P3K, deteksi gejala kritis, toleransi typo, reset, dan FAQ. Bisa jadi referensi waktu menjelaskan transisi state ke dosen.

## Apa saja yang bisa ditanyakan

- **Konsultasi gejala**, misalnya: *"saya batuk berdahak dan demam ringan sudah dua hari"*
- **Definisi istilah medis**, misalnya: *"apa itu kolesterol"*
- **Pertolongan pertama**, misalnya: *"cara mengatasi mimisan"*
- **Tips gaya hidup sehat**, misalnya: *"berapa lama tidur ideal"*
- **Nomor darurat kesehatan**, misalnya: *"nomor ambulans"*

Bot akan otomatis pindah ke mode darurat kalau lo nyebut gejala kritis seperti nyeri dada, kejang, atau stroke. Sistem terkunci sampai lo ketik "mulai ulang". Ini disengaja, biar nggak salah kasih saran di kondisi yang seharusnya langsung ke IGD.

## Struktur proyek

```
healthbuddy/
├── app.py              Halaman Streamlit utama
├── requirements.txt
├── smoke_test.py       Tes percakapan tanpa UI
├── assets/
│   └── styles.css      Custom CSS bertema editorial magazine
├── core/
│   ├── fsm.py          Finite State Machine + dialog manager
│   └── nlp.py          Stemming, scoring gejala, deteksi intent
└── data/
    ├── diseases.py     30 kondisi medis dengan saran lengkap
    ├── red_flags.py    20 gejala kritis
    ├── first_aid.py    10 panduan P3K
    ├── definitions.py  70+ istilah medis
    └── faq.py          18 pertanyaan umum + tips wellness
```

## Diagram FSM (versi sederhana)

```
IDLE -> GREETING -> MAIN_MENU
                       |
       +---------------+---------------+
       |               |               |
    TRIAGE       DEFINITION /     EMERGENCY_INFO
       |         FIRST_AID /
       |         FAQ
    ADVICE  <-->  CLARIFY

Dari state apapun:
  - Deteksi gejala kritis -> EMERGENCY (terkunci)
  - Intent reset           -> IDLE
```

Setiap transisi state dicatat di `bot.transition_log` dan ditampilkan real-time di panel samping antarmuka. Jadi waktu demo, dosen bisa lihat sendiri state berpindah tiap kali lo ketik sesuatu. Lumayan buat nilai tambah.

## Bagaimana NLP-nya bekerja

Singkatnya:

1. Input mentah dari user dibersihkan, lowercase, hilangkan tanda baca.
2. Tiap kata di-stem pakai Sastrawi. Misalnya "menyakitkan" jadi "sakit", "kedinginan" jadi "dingin".
3. Hasil stemming dicocokkan dengan indeks kata kunci yang sudah pre-built dari `data/diseases.py`. Kalau cocok persis, langsung skor. Kalau tidak, RapidFuzz mencoba *partial ratio match* dengan threshold 88%.
4. Skor diakumulasi antar turn. Jadi kalau user awal bilang "perut perih", lalu turn berikutnya "kembung", bot menggabungkan keduanya untuk skor Maag yang lebih tinggi.
5. Begitu skor melewati ambang batas (`CONFIDENCE_THRESHOLD = 4.0`), bot pindah ke state ADVICE dan menyajikan saran perawatan.

Tidak ada training, tidak ada vector embedding, tidak ada model. Cuma indeks string yang dibangun saat aplikasi pertama kali start.

## Sumber knowledge base

Disusun manual dari sumber publik yang bebas dipakai:

- Kemenkes RI: Pedoman Pengendalian Penyakit, Pedoman Gizi Seimbang
- WHO: Fact Sheets (public domain)
- Standar P3K Palang Merah Indonesia
- Pedoman Imunisasi Kemenkes

Kalau ada yang mau menambah penyakit baru, format-nya konsisten dan ada di `data/diseases.py`. Tinggal duplikat satu entry, ganti isinya, restart aplikasi. NLP engine akan otomatis re-index.

## Catatan penting

Ini alat edukasi. Bukan pengganti dokter, perawat, atau apoteker beneran. Untuk diagnosis dan pengobatan, tetap konsultasikan dengan tenaga medis profesional. Untuk situasi mengancam nyawa, hubungi **119**.

Saran perawatan yang bot berikan sudah dirancang konservatif: hanya tindakan rumahan yang aman dilakukan tanpa pengawasan medis (kompres, hidrasi, istirahat, pola makan). Tidak ada rekomendasi obat, tidak ada dosis, tidak ada diagnosis pasti. Semua keluhan yang berpotensi serius akan diarahkan untuk segera ke fasilitas kesehatan.

## Anggota Kelompok

Lihat daftar kontributor di tab GitHub. Pembagian peran:

- Knowledge engineering & FSM design
- NLP engine & stemming
- UI/UX Streamlit
- Dokumentasi & pengujian

## Lisensi

Untuk keperluan akademik. Bebas dipakai dan dikembangkan untuk tugas atau pembelajaran lain.
