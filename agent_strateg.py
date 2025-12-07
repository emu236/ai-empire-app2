# Agent 0: Strateg Rynkowy (v1.0)

import os
import logging
import ast # Do bezpiecznego parsowania listy z AI
from openai import OpenAI
from dotenv import load_dotenv

# Importujemy naszego zaktualizowanego researchera
from agent_researcher import uruchom_researchera

# Konfiguracja
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ustawiamy loggera
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def uruchom_agenta_stratega(klucz_api: str) -> list[str]:
    """
    Analizuje ogólne trendy rynkowe i zwraca listę 10 najlepszych kategorii.
    """
    logging.info("[Agent Strateg] Uruchamiam... Będę szukał Top 10 kategorii.")
    
    # 1. Definiujemy ogólne zapytania do researchu
    zapytania_badawcze = [
        "najbardziej dochodowe kategorie e-booków 2025",
        "popularne tematy kursów online samorozwój",
        "trending topics online business 2025",
        "najlepsze nisze dla produktów cyfrowych zdrowie i fitness"
    ]
    
    # 2. Zbieramy notatki
    zebrane_notatki = ""
    logging.info("[Agent Strateg] Rozpoczynam zbieranie danych rynkowych...")
    for zapytanie in zapytania_badawcze:
        notatki = uruchom_researchera(zapytanie)
        zebrane_notatki += f"--- Notatki dla zapytania: '{zapytanie}' ---\n{notatki}\n\n"
    
    logging.info("[Agent Strateg] Dane zebrane. Uruchamiam analizę AI...")
    
    # 3. Tworzymy prompt dla "Mózgu" Stratega (GPT-4o)
    mega_prompt_stratega = f"""
    Jesteś światowej klasy analitykiem trendów rynkowych i strategiem biznesowym. Przeanalizowałem internet pod kątem popularnych tematów i nisz.
    Twoim zadaniem jest przeanalizowanie poniższych notatek i zidentyfikowanie 10 najbardziej obiecujących, SZEROKICH kategorii tematycznych, na które jest obecnie największy popyt na produkty cyfrowe (e-booki, kursy).

    Nie interesują mnie wąskie nisze (np. "trening psa rasy husky"), ale szerokie, główne kategorie (np. "Trening Zwierząt", "Finanse Osobiste", "Marketing Cyfrowy").

    --- ZEBRANE NOTATKI Z RESEARCHU ---
    {zebrane_notatki}
    --- KONIEC NOTATEK ---

    Przeanalizuj powyższe dane i zwróć TYLKO I WYŁĄCZNIE listę 10 najlepszych kategorii.
    Użyj wymaganego formatu: lista Pythona, np. ['Kategoria 1', 'Kategoria 2', 'Kategoria 3', ...]
    """
    
    # 4. Wywołujemy AI
    try:
        client = OpenAI(api_key=klucz_api)
        response = client.chat.completions.create(
            model="gpt-4o", # Używamy najmądrzejszego modelu do tej analizy
            messages=[{"role": "user", "content": mega_prompt_stratega}]
        )
        odpowiedz_ai = response.choices[0].message.content.strip()
        
        logging.info(f"[Agent Strateg] AI zwróciło surową listę: {odpowiedz_ai}")
        
        # 5. Bezpieczne parsowanie listy
        # Używamy ast.literal_eval, aby bezpiecznie zamienić string "['a', 'b']" na listę Pythona
        lista_kategorii = ast.literal_eval(odpowiedz_ai)
        
        if isinstance(lista_kategorii, list) and len(lista_kategorii) > 0:
            logging.info(f"[Agent Strateg] Pomyślnie sparsowano {len(lista_kategorii)} kategorii.")
            return lista_kategorii
        else:
            raise ValueError("AI nie zwróciło poprawnej listy.")
            
    except Exception as e:
        logging.error(f"[Agent Strateg] Nie udało się stworzyć listy kategorii: {e}")
        # Zwracamy listę awaryjną
        return [
            "Finanse Osobiste", "Marketing w Mediach Społecznościowych", "Zdrowie i Fitness",
            "Rozwój Osobisty", "Produktywność i Zarządzanie Czasem", "Programowanie dla Początkujących",
            "Sztuczna Inteligencja w Biznesie", "Inwestowanie w Nieruchomości", "Copywriting i Content Marketing",
            "Psychologia i Relacje"
        ]

# --- BLOK TESTOWY ---
if __name__ == '__main__':
    if not OPENAI_API_KEY:
        print("BŁĄD: Nie znaleziono klucza OPENAI_API_KEY w pliku .env")
    else:
        print("--- TEST AGENTA STRATEGA v1.0 ---")
        top_10_kategorii = uruchom_agenta_stratega(OPENAI_API_KEY)
        print("\n--- OSTATECZNA LISTA TOP 10 KATEGORII ---")
        print(top_10_kategorii)