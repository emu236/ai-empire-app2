import streamlit as st
import os
import replicate
from openai import OpenAI
import requests
import random
import base64
from io import BytesIO

# --- Konfiguracja Strony ---
st.set_page_config(page_title="AI Influencer & Reels", page_icon="💃", layout="wide")

st.title("💃 Fabryka Influencerów (v18.0 - Full Body Realism)")
st.markdown("Cała sylwetka (od stóp do głów) + Fotorealizm.")

# --- PRESETY VIBE ---
PRESETS_VIBE = [
    "Energetyczna i motywująca 🔥",
    "Spokojna i melancholijna 🍂",
    "Profesjonalna i konkretna 📈",
    "Zabawna i luźna 😂"
]

# --- INTELIGENTNA GARDEROBA ---
ACTIVITIES_MAP = {
    "✍️ Własna scenka (Wpisz ręcznie...)": {
        "type": "custom"
    },
    "Pije kawę w kawiarni": {
        "prompt": "sitting comfortably on a chair at cafe table, holding a coffee cup",
        "outfit": "wearing knitted sweater, jeans and sneakers",
        "bg": "window reflection, cafe interior, natural daylight"
    },
    "Pracuje w biurze": {
        "prompt": "sitting at desk, typing on laptop, looking away",
        "outfit": "wearing white shirt, blazer, skirt and high heels",
        "bg": "office background, depth of field"
    },
    "Spacer po mieście": {
        "prompt": "walking on street towards camera, wind in hair",
        "outfit": "wearing trench coat and boots",
        "bg": "city street, overcast soft lighting"
    },
    "Trening na siłowni": {
        "prompt": "standing resting pose, holding water bottle",
        "outfit": "wearing sport top, leggings and running shoes",
        "bg": "gym interior"
    },
    "Relaks na plaży": {
        "prompt": "walking on sand, looking at horizon",
        "outfit": "wearing summer dress and sandals",
        "bg": "ocean waves, sunset"
    },
    "Selfie w domu": {
        "prompt": "standing mirror selfie pose",
        "outfit": "wearing cotton t-shirt and socks",
        "bg": "bedroom interior, soft shadows"
    }
}

# --- Pasek boczny ---
with st.sidebar:
    st.header("⚙️ Konfiguracja")
    api_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.get('api_key', ''))
    replicate_key = st.text_input("Replicate API Token", type="password", value=st.session_state.get('replicate_key', ''))
    
    if api_key: st.session_state.api_key = api_key
    if replicate_key: 
        st.session_state.replicate_key = replicate_key
        os.environ["REPLICATE_API_TOKEN"] = replicate_key

    # --- FUNKCJA TŁUMACZENIA ---
    def translate_to_english(text, key):
        if not text or not key: return text
        try:
            client = OpenAI(api_key=key)
            resp = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Translate to English for AI image prompt. Return ONLY translation."},
                    {"role": "user", "content": text}
                ]
            )
            return resp.choices[0].message.content
        except: return text 

    st.divider()
    
    # --- KROK 1: KREATOR POSTACI ---
    st.header("🛠️ Krok 1: Stwórz Postać")
    with st.expander("Kreator Nowej Twarzy", expanded=True):
        new_char_desc_pl = st.text_area("Opisz wygląd (PO POLSKU):", "Piękna blondynka o niebieskich oczach, naturalna cera, bez makijażu")
        
        if st.button("🎲 Generuj Twarz Startową"):
            if not replicate_key or not api_key:
                st.error("Podaj klucze API!")
            else:
                with st.spinner("Tłumaczę i generuję..."):
                    try:
                        prompt_en = translate_to_english(new_char_desc_pl, api_key)
                        
                        model = replicate.models.get("black-forest-labs/flux-schnell")
                        latest_id = model.latest_version.id
                        
                        out = replicate.run(
                            f"black-forest-labs/flux-schnell:{latest_id}",
                            input={
                                "prompt": f"Raw portrait photo of {prompt_en}. Front facing, neutral expression. 35mm photography, film grain, skin texture, pores, natural lighting, unpolished.",
                                "aspect_ratio": "1:1",
                                "output_quality": 90
                            }
                        )
                        img_url = str(out[0])
                        st.session_state.generated_face_url = img_url
                        
                    except Exception as e:
                        st.error(f"Błąd: {e}")

        if 'generated_face_url' in st.session_state:
            st.image(st.session_state.generated_face_url, caption="Twoja Nowa Postać")
            try:
                img_data = requests.get(st.session_state.generated_face_url).content
                st.download_button("📥 Pobierz Twarz (JPG)", img_data, "moja_postac_twarz.jpg", "image/jpeg")
            except: pass
            st.success("👆 Pobierz zdjęcie i wgraj je poniżej w Kroku 2.")

    st.divider()
    
    # --- KROK 2: PULID ---
    st.header("🧬 Krok 2: Wgraj Wzorzec")
    uploaded_face = st.file_uploader("Plik wzorcowy (JPG/PNG)", type=['jpg', 'png', 'jpeg'])
    if uploaded_face: st.image(uploaded_face, width=100, caption="Aktywny Wzorzec")
    
    st.divider()
    identity_strength = st.slider("Siła podobieństwa (0.65 = Realniej):", 0.4, 0.9, 0.65)
    persona_vibe = st.selectbox("Charakter:", PRESETS_VIBE)

