import streamlit as st
import os
import requests
import replicate
from openai import OpenAI
from io import BytesIO

# --- Konfiguracja Strony ---
st.set_page_config(page_title="Studio Wideo AI", page_icon="🎬", layout="wide")

st.title("🎬 Studio Wideo: Reklamy AI")
st.markdown("Zamień pomysł na aplikację w wideo promocyjne (Image-to-Video).")

# --- Pasek boczny ---
with st.sidebar:
    st.header("⚙️ Konfiguracja Studia")
    api_key = st.text_input("OpenAI API Key", type="password")
    
    st.info("Do generowania wideo potrzebujesz konta na Replicate.com (jest tanie i potężne).")
    replicate_key = st.text_input("Replicate API Token", type="password", help="Zdobądź na replicate.com/account/api-tokens")
    
    # Ustawienie zmiennej środowiskowej dla Replicate
    if replicate_key:
        os.environ["REPLICATE_API_TOKEN"] = replicate_key

# --- Funkcje Agentów (Zintegrowane) ---

def agent_rezyser(product_name, problem, solution, style, key):
    """Tworzy opis wizualny sceny (Prompt)"""
    client = OpenAI(api_key=key)
    prompt = f"""
    Jesteś Reżyserem filmowym. Tworzymy reklamę wideo dla aplikacji: "{product_name}".
    Problem: {problem}
    Rozwiązanie: {solution}
    Styl: {style}
    
    Twoim zadaniem jest opisanie JEDNEJ, kluczowej sceny filmowej, która najlepiej sprzeda ten produkt.
    Opis musi być po angielsku, bardzo wizualny, szczegółowy.
    Skup się na oświetleniu, kadrze (cinematic shot), kolorach.
    Nie dodawaj tekstu na ekranie.
    
    Zwróć TYLKO opis sceny (prompt do generatora obrazu).
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def agent_grafik(image_prompt, key):
    """Generuje pierwszą klatkę wideo (DALL-E 3)"""
    client = OpenAI(api_key=key)
    response = client.images.generate(
        model="dall-e-3",
        prompt=f"Cinematic movie still, 16:9 aspect ratio, high quality, 8k. {image_prompt}",
        size="1024x1024", # DALL-E 3 wspiera też formaty poziome, ale standard to 1024
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    return image_url

def agent_producent(image_url):
    """Ożywia zdjęcie w wideo (Replicate: Stable Video Diffusion)"""
    try:
        output = replicate.run(
            "stability-ai/stable-video-diffusion:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "input_image": image_url,
                "video_length": "25_frames_with_svd_xt",
                "sizing_strategy": "maintain_aspect_ratio",
                "frames_per_second": 6,
                "motion_bucket_id": 127
            }
        )
        return output # Zwraca URL do pliku mp4
    except Exception as e:
        return f"Error: {str(e)}"

# --- Interfejs Użytkownika ---

# Pobieranie danych z sesji (jeśli przyszliśmy z Łowcy Nisz)
default_name = ""
default_problem = ""
if 'generated_ideas' in st.session_state:
    st.info("💡 Wykryto pomysły z modułu 'Łowca Nisz'. Możesz użyć ich do stworzenia reklamy.")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Scenariusz")
    product_name = st.text_input("Nazwa Produktu", placeholder="Np. PhotoBot")
    problem = st.text_area("Jaki problem rozwiązuje?", placeholder="Bałagan w zdjęciach...", height=100)
    solution = st.text_area("Co widać na wideo?", placeholder="Futurystyczny interfejs porządkujący zdjęcia...", height=100)
    style = st.selectbox("Styl Wideo", ["Cinematic", "3D Render", "Anime", "Cyberpunk", "Minimalist Tech"])
    
    generate_prompt_btn = st.button("✨ Stwórz Scenę (Reżyser)")

with col2:
    st.subheader("2. Podgląd i Produkcja")
    
    # Stan aplikacji
    if 'video_prompt' not in st.session_state: st.session_state.video_prompt = ""
    if 'image_url' not in st.session_state: st.session_state.image_url = ""
    
    # Krok 1: Reżyser
    if generate_prompt_btn:
        if not api_key:
            st.error("Podaj klucz OpenAI.")
        else:
            with st.spinner("Reżyser pisze scenopis..."):
                prompt = agent_rezyser(product_name, problem, solution, style, api_key)
                st.session_state.video_prompt = prompt
                st.success("Scenopis gotowy!")
    
    if st.session_state.video_prompt:
        st.text_area("Prompt dla AI (możesz edytować):", st.session_state.video_prompt, height=80)
        
        # Krok 2: Grafik
        if st.button("🖼️ Generuj Klatkę Startową (DALL-E 3)"):
            with st.spinner("Rysowanie klatki filmowej..."):
                img_url = agent_grafik(st.session_state.video_prompt, api_key)
                st.session_state.image_url = img_url
                st.rerun()

    # Krok 3: Producent (Wideo)
    if st.session_state.image_url:
        st.image(st.session_state.image_url, caption="Klatka startowa", width=400)
        
        st.write("---")
        st.subheader("3. Renderowanie Wideo")
        
        if st.button("🎬 Ożyw to zdjęcie (Action!)", type="primary"):
            if not replicate_key:
                st.error("Potrzebujesz klucza API z Replicate.com")
            else:
                with st.status("Rendering w chmurze (to potrwa ok. 2 minuty)...", expanded=True):
                    st.write("Wysyłanie danych do Stable Video Diffusion...")
                    video_url = agent_producent(st.session_state.image_url)
                    
                    if "Error" in str(video_url):
                        st.error(video_url)
                    else:
                        st.success("Wideo gotowe!")
                        st.video(video_url)
                        st.balloons()