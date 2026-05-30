"""Smoke test: simulate a few conversations to verify FSM transitions and NLP."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core import HealthBuddyFSM


def run_dialog(name, inputs):
    print(f"\n{'='*70}\nTEST: {name}\n{'='*70}")
    bot = HealthBuddyFSM()
    bot.step("")
    print(f"[{bot.state.name}] BOT: {bot.get_response()[:120]}...")
    for user_in in inputs:
        print(f"\nUSER: {user_in}")
        bot.step(user_in)
        snippet = bot.get_response().replace("\n", " ")[:200]
        print(f"[{bot.state.name}] BOT: {snippet}...")


if __name__ == "__main__":
    run_dialog("Greeting + symptom direct match", [
        "halo",
        "saya demam dan pusing sudah 2 hari",
    ])

    run_dialog("Multi-turn triage", [
        "perut saya tidak enak",
        "rasanya perih dan kembung",
        "kalau telat makan jadi mual",
    ])

    run_dialog("Definition lookup", [
        "apa itu kolesterol",
        "apa itu hipertensi",
    ])

    run_dialog("First aid query", [
        "pertolongan pertama luka bakar",
        "kalau mimisan bagaimana",
    ])

    run_dialog("Red flag detection (must lock)", [
        "saya merasa nyeri dada hebat",
        "halo masih bisa konsultasi?",
    ])

    run_dialog("Typo tolerance", [
        "saya batok berdahak dan pilek",
    ])

    run_dialog("Reset flow", [
        "saya batuk",
        "mulai ulang",
        "halo",
    ])

    run_dialog("FAQ lookup", [
        "berapa lama tidur ideal",
        "tips olahraga",
    ])

    print("\n\nAll smoke tests completed.")
