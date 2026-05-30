import re

class NLPEngine():
    def __init__(self):
        # Database Obat & Alat Kesehatan (Hanya Obat Bebas Berlogo Hijau/Biru)
        self.menu_data = {
            "paracetamol": {"price": 10000, "emoji": "💊", "desc": "Obat bebas pereda demam dan sakit kepala ringan"},
            "antasida": {"price": 8000, "emoji": "🧪", "desc": "Obat bebas untuk maag dan menetralkan asam lambung"},
            "obh": {"price": 15000, "emoji": "🧴", "desc": "Sirup obat batuk hitam bebas untuk mengencerkan dahak"},
            "ctm": {"price": 5000, "emoji": "💊", "desc": "Obat bebas terbatas untuk alergi dan gatal (menyebabkan kantuk)"},
            "vitamin": {"price": 25000, "emoji": "🍊", "desc": "Suplemen Vitamin C untuk menjaga imun tubuh"},
            "masker": {"price": 15000, "emoji": "😷", "desc": "1 kotak masker medis isi 50 lembar"}
        }
        
        # Mapping keluhan ringan ke obat tertentu
        self.symptom_map = {
            r"\b(pusing|demam|panas|sakit kepala|nyeri)\b": {
                "item": "paracetamol",
                "saran": "Istirahat yang cukup di ruangan sejuk, kompres dahi dengan air hangat, dan penuhi kebutuhan cairan tubuh."
            },
            r"\b(maag|lambung|mual|perih|perut)\b": {
                "item": "antasida",
                "saran": "Cobalah untuk makan tepat waktu dengan porsi kecil tetapi sering. Hindari makanan pedas, terlalu asam, dan kopi untuk sementara."
            },
            r"\b(batuk|pilek|flu|dahak|tenggorokan)\b": {
                "item": "obh",
                "saran": "Perbanyak minum air putih hangat, hindari gorengan, makanan manis/berminyak, serta es."
            },
            r"\b(gatal|alergi|bersin)\b": {
                "item": "ctm",
                "saran": "Hindari pemicu alergi (seperti debu atau makanan tertentu). Gunakan pakaian longgar dan jangan menggaruk area yang gatal."
            }
        }

        # Daftar kata kunci tanda bahaya medis (Wajib ke Dokter/IGD)
        self.red_flags = r"\b(nyeri dada|sesak napas|kejang|perut kanan bawah|muntah darah|stroke|pingsan|pelo)\b"

        self.re_number = r"\b(\d+)\b"
        menu_keys = "|".join(self.menu_data.keys())
        self.re_menu = rf"\b({menu_keys})\b"
        self.re_split = r"[,.]|\bdan\b|\b&\b"
        
        self.re_cancel_all = r"\b(batalkan semua|hapus semua|reset|kosongkan)\b"
        self.re_reduce = r"\b(batalkan|kurangi|tidak jadi|hapus|cancel)\b"

    def detect_red_flag(self, text):
        """Mendeteksi apakah gejala termasuk kondisi darurat"""
        match = re.search(self.red_flags, text.lower())
        if match:
            return match.group(1)
        return None

    def detect_symptom(self, text):
        """Mendeteksi rekomendasi obat dan saran pertolongan pertama berdasarkan kata kunci keluhan"""
        text = text.lower()
        for pattern, data in self.symptom_map.items():
            if re.search(pattern, text):
                return data
        return None

    def _parse_single_segment(self, text):
        text = text.lower().strip()
        item_match = re.search(self.re_menu, text)
        if not item_match:
            return None
        item_key = item_match.group(1)
        
        qty_match = re.search(self.re_number, text)
        qty = int(qty_match.group(1)) if qty_match else 1
        return {
            "item": item_key,
            "qty": qty,
            "price": self.menu_data[item_key]['price'],
            "emoji": self.menu_data[item_key]['emoji']
        }
    
    def parse_orders(self, full_text):
        segments = re.split(self.re_split, full_text)
        found_orders = []
        for segment in segments:
            if segment.strip():
                order = self._parse_single_segment(segment)
                if order:
                    found_orders.append(order)
        return found_orders
    
    def detect_intent(self, text):
        text = text.lower()
        if re.search(r"\b(reset|ulang)\b", text): return "RESET_SYSTEM"
        if re.search(self.re_cancel_all, text): return "CANCEL_ALL"
        if re.search(self.re_reduce, text): return "REDUCE_ITEM"
        if re.search(r"\b(menu|daftar|obat apa saja|list)\b", text): return "ASK_MENU"
        if re.search(r"\b(selesai|bayar|checkout|cukup)\b", text): return "CHECKOUT"
        if re.search(r"\b(ya|yes|oke|betul|siap|baik)\b", text): return "YES"
        if re.search(r"\b(tidak|enggak|batal|no)\b", text): return "NO"
        return "UNKNOWN"