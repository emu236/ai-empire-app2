# Agent 3: Specjalista Marketingu (Multi-Lang v2.0)

from openai import OpenAI
from typing import Tuple, Optional
import logging
import re

# Dodano argument: jezyk_docelowy
def uruchom_agenta_marketera(prospekt_produktu: str, klucz_api: str, jezyk_docelowy: str = "Polski") -> Optional[Tuple[str, str]]:
    logging.info(f"  [Agent 3] Generuję marketing ({jezyk_docelowy})...")
    client = OpenAI(api_key=klucz_api)
    
    instrukcja_jezykowa = f"Opisy mają być w języku: {jezyk_docelowy}."
    if jezyk_docelowy != "Polski":
        instrukcja_jezykowa += " Dodaj również polskie tłumaczenie poniżej każdego opisu."

    prompt_marketingowy = f"""
    Jesteś copywriterem. Stwórz dwa opisy dla e-booka na podstawie prospektu.
    {instrukcja_jezykowa}

    --- ZADANIE ---
    1. OPIS KRÓTKI (Social Media): Max 3 zdania. Chwytliwy.
    2. OPIS DŁUGI (Landing Page): Korzyści, bullet points.

    --- PROSPEKT ---
    {prospekt_produktu}

    Formatuj odpowiedź używając znaczników:
    [OPIS_KROTKI_START]...[OPIS_KROTKI_END]
    [OPIS_DLUGI_START]...[OPIS_DLUGI_END]
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jesteś copywriterem. Używaj wymaganych znaczników."},
                {"role": "user", "content": prompt_marketingowy}
            ]
        )
        wynik = response.choices[0].message.content
        
        opis_krotki_match = re.search(r"\[OPIS_KROTKI_START\](.*?)\[OPIS_KROTKI_END\]", wynik, re.DOTALL)
        opis_dlugi_match = re.search(r"\[OPIS_DLUGI_START\](.*?)\[OPIS_DLUGI_END\]", wynik, re.DOTALL)

        opis_krotki = opis_krotki_match.group(1).strip() if opis_krotki_match else "Błąd generowania."
        opis_dlugi = opis_dlugi_match.group(1).strip() if opis_dlugi_match else "Błąd generowania."
        
        return opis_krotki, opis_dlugi
        
    except Exception as e:
        logging.error(f"  [Agent 3] Błąd: {e}")
        return None