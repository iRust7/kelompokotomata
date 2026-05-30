import streamlit as st
from FSM import CoffeeFSM, State  

st.set_page_config(
    page_title="Logic Pharmacy Bot", 
    page_icon="💊",                 
    layout="wide"
)

# CSS Kustom bertema Apotek / Farmasi Hijau Sehat
st.markdown("""
<style>
div[data-testid="stMetric"] {
    background-color: #f0fcf7;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #ccefe0;
}
.stChatMessage { padding: 10px; }
</style>
""", unsafe_allow_html=True)

# Inisialisasi Session State
if 'bot' not in st.session_state:
    st.session_state.bot = CoffeeFSM()  
    st.session_state.bot.step("")       
    st.session_state.history = [{"role": "assistant", "content": st.session_state.bot.get_response()}]

st.title("💊 Logic Digital Pharmacy")

# === DISCLAIMER MEDIS STATIS (PAGAR AMAN) ===
st.warning(
    "⚠️ **Disclaimer Medis Penting:** Bot ini merupakan asisten virtual penyedia informasi **Obat Bebas (Over-The-Counter)** "
    "dan edukasi pertolongan pertama untuk gejala ringan. Asisten ini **TIDAK** mengeluarkan resep obat keras atau menggantikan diagnosis resmi Dokter. "
    "Jika Anda mengalami gejala berat atau darurat medis, segera kunjungi fasilitas kesehatan terdekat."
)
st.markdown("---")

# === LAYOUT UTAMA DENGAN TAB ===
tab1, tab2 = st.tabs(["💬 Konsultasi & Gejala", "📋 Etalase Obat Bebas"])  

# === TAB 1: CHATBOT KONSULTASI ===
with tab1:
    col_chat, col_info = st.columns([2, 1])
    
    with col_info:
        st.subheader("🛒 Struk Belanja Obat")
        if st.session_state.bot.cart:
            total = 0
            for i, item in enumerate(st.session_state.bot.cart):
                subtotal = item['price'] * item['qty']
                total += subtotal
                st.markdown(f"**{i + 1}. {item['emoji']} {item['item'].capitalize()}**")
                st.caption(f"{item['qty']} sediaan x Rp {item['price']:,} = Rp {subtotal:,}")
            st.divider()
            st.metric("Total Pembayaran", f"Rp {total:,}")
            
            if st.button("Kosongkan Keranjang"):
                st.session_state.bot.cart = []
                st.rerun()
        else:
            st.info("Keranjang belanja obat masih kosong.")
            
        st.markdown("---")
        # Visualisasi tanda state emergency menggunakan penanda warna
        if st.session_state.bot.state == State.EMERGENCY:
            st.error(f"Tahap Sistem: 🚨 {st.session_state.bot.state.name}")
        else:
            st.caption(f"Tahap Sistem: 🟢 {st.session_state.bot.state.name}")
        
        if st.button("Mulai Ulang Konsultasi", type="primary"):
            st.session_state.clear()
            st.rerun()

    with col_chat:
        chat_container = st.container(height=500)
        
        # Render Riwayat Chat
        with chat_container:
            for msg in st.session_state.history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    
        # Input User
        if prompt := st.chat_input("Contoh: 'Saya merasa demam', 'perut maag perih', atau 'Beli paracetamol 2'..."):
            st.session_state.history.append({"role": "user", "content": prompt})
            
            # Proses di FSM
            st.session_state.bot.step(prompt)
            bot_reply = st.session_state.bot.get_response()
            
            st.session_state.history.append({"role": "assistant", "content": bot_reply})
            st.rerun()

# === TAB 2: ETALASE OBAT ===
with tab2:
    st.header("Katalog Sediaan Obat Bebas & Suplemen")
    st.markdown("Daftar sediaan obat umum resmi apotek yang aman dibeli tanpa resep dokter.")
    
    menu_items = st.session_state.bot.nlp.menu_data
    cols = st.columns(2)
    
    for index, (key, data) in enumerate(menu_items.items()):
        with cols[index % 2]:
            with st.container(border=True): 
                st.markdown(f"### {data['emoji']} {key.capitalize()}")
                st.markdown(f"*{data['desc']}*")
                st.metric(label="Harga Resmi Sediaan", value=f"Rp {data['price']:,}")