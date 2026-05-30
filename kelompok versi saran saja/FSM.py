from enum import Enum, auto
from engine import NLPEngine

class State(Enum):
    IDLE = auto()       
    MONITORING = auto()   # State aktif memproses keluhan & memberikan saran
    EMERGENCY = auto()    # State kunci jika mendeteksi kondisi gawat darurat

class CoffeeFSM: # Nama dipertahankan agar app.py tidak eror saat import awal
    def __init__(self):
        self.state = State.IDLE
        self.nlp = NLPEngine()
        self.response = ""
        # Variabel cart dan nlp.menu_data dikosongkan agar app.py tidak crash saat dibaca
        self.cart = [] 

    def get_response(self):
        return self.response

    def step(self, user_input=""):
        user_input = user_input.strip()
        intent = self.nlp.detect_intent(user_input)
        
        # Fitur Reset Sistem
        if intent == "RESET_SYSTEM":
            self.__init__() 
            self.response = "Sistem edukasi berhasil di-reset. Halo, apa keluhan atau gejala kesehatan ringan yang sedang Anda rasakan?"
            return
            
        # 🚨 GUARDRAIL DETEKSI RED FLAG (Kondisi Gawat Darurat)
        flag_terdeteksi = self.nlp.detect_red_flag(user_input)
        if flag_terdeteksi:
            self.state = State.EMERGENCY
            self.response = (
                f"🚨 **PERINGATAN DARURAT MEDIS (RED FLAG):**\n"
                f"Gejala *'{flag_terdeteksi}'* yang Anda sebutkan **BUKAN** merupakan gejala ringan dan berpotensi menandakan kondisi medis kritis.\n\n"
                "**Tindakan yang Wajib Anda Lakukan Sekarang:**\n"
                "1. Segera hubungi layanan ambulans/darurat medis (119) atau langsung pergi ke IGD Rumah Sakit terdekat.\n"
                "2. Jangan menunda penanganan atau mencoba mengobati sendiri di rumah.\n\n"
                "*Sistem otomatis mengunci percakapan demi keamanan medis Anda.*"
            )
            return

        # Jika sistem dalam keadaan terkunci emergency
        if self.state == State.EMERGENCY:
            self.response = "Sistem saat ini terkunci pada mode Peringatan Darurat Medis. Harap utamakan keselamatan Anda dengan mencari bantuan medis profesional. Tekan 'Mulai Ulang Konsultasi' untuk membuka kembali."
            return

        # STATE: IDLE (Awal Percakapan)
        if self.state == State.IDLE: 
            self.state = State.MONITORING
            self.response = "Halo! Saya adalah asisten edukasi kesehatan virtual Anda. Silakan ceritakan keluhan kesehatan ringan yang Anda rasakan saat ini?"
            
        # STATE: MONITORING (Mendeteksi Gejala dan Memberikan Saran Pertolongan)
        elif self.state == State.MONITORING:
            symptom_data = self.nlp.detect_symptom(user_input)
            
            if symptom_data:
                self.response = (
                    f"Saya memahami ketidaknyamanan Anda mengenai gejala **{symptom_data['kondisi']}**.\n\n"
                    f"💡 **Saran Pertolongan Pertama & Perawatan Mandiri:**\n{symptom_data['saran']}\n\n"
                    f"---\n"
                    f"⚠️ *Catatan: Saran di atas hanya untuk tindakan awal pereda gejala ringan. Jika dalam 2-3 hari keluhan tidak kunjung membaik, harap segera memeriksakan diri ke Dokter untuk diagnosis resmi.*"
                )
            else:
                self.response = (
                    "Saya memahami Anda sedang merasa kurang sehat. Namun, kata kunci keluhan tersebut belum teridentifikasi di sistem edukasi ringan saya.\n\n"
                    "Cobalah masukkan kata kunci gejala ringan yang umum seperti: *'saya sedang demam'*, *'perut terasa perih maag'*, *'batuk berdahak'*, atau *'sakit kepala pusing'*."
                )