# agent_influencer_foto.py - Generuje zdjęcia Influencera (FLUX)

import replicate
import os
import requests
import time

def generuj_zdjecie_influencera(wyglad_postaci: str, sytuacja: str, klucz_replicate: str, sciezka_projektu: str) -> str:
    """
    Łączy opis stały postaci z nową sytuacją i generuje foto przez FLUX.1-schnell.
    """
    os.environ["REPLICATE_API_TOKEN"] = klucz_replicate.strip()
    
    # Prompt łączący postać z sytuacją
    # FLUX lubi proste, opisowe prompty
    prompt = f"""
    A photorealistic instagram photo of {wyglad_postaci}. 
    Scene: {sytuacja}. 
    Style: High quality, 4k, dslr, raw candid photo, influencer aesthetics, natural lighting.
    """
    
    print(f"  [Foto] Generuję: {sytuacja}...")

    try:
        # Używamy modelu FLUX.1-schnell (jest super szybki i tani)
        output = replicate.run(
            "black-forest-labs/flux-1-schnell",
            input={
                "prompt": prompt,
                "aspect_ratio": "4:5", # Format Instagrama
                "output_format": "jpg",
                "output_quality": 90
            }
        )
        
        # Replicate zwraca listę URLi (zazwyczaj jeden)
        image_url = output[0]
        
        # Pobieranie
        img_data = requests.get(image_url).content
        nazwa_pliku = f"influ_{os.urandom(3).hex()}.jpg"
        pelna_sciezka = os.path.join(sciezka_projektu, nazwa_pliku)
        
        with open(pelna_sciezka, "wb") as f:
            f.write(img_data)
            
        return pelna_sciezka

    except Exception as e:
        print(f"  [Foto] Błąd: {e}")
        return None