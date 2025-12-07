# Agent: Osobisty Konsultant
# Cel: Generowanie spersonalizowanych planów i audytów na życzenie.

from openai import OpenAI
import os
import time

# --- KONFIGURACJA ---
# Odczyt klucza API z pliku .env (upewnij się, że masz go w tym pliku)
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === PRZYKŁADOWE ZAMÓWIENIE OD "KLIENTA" ===
# W prawdziwym systemie te dane pochodziłyby z formularza na stronie.
CEL_KLIENTA = "Chcę schudnąć 8 kg w 3 miesiące. Pracuję przy biurku, mam mało czasu na gotowanie, mogę ćwiczyć 3 razy w tygodniu po 45 minut w domu (mam hantle i matę)."
# ============================================

def uruchom_konsultanta(cel: str, klucz_api: str):
    """
    Generuje spersonalizowany plan działania na podstawie celu klienta.
    """
    client = OpenAI(api_key=klucz_api)

    print(f"  [Konsultant] Otrzymałem zamówienie. Analizuję cel klienta i generuję spersonalizowany plan...")
    
    prompt = f"""
    Jesteś światowej klasy ekspertem w dziedzinie, której dotyczy cel klienta (np. dietetyka, finanse, marketing).
    Twoim zadaniem jest stworzenie szczegółowego, spersonalizowanego i realistycznego planu działania na podstawie poniższych informacji.

    --- CEL KLIENTA ---
    {cel}
    --- KONIEC CELU ---

    Wygeneruj kompletny plan w formacie markdown. Plan musi być podzielony na logiczne sekcje, być motywujący i bardzo praktyczny.
    Struktura planu powinna zawierać:
    1.  **Analiza Celu:** Krótkie podsumowanie i potwierdzenie, że cel jest realistyczny.
    2.  **Filozofia Działania:** 2-3 kluczowe zasady, którymi klient powinien się kierować.
    3.  **Plan Działania Krok po Kroku:** Podzielony na tygodnie lub miesiące, z konkretnymi, wykonalnymi zadaniami.
    4.  **Przykładowy Jadłospis / Harmonogram:** Prosty przykład jednego dnia lub tygodnia.
    5.  **Potencjalne Wyzwania i Jak Sobie z Nimi Radzić:** Przewiduj 2-3 problemy i podaj gotowe rozwiązania.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jesteś osobistym konsultantem i ekspertem w planowaniu."},
                {"role": "user", "content": prompt}
            ]
        )
        spersonalizowany_plan = response.choices[0].message.content
        
        # Zapisujemy plan do pliku
        bezpieczna_nazwa_celu = cel.replace(" ", "_")[:30]
        nazwa_pliku = f"plan_dla_{bezpieczna_nazwa_celu}.md" # Używamy rozszerzenia .md (markdown)
        with open(nazwa_pliku, "w", encoding="utf-8") as f:
            f.write(spersonalizowany_plan)
        print(f"  [Konsultant] Spersonalizowany plan został zapisany w pliku '{nazwa_pliku}'")

    except Exception as e:
        print(f"  [Konsultant] Wystąpił błąd: {e}")

if __name__ == '__main__':
    if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
        print("BŁĄD: Klucz API OpenAI nie został znaleziony lub jest niepoprawny w pliku .env!")
    else:
        print("--- OSOBISTY KONSULTANT: START ---")
        uruchom_konsultanta(CEL_KLIENTA, OPENAI_API_KEY)
        print("\n--- OSOBISTY KONSULTANT: ZAKOŃCZONO ---")