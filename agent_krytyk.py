# Agent 7: Krytyk / Walidator Treści (WERSJA Z WYMUSZONYM JSON)

from openai import OpenAI
from typing import Optional
import json

MODEL_LLM = "gpt-4o" 

def uruchom_agenta_krytyka(prospekt: str, tytul_rozdzialu: str, tresc_do_oceny: str, klucz_api: str) -> str:
    """
    Agent, który ocenia jakość treści rozdziału na podstawie prospektu.
    Zwraca szczegółowy feedback i decyzję (AKCEPTACJA/KOREKTA) w formacie JSON.
    """
    client = OpenAI(api_key=klucz_api)

    system_prompt = f"""
    Jesteś agentem Krytykiem i ekspertem ds. jakości treści, specjalizującym się w produktach cyfrowych (e-bookach). Twoim jedynym zadaniem jest ocena dostarczonego rozdziału na podstawie jego zgodności z Prospektem i obietnicami marketingowymi.

    Zawsze postępuj zgodnie z tymi zasadami:
    1. Oceń, czy treść rozdziału faktycznie dostarcza wartość obiecaną w tytule rozdziału i jest zgodna z Prospektem.
    2. Sprawdź, czy język jest spójny, profesjonalny i bez błędów.
    3. Sprawdź, czy treść jest wystarczająco głęboka.
    4. Na koniec, musisz podjąć JEDNĄ DECYZJĘ: AKCEPTACJA lub KOREKTA.

    Zwróć odpowiedź w formacie JSON, który musi zawierać dwa klucze:
    1. 'decyzja': Wartość MUSI być albo "AKCEPTACJA" albo "KOREKTA".
    2. 'feedback_pisarz': Szczegółowy i konstruktywny feedback dla Agenta Pisarza. Jeśli decyzja to "AKCEPTACJA", wpisz "Treść spełnia standardy i jest gotowa do publikacji."

    Nie dodawaj żadnego innego tekstu poza czystym obiektem JSON.
    """

    user_prompt = f"""
    --- PROSPEKT PROJEKTU ---
    {prospekt}
    ---
    
    --- ROZDZIAŁ DO OCENY ---
    Tytuł Rozdziału: {tytul_rozdzialu}
    Treść: 
    {tresc_do_oceny}
    ---

    Przeanalizuj treść i wydaj werdykt.
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_LLM,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            # KRYTYCZNA ZMIANA: WYMUSZENIE FORMATU JSON
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"BŁĄD w Agencie Krytyku: {e}")
        # W przypadku błędu API, zawsze wymuszamy KOREKTĘ
        return json.dumps({"decyzja": "KOREKTA", "feedback_pisarz": f"Błąd API/Systemu Krytyka: {e}. Wymagana ponowna próba."})