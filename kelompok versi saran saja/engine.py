import re

class NLPEngine():
    def __init__(self):
        # Database Gejala Ringan & Saran Pertolongan Pertama (Tanpa Obat)
        self.symptom_map = {
            r"\b(pusing|demam|panas|sakit kepala|nyeri)\b": {
                "kondisi": "Demam / Sakit Kepala Ringan",
                "saran": "1. Istirahat yang cukup di ruangan yang sejuk dan tenang.\n2. Kompres dahi menggunakan kain yang dibasahi air hangat.\n3. Penuhi kebutuhan cairan dengan minum air putih minimal 8 gelas sehari untuk mencegah dehidrasi."
            },
            r"\b(maag|lambung|mual|perih|perut)\b": {
                "kondisi": "Gangguan Lambung / Maag Ringan",
                "saran": "1. Cobalah untuk makan tepat waktu dengan porsi kecil tetapi lebih sering (small frequent meals).\n2. Hindari konsumsi makanan yang terlalu pedas, asam, bersantan, serta minuman berkafein atau soda untuk sementara waktu.\n3. Usahakan tidak langsung berbaring minimal 2 jam setelah makan."
            },
            r"\b(batuk|pilek|flu|dahak|tenggorokan)\b": {
                "kondisi": "Batuk / Flu Ringan",
                "saran": "1. Perbanyak minum air putih hangat untuk membantu mengencerkan dahak dan melegakan tenggorokan.\n2. Hindari konsumsi makanan berminyak (gorengan), makanan terlalu manis, dan minuman dingin/es.\n3. Jagalah kelembapan udara ruangan dan istirahat yang cukup."
            },
            r"\b(gatal|alergi|bersin)\b": {
                "kondisi": "Alergi / Gatal Ringan",
                "saran": "1. Identifikasi dan hindari pemicu alergi Anda (seperti debu, bulu hewan, atau makanan tertentu).\n2. Gunakan pakaian yang longgar, berbahan katun lembut, dan tidak panas.\n3. Hindari menggaruk area yang gatal secara berlebihan agar tidak memicu infeksi sekunder pada kulit."
            }
        }

        # Daftar kata kunci tanda bahaya medis (Wajib Dirujuk ke Dokter/IGD)
        self.red_flags = r"\b(nyeri dada|sesak napas|kejang|perut kanan bawah|muntah darah|stroke|pingsan|pelo)\b"
        self.re_intent_reset = r"\b(reset|ulang|mulai kembali|bersihkan)\b"

    def detect_red_flag(self, text):
        """Mendeteksi apakah gejala termasuk kondisi kritis/darurat"""
        match = re.search(self.red_flags, text.lower())
        if match:
            return match.group(1)
        return None

    def detect_symptom(self, text):
        """Mendeteksi keluhan ringan untuk diberikan saran perawatan"""
        text = text.lower()
        for pattern, data in self.symptom_map.items():
            if re.search(pattern, text):
                return data
        return None
    
    def detect_intent(self, text):
        text = text.lower()
        if re.search(self.re_intent_reset, text): 
            return "RESET_SYSTEM"
        return "UNKNOWN"