# agent_trener.py - LOGIKA TRENINGOWA I DIETETYCZNA
from openai import OpenAI
from fpdf import FPDF
import os

def oblicz_kalorie(waga, wzrost, wiek, plec, aktywnosc, cel):
    """
    Oblicza BMR (Wzór Mifflina) i TDEE oraz makroskładniki.
    """
    # 1. BMR
    if plec == "Mężczyzna":
        bmr = (10 * waga) + (6.25 * wzrost) - (5 * wiek) + 5
    else:
        bmr = (10 * waga) + (6.25 * wzrost) - (5 * wiek) - 161
        
    # 2. TDEE (Całkowita przemiana)
    wspolczynniki = {
        "Siedzący (Biuro + brak treningu)": 1.2,
        "Lekki (1-3 treningi)": 1.375,
        "Średni (3-5 treningów)": 1.55,
        "Duży (6-7 treningów)": 1.725
    }
    tdee = bmr * wspolczynniki.get(aktywnosc, 1.2)
    
    # 3. Cel
    if cel == "Redukcja (Schudnij)":
        target_kcal = tdee - 400
    elif cel == "Masa (Buduj mięśnie)":
        target_kcal = tdee + 300
    else: # Rekompozycja
        target_kcal = tdee
        
    # 4. Makro (Białko 2g, Tłuszcz 0.8g, Reszta Węgle)
    bialko = 2.2 * waga # Wysokie białko
    tluszcz = 0.8 * waga
    kcal_z_bialka = bialko * 4
    kcal_z_tluszczu = tluszcz * 9
    
    pozostale_kcal = target_kcal - (kcal_z_bialka + kcal_z_tluszczu)
    wegle = pozostale_kcal / 4
    
    return {
        "BMR": round(bmr),
        "TDEE": round(tdee),
        "CEL_KCAL": round(target_kcal),
        "BIALKO": round(bialko),
        "TLUSZCZ": round(tluszcz),
        "WEGLE": round(wegle)
    }

def generuj_plan_treningowy(api_key, profil_user):
    """Generuje plan treningowy tekstowy przy użyciu GPT-4."""
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    Jesteś elitarnym trenerem personalnym (jak Goggins).
    Stwórz 4-tygodniowy plan treningowy dla klienta:
    
    DANE:
    - Płeć: {profil_user['plec']}
    - Waga: {profil_user['waga']} kg
    - Cel: {profil_user['cel']}
    - Sprzęt: {profil_user['sprzet']}
    - Poziom: {profil_user['poziom']}
    - Dni treningowe: {profil_user['dni']}
    
    WYMAGANY FORMAT (Markdown):
    1. Rozpisz konkretny plan na tydzień (Dzień 1, Dzień 2...).
    2. Podaj ćwiczenia, serie i powtórzenia.
    3. Dodaj progresję (co zmieniać w kolejnych tygodniach).
    4. Dodaj 5 żelaznych zasad żywieniowych pod ten cel.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def stworz_pdf_plan(tresc_planu, makro, filename):
    """Tworzy prosty PDF z planem."""
    pdf = FPDF()
    pdf.add_page()
    
    # Obsługa polskich znaków w FPDF jest trudna bez czcionek .ttf
    # Używamy standardowej czcionki i usuwamy polskie znaki dla bezpieczeństwa technicznego (MVP)
    # W wersji PRO trzeba by załadować czcionkę DejaVuSans.ttf
    
    def safe_text(text):
        replacements = {
            'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
            'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        return text.encode('latin-1', 'replace').decode('latin-1')

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "TWOJ PLAN TRANSFORMACJI - AI EMPIRE", 0, 1, 'C')
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Cel Kalorie: {makro['CEL_KCAL']} kcal", 0, 1)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Bialko: {makro['BIALKO']}g | Tluszcze: {makro['TLUSZCZ']}g | Wegle: {makro['WEGLE']}g", 0, 1)
    
    pdf.ln(10)
    pdf.set_font("Arial", '', 10)
    
    # Wrzucamy treść treningu (proste formatowanie)
    for line in tresc_planu.split('\n'):
        clean_line = safe_text(line)
        pdf.multi_cell(0, 6, clean_line)
        
    pdf.output(filename)
    return filename