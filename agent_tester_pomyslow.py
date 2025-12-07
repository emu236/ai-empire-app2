# Agent: Tester Pomysłów v2.0 (Pełna Automatyzacja)
# Cel: Automatyczne znajdowanie tematów, generowanie postów testowych i ich publikacja.

import os
import time
import re
import logging
from dotenv import load_dotenv

# Importujemy potrzebne moduły z naszego projektu
from agent_analityk_v2 import uruchom_analityka_rynku
from main import formatuj_raport_dla_ai, filtruj_i_ocen_nisze # Importujemy logikę filtra z main.py
from agent_social import uruchom_agenta_social
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler("tester_pomyslow.log", mode='w', encoding='utf-8'), logging.StreamHandler()])

# --- KONFIGURACJA ---
LICZBA_POSTOW_NA_TEMAT = 3
LICZBA_TEMATOW_DO_TESTOWANIA = 3 # Ile najlepszych tematów chcemy przetestować
PAUZA_MIEDZY_POSTAMI_SEKUNDY = 10 # Do testów, zmień na np. 4 * 3600 dla produkcji
# --------------------

def generuj_posty_testowe(temat: str, liczba: int, klucz_api: str) -> list:
    """Generuje listę postów testowych dla danego tematu."""
    logging.info(f"  [Tester] Generuję {liczba} postów testowych dla tematu: '{temat}'...")
    client = OpenAI(api_key=klucz_api)
    prompt = f"""
    Jesteś ekspertem od marketingu wiralowego na X (Twitterze). Stwórz {liczba} krótkich, angażujących postów (max 280 znaków) testujących zainteresowanie tematem: "{temat}". Posty powinny być różnorodne (pytanie, teza, obietnica). Zwróć jako listę numerowaną. Dodaj 2-3 hashtagi.
    """
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        posty_tekst = response.choices[0].message.content
        posty_lista = [re.sub(r'^\d+\.\s*', '', linia).strip() for linia in posty_tekst.split('\n') if linia.strip()]
        logging.info(f"  [Tester] Wygenerowano {len(posty_lista)} postów dla tematu '{temat}'.")
        return posty_lista
    except Exception as e:
        logging.error(f"  [Tester] Błąd podczas generowania postów: {e}")
        return []

if __name__ == '__main__':
    logging.info("--- TESTER POMYSŁÓW v2.0 (AUTOMATYCZNY): START ---")
    if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
        logging.error("BŁĄD: Klucz API OpenAI nie znaleziony w pliku .env!"); exit()

    # Krok 1: Uruchom Badacza Rynku
    logging.info("Krok 1: Uruchamiam Badacza Rynku...")
    raport_rynkowy = uruchom_analityka_rynku()
    if not raport_rynkowy:
        logging.error("BŁĄD: Badacz Rynku nie zebrał danych. Zatrzymuję proces."); exit()
    logging.info(f"Badacz Rynku zebrał dane dla {len(raport_rynkowy)} tematów.")

    # Krok 2: Uruchom Agenta-Filtra, aby wybrać N najlepszych tematów
    logging.info("Krok 2: Uruchamiam Agenta-Filtra...")
    # Zmodyfikowany prompt dla Filtra, aby zwrócił listę N tematów
    client = OpenAI(api_key=OPENAI_API_KEY)
    sformatowany_raport = formatuj_raport_dla_ai(raport_rynkowy)
    prompt_filtrujacy_top_n = f"""
    Jesteś analitykiem biznesowym [...]. Przeanalizuj poniższy raport i wybierz {LICZBA_TEMATOW_DO_TESTOWANIA} tematy z największym potencjałem sprzedażowym.
    Zwróć odpowiedź jako listę numerowaną.
    --- RAPORT Z BADANIA RYNKU ---
    {sformatowany_raport}
    --- KONIEC RAPORTU ---
    """
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt_filtrujacy_top_n}])
        top_tematy_tekst = response.choices[0].message.content
        top_tematy = [re.sub(r'^\d+\.\s*', '', linia).strip() for linia in top_tematy_tekst.split('\n') if linia.strip()]
        if not top_tematy: raise ValueError("Filtr nie zwrócił żadnych tematów.")
        logging.info(f"Agent-Filtr wybrał {len(top_tematy)} najlepsze tematy do testowania: {', '.join(top_tematy)}")
    except Exception as e:
        logging.error(f"BŁĄD: Agent-Filtr nie wybrał tematów: {e}"); exit()
    
    # Krok 3: Generowanie postów testowych dla wybranych tematów
    logging.info("\nKrok 3: Generowanie postów testowych...")
    wszystkie_posty = []
    for temat in top_tematy:
        posty_dla_tematu = generuj_posty_testowe(temat, LICZBA_POSTOW_NA_TEMAT, OPENAI_API_KEY)
        wszystkie_posty.extend(posty_dla_tematu)
        time.sleep(5) 

    if not wszystkie_posty:
        logging.error("Nie udało się wygenerować żadnych postów testowych."); exit()
    
    # Krok 4: Publikacja postów testowych
    logging.info(f"\nKrok 4: Rozpoczynam publikację {len(wszystkie_posty)} postów testowych...")
    for i, post in enumerate(wszystkie_posty):
        logging.info(f"\nPublikuję post {i+1}/{len(wszystkie_posty)}:")
        logging.info(f"Treść: {post}") 
        uruchom_agenta_social(post)
        
        if i < len(wszystkie_posty) - 1:
            logging.info(f"Czekam {PAUZA_MIEDZY_POSTAMI_SEKUNDY} sekund przed publikacją kolejnego posta...")
            time.sleep(PAUZA_MIEDZY_POSTAMI_SEKUNDY)

    logging.info("--- TESTER POMYSŁÓW: ZAKOŃCZONO ---")