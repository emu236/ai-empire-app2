# agent_analityk_v2.py
# UWAGA: Ten plik zawiera logikę Architekta (generowanie prospektu), 
# ale działa technicznie jako Analityk zwracający słownik.

from openai import OpenAI
from typing import Optional
import json
import logging

# Konfiguracja loggera, jeśli potrzebna
logging.basicConfig(level=logging.INFO)

def uruchom_agenta_analityka(temat_produktu: str, klucz_api: str) -> dict | None:
    """
    Funkcja generuje dane (w tym przypadku Prospekt) i zwraca je jako SŁOWNIK (DICT),
    aby main.py mógł iterować po .items().
    """
    client = OpenAI(api_key=klucz_api)

    # Prompt (z Twojego kodu)
    prompt_architektury = f"""
    Jesteś doświadczonym Architektem Produktów Cyfrowych. Twoim zadaniem jest stworzenie kompleksowego Prospektu dla e-booka na temat: "{temat_produktu}". 
    
    Prospekt musi być w formacie JSON i zawierać następujące klucze:
    1. 'Tytul': Sugestywny i chwytliwy tytuł e-booka.
    2. 'Kluczowa_Obietnica_USP': Unikalna Propozycja Sprzedaży (1-2 zdania).
    3. 'Segment_Docelowy': Kim jest idealny klient (3-4 konkretne grupy osób).
    4. 'Cel_Ebooka': Co czytelnik osiągnie po przeczytaniu (3-5 palących problemów i ich rozwiązanie).
    5. 'Spis_Tresci': Lista modułów/rozdziałów (co najmniej 7, maksimum 9) w formacie: Moduł [Numer]: [Nazwa Modułu].
    6. 'Bonusy': Lista dwóch wartościowych bonusów do e-booka.

    Nie dodawaj żadnego dodatkowego tekstu ani wyjaśnień poza czystym obiektem JSON.
    """
    
    print(f"  [Agent Analityk/Architekt] Generuję dane JSON dla tematu: '{temat_produktu}'...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jesteś Architektem Produktów. Zawsze zwracaj czysty, poprawny obiekt JSON."},
                {"role": "user", "content": prompt_architektury}
            ],
            # WYMUSZENIE FORMATU JSON
            response_format={"type": "json_object"}
        )
        
        # 1. Otrzymujemy wynik jako STRING (napis)
        wynik_tekstowy = response.choices[0].message.content
        print("  [Agent Analityk] Otrzymano odpowiedź JSON. Przetwarzanie na słownik...")

        # 2. KRYTYCZNA POPRAWKA: Konwersja STRING -> DICT
        try:
            wynik_slownik = json.loads(wynik_tekstowy)
            # Zwracamy słownik, dzięki czemu w main.py zadziała .items()
            return wynik_slownik
        except json.JSONDecodeError as e:
            print(f"  [Agent Analityk] BŁĄD parsowania JSON: {e}")
            return None

    except Exception as e:
        print(f"  [Agent Analityk] Wystąpił błąd API: {e}")
        return None