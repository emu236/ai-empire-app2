# agent_scenarzysta_podcast.py - Pisze dialogi

from openai import OpenAI
import json
import logging

def napisz_scenariusz(temat: str, klucz_api: str) -> list:
    client = OpenAI(api_key=klucz_api)
    
    prompt = f"""
    Jesteś producentem radiowym. Napisz krótki, dynamiczny scenariusz podcastu na temat: "{temat}".
    
    Postacie:
    1. PROWADZĄCY (Host): Entuzjastyczny, zadaje pytania, wita słuchaczy.
    2. EKSPERT (Guest): Rzeczowy, mądry, tłumaczy zagadnienia.
    
    Wymagania:
    - Dialog ma trwać ok. 1-2 minuty (ok. 6-8 wymian zdań).
    - Rozmowa ma być naturalna (trochę luzu, nie czytanie z kartki).
    - Zwróć TYLKO czysty JSON w formacie listy obiektów:
    [
        {{"rola": "PROWADZĄCY", "tekst": "Cześć wszystkim! Dziś gadamy o..."}},
        {{"rola": "EKSPERT", "tekst": "Dzień dobry, to fascynujący temat..."}}
    ]
    """
    
    print(f"  [Scenarzysta] Piszę scenariusz o: {temat}...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a podcast scriptwriter. Output JSON only."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        
        # Obsługa różnych struktur JSON jakie może zwrócić GPT
        if "dialog" in data: return data["dialog"]
        if "scenariusz" in data: return data["scenariusz"]
        if isinstance(data, list): return data
        # Jeśli zwrócił słownik z inną nazwą klucza, bierzemy pierwszą wartość będącą listą
        for key, val in data.items():
            if isinstance(val, list): return val
            
        return []

    except Exception as e:
        print(f"  [Scenarzysta] Błąd: {e}")
        return []