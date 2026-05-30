from enum import Enum, auto
from engine import NLPEngine

class State(Enum):
    IDLE = auto()       
    DIAGNOSING = auto()   
    AGE_CHECK = auto()    
    ORDERING = auto()     
    CONFIRMATION = auto()
    PAYMENT = auto()
    EMERGENCY = auto()  # State Baru: Kunci sistem jika kondisi gawat darurat

class CoffeeFSM: 
    def __init__(self):
        self.state = State.IDLE
        self.nlp = NLPEngine()
        self.cart = []
        self.response = ""
        self.temp_item = None 

    def get_response(self):
        return self.response

    def calculate_total(self):
        return sum(item['price'] * item['qty'] for item in self.cart)

    def get_menu_text(self):
        teks_menu = "💊 **Daftar Obat & Produk Apotek Logic:**\n\n"
        for key, data in self.nlp.menu_data.items():
            teks_menu += f"- {data['emoji']} **{key.capitalize()}** (Rp {data['price']:,}): *{data['desc']}*\n"
        teks_menu += "\nAnda bisa langsung memesan (contoh: 'Beli paracetamol 2, masker 1')."
        return teks_menu

    def reduce_cart(self, item_to_reduce, qty_to_remove):
        found = False
        message = ""
        for item in self.cart:
            if item['item'] == item_to_reduce:
                item['qty'] -= qty_to_remove
                found = True
                if item['qty'] <= 0:
                    self.cart.remove(item)
                    message = f"❌ **{item_to_reduce.capitalize()}** dihapus dari keranjang."
                else:
                    message = f"📉 **{item_to_reduce.capitalize()}** dikurangi {qty_to_remove}. Sisa: {item['qty']}."
                break
        if not found:
            message = f"Gagal: **[{item_to_reduce}]** tidak ada di keranjang."
        return message

    def step(self, user_input=""):
        user_input = user_input.strip()
        intent = self.nlp.detect_intent(user_input)
        
        if intent == "RESET_SYSTEM":
            self.__init__() 
            self.response = "Sistem apotek di-reset. Halo, apa keluhan kesehatan ringan yang Anda rasakan saat ini?"
            return
            
        # 🚨 GUARDRAIL UTAMA: Deteksi Gejala Red Flag (Lampu Merah Medis)
        flag_terdeteksi = self.nlp.detect_red_flag(user_input)
        if flag_terdeteksi:
            self.state = State.EMERGENCY
            self.cart = [] # Kosongkan keranjang demi keselamatan
            self.response = (
                f"🚨 **PERINGATAN DARURAT MEDIS (RED FLAG):**\n"
                f"Keluhan mengenai *'{flag_terdeteksi}'* berpotensi menandakan kondisi medis kritis serius "
                "yang membutuhkan penanganan dokter segera.\n\n"
                "**Tindakan yang Wajib Anda Lakukan:**\n"
                "1. Segera hubungi layanan darurat medis (119) atau pergi ke IGD Rumah Sakit terdekat.\n"
                "2. Jangan menunda penanganan dengan mencoba mengonsumsi obat bebas sembarangan.\n\n"
                "*Sistem otomatis mengunci fitur pembelian demi keselamatan Anda.*"
            )
            return

        # JIKA DI DALAM STATE EMERGENCY, BLOKIR SEMUA PERINTAH LAIN
        if self.state == State.EMERGENCY:
            self.response = "Sistem terkunci dalam mode peringatan darurat medis. Silakan klik tombol 'Mulai Ulang Konsultasi' di panel samping jika Anda ingin mereset."
            return

        # STATE: IDLE
        if self.state == State.IDLE: 
            self.state = State.DIAGNOSING
            self.response = "Halo! Selamat datang di Apotek Logic. Silakan sebutkan keluhan sakit atau gejala ringan yang Anda rasakan?"
            
        # STATE: DIAGNOSING (Proses Keluhan & Saran Kombinasi)
        elif self.state == State.DIAGNOSING:
            symptom_data = self.nlp.detect_symptom(user_input)
            if symptom_data:
                self.temp_item = symptom_data["item"]
                self.state = State.AGE_CHECK
                
                # Menggabungkan Saran Medis Non-Obat + Informasi Obat Bebas
                self.response = (
                    f"Mengenai gejala yang Anda rasakan, berikut panduan penanganannya:\n\n"
                    f"💡 **Saran Pertolongan Pertama:**\n{symptom_data['saran']}\n\n"
                    f"🟢 **Rekomendasi Sediaan Obat Bebas:**\nKami menyarankan **{symptom_data['item'].capitalize()}** untuk membantu meredakan gejala ringan tersebut.\n\n"
                    f"Sebelum obat ditambahkan ke nota belanja, mohon informasikan berapa **umur pasien** saat ini guna penentuan aturan dosis?"
                )
            else:
                new_orders = self.nlp.parse_orders(user_input)
                if new_orders:
                    self.state = State.ORDERING
                    self.state_ordering_logic(new_orders, user_input, intent)
                else:
                    self.response = "Maaf, kami belum mendeteksi obat bebas yang cocok untuk deskripsi gejala tersebut. Anda bisa mengetik 'menu' untuk memesan sediaan umum secara manual."
                    self.state = State.ORDERING

        # STATE: AGE_CHECK (Proses Umur & Dosis)
        elif self.state == State.AGE_CHECK:
            import re
            age_match = re.search(self.nlp.re_number, user_input)
            if age_match:
                age = int(age_match.group(1))
                if age < 12:
                    dosis = "Aturan Dosis Anak: 3 x sehari 1/2 tablet (atau sesuai takaran sirup)."
                elif age < 60:
                    dosis = "Aturan Dosis Dewasa: 3 x sehari 1 tablet."
                else:
                    dosis = "Aturan Dosis Lansia: 2 x sehari 1 tablet (Gunakan di bawah pengawasan ketat)."
                
                menu_info = self.nlp.menu_data[self.temp_item]
                self.cart.append({
                    "item": self.temp_item,
                    "qty": 1,
                    "price": menu_info['price'],
                    "emoji": menu_info['emoji']
                })
                
                self.response = (
                    f"📋 **Aturan Dosis Berdasarkan Umur ({age} tahun):**\n*{dosis}*\n\n"
                    f"Sediaan **{self.temp_item.capitalize()}** telah dimasukkan ke dalam keranjang.\n\n"
                    f"Apakah ada tambahan obat atau alat kesehatan lain? (Ketik pesanan baru atau ketik **'bayar'** jika sudah cukup)"
                )
                self.temp_item = None
                self.state = State.ORDERING
            else:
                self.response = "Mohon masukkan angka umur Anda dengan benar agar kami dapat menentukan dosisnya (contoh: '20' atau '20 tahun')."

        # STATE: ORDERING
        elif self.state == State.ORDERING:
            new_orders = self.nlp.parse_orders(user_input)
            self.state_ordering_logic(new_orders, user_input, intent)

        # STATE: CONFIRMATION
        elif self.state == State.CONFIRMATION:
            if intent == "YES": 
                self.state = State.PAYMENT
                self.step(user_input) 
            elif intent == "NO":
                self.state = State.ORDERING
                self.response = "Pemesanan ditangguhkan. Silakan periksa keranjang atau tambahkan obat kembali."
            else:
                self.response = "Mohon berikan jawaban konfirmasi dengan jelas berupa 'Ya' atau 'Tidak'."
                
        # STATE: PAYMENT
        elif self.state == State.PAYMENT:
            total = self.calculate_total()
            self.response = f"Terima kasih! Nota pembayaran sebesar Rp {total:,} dikonfirmasi. Sediaan obat bebas Anda sedang disiapkan oleh Apoteker resmi kami. Semoga lekas sembuh! ✨\n\n*Ketik apa pun jika ingin memulai sesi baru.*"
            self.state = State.IDLE

    def state_ordering_logic(self, new_orders, user_input, intent):
        if intent == "ASK_MENU": 
            self.response = self.get_menu_text()
        elif intent == "CANCEL_ALL":
            self.cart = [] 
            self.response = "Keranjang belanja obat bebas telah dikosongkan."
        elif intent == "REDUCE_ITEM":
            items_to_remove = self.nlp.parse_orders(user_input) 
            if items_to_remove:
                results = [self.reduce_cart(itm['item'], itm['qty']) for itm in items_to_remove]
                self.response = "\n".join(results)
            else:
                self.response = "Sediaan obat apa yang ingin dikurangi? Contoh: 'hapus 1 paracetamol'."
        elif intent == "CHECKOUT":
            if not self.cart:
                self.response = "Keranjang belanja Anda masih kosong."
            else:
                self.state = State.CONFIRMATION
                self.response = f"Total nota belanja sediaan farmasi Anda: Rp {self.calculate_total():,}.\nApakah rincian pesanan sudah benar dan setuju untuk melanjutkan ke proses penyiapan? (Ya/Tidak)"
        else:
            if new_orders:
                for order in new_orders: 
                    existing = next((item for item in self.cart if item['item'] == order['item']), None)
                    if existing:
                        existing['qty'] += order['qty']
                    else:
                        menu_info = self.nlp.menu_data[order['item']] 
                        order.update({"price": menu_info['price'], "emoji": menu_info['emoji']}) 
                        self.cart.append(order)
                self.response = "Obat berhasil ditambahkan ke keranjang belanja. Ada tambahan kebutuhan lainnya? (Ketik 'bayar' jika sudah selesai)"
            else:
                self.response = "Maaf, perintah tidak dikenali. Anda bisa memesan langsung seperti 'beli 2 vitamin' atau ketik 'menu' untuk melihat daftar sediaan resmi."