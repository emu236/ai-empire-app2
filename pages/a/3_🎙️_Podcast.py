import streamlit as st
import os
import requests
from openai import OpenAI
from io import BytesIO

# --- Konfiguracja Strony ---
st.set_page_config(page_title="AI Podcast Studio", page_icon="🎙️", layout="wide")

st.title("🎙️ AI Podcast Studio")
st.markdown("Twórz realistyczne dialogi radiowe. Wybierz temat, a AI napisze i nagra rozmowę.")

# --- Pasek boczny ---
with st.sidebar:
    st.header("⚙️ Ustawienia Dźwięku")
    api_key = st.text_input("OpenAI API Key", type="password")
    
    st.divider()
    st.subheader("🔊 Silnik Głosu")
    provider = st.radio("Wybierz technologię:", ["OpenAI (Szybkie/Tanie)", "ElevenLabs (Premium)"])
    
    eleven_key = ""
    if provider == "ElevenLabs (Premium)":
        eleven_key = st.text_input("ElevenLabs API Key", type="password")
        st.info("💡 ElevenLabs oferuje najbardziej realistyczne głosy na rynku.")

# --- Funkcje Logiczne (Backend) ---

def generuj_scenariusz(topic, key):
    """Generuje dialog między dwiema osobami w formacie JSON-podobnym"""
    client = OpenAI(api_key=key)
    prompt = f"""
    Napisz krótki scenariusz podcastu na temat: "{topic}".
    
    ZASADY:
    1. Rozmawia dwóch prowadzących: "Alex" (Host - energiczny) i "Marek" (Gość - ekspert, spokojny).
    2. Rozmowa ma być naturalna, krótka (ok. 4 wymiany zdań na osobę).
    3. Użyj formatu:
    Alex: [Tekst]
    Marek: [Tekst]
    
    Nie dodawaj opisów scenicznych (np. *śmiech*), tylko sam tekst do wypowiedzenia.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    # Parsowanie tekstu na listę obiektów
    raw_text = response.choices[0].message.content
    lines = []
    for line in raw_text.split('\n'):
        if line.startswith("Alex:"):
            lines.append({"rola": "Alex", "tekst": line.replace("Alex:", "").strip()})
        elif line.startswith("Marek:"):
            lines.append({"rola": "Marek", "tekst": line.replace("Marek:", "").strip()})
            
    return lines

def tts_openai(text, voice, key):
    """Zamienia tekst na audio (OpenAI)"""
    client = OpenAI(api_key=key)
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )
    return response.content # Zwraca bajty

def tts_elevenlabs(text, voice_id, key):
    """Zamienia tekst na audio (ElevenLabs)"""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": key,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        st.error(f"Błąd ElevenLabs: {response.text}")
        return None

# --- Interfejs Główny ---

# Integracja z Łowcą Nisz (jeśli mamy zapisany pomysł)
default_topic = ""
if 'generated_ideas' in st.session_state:
    st.info("💡 Możesz stworzyć podcast promujący pomysł z 'Łowcy Nisz'.")

# Krok 1: Temat
topic = st.text_input("O czym mają rozmawiać?", placeholder="Np. Przyszłość sztucznej inteligencji w medycynie")

if st.button("📝 Napisz Scenariusz"):
    if not api_key:
        st.error("Podaj klucz OpenAI.")
    else:
        with st.spinner("Pisanie scenariusza..."):
            script = generuj_scenariusz(topic, api_key)
            st.session_state['podcast_script'] = script
            st.rerun()

# Krok 2: Edycja i Generowanie
if 'podcast_script' in st.session_state:
    st.divider()
    st.subheader("2. Edycja i Nagranie")
    
    script_data = st.session_state['podcast_script']
    
    # Wyświetlenie edytowalne (uproszczone)
    updated_script = []
    with st.form("script_form"):
        for i, line in enumerate(script_data):
            col1, col2 = st.columns([1, 5])
            role = col1.text_input("Kto?", line['rola'], key=f"role_{i}")
            text = col2.text_area("Co mówi?", line['tekst'], key=f"text_{i}", height=70)
            updated_script.append({"rola": role, "tekst": text})
        
        generate_audio = st.form_submit_button("🎙️ Nagraj Podcast (Generuj Audio)")

    # Krok 3: Przetwarzanie Audio
    if generate_audio:
        if not api_key:
            st.error("Brak klucza API.")
        else:
            full_audio = BytesIO() # Bufor w pamięci na cały plik
            
            with st.status("Nagrywanie w wirtualnym studiu...", expanded=True) as status:
                
                for i, line in enumerate(updated_script):
                    st.write(f"Nagrywanie linii {i+1}: {line['rola']}...")
                    
                    audio_chunk = None
                    
                    # Logika wyboru głosu
                    if provider == "OpenAI (Szybkie/Tanie)":
                        # Alex = Onyx, Marek = Alloy
                        voice = "onyx" if line['rola'] == "Alex" else "alloy"
                        audio_chunk = tts_openai(line['tekst'], voice, api_key)
                        
                    elif provider == "ElevenLabs (Premium)":
                        if not eleven_key:
                            st.error("Brak klucza ElevenLabs!")
                            break
                        # Przykładowe ID głosów (Adam i Nicole - standardowe w 11Labs)
                        # Możesz tu wpisać własne Voice ID ze swojego konta
                        voice_id = "pNInz6obpgDQGcFmaJgB" if line['rola'] == "Alex" else "EXAVITQu4vr4xnSDxMaL"
                        audio_chunk = tts_elevenlabs(line['tekst'], voice_id, eleven_key)
                    
                    # Łączenie plików (prosta konkatenacja bajtów działa dla MP3)
                    if audio_chunk:
                        full_audio.write(audio_chunk)
                
                status.update(label="✅ Podcast gotowy!", state="complete")
            
            # Odtwarzanie i Pobieranie
            st.divider()
            st.subheader("🎧 Twój Podcast")
            
            # Przewiń bufor na początek
            full_audio.seek(0)
            st.audio(full_audio)
            
            st.download_button(
                label="Pobierz Podcast (.mp3)",
                data=full_audio,
                file_name="moj_podcast_ai.mp3",
                mime="audio/mpeg"
            )