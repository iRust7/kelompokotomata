"""HealthBuddy Streamlit application."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from core import HealthBuddyFSM, State
from data import DISEASES, CATEGORIES, FAQ, FIRST_AID, EMERGENCY_NUMBERS, WELLNESS_TIPS

st.set_page_config(
    page_title="HealthBuddy — Asisten Edukasi Kesehatan",
    page_icon="◐",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def load_css():
    css_path = Path(__file__).parent / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def init_state():
    if "bot" not in st.session_state:
        st.session_state.bot = HealthBuddyFSM()
        st.session_state.bot.step("")
        st.session_state.history = [
            {"role": "assistant", "content": st.session_state.bot.get_response()}
        ]
        st.session_state.tip_index = 0


def render_header():
    st.markdown(
        """
        <div class="hb-header">
            <div class="hb-brand">
                <span class="hb-mark">◐</span>
                <div>
                    <div class="hb-brand-name">HealthBuddy</div>
                    <div class="hb-brand-sub">Edisi Mei MMXXVI / No. 01</div>
                </div>
            </div>
            <div class="hb-meta">
                <span class="hb-pill">Berbasis Finite State Machine</span>
                <span class="hb-divider">/</span>
                <span class="hb-meta-text">Teori Bahasa &amp; Otomata</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
        <section class="hb-hero">
            <div class="hb-hero-tag">Vol. 01 — Edukasi Mandiri</div>
            <h1 class="hb-hero-title">Bicara dengan tubuh<br><em>sebelum tubuh berbicara terlalu keras.</em></h1>
            <p class="hb-hero-lead">
                Asisten percakapan untuk mengenali gejala ringan, memahami istilah medis,
                dan memandu pertolongan pertama. Tanpa diagnosis. Tanpa resep. Hanya rambu-rambu
                untuk membantu Anda mengambil keputusan yang lebih tenang.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_state_indicator(bot):
    state = bot.state
    if state == State.EMERGENCY:
        cls, label, desc = "alert", "Mode Darurat", "Sistem terkunci. Cari bantuan medis."
    elif state == State.TRIAGE:
        cls, label, desc = "active", "Mengakumulasi Gejala", "Sebutkan keluhan tambahan."
    elif state == State.ADVICE:
        cls, label, desc = "active", "Memberi Saran", "Edukasi keluhan ringan."
    elif state in (State.DEFINITION, State.FAQ_VIEW, State.FIRST_AID_VIEW, State.EMERGENCY_INFO):
        cls, label, desc = "active", "Menyajikan Informasi", state.name.replace("_", " ").title()
    elif state == State.GREETING:
        cls, label, desc = "idle", "Menunggu Keluhan", "Silakan mulai percakapan."
    elif state == State.MAIN_MENU:
        cls, label, desc = "idle", "Menu Utama", "Pilih topik atau ceritakan keluhan."
    elif state == State.CLARIFY:
        cls, label, desc = "active", "Meminta Klarifikasi", "Coba reformulasi pertanyaan."
    else:
        cls, label, desc = "idle", state.name.title(), "Sistem siap."

    st.markdown(
        f"""
        <div class="hb-state hb-state-{cls}">
            <div class="hb-state-dot"></div>
            <div>
                <div class="hb-state-label">{label}</div>
                <div class="hb-state-desc">{desc}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_topic_panel():
    st.markdown('<div class="hb-panel"><div class="hb-panel-eyebrow">Indeks</div>', unsafe_allow_html=True)
    st.markdown('<div class="hb-panel-title">Cakupan Pengetahuan</div>', unsafe_allow_html=True)

    by_category = {}
    for key, info in DISEASES.items():
        by_category.setdefault(info["kategori"], []).append(info["nama"])

    rows = []
    for cat_key, names in by_category.items():
        label = CATEGORIES.get(cat_key, cat_key)
        rows.append(f'<li><span class="hb-cat">{label}</span><span class="hb-count">{len(names)}</span></li>')
    st.markdown(f'<ul class="hb-cat-list">{"".join(rows)}</ul>', unsafe_allow_html=True)

    total_diseases = len(DISEASES)
    total_definitions = len(__import__("data").DEFINITIONS)
    total_first_aid = len(FIRST_AID)
    total_faq = len(FAQ)

    st.markdown(
        f"""
        <div class="hb-stat-grid">
            <div class="hb-stat"><div class="hb-stat-num">{total_diseases}</div><div class="hb-stat-lbl">Kondisi</div></div>
            <div class="hb-stat"><div class="hb-stat-num">{total_definitions}</div><div class="hb-stat-lbl">Istilah</div></div>
            <div class="hb-stat"><div class="hb-stat-num">{total_first_aid}</div><div class="hb-stat-lbl">P3K</div></div>
            <div class="hb-stat"><div class="hb-stat-num">{total_faq}</div><div class="hb-stat-lbl">FAQ</div></div>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_quick_actions():
    st.markdown('<div class="hb-panel"><div class="hb-panel-eyebrow">Aksi Cepat</div>', unsafe_allow_html=True)
    st.markdown('<div class="hb-panel-title">Mulai dari sini</div>', unsafe_allow_html=True)

    quick_buttons = [
        ("Saya merasa demam", "saya demam dan pusing"),
        ("Perut saya perih", "perut saya perih, gejala maag"),
        ("Apa itu kolesterol", "apa itu kolesterol"),
        ("P3K luka bakar", "pertolongan pertama luka bakar"),
        ("Tips tidur ideal", "berapa lama tidur ideal"),
        ("Nomor darurat", "nomor darurat kesehatan"),
    ]

    cols = st.columns(2)
    for i, (label, prompt) in enumerate(quick_buttons):
        with cols[i % 2]:
            if st.button(label, key=f"quick_{i}", use_container_width=True):
                handle_user_input(prompt)
    st.markdown("</div>", unsafe_allow_html=True)


def render_transition_panel(bot):
    log = bot.get_transition_log()
    if not log:
        return
    st.markdown('<div class="hb-panel hb-panel-mono"><div class="hb-panel-eyebrow">Log Transisi FSM</div>', unsafe_allow_html=True)
    st.markdown('<div class="hb-panel-title">Jejak State</div>', unsafe_allow_html=True)
    rows = []
    for entry in log[-6:]:
        rows.append(
            f'<li><span class="hb-tr-from">{entry["from"]}</span>'
            f'<span class="hb-arrow">&rarr;</span>'
            f'<span class="hb-tr-to">{entry["to"]}</span>'
            f'<div class="hb-tr-reason">{entry["reason"]}</div></li>'
        )
    st.markdown(f'<ol class="hb-tr-list">{"".join(rows)}</ol></div>', unsafe_allow_html=True)


def render_disclaimer():
    st.markdown(
        """
        <aside class="hb-disclaimer">
            <div class="hb-disclaimer-mark">!</div>
            <div>
                <strong>Catatan Penting.</strong>
                HealthBuddy adalah alat edukasi berbasis aturan, bukan pengganti tenaga medis profesional.
                Untuk diagnosis dan terapi, konsultasikan dengan dokter atau fasilitas kesehatan terdekat.
                Dalam keadaan darurat, hubungi <strong>119</strong>.
            </div>
        </aside>
        """,
        unsafe_allow_html=True,
    )


def render_pullquote():
    tips = WELLNESS_TIPS
    idx = st.session_state.get("tip_index", 0) % len(tips)
    quote = tips[idx]
    st.markdown(
        f"""
        <blockquote class="hb-pullquote">
            <div class="hb-quote-mark">&ldquo;</div>
            <p>{quote}</p>
            <footer>Catatan harian — tips gaya hidup #{idx + 1:02d}</footer>
        </blockquote>
        """,
        unsafe_allow_html=True,
    )


def render_messages():
    for msg in st.session_state.history:
        role_class = "hb-msg-bot" if msg["role"] == "assistant" else "hb-msg-user"
        role_label = "HealthBuddy" if msg["role"] == "assistant" else "Anda"
        with st.container():
            st.markdown(
                f'<div class="hb-msg {role_class}"><div class="hb-msg-role">{role_label}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(msg["content"])
            st.markdown("</div>", unsafe_allow_html=True)


def handle_user_input(prompt):
    st.session_state.history.append({"role": "user", "content": prompt})
    st.session_state.bot.step(prompt)
    reply = st.session_state.bot.get_response()
    st.session_state.history.append({"role": "assistant", "content": reply})
    st.session_state.tip_index = st.session_state.get("tip_index", 0) + 1
    st.rerun()


def main():
    load_css()
    init_state()

    render_header()
    render_hero()

    col_main, col_side = st.columns([2.1, 1], gap="large")

    with col_main:
        st.markdown('<div class="hb-section-eyebrow">Percakapan</div>', unsafe_allow_html=True)
        st.markdown('<h2 class="hb-section-title">Ceritakan keluhan Anda</h2>', unsafe_allow_html=True)
        render_state_indicator(st.session_state.bot)

        chat_box = st.container(height=520)
        with chat_box:
            render_messages()

        prompt = st.chat_input("Ketik keluhan, gejala, atau pertanyaan kesehatan Anda...")
        if prompt:
            handle_user_input(prompt)

        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("Mulai Ulang Konsultasi", use_container_width=True, key="reset_main"):
                st.session_state.clear()
                st.rerun()
        with col_b:
            if st.button("Tampilkan Bantuan", use_container_width=True, key="help_main"):
                handle_user_input("bantuan")

    with col_side:
        render_disclaimer()
        render_pullquote()
        render_quick_actions()
        render_topic_panel()
        render_transition_panel(st.session_state.bot)

    st.markdown(
        """
        <footer class="hb-footer">
            <div class="hb-footer-left">
                <div class="hb-footer-title">HealthBuddy</div>
                <div class="hb-footer-sub">Asisten Edukasi Kesehatan Berbasis FSM</div>
            </div>
            <div class="hb-footer-right">
                <span>Tugas Akhir / Teori Bahasa &amp; Otomata</span>
                <span class="hb-divider">/</span>
                <span>Knowledge base: Kemenkes RI, WHO, gizi seimbang</span>
            </div>
        </footer>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
