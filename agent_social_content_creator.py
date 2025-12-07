# Agent 12: Kreator Treści Social Media v2.3 (Dynamiczne tematy via DDGS Search)

import os
import time
import re
import logging
from dotenv import load_dotenv
from openai import OpenAI
import requests
from bs4 import BeautifulSoup # Potrzebne dla szukaj_w_internecie
import urllib.parse # Potrzebne dla szukaj_w_internecie
import random # Dodano import random

# Importujemy agentów i funkcję wyszukiwania
from agent_social import uruchom_agenta_social
from agent_grafik import uruchom_agenta_grafika
# Importujemy funkcję z agent_researcher.py (zakładamy, że plik istnieje i ma tę funkcję)
try:
    # Upewnij się, że nazwa pliku jest poprawna (może być agent_analityk_v2.py?)
    from agent_researcher import szukaj_w_internecie
except ImportError:
     logging.error("BŁĄD: Nie można zaimportować funkcji 'szukaj_w_internecie'. Sprawdź nazwę pliku.")
     # Definicja funkcji awaryjnej (skopiowana)
     def szukaj_w_internecie(temat: str, ilosc_wynikow: int = 3) -> list:
        logging.info(f"    [Search-Fallback] Wyszukuję w DuckDuckGo: '{temat}'")
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            res = requests.post("https://html.duckduckgo.com/html/", data={'q': temat}, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            linki = soup.find_all('a', class_='result__a')
            if not linki: return []
            znalezione_linki = [{'title': link.text, 'href': link['href']} for link in linki]
            return znalezione_linki[:ilosc_wynikow]
        except Exception as e:
            logging.error(f"    [Search-Fallback] Błąd podczas wyszukiwania: {e}")
            return []


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

log_file = os.path.join('ai_social_content', 'social_creator.log')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler(log_file, mode='w', encoding='utf-8'), logging.StreamHandler()])

# --- KONFIGURACJA ---
LICZBA_TEMATOW_DO_OPRACOWANIA = 5 # Ile najnowszych tematów AI chcemy znaleźć
# --------------------

def znajdz_aktualne_tematy_ai() -> list:
    """Używa własnej funkcji wyszukiwania do znalezienia najnowszych artykułów/wiadomości o AI."""
    logging.info("  [Kreator SM] Wyszukuję aktualne tematy AI za pomocą własnej wyszukiwarki...")

    # Zapytania do wyszukiwarki
    zapytania_wyszukiwania = ["najnowsze wiadomości AI Polska", "AI trendy", "co nowego w AI"]
    znalezione_tytuly = []

    for zapytanie in zapytania_wyszukiwania:
        wyniki = szukaj_w_internecie(zapytanie, ilosc_wynikow=3) # Bierzemy 3 wyniki na zapytanie
        znalezione_tytuly.extend([wynik['title'] for wynik in wyniki])
        time.sleep(random.uniform(1, 2)) # Pauza

    if not znalezione_tytuly:
        logging.warning("  [Kreator SM] Nie znaleziono żadnych aktualnych tematów AI.")
        return []

    # Usuwamy duplikaty i zwracamy unikalne tytuły jako tematy
    unikalne_tematy = list(set(znalezione_tytuly))
    # Wybieramy N najciekawszych (na razie bierzemy pierwsze N)
    wybrane_tematy = unikalne_tematy[:LICZBA_TEMATOW_DO_OPRACOWANIA]
    logging.info(f"  [Kreator SM] Znaleziono {len(wybrane_tematy)} aktualnych tematów do opracowania.")
    return wybrane_tematy

