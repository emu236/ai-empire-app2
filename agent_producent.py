# agent_producent.py - Generuje Wideo z Obrazka (Wersja Diagnostyczna)

import replicate
import os
import requests
import time

def uruchom_producenta(sciezka_obrazu: str, klucz_replicate: str, sciezka_projektu: str) -> tuple[str, str]:
    """
    Zwraca krotkę: (sciezka_do_pliku, blad).
    Jeśli sukces: (sciezka, None).
    Jeśli błąd: (None, tresc_bledu).
    """
    # Ustawiamy klucz środowiskowy
    os.environ["REPLICATE_API_TOKEN"] = klucz_replicate.strip() # strip usuwa spacje
    
    print(f"  [Producent] Rozpoczynam renderowanie wideo z: {os.path.basename(sciezka_obrazu)}...")

    try:
        # Weryfikacja czy plik istnieje
        if not os.path.exists(sciezka_obrazu):
            return None, f"Nie znaleziono pliku obrazu: {sciezka_obrazu}"

        # Używamy modelu Stable Video Diffusion (SVD)
        output = replicate.run(
            "stability-ai/stable-video-diffusion:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "cond_aug": 0.02,
                "decoding_t": 7,
                "input_image": open(sciezka_obrazu, "rb"),
                "video_length": "25_frames_with_svd_xt",
                "sizing_strategy": "maintain_aspect_ratio",
                "motion_bucket_id": 127,
                "frames_per_second": 24
            }
        )
        
        video_url = output
        print(f"  [Producent] Wideo wygenerowane: {video_url}")
        
        video_data = requests.get(video_url).content
        nazwa_wideo = f"wideo_{os.urandom(3).hex()}.mp4"
        pelna_sciezka = os.path.join(sciezka_projektu, nazwa_wideo)
        
        with open(pelna_sciezka, "wb") as f:
            f.write(video_data)
            
        return pelna_sciezka, None

    except Exception as e:
        # Zwracamy pełną treść błędu
        print(f"  [Producent] Błąd renderowania: {e}")
        return None, str(e)