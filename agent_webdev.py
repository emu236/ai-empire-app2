# agent_webdev.py - Generuje Landing Page (HTML/CSS/Copy)

from openai import OpenAI
import logging

def generuj_landing_page(tytul: str, usp: str, grupa_docelowa: str, rozdzialy: list, klucz_api: str) -> str:
    client = OpenAI(api_key=klucz_api)
    
    rozdzialy_str = "\n".join([f"- {r}" for r in rozdzialy[:5]]) # Bierzemy pierwsze 5 dla przykładu

    prompt = f"""
    Jesteś ekspertem od Marketingu i Web Developmentu. 
    Twoim zadaniem jest napisać KOMPLETNY kod HTML nowoczesnego Landing Page'a sprzedającego e-booka.

    INFORMACJE O PRODUKCIE:
    - Tytuł: "{tytul}"
    - Główna obietnica (USP): "{usp}"
    - Dla kogo: "{grupa_docelowa}"
    - Czego się nauczą (spis treści):
    {rozdzialy_str}

    WYMAGANIA TECHNICZNE:
    1. Użyj frameworka **Tailwind CSS** (załaduj go przez CDN: <script src="https://cdn.tailwindcss.com"></script>).
    2. Strona musi być piękna, nowoczesna, responsywna (mobile-friendly).
    3. Musi być to JEDEN plik HTML (CSS i JS wewnątrz).
    4. Użyj placeholderów na obrazki (np. https://placehold.co/600x400?text=Ebook+Cover).
    
    STRUKTURA STRONY (Sekcje):
    1. **Hero Section**: Nagłówek, podtytuł, przycisk "Kup teraz" (niech prowadzi do #buy), miejsce na okładkę.
    2. **Problem/Rozwiązanie**: Dlaczego ten e-book jest potrzebny? (Napisz perswazyjny tekst marketingowy).
    3. **Czego się nauczysz**: Lista korzyści (wykorzystaj przesłane rozdziały).
    4. **O autorze**: Krótka notka (zmyślona, profesjonalna).
    5. **CTA (Call to Action)**: Sekcja końcowa z ceną (wymyśl atrakcyjną cenę) i przyciskiem.
    6. **Stopka**: Copyright 2025.

    Zwróć TYLKO czysty kod HTML, bez bloków ```html ```. Kod ma być gotowy do zapisania jako index.html.
    """
    
    logging.info(f"  [WebDev] Projektuję stronę dla: {tytul}...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jesteś Senior Frontend Developerem i Copywriterem."},
                {"role": "user", "content": prompt}
            ]
        )
        # Czyścimy ewentualne znaczniki markdown, jeśli GPT je doda
        kod = response.choices[0].message.content.strip()
        if kod.startswith("```html"):
            kod = kod.replace("```html", "").replace("```", "")
        return kod

    except Exception as e:
        logging.error(f"  [WebDev] Błąd: {e}")
        return f""