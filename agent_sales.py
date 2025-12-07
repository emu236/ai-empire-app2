# agent_sales.py - Analiza klientów i pisanie maili sprzedażowych

import requests
from openai import OpenAI

def analizuj_strone_klienta(url: str) -> str:
    """
    Pobiera treść strony klienta i zamienia ją na czysty tekst (Markdown)
    używając serwisu r.jina.ai (świetne dla AI).
    """
    if not url.startswith("http"):
        url = "https://" + url
        
    print(f"  [Sales] Analizuję stronę: {url}...")
    
    try:
        # Używamy Jina Reader do wyciągnięcia samej "mięsistej" treści
        jina_url = f"https://r.jina.ai/{url}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(jina_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.text[:10000] # Limitujemy do 10k znaków dla bezpieczeństwa
        else:
            return f"Nie udało się pobrać strony (Status: {response.status_code})."
            
    except Exception as e:
        return f"Błąd pobierania: {e}"

def generuj_cold_email(tresc_strony_klienta: str, twoja_oferta: str, cel_maila: str, klucz_api: str) -> str:
    client = OpenAI(api_key=klucz_api)
    
    prompt = f"""
    Jesteś światowej klasy ekspertem od sprzedaży B2B i Cold Emailingu.
    Twóim zadaniem jest napisać skuteczny, krótki i spersonalizowany e-mail do potencjalnego klienta.

    --- DANE O KLIENCIE (Ze strony www) ---
    {tresc_strony_klienta[:3000]}... (skrócone)
    
    --- MOJA OFERTA (Co sprzedaję) ---
    {twoja_oferta}
    
    --- CEL MAILA ---
    {cel_maila} (np. umówienie rozmowy, sprzedaż e-booka)

    ZASADY:
    1. Zacznij od "Icebreakera" - nawiąż do czegoś konkretnego, co znalazłeś na ich stronie (np. gratulacje za projekt X, wzmianka o ich misji). To musi wyglądać, jakby pisał to człowiek, który zrobił research.
    2. Nie bądź nachalny. Bądź pomocny.
    3. Krótko i na temat (maks 150 słów).
    4. Zakończ jasnym Call to Action (CTA).
    5. Styl: Profesjonalny, ale luźny (Business Casual).

    Wygeneruj samą treść maila (z tematem).
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Błąd AI: {e}"