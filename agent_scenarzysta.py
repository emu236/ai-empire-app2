# Agent: Scenarzysta Wideo
# Cel: Tworzenie paczek gotowych scenariuszy na krótkie formy wideo.

from openai import OpenAI
import os
import time
import re

# --- KONFIGURACJA ---
OPENAI_API_KEY = "sk-TWOJ-KLUCZ-API-TUTAJ"
NAZWA_FOLDERU_PROJEKTU = "2025-10-15_Pasywne_inwestowanie_w_ETF-y" # <--- ZMIEŃ NA WŁAŚCIWĄ NAZWĘ
LICZBA_SCENARIUSZY = 10
# --------------------

def uruchom_scenarzyste(prospekt_produktu: str, liczba: int, klucz_api: str, folder_docelowy: str):
    """
    Generuje paczkę scenariuszy wideo i zapisuje ją do pliku.
    """
    client = OpenAI(api_key=klucz_api)

    print(f"  [Scenarzysta] Rozpoczynam generowanie paczki {liczba} scenariuszy wideo...")
    
    prompt = f"""
    Jesteś światowej klasy scenarzystą specjalizującym się w wiralowych, krótkich filmach na TikTok, Instagram Reels i YouTube Shorts.
    Twoim zadaniem jest stworzenie paczki {liczba} scenariuszy wideo na podstawie poniższego prospektu.

    --- PROSPEKT (KONTEKST) ---
    {prospekt_produktu}
    --- KONIEC PROSPEKTU ---

    Każdy scenariusz musi być kompletny i gotowy do nagrania. Zastosuj DOKŁADNIE poniższą strukturę dla każdego scenariusza:

    --- Scenariusz [Numer] ---
    TYTUŁ: [Chwytliwy tytuł / pomysł na film]
    HAK (Pierwsze 3 sekundy): [Jedno, mocne zdanie, które przyciągnie uwagę widza]
    TREŚĆ (15-20 sekund): [W 3-4 krótkich punktach lub zdaniach przekaż główną wartość / poradę]
    WEZWANIE DO DZIAŁANIA (CTA): [Proste polecenie dla widza, np. "Skomentuj...", "Sprawdź link w bio..."]
    PROPOZYCJA WIZUALNA: [Krótki opis, co może pojawiać się na ekranie, np. "Mówca pokazuje wykres na telefonie", "Dynamiczne przebitki z podróży"]
    ---
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem od wiralowych scenariuszy wideo."},
                {"role": "user", "content": prompt}
            ]
        )
        tresc_scenariuszy = response.choices[0].message.content
        
        nazwa_pliku = "wynik_scenariusze_wideo.txt"
        sciezka_pliku = os.path.join(folder_docelowy, nazwa_pliku)
        with open(sciezka_pliku, "w", encoding="utf-8") as f:
            f.write(tresc_scenariuszy)
        print(f"  [Scenarzysta] Paczka scenariuszy została zapisana w pliku '{sciezka_pliku}'")

    except Exception as e:
        print(f"  [Scenarzysta] Wystąpił błąd: {e}")

if __name__ == '__main__':
    if not OPENAI_API_KEY.startswith("sk-"):
        print("BŁĄD: Wklej swój klucz API OpenAI do pliku agent_scenarzysta.py!")
    else:
        try:
            sciezka_prospektu = os.path.join(NAZWA_FOLDERU_PROJEKTU, "prospekt.txt")
            with open(sciezka_prospektu, "r", encoding="utf-8") as f:
                prospekt_tekst = f.read()
            
            print("--- KREATOR SCENARIUSZY WIDEO: START ---")
            uruchom_scenarzyste(prospekt_tekst, LICZBA_SCENARIUSZY, OPENAI_API_KEY, NAZWA_FOLDERU_PROJEKTU)
            print("\n--- KREATOR SCENARIUSZY WIDEO: ZAKOŃCZONO ---")

        except FileNotFoundError:
            print(f"BŁĄD: Nie znaleziono pliku 'prospekt.txt' w folderze '{NAZWA_FOLDERU_PROJEKTU}'.")