# Agent: Kreator Artykułów SEO v2.1 (wersja modułowa)

from openai import OpenAI
import os
import re
import logging

def wygeneruj_tytuly_artykulow(temat_glowny: str, liczba: int, klucz_api: str) -> list:
    """Etap 1: Generuje listę tytułów artykułów SEO."""
    logging.info(f"  [Kreator SEO] Etap 1: Generuję {liczba} pomysłów na tytuły artykułów o '{temat_glowny}'...")
    client = OpenAI(api_key=klucz_api)
    
    prompt = f"""
    Jesteś strategiem SEO i content marketingu. Twoim zadaniem jest stworzenie listy {liczba} angażujących i zoptymalizowanych pod SEO tytułów artykułów blogowych na główny temat: "{temat_glowny}".
    Tytuły powinny być w formie pytań, poradników "jak to zrobić" lub list (np. "5 sposobów na...").
    Zwróć odpowiedź jako listę numerowaną.
    """
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        tytuly_tekst = response.choices[0].message.content
        tytuly_lista = [re.sub(r'^\d+\.\s*', '', linia).strip() for linia in tytuly_tekst.split('\n') if linia.strip()]
        logging.info("  [Kreator SEO] Lista tytułów została wygenerowana.")
        return tytuly_lista
    except Exception as e:
        logging.error(f"  [Kreator SEO] Błąd podczas generowania tytułów: {e}")
        return []

def napisz_artykul(tytul: str, dlugosc: int, klucz_api: str) -> str:
    """Etap 2: Pisze treść artykułu na podstawie tytułu."""
    logging.info(f"    - Piszę artykuł: '{tytul}'...")
    client = OpenAI(api_key=klucz_api)
    prompt = f"""
    Jesteś ekspertem SEO i copywriterem. Napisz wysokiej jakości, merytoryczny artykuł blogowy o długości około {dlugosc} słów na podstawie tytułu: "{tytul}".
    Artykuł musi być dobrze ustrukturyzowany, używając nagłówków (H2, H3) i list.
    """
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"    - Błąd podczas pisania artykułu '{tytul}': {e}")
        return None