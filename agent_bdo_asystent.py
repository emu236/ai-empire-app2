# Agent: Asystent BDO v2.0 (z Researcherem)

import os
import logging
from dotenv import load_dotenv
from openai import OpenAI
# Importujemy funkcję Researchera
from agent_researcher import uruchom_researchera

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler("asystent_bdo.log", mode='w', encoding='utf-8'), logging.StreamHandler()])

# === PRZYKŁADOWE DANE WEJŚCIOWE ===
OPIS_FIRMY_DO_REJESTRACJI = """
Firma: Nowy warsztat samochodowy (jednoosobowa działalność gospodarcza)
Działalność: Naprawa samochodów osobowych.
Odpady: Generujemy odpady typowe dla warsztatu: zużyte oleje, filtry, opony, akumulatory, złom metalowy, tworzywa sztuczne z części.
Opakowania: Nie wprowadzamy opakowań na rynek (nie sprzedajemy części w opakowaniach).
Sprzęt E/E i Baterie: Nie wprowadzamy.
"""

PYTANIE_O_PRZEPISY = "Jakie są główne obowiązki sprawozdawcze w BDO dla sklepu internetowego sprzedającego ubrania i używającego kartonów do wysyłki?"
# ==================================

def generuj_instrukcje_rejestracji(opis_firmy: str, klucz_api: str):
    """Generuje spersonalizowaną instrukcję rejestracji w BDO."""
    # ... (kod tej funkcji pozostaje bez zmian) ...
    client = OpenAI(api_key=klucz_api)
    logging.info(f"  [Asystent BDO] Generuję instrukcję rejestracji dla firmy...")
    prompt = f"""
    Jesteś ekspertem ds. BDO w Polsce. Stwórz szczegółową, spersonalizowaną instrukcję krok po kroku dotyczącą procesu rejestracji w BDO dla firmy opisanej poniżej.

    --- OPIS FIRMY ---
    {opis_firmy}
    --- KONIEC OPISU ---

    Instrukcja powinna zawierać: Potwierdzenie obowiązku, Kluczowe informacje do przygotowania, Wskazówki dotyczące działów wniosku, Kolejne kroki.
    Format: Przejrzysty tekst w markdown.
    """
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        instrukcja = response.choices[0].message.content
        nazwa_pliku = "instrukcja_rejestracji_bdo.md"
        with open(nazwa_pliku, "w", encoding="utf-8") as f: f.write(instrukcja)
        logging.info(f"  [Asystent BDO] Instrukcja rejestracji zapisana w pliku '{nazwa_pliku}'")
    except Exception as e:
        logging.error(f"  [Asystent BDO] Błąd podczas generowania instrukcji: {e}")


