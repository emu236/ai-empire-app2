# agent_lektor.py - Generuje Audio (OpenAI + ElevenLabs Fix)

from openai import OpenAI
from elevenlabs.client import ElevenLabs
import os
import logging

def generuj_podcast_audio(scenariusz: list, klucz_openai: str, sciezka_projektu: str, provider="openai", klucz_elevenlabs=None) -> str:
    """
    Generuje podcast używając wybranego dostawcy (openai/elevenlabs).
    """
    output_file = os.path.join(sciezka_projektu, "podcast_final.mp3")
    os.makedirs(sciezka_projektu, exist_ok=True)
    
    # Czyścimy stary plik jeśli istnieje
    if os.path.exists(output_file):
        os.remove(output_file)
        
    # Inicjalizacja klientów
    client_openai = OpenAI(api_key=klucz_openai)
    client_eleven = None
    if provider == "elevenlabs" and klucz_elevenlabs:
        client_eleven = ElevenLabs(api_key=klucz_elevenlabs)

    # Głosy
    # OpenAI: alloy, echo, fable, onyx, nova, shimmer
    # ElevenLabs: Przykładowe ID (Rachel i Drew)
    VOICES = {
        "openai": {"HOST": "onyx", "GUEST": "shimmer"},
        "elevenlabs": {
            "HOST": "21m00Tcm4TlvDq8ikWAM", # Rachel
            "GUEST": "29vD33N1CtxCmqQRPOHJ"  # Drew
        }
    }

    print(f"  [Lektor] Rozpoczynam nagrywanie ({provider})...")

    # Otwieramy plik do zapisu (tryb append binary)
    with open(output_file, "wb") as f_out:
        for i, linia in enumerate(scenariusz):
            rola = linia.get("rola", "HOST").upper()
            tekst = linia.get("tekst", "")
            if not tekst: continue
            
            # Wybór głosu
            role_key = "HOST" if "PROWADZĄCY" in rola or "HOST" in rola else "GUEST"
            voice_id = VOICES.get(provider, VOICES["openai"])[role_key]
            
            print(f"    Lektor czyta linię {i+1} jako {rola}...")

            try:
                if provider == "elevenlabs" and client_eleven:
                    # --- POPRAWKA TUTAJ ---
                    # Używamy client.text_to_speech.convert zamiast client.generate
                    audio_generator = client_eleven.text_to_speech.convert(
                        text=tekst,
                        voice_id=voice_id,
                        model_id="eleven_multilingual_v2"
                    )
                    for chunk in audio_generator:
                        f_out.write(chunk)
                        
                else:
                    # OpenAI Generation (Fallback lub domyślny)
                    response = client_openai.audio.speech.create(
                        model="tts-1",
                        voice=voice_id,
                        input=tekst
                    )
                    for chunk in response.iter_bytes():
                        f_out.write(chunk)
                        
            except Exception as e:
                print(f"    ❌ Błąd audio linii {i}: {e}")

    return output_file