# Agent: Kreator Szablonów v2.0 (z autonomiczną burzą mózgów)

from openai import OpenAI
import os
import time
import re

# --- KONFIGURACJA ---
OPENAI_API_KEY = "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"
NAZWA_FOLDERU_PROJEKTU = "2025-10-15_produktywność" # <--- ZMIEŃ NA WŁAŚCIWĄ NAZWĘ
# --------------------

def wygeneruj_pomysly_na_szablony(prospekt_produktu: str, klucz_api: str) -> list:
    """Etap 1: Generuje listę 10 pomysłów na paczki szablonów."""
    print("  [Kreator Szablonów] Etap 1: Rozpoczynam burzę mózgów na 10 typów szablonów...")
    client = OpenAI(api_key=klucz_api)
    
    prompt_pomyslow = f"""
    Jesteś ekspertem od tworzenia produktów cyfrowych. Przeanalizuj poniższy prospekt e-booka.

    --- PROSPEKT ---
    {prospekt_produktu}
    --- KONIEC PROSPEKTU ---

    Twoim zadaniem jest wymyślenie 10 różnych, konkretnych i wartościowych pomysłów na "paczki szablonów", które byłyby idealnym uzupełnieniem tego e-booka i byłyby przydatne dla jego grupy docelowej.

    Przykłady dla innego tematu mogłyby wyglądać tak:
    - 15 szablonów maili sprzedażowych
    - 30 pomysłów na posty na Instagram
    - 7 scenariuszy krótkich wideo na TikTok

    Zwróć odpowiedź jako listę numerowaną od 1 do 10. Każdy element listy to jeden pomysł. Nie dodawaj żadnych innych opisów.
    """
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt_pomyslow}])
        pomysly_tekst = response.choices[0].message.content
        # Dzielimy tekst na linie i usuwamy numerację, aby uzyskać czystą listę pomysłów
        pomysly_lista = [re.sub(r'^\d+\.\s*', '', linia).strip() for linia in pomysly_tekst.split('\n') if linia.strip()]
        print("  [Kreator Szablonów] Burza mózgów zakończona. Wygenerowano listę pomysłów.")
        return pomysly_lista
    except Exception as e:
        print(f"  [Kreator Szablonów] Błąd podczas burzy mózgów: {e}")
        return []

def stworz_paczke_szablonow(prospekt_produktu: str, opis_szablonu: str, klucz_api: str) -> str:
    """Etap 2: Generuje treść dla pojedynczej paczki szablonów."""
    print(f"    - Produkuję paczkę: '{opis_szablonu}'...")
    client = OpenAI(api_key=klucz_api)
    prompt_produkcyjny = f"""
    Jesteś światowej klasy ekspertem w dziedzinie, której dotyczy poniższy prospekt. 
    Twoim zadaniem jest stworzenie paczki szablonów na temat: "{opis_szablonu}".

    --- PROSPEKT (KONTEKST) ---
    {prospekt_produktu}
    --- KONIEC PROSPEKTU ---

    Wygeneruj kompletny zestaw szablonów zgodnie z opisem. Zachowaj przejrzystą strukturę, numerując każdy szablon.
    """
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt_produkcyjny}])
        return response.choices[0].message.content
    except Exception as e:
        print(f"    - Błąd podczas produkcji paczki '{opis_szablonu}': {e}")
        return None

if __name__ == '__main__':
    if not OPENAI_API_KEY.startswith("sk-"):
        print("BŁĄD: Wklej swój klucz API OpenAI do pliku agent_kreator_szablonow.py!")
    else:
        try:
            sciezka_prospektu = os.path.join(NAZWA_FOLDERU_PROJEKTU, "prospekt.txt")
            with open(sciezka_prospektu, "r", encoding="utf-8") as f:
                prospekt_tekst = f.read()
            
            print("--- KREATOR SZABLONÓW v2.0: START ---")
            
            # Etap 1: Burza mózgów
            lista_pomyslow = wygeneruj_pomysly_na_szablony(prospekt_tekst, OPENAI_API_KEY)

            if lista_pomyslow:
                # Tworzymy podfolder na wyniki
                folder_wynikowy = os.path.join(NAZWA_FOLDERU_PROJEKTU, "wynik_paczki_szablonow")
                os.makedirs(folder_wynikowy, exist_ok=True)
                print(f"\n  [Kreator Szablonów] Etap 2: Rozpoczynam produkcję {len(lista_pomyslow)} paczek szablonów...")

                # Etap 2: Pętla produkcyjna
                for i, pomysl in enumerate(lista_pomyslow):
                    tresc_paczki = stworz_paczke_szablonow(prospekt_tekst, pomysl, OPENAI_API_KEY)
                    if tresc_paczki:
                        bezpieczna_nazwa_pliku = re.sub(r'[\\/*?:"<>|]', "", pomysl).replace(" ", "_")[:50]
                        nazwa_pliku = f"{i+1:02d}_{bezpieczna_nazwa_pliku}.txt"
                        sciezka_pliku = os.path.join(folder_wynikowy, nazwa_pliku)
                        with open(sciezka_pliku, "w", encoding="utf-8") as f:
                            f.write(tresc_paczki)
                        print(f"    - Paczka szablonów zapisana jako '{nazwa_pliku}'")
                    time.sleep(5) # Pauza między generowaniem kolejnych paczek

            print("\n--- KREATOR SZABLONÓW: ZAKOŃCZONO ---")

        except FileNotFoundError:
            print(f"BŁĄD: Nie znaleziono pliku 'prospekt.txt' w folderze '{NAZWA_FOLDERU_PROJEKTU}'.")