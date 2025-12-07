# Krok 1: Zaimportowanie potrzebnych bibliotek
import os
from openai import OpenAI
# UWAGA: Nie importujemy już pytrends, bo go nie używamy w tej wersji

# --- KONFIGURACJA ---
# Wklej tutaj swój klucz API od OpenAI!
OPENAI_API_KEY = "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" 
# --------------------

# Krok 2: Inicjalizacja klienta OpenAI
if not OPENAI_API_KEY.startswith("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"):
    print("BŁĄD: Nie wkleiłeś swojego klucza API OpenAI. Otwórz plik i wklej go.")
else:
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Krok 3: Zdefiniowanie listy trendów do analizy
    # Zamiast pobierać dane z zepsutej funkcji, podajemy je sami!
    print("Przygotowuję listę tematów do analizy...")
    top_trends = [
        "AI w marketingu",
        "praca zdalna",
        "inwestowanie w nieruchomości",
        "kursy online",
        "zdrowy styl życia"
    ]

    print(f"Wybrane tematy: {', '.join(top_trends)}")
    print("-" * 30)

    # Krok 4: Pętla przez każdy trend i pytanie AI o pomysły
    for trend in top_trends:
        print(f"Analizuję temat: '{trend}'...")

        # Przygotowujemy zapytanie (prompt) do AI
        prompt = f"""
        Jesteś ekspertem od tworzenia produktów cyfrowych. 
        W Polsce obserwuje się stałe zainteresowanie tematem: "{trend}".

        Podaj 2 konkretne i kreatywne pomysły na produkty cyfrowe (np. e-book, kurs online, webinar, szablon), które można stworzyć w oparciu o ten temat. 
        Dla każdego pomysłu krótko uzasadnij, dlaczego ma potencjał.

        Format odpowiedzi:
        Pomysł 1: [Nazwa pomysłu]
        Uzasadnienie: [Krótkie uzasadnienie]

        Pomysł 2: [Nazwa pomysłu]
        Uzasadnienie: [Krótkie uzasadnienie]
        """

        # Wysyłamy zapytanie do OpenAI
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Jesteś pomocnym asystentem biznesowym."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Wyświetlamy odpowiedź od AI
            ai_response = response.choices[0].message.content
            print(ai_response)
            print("-" * 30)

        except Exception as e:
            print(f"Wystąpił błąd podczas komunikacji z OpenAI: {e}")