def odpowiedz_na_pytanie_bdo(pytanie: str, klucz_api: str):
    """Odpowiada na pytanie o przepisy BDO, wzbogacając odpowiedź o research."""
    client = OpenAI(api_key=klucz_api)
    logging.info(f"  [Asystent BDO] Odpowiadam na pytanie: '{pytanie}'...")

    # === KROK 1: URUCHOM RESEARCHERA ===
    logging.info("    - Uruchamiam Researchera, aby zebrać aktualne informacje...")
    notatki_z_researchu = uruchom_researchera(pytanie) # Używamy pytania jako tematu researchu
    if notatki_z_researchu:
        logging.info("    - Researcher zakończył pracę. Przygotowuję odpowiedź.")
    else:
        logging.warning("    - Researcher nie znalazł dodatkowych informacji. Odpowiadam na podstawie wiedzy ogólnej.")
        notatki_z_researchu = "Nie znaleziono dodatkowych informacji w internecie."
    # ==================================

    # === KROK 2: WYGENERUJ ODPOWIEDŹ Z UWZGLĘDNIENIEM RESEARCHU ===
    prompt = f"""
    Jesteś ekspertem ds. Bazy Danych Odpadowych (BDO) w Polsce. Odpowiedz precyzyjnie i zrozumiale na poniższe pytanie, wykorzystując swoją wiedzę oraz dodatkowe informacje zebrane z internetu.

    PYTANIE: "{pytanie}"

    --- DODATKOWE INFORMACJE Z INTERNETU ---
    {notatki_z_researchu}
    --- KONIEC INFORMACJI ---

    Odpowiedź powinna być:
    - Merytoryczna, dokładna i aktualna.
    - Napisana prostym językiem.
    - Zawierać konkretne wskazówki lub odniesienia do obowiązków.
    - Ustrukturyzowana (np. punktami).
    - Jeśli informacje z internetu są sprzeczne lub niejasne, wskaż to.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem od przepisów BDO w Polsce."},
                {"role": "user", "content": prompt}
            ]
        )
        odpowiedz = response.choices[0].message.content
        nazwa_pliku = "odpowiedz_bdo_z_researchem.md" # Nowa nazwa pliku
        with open(nazwa_pliku, "w", encoding="utf-8") as f: f.write(odpowiedz)
        logging.info(f"  [Asystent BDO] Odpowiedź (wzbogacona o research) zapisana w pliku '{nazwa_pliku}'")
    except Exception as e:
        logging.error(f"  [Asystent BDO] Błąd podczas generowania odpowiedzi: {e}")
    # =========================================================

if __name__ == '__main__':
    if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
        logging.error("BŁĄD: Klucz API OpenAI nie został znaleziony lub jest niepoprawny w pliku .env!")
    else:
        logging.info("--- ASYSTENT BDO v2.0 (z Researcherem): START ---")

        # === Wybierz, co chcesz zrobić ===

        # Opcja 1: Generuj instrukcję rejestracji (działa jak poprzednio)
        # logging.info("Generowan# Agent: Asystent BDO v2.0 (z Researcherem)

import os
import logging
from dotenv import load_dotenv
from openai import OpenAI
# Importujemy funkcję Researchera
from agent_researcher import uruchom_researchera

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler("asystent_bdo.log", mode='w', encoding='utf-8'), logging.StreamHandler()])

# === PRZYKŁADOWE DANE WEJŚCIOWE ===
OPIS_FIRMY_DO_REJESTRACJI = """
Firma: Nowy warsztat samochodowy (jednoosobowa działalność gospodarcza)
Działalność: Naprawa samochodów osobowych.
Odpady: Generujemy odpady typowe dla warsztatu: zużyte oleje, filtry, opony, akumulatory, złom metalowy, tworzywa sztuczne z części.
Opakowania: Nie wprowadzamy opakowań na rynek (nie sprzedajemy części w opakowaniach).
Sprzęt E/E i Baterie: Nie wprowadzamy.
"""

PYTANIE_O_PRZEPISY = "Jakie są główne obowiązki sprawozdawcze w BDO dla sklepu internetowego sprzedającego ubrania i używającego kartonów do wysyłki?"
# ==================================

def generuj_instrukcje_rejestracji(opis_firmy: str, klucz_api: str):
    """Generuje spersonalizowaną instrukcję rejestracji w BDO."""
    # ... (kod tej funkcji pozostaje bez zmian) ...
    client = OpenAI(api_key=klucz_api)
    logging.info(f"  [Asystent BDO] Generuję instrukcję rejestracji dla firmy...")
    prompt = f"""
    Jesteś ekspertem ds. BDO w Polsce. Stwórz szczegółową, spersonalizowaną instrukcję krok po kroku dotyczącą procesu rejestracji w BDO dla firmy opisanej poniżej.

    --- OPIS FIRMY ---
    {opis_firmy}
    --- KONIEC OPISU ---

    Instrukcja powinna zawierać: Potwierdzenie obowiązku, Kluczowe informacje do przygotowania, Wskazówki dotyczące działów wniosku, Kolejne kroki.
    Format: Przejrzysty tekst w markdown.
    """
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        instrukcja = response.choices[0].message.content
        nazwa_pliku = "instrukcja_rejestracji_bdo.md"
        with open(nazwa_pliku, "w", encoding="utf-8") as f: f.write(instrukcja)
        logging.info(f"  [Asystent BDO] Instrukcja rejestracji zapisana w pliku '{nazwa_pliku}'")
    except Exception as e:
        logging.error(f"  [Asystent BDO] Błąd podczas generowania instrukcji: {e}")


def odpowiedz_na_pytanie_bdo(pytanie: str, klucz_api: str):
    """Odpowiada na pytanie o przepisy BDO, wzbogacając odpowiedź o research."""
    client = OpenAI(api_key=klucz_api)
    logging.info(f"  [Asystent BDO] Odpowiadam na pytanie: '{pytanie}'...")

    # === KROK 1: URUCHOM RESEARCHERA ===
    logging.info("    - Uruchamiam Researchera, aby zebrać aktualne informacje...")
    notatki_z_researchu = uruchom_researchera(pytanie) # Używamy pytania jako tematu researchu
    if notatki_z_researchu:
        logging.info("    - Researcher zakończył pracę. Przygotowuję odpowiedź.")
    else:
        logging.warning("    - Researcher nie znalazł dodatkowych informacji. Odpowiadam na podstawie wiedzy ogólnej.")
        notatki_z_researchu = "Nie znaleziono dodatkowych informacji w internecie."
    # ==================================

    # === KROK 2: WYGENERUJ ODPOWIEDŹ Z UWZGLĘDNIENIEM RESEARCHU ===
    prompt = f"""
    Jesteś ekspertem ds. Bazy Danych Odpadowych (BDO) w Polsce. Odpowiedz precyzyjnie i zrozumiale na poniższe pytanie, wykorzystując swoją wiedzę oraz dodatkowe informacje zebrane z internetu.

    PYTANIE: "{pytanie}"

    --- DODATKOWE INFORMACJE Z INTERNETU ---
    {notatki_z_researchu}
    --- KONIEC INFORMACJI ---

    Odpowiedź powinna być:
    - Merytoryczna, dokładna i aktualna.
    - Napisana prostym językiem.
    - Zawierać konkretne wskazówki lub odniesienia do obowiązków.
    - Ustrukturyzowana (np. punktami).
    - Jeśli informacje z internetu są sprzeczne lub niejasne, wskaż to.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem od przepisów BDO w Polsce."},
                {"role": "user", "content": prompt}
            ]
        )
        odpowiedz = response.choices[0].message.content
        nazwa_pliku = "odpowiedz_bdo_z_researchem.md" # Nowa nazwa pliku
        with open(nazwa_pliku, "w", encoding="utf-8") as f: f.write(odpowiedz)
        logging.info(f"  [Asystent BDO] Odpowiedź (wzbogacona o research) zapisana w pliku '{nazwa_pliku}'")
    except Exception as e:
        logging.error(f"  [Asystent BDO] Błąd podczas generowania odpowiedzi: {e}")
    # =========================================================

