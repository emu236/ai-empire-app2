# Agent 8: Kreator Kursów Mailowych
# Cel: Tworzenie wielodniowych, automatycznych kursów mailowych na podstawie prospektu.

from openai import OpenAI
import os
import time

# --- KONFIGURACJA ---
OPENAI_API_KEY = "sk-TWOJ-KLUCZ-API-TUTAJ"
# Nazwa folderu projektu, z którego agent ma czytać prospekt
# UWAGA: Musisz go zaktualizować na nazwę folderu stworzonego przez main.py
NAZWA_FOLDERU_PROJEKTU = "2025-10-15_Pasywne_inwestowanie_w_ETF-y" # <--- ZMIEŃ NA WŁAŚCIWĄ NAZWĘ
LICZBA_DNI_KURSU = 7
# --------------------

def uruchom_kreatora_kursow(prospekt_produktu: str, klucz_api: str, folder_docelowy: str):
    """
    Generuje w pętli treść maili na każdy dzień kursu i zapisuje je do plików.
    """
    client = OpenAI(api_key=klucz_api)

    for dzien in range(1, LICZBA_DNI_KURSU + 1):
        print(f"\n  [Kreator Kursów] Piszę treść maila na Dzień {dzien}/{LICZBA_DNI_KURSU}...")
        
        # Specjalna instrukcja dla ostatniego dnia kursu, aby zawierał sprzedaż
        dodatkowa_instrukcja = ""
        if dzien == LICZBA_DNI_KURSU:
            dodatkowa_instrukcja = "To jest ostatni mail kursu. Na końcu dodaj mocne wezwanie do działania (CTA) i zachętę do zakupu pełnego e-booka, którego dotyczy prospekt. Przedstaw go jako naturalny, kolejny krok dla osoby, która ukończyła ten darmowy kurs."

        prompt_mailowy = f"""
        Jesteś ekspertem od email marketingu i tworzenia angażujących kursów.
        Twoim zadaniem jest napisać treść maila na DZIEŃ {dzien} z {LICZBA_DNI_KURSU}-dniowego, darmowego kursu mailowego.
        Kurs dotyczy tematu opisanego w poniższym prospekcie.

        --- PROSPEKT PRODUKTU ---
        {prospekt_produktu}
        --- KONIEC PROSPEKTU ---

        Napisz treść maila, który ma około 300-400 słów. Mail powinien:
        1. Zaczynać się od chwytliwego tematu (np. "Temat: [Twój temat]").
        2. Być napisany w przyjaznym, bezpośrednim tonie.
        3. Dostarczać realną, wartościową wiedzę związaną z tematem na dany dzień.
        4. Kończyć się krótkim "haczykiem" i zapowiedzią tego, czego odbiorca dowie się w mailu następnego dnia.
        
        {dodatkowa_instrukcja}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Jesteś ekspertem od email marketingu."},
                    {"role": "user", "content": prompt_mailowy}
                ]
            )
            tresc_maila = response.choices[0].message.content
            
            # Zapisujemy maila do pliku
            nazwa_pliku = f"dzien_{dzien}.txt"
            sciezka_pliku = os.path.join(folder_docelowy, nazwa_pliku)
            with open(sciezka_pliku, "w", encoding="utf-8") as f:
                f.write(tresc_maila)
            print(f"  [Kreator Kursów] Mail na Dzień {dzien} został zapisany w pliku '{sciezka_pliku}'")
            
            # Pauza, aby nie przeciążać API
            time.sleep(5)

        except Exception as e:
            print(f"  [Kreator Kursów] Wystąpił błąd podczas pisania maila na Dzień {dzien}: {e}")
            break # Przerywamy pętlę w razie błędu

if __name__ == '__main__':
    if not OPENAI_API_KEY.startswith("sk-"):
        print("BŁĄD: Wklej swój klucz API OpenAI w pliku agent_kurs_mailowy.py!")
    else:
        # Tworzymy folder na wyniki, jeśli nie istnieje
        folder_wynikowy = os.path.join(NAZWA_FOLDERU_PROJEKTU, "kurs_mailowy")
        os.makedirs(folder_wynikowy, exist_ok=True)
        
        # Wczytujemy prospekt z pliku
        try:
            sciezka_prospektu = os.path.join(NAZWA_FOLDERU_PROJEKTU, "prospekt.txt")
            with open(sciezka_prospektu, "r", encoding="utf-8") as f:
                prospekt_tekst = f.read()
            
            print("--- KREATOR KURSÓW MAILOWYCH: START ---")
            uruchom_kreatora_kursow(prospekt_tekst, OPENAI_API_KEY, folder_wynikowy)
            print("\n--- KREATOR KURSÓW MAILOWYCH: ZAKOŃCZONO ---")

        except FileNotFoundError:
            print(f"BŁĄD: Nie znaleziono pliku 'prospekt.txt' w folderze '{NAZWA_FOLDERU_PROJEKTU}'.")
            print("Najpierw uruchom 'main.py', aby wygenerować prospekt.")