# --- Funkcje Logiczne ---

def generate_caption(context, key):
    client = OpenAI(api_key=key)
    prompt = f"Jesteś influencerką. Styl: {persona_vibe}. Napisz krótki opis na Instagram. Sytuacja: {context}. Pisz po polsku."
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return response.choices[0].message.content
    except Exception as e: return f"Błąd tekstu: {e}"

def generate_with_pulid_dynamic(uploaded_file, prompt_en, id_strength):
    """Generuje zdjęcie - WERSJA FULL BODY REALISM"""
    try:
        uploaded_file.seek(0)
        
        # ZMIANA: Wide full body shot, showing shoes
        realism_prompt = f"Wide full body shot of a woman, showing entire figure and shoes. {prompt_en}. Shot on Kodak Portra 400, 35mm film grain, skin texture, visible pores, natural imperfection, soft natural lighting, cinematic composition, sharp focus."
        
        output = replicate.run(
            "zsxkib/flux-pulid:8baa7ef2255075b46f4d91cd238c21d31181b3e6a864463f967960bb0112525b",
            input={
                "main_face_image": uploaded_file,
                "prompt": realism_prompt,
                "width": 896, 
                "height": 1152,
                "num_steps": 20,        # Limit API
                "guidance_scale": 2.5,  # Niski CFG = Realizm
                "id_weight": id_strength,
                "true_cfg": 1,
                "max_sequence_length": 128
            }
        )
        return str(output[0])
    except Exception as e:
        return f"Error PulID: {str(e)}"

def animate_photo(image_url):
    try:
        model = replicate.models.get("ali-vilab/i2vgen-xl")
        latest_id = model.latest_version.id
        output = replicate.run(
            f"ali-vilab/i2vgen-xl:{latest_id}",
            input={"image": image_url, "prompt": "High quality video, realistic subtle movement, 4k", "max_frames": 16, "frame_rate": 8}
        )
        return str(output)
    except Exception as e: return f"Error Video: {str(e)}"

# --- Interfejs Główny ---

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("3. Wybierz lub Wpisz Sytuację")
    wybor_akcji = st.selectbox("Scenariusz:", list(ACTIVITIES_MAP.keys()))
    
    final_prompt_en = ""
    
    if "Własna scenka" in wybor_akcji:
        st.info("✍️ Tutaj możesz wpisać cokolwiek po polsku.")
        custom_desc_pl = st.text_area("Co robi postać?", "Idzie po plaży, trzyma kapelusz")
        is_custom = True
    else:
        is_custom = False
        detale = ACTIVITIES_MAP[wybor_akcji]
        st.info(f"👗 **Strój:** {detale['outfit']}\n🌍 **Tło:** {detale['bg']}")

    if not uploaded_face:
        st.warning("⚠️ Najpierw wgraj zdjęcie w pasku bocznym (Krok 2).")
        btn_photo = st.button("📸 Generuj", disabled=True)
    else:
        btn_photo = st.button("📸 Generuj (Full Body)", type="primary")

with col2:
    st.subheader("4. Wynik")
    if 'current_image' not in st.session_state: st.session_state.current_image = None
    if 'current_caption' not in st.session_state: st.session_state.current_caption = None

    if btn_photo and uploaded_face:
        if not st.session_state.get('replicate_key') or not st.session_state.get('api_key'): 
            st.error("Brak kluczy API!")
        else:
            with st.status("Tłumaczenie i Generowanie (Cała Sylwetka)...", expanded=True):
                
                if is_custom:
                    desc_en = translate_to_english(custom_desc_pl, st.session_state.api_key)
                    final_prompt_en = f"{desc_en}" 
                    caption_context = custom_desc_pl
                else:
                    det = ACTIVITIES_MAP[wybor_akcji]
                    final_prompt_en = f"{det['prompt']}. She is {det['outfit']}. Background is {det['bg']}."
                    caption_context = wybor_akcji

                img_url = generate_with_pulid_dynamic(uploaded_face, final_prompt_en, identity_strength)
                
                if "Error" in img_url:
                    st.error(img_url)
                else:
                    st.session_state.current_image = img_url
                    st.session_state.current_caption = generate_caption(caption_context, st.session_state.api_key)
                    st.rerun()

    if st.session_state.current_image:
        st.image(st.session_state.current_image, caption="Cała Sylwetka") 
        
        try:
            img_bytes = requests.get(st.session_state.current_image).content
            st.download_button("📥 Pobierz Zdjęcie (JPG)", img_bytes, "influencer_fullbody.jpg", "image/jpeg")
        except Exception as e: st.error(f"Błąd pobierania: {e}")

        st.success(st.session_state.current_caption)
        
        if st.button("✨ Generuj Wideo"):
            with st.status("🎬 Kręcenie wideo..."):
                video_url = animate_photo(st.session_state.current_image)
                if "Error" in video_url: st.error(video_url)
                else:
                    st.video(video_url)