if __name__ == '__main__':
    if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
        logging.error("BŁĄD: Klucz API OpenAI nie został znaleziony lub jest niepoprawny w pliku .env!")
    else:
        logging.info("--- ASYSTENT BDO v2.0 (z Researcherem): START ---")

        # === Wybierz, co chcesz zrobić ===

        # Opcja 1: Generuj instrukcję rejestracji (działa jak poprzednio)
        # logging.info("Generowanie instrukcji rejestracji...")
        # generuj_instrukcje_rejestracji(OPIS_FIRMY_DO_REJESTRACJI, OPENAI_API_KEY)

        # Opcja 2: Odpowiedz na pytanie o przepisy (teraz z researchem)
        logging.info("Odpowiadanie na pytanie o przepisy (z researchem)...")
        odpowiedz_na_pytanie_bdo(PYTANIE_O_PRZEPISY, OPENAI_API_KEY)

        # ================================

        logging.info("\n--- ASYSTENT BDO: ZAKOŃCZONO ---")ie instrukcji rejestracji...")
        # generuj_instrukcje_rejestracji(OPIS_FIRMY_DO_REJESTRACJI, OPENAI_API_KEY)

        # Opcja 2: Odpowiedz na pytanie o przepisy (teraz z researchem)
        logging.info("Odpowiadanie na pytanie o przepisy (z researchem)...")
        odpowiedz_na_pytanie_bdo(PYTANIE_O_PRZEPISY, OPENAI_API_KEY)

        # ================================

        logging.info("\n--- ASYSTENT BDO: ZAKOŃCZONO ---")