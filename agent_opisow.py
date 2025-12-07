# Agent 11: Agent Opisów Produktu (v1.1 - Niezawodny JSON)

import os
import logging
import re
import json # Będziemy używać formatu JSON do niezawodnej odpowiedzi
from openai import OpenAI
from dotenv import load_dotenv

# Konfiguracja
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ustawiamy loggera
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def uruchom_agenta_opisow(prospekt_tekst: str, klucz_api: str) -> dict:
    """
    Bierze pełen prospekt i generuje DWA opisy (krótki i długi).
    Zwraca słownik: {"krotki_opis": "...", "dlugi_opis": "..."}
    """
    logger.info("  [Agent Opisów v1.1] Uruchamiam... Generuję opisy produktu...")
    
    client = OpenAI(api_key=klucz_api)
    
    # Używamy specjalnego trybu "JSON Mode" w GPT-4o, aby ZMUSIĆ AI
    # do zwrócenia idealnie sformatowanej odpowiedzi.
    prompt_opisow = f"""
    Jesteś ekspertem SEO i copywriterem. Przeanalizuj poniższy prospekt e-booka.
    Twoim zadaniem jest wygenerowanie dwóch oddzielnych opisów marketingowych dla sklepu internetowego.

    1.  **krotki_opis**: Bardzo krótki, chwytliwy opis (maksymalnie 2-3 zdania). Idealny na miniaturkę produktu.
    2.  **dlugi_opis**: Dłuższy, szczegółowy opis (około 2-3 akapity). Ma on zachęcić do zakupu na stronie produktu. Powinien wyjaśniać, co klient znajdzie w środku i jaki problem rozwiąże. Użyj formatowania akapitów (znaków nowej linii \n).

    --- PROSPEKT ---
    {prospekt_tekst}
    --- KONIEC PROSPEKTU ---

    Zwróć odpowiedź WYŁĄCZNIE w formacie JSON, zgodnie z poniższym schematem:
    {{
      "krotki_opis": "Tutaj wpisz krótki opis...",
      "dlugi_opis": "Tutaj wpisz dłuższy opis produktu...\n\nZ podziałem na akapity."
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # Używamy GPT-4o dla najlepszej jakości
            response_format={"type": "json_object"}, # Wymuszamy odpowiedź JSON
            messages=[
                {"role": "system", "content": "Jesteś copywriterem zwracającym tylko format JSON."},
                {"role": "user", "content": prompt_opisow}
            ]
        )
        odpowiedz_ai_json = response.choices[0].message.content.strip()
        
        # Parsujemy odpowiedź JSON
        opisy = json.loads(odpowiedz_ai_json)
        
        if opisy.get("krotki_opis") and opisy.get("dlugi_opis"):
            logger.info("  [Agent Opisów v1.1] Pomyślnie wygenerowano oba opisy.")
            return opisy
        else:
            raise ValueError("AI nie zwróciło poprawnych kluczy 'krotki_opis' lub 'dlugi_opis'.")
            
    except Exception as e:
        logger.error(f"  [Agent Opisów v1.1] Błąd: {e}")
        # Zwracamy słownik awaryjny
        return {
            "krotki_opis": "Szczegółowy przewodnik, który pomoże Ci zrozumieć kluczowe koncepcje i strategie.",
            "dlugi_opis": "Ten e-book to kompleksowe źródło wiedzy, które przeprowadzi Cię przez wszystkie etapy.\n\nDowiesz się z niego, jak unikać najczęstszych błędów i jak skutecznie wdrażać nowe rozwiązania."
        }

# --- BLOK TESTOWY ---
if __name__ == '__main__':
    if not OPENAI_API_KEY:
        print("BŁĄD: Nie znaleziono klucza OPENAI_API_KEY w pliku .env")
    else:
        print("--- TEST AGENTA OPISÓW v1.1 ---")
        TEST_PROSPEKT = """
        **1. Tytuł Roboczy:** Baniek w 10 lat –
        **2. Grupa Docelowa:** Młodzi profesjonaliści, osoby chcące budować bogactwo
        **3. Kluczowa Obietnica / USP:** Osiągnij wolność finansową w dekadę.
        [SPIS_START]
        Moduł 1: Fundamenty Bogactwa - Zarządzanie Finansami Osobistymi
        Moduł 2: Psychologia Pieniądza
        [SPIS_END]
        """
        wynikowe_opisy = uruchom_agenta_opisow(TEST_PROSPEKT, OPENAI_API_KEY)
        print("\n--- WYGENEROWANE OPISY ---")
        print(f"KRÓTKI OPIS:\n{wynikowe_opisy['krotki_opis']}")
        print(f"\nDŁUGI OPIS:\n{wynikowe_opisy['dlugi_opis']}")