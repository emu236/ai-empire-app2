# Agent 7: Producent Wideo
# Cel: Tworzenie kompletnego zestawu do produkcji shorta (scenariusz, audio, grafiki).

from openai import OpenAI
import requests
import re
import os

def uruchom_producenta_wideo(prospekt_produktu: str, materialy_marketingowe: str, klucz_api: str):
    """
    Generuje kompletny zestaw do produkcji wideo: scenariusz, plik audio i grafiki do scen.
    """
    client = OpenAI(api_key=klucz_api)
    
    # === ETAP 1: GENEROWANIE SCENARIUSZA ===
    print("  [Producent Wideo] Etap 1: Generuję scenariusz...")
    prompt_scenariusza = f"""
    Jesteś scenarzystą specjalizującym się w krótkich, wiralowych formach wideo (TikTok, YouTube Shorts).
    Na podstawie poniższych materiałów stwórz scenariusz na dynamicznego, 30-sekundowego shorta reklamującego e-book.

    --- MATERIAŁY ŹRÓDŁOWE ---
    {prospekt_produktu}
    {materialy_marketingowe}
    --- KONIEC MATERIAŁÓW ---

    Scenariusz musi być podzielony na 4 sceny. Każdą scenę opisz w formacie:
    SCENA [Numer]:
    TEKST LEKTORA: [Tekst, który ma być przeczytany]
    OPIS WIZUALNY: [Opis grafiki, która ma się pojawić, np. "minimalistyczna ikona mózgu z żarówką"]
    """
    
    try:
        response_scenariusz = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_scenariusza}]
        )
        scenariusz = response_scenariusz.choices[0].message.content
        print("  [Producent Wideo] Scenariusz został wygenerowany.")
        with open("wynik_scenariusz.txt", "w", encoding="utf-8") as f:
            f.write(scenariusz)
            print("  [Producent Wideo] Scenariusz zapisany do pliku 'wynik_scenariusz.txt'")
    except Exception as e:
        print(f"  [Producent Wideo] BŁĄD podczas generowania scenariusza: {e}")
        return

    # === ETAP 2: GENEROWANIE AUDIO (VOICEOVER) ===
    print("\n  [Producent Wideo] Etap 2: Generuję głos lektora...")
    tekst_lektora = " ".join(re.findall(r"TEKST LEKTORA: (.*?)\n", scenariusz, re.DOTALL))
    
    try:
        response_audio = client.audio.speech.create(
            model="tts-1",
            voice="onyx", # Możesz eksperymentować z innymi głosami: "alloy", "echo", "fable", "nova", "shimmer"
            input=tekst_lektora,
        )
        response_audio.stream_to_file("wynik_lektor.mp3")
        print("  [Producent Wideo] Głos lektora został zapisany do pliku 'wynik_lektor.mp3'")
    except Exception as e:
        print(f"  [Producent Wideo] BŁĄD podczas generowania audio: {e}")
        return

    # === ETAP 3: GENEROWANIE GRAFIK DO SCEN ===
    print("\n  [Producent Wideo] Etap 3: Generuję grafiki do scen...")
    opisy_wizualne = re.findall(r"OPIS WIZUALNY: (.*?)\n", scenariusz, re.DOTALL)
    
    if not os.path.exists("grafiki_do_shorta"):
        os.makedirs("grafiki_do_shorta")

    for i, opis in enumerate(opisy_wizualne):
        numer_sceny = i + 1
        print(f"    - Generuję grafikę dla Sceny {numer_sceny}...")
        prompt_graficzny = f"""
        Stwórz minimalistyczną, nowoczesną i estetyczną grafikę w stylu flat design, idealną jako tło do filmu na social media. 
        Grafika ma ilustrować następującą koncepcję: "{opis}". 
        Użyj 2-3 dominujących kolorów, czyste linie. Bez tekstu. Format kwadratowy.
        """
        try:
            response_grafika = client.images.generate(
                model="dall-e-3",
                prompt=prompt_graficzny,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response_grafika.data[0].url
            image_data = requests.get(image_url).content
            nazwa_pliku = f"grafiki_do_shorta/scena_{numer_sceny}.png"
            with open(nazwa_pliku, "wb") as f:
                f.write(image_data)
            print(f"    - Grafika dla Sceny {numer_sceny} zapisana jako '{nazwa_pliku}'")
        except Exception as e:
            print(f"    - BŁĄD podczas generowania grafiki dla Sceny {numer_sceny}: {e}")
    
    print("\n--- PRODUCENT WIDEO: ZAKOŃCZONO ---")
    print("Twój 'Zestaw do Produkcji Wideo' jest gotowy!")