import streamlit as st
from FSM import CoffeeFSM, State  

st.set_page_config(
    page_title="Health Info Bot", 
    page_icon="🩺",                 
    layout="wide"
)

# Inisialisasi Session State
if 'bot' not in st.session_state:
    st.session_state.bot = CoffeeFSM()  
    st.session_state.bot.step("")       
    st.session_state.history = [{"role": "assistant", "content": st.session_state.bot.get_response()}]

# Judul Aplikasi Bertema Edukasi Kesehatan
st.title("🩺 HealthBuddy: Asisten Informasi & Gejala Ringan")

# === DISCLAIMER MEDIS STATIS PERMANEN ===
st.warning(
    "⚠️ **Disclaimer Medis Resmi:** Chatbot ini bekerja **MURNI** sebagai media edukasi informasi pertolongan pertama "
    "gejala ringan dan **TIDAK** menyediakan rekomendasi obat ataupun diagnosis medis. "
    "Sistem ini dilengkapi pemantau tanda bahaya klinis (Red Flags). Jika Anda mengalami kondisi darurat, segera hubungi fasilitas medis."
)
st.markdown("---")

# === LAYOUT CHAT DENGAN PANEL INFO SAMPING ===
col_chat, col_info = st.columns([3, 1])

with col_info:
    st.subheader("📌 Panduan Penggunaan")
    st.info(
        "Anda dapat berkonsultasi mengenai keluhan ringan seperti:\n"
        "- 🤒 Demam / Pusing / Sakit Kepala\n"
        "- 🤢 Perut Perih / Gejala Maag\n"
        "- 😷 Batuk / Pilek / Flu\n"
        "- 🍁 Alergi Ringan / Gatal-gatal"
    )
    st.divider()
    
    # Status Keamanan FSM
    if st.session_state.bot.state == State.EMERGENCY:
        st.error(f"Status Bot: 🚨 EMERGENCY LOCK")
    else:
        st.success(f"Status Bot: 🟢 ACTIVE MONITORING")
        
    if st.button("Mulai Ulang Konsultasi", type="primary", use_container_width=True):
        st.session_state.clear()
        st.rerun()

with col_chat:
    chat_container = st.container(height=500)
    
    # Menampilkan Riwayat Obrolan
    with chat_container:
        for msg in st.session_state.history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    # Menangkap Input Pesan dari Pengguna
    if prompt := st.chat_input("Ceritakan apa yang sedang Anda rasakan saat ini..."):
        st.session_state.history.append({"role": "user", "content": prompt})
        
        # Memproses input ke dalam FSM
        st.session_state.bot.step(prompt)
        bot_reply = st.session_state.bot.get_response()
        
        st.session_state.history.append({"role": "assistant", "content": bot_reply})
        st.rerun()