def generuj_tresc_dla_platform(temat: str, klucz_api: str) -> dict | None:
    logging.info(f"  [Kreator SM] Generuję pakiet treści dla tematu: '{temat}'...")
    client = OpenAI(api_key=klucz_api)
    prompt = f"""
    Jesteś ekspertem od social media marketingu specjalizującym się w tematyce AI.
    Stwórz kompletny pakiet treści na temat: "{temat}", dostosowany do różnych platform.

    Wygeneruj DOKŁADNIE poniższe elementy:

    --- FACEBOOK POST ---
    [Angażujący post (ok. 100-150 słów) na Facebooka.]

    --- INSTAGRAM POST ---
    TEKST: [Krótki, chwytliwy caption na Instagram (ok. 50-70 słów).]
    PROMPT GRAFIKI: [Szczegółowy opis pomysłu na atrakcyjną grafikę (styl flat design, bez tekstu) do tego posta, którą można stworzyć w DALL-E.]
    HASHTAGI_IG: [10-15 relevantnych hashtagów na Instagram.]

    --- REEL/SHORTS SCRIPT (30 sekund) ---
    TYTUŁ ROLKI: [Chwytliwy tytuł]
    SCENA 1 (0-5s): [Opis wizualny + Tekst na ekranie/Lektor - Hak]
    SCENA 2 (5-15s): [Opis wizualny + Tekst na ekranie/Lektor - Główna wartość/porada]
    SCENA 3 (15-25s): [Opis wizualny + Tekst na ekranie/Lektor - Przykład/Rozwinięcie]
    SCENA 4 (25-30s): [Opis wizualny + Tekst na ekranie/Lektor - CTA]
    MUZYKA: [Sugestia rodzaju muzyki, np. "dynamiczna, elektroniczna"]
    HASHTAGI_VIDEO: [5-7 relevantnych hashtagów na Reels/Shorts.]

    --- X (TWITTER) POST ---
    [Krótki post (max 280 znaków) na X. Dodaj 2-3 hashtagi.]
    """
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        tresc_pakietu = response.choices[0].message.content
        wyniki = {
            "facebook": re.search(r"--- FACEBOOK POST ---\s*(.*?)\s*--- INSTAGRAM POST ---", tresc_pakietu, re.DOTALL).group(1).strip(),
            "instagram_text": re.search(r"TEKST:\s*(.*?)\s*PROMPT GRAFIKI:", tresc_pakietu, re.DOTALL).group(1).strip(),
            "instagram_grafika_prompt": re.search(r"PROMPT GRAFIKI:\s*(.*?)\s*HASHTAGI_IG:", tresc_pakietu, re.DOTALL).group(1).strip(),
            "instagram_hashtagi": re.search(r"HASHTAGI_IG:\s*(.*?)\s*--- REEL/SHORTS SCRIPT", tresc_pakietu, re.DOTALL).group(1).strip(),
            "reel_script": re.search(r"--- REEL/SHORTS SCRIPT \(30 sekund\)\s*---\s*(.*?)\s*--- X \(TWITTER\) POST ---", tresc_pakietu, re.DOTALL).group(1).strip(),
            "x_post": re.search(r"--- X \(TWITTER\) POST ---\s*(.*)", tresc_pakietu, re.DOTALL).group(1).strip()
        }
        if not all(wyniki.values()): raise ValueError("Nie udało się sparsować wszystkich sekcji odpowiedzi AI.")
        logging.info(f"  [Kreator SM] Pakiet treści dla '{temat}' wygenerowany.")
        return wyniki
    except Exception as e:
        logging.error(f"  [Kreator SM] Błąd podczas generowania lub parsowania pakietu treści dla '{temat}': {e}")
        return None

if __name__ == '__main__':
    logging.info("--- KREATOR TREŚCI SOCIAL MEDIA v2.3 (DYNAMICZNE via Własna Wyszukiwarka): START ---")
    if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
        logging.error("BŁĄD: Klucz API OpenAI nie znaleziony w pliku .env!"); exit()

    # Krok 1: Znajdź aktualne tematy AI za pomocą własnej wyszukiwarki
    aktualne_tematy = znajdz_aktualne_tematy_ai()

    if not aktualne_tematy:
        logging.error("Nie udało się znaleźć żadnych aktualnych tematów AI. Zatrzymuję proces."); exit()

    logging.info(f"Znaleziono {len(aktualne_tematy)} tematów do opracowania: {', '.join(aktualne_tematy)}")

    # Krok 2: Pętla generująca treści dla znalezionych tematów
    for temat in aktualne_tematy:
        pakiet = generuj_tresc_dla_platform(temat, OPENAI_API_KEY)

        if pakiet:
            bezpieczna_nazwa_tematu = re.sub(r'[\\/*?:"<>|]', "", temat).replace(" ", "_")[:50]
            folder_tematu = os.path.join('ai_social_content', bezpieczna_nazwa_tematu)
            os.makedirs(folder_tematu, exist_ok=True)

            # Zapisywanie plików tekstowych
            with open(os.path.join(folder_tematu, "facebook_post.txt"), "w", encoding="utf-8") as f: f.write(pakiet['facebook'])
            with open(os.path.join(folder_tematu, "instagram_post.txt"), "w", encoding="utf-8") as f: f.write(f"Tekst:\n{pakiet['instagram_text']}\n\nPrompt Grafiki:\n{pakiet['instagram_grafika_prompt']}\n\nHashtagi:\n{pakiet['instagram_hashtagi']}")
            with open(os.path.join(folder_tematu, "reel_script.txt"), "w", encoding="utf-8") as f: f.write(pakiet['reel_script'])
            with open(os.path.join(folder_tematu, "x_post.txt"), "w", encoding="utf-8") as f: f.write(pakiet['x_post'])
            logging.info(f"Treści tekstowe dla '{temat}' zapisane w folderze '{folder_tematu}'.")

            # Generowanie i zapis grafiki
            logging.info(f"  [Kreator SM] Uruchamiam Agenta Grafika dla '{temat}'...")
            sciezka_grafiki_temp = uruchom_agenta_grafika(temat, pakiet['instagram_grafika_prompt'], OPENAI_API_KEY)
            if sciezka_grafiki_temp:
                nowa_sciezka_grafiki = os.path.join(folder_tematu, "grafika_instagram.png")
                if os.path.exists(nowa_sciezka_grafiki): os.remove(nowa_sciezka_grafiki)
                os.rename(sciezka_grafiki_temp, nowa_sciezka_grafiki)
                logging.info(f"  Grafika dla '{temat}' zapisana jako 'grafika_instagram.png'")

            # Automatyczna publikacja na X
            logging.info(f"Publikuję post na X dla tematu '{temat}'...")
            uruchom_agenta_social(pakiet['x_post'])

            pauza = random.uniform(15, 25)
            logging.info(f"Czekam {pauza:.1f} sekund przed kolejnym tematem...")
            time.sleep(pauza)

    logging.info("--- KREATOR TREŚCI SOCIAL MEDIA: ZAKOŃCZONO ---")