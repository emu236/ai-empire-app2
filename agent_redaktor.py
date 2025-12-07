# agent_redaktor.py - KONTROLA JAKOŚCI I KOREKTA
from openai import OpenAI

def uruchom_koretke_redaktorska(tekst_roboczy, temat_rozdzialu, api_key):
    """
    Analizuje tekst, usuwa lanie wody i podnosi jakość merytoryczną.
    """
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    Jesteś Surowym Redaktorem Naczelnym (Senior Editor) w wydawnictwie premium.
    Twoim zadaniem jest drastyczne podniesienie jakości poniższego tekstu.
    
    TEMAT ROZDZIAŁU: {temat_rozdzialu}
    
    TWOJE WYTYCZNE:
    1. **Zero Lania Wody:** Usuń wszystkie zdania, które nic nie wnoszą (np. "W dzisiejszych czasach...", "To bardzo ważne, aby..."). Przejdź do konkretów.
    2. **Zwiększ Wartość:** Jeśli tekst jest zbyt ogólny, doprecyzuj go, używając języka korzyści i faktów.
    3. **Styl:** Zmień styl na ekspercki, dynamiczny i bezpośredni. Unikaj stylu "robota".
    4. **Formatowanie:** Użyj pogrubień (**bold**) dla najważniejszych myśli. Stosuj listy punktowane tam, gdzie to ułatwia czytanie.
    5. **Zachowaj Strukturę:** Nie usuwaj nagłówków, ale popraw ich treść pod nimi.
    
    TEKST DO POPRAWY:
    {tekst_roboczy}
    
    Zwróć TYLKO poprawioną, gotową do druku wersję tekstu (Markdown).
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # Używamy najlepszego modelu do redakcji
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6 # Nieco niższa temperatura dla precyzji
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Błąd Redaktora: {e}")
        return None # W razie błędu zwrócimy None i użyjemy oryginału