import streamlit as st
import db
import replicate
from openai import OpenAI
import requests
import os

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Kreator Postaci", page_icon="👤", layout="wide")

# --- SPRAWDZENIE LOGOWANIA ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⛔ Musisz się zalogować na stronie głównej, aby używać tego narzędzia.")
    st.stop()

# --- POBRANIE API KEYS Z SESJI (lub input, jeśli brakuje) ---
# Zakładamy, że użytkownik wpisał klucze w Home.py lub tutaj w Sidebarze
with st.sidebar:
    st.header("⚙️ Klucze API")
    api_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.get('api_key', ''))
    replicate_key = st.text_input("Replicate API Token", type="password", value=st.session_state.get('replicate_key', ''))
    
    if api_key: st.session_state.api_key = api_key
    if replicate_key: 
        st.session_state.replicate_key = replicate_key
        os.environ["REPLICATE_API_TOKEN"] = replicate_key

# --- LOGIKA KREDYTÓW ---
current_credits = db.get_credits(st.session_state.username)
COST = 5

# --- FUNKCJA TŁUMACZENIA ---
def translate_to_english(text, key):
    if not text: return ""
    try:
        client = OpenAI(api_key=key)
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Translate this character description to English for AI image prompt. Return ONLY the English text."},
                {"role": "user", "content": text}
            ]
        )
        return resp.choices[0].message.content
    except Exception as e:
        st.error(f"Błąd tłumaczenia: {e}")
        return text

# --- UI GŁÓWNE ---
st.title("1. Stwórz swojego Awatara")
st.markdown(f"Wygeneruj unikalną twarz, która stanie się Twoją marką.")
st.info(f"💰 Koszt generacji: **{COST} kredytów**. Twój stan konta: **{current_credits}**.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Opisz wygląd")
    desc_pl = st.text_area("Jak ma wyglądać postać? (Wpisz po polsku)", 
                           "Młoda kobieta o skandynawskiej urodzie, platynowe włosy, niebieskie oczy, piegi, naturalny makijaż")
    
    generate_btn = st.button("📸 Generuj Twarz", type="primary", use_container_width=True)

with col2:
    st.subheader("Wynik")
    
    if generate_btn:
        # Walidacja
        if not api_key or not replicate_key:
            st.error("⚠️ Brakuje kluczy API w pasku bocznym!")
        elif current_credits < COST:
            st.error(f"❌ Masz za mało kredytów! Potrzebujesz {COST}, masz {current_credits}.")
        else:
            # --- PROCES GENEROWANIA ---
            with st.status("Praca w toku...", expanded=True) as status:
                # 1. Pobranie opłaty
                db.deduct_credits(st.session_state.username, COST)
                st.write(f"💸 Pobrano {COST} kredytów.")
                
                # 2. Tłumaczenie
                st.write("🌍 Tłumaczenie opisu...")
                prompt_en = translate_to_english(desc_pl, api_key)
                
                # 3. Generowanie (FLUX)
                st.write("🎨 Rysowanie twarzy (FLUX.1)...")
                try:
                    # Używamy bezpiecznej metody run()
                    model = replicate.models.get("black-forest-labs/flux-schnell")
                    latest_id = model.latest_version.id
                    
                    output = replicate.run(
                        f"black-forest-labs/flux-schnell:{latest_id}",
                        input={
                            "prompt": f"Close up portrait of {prompt_en}. Front facing, neutral expression, looking at camera. High quality, 8k, plain background, realistic skin texture.",
                            "aspect_ratio": "1:1",
                            "output_quality": 90
                        }
                    )
                    
                    image_url = str(output[0])
                    st.session_state['generated_avatar_url'] = image_url # Zapisz w sesji
                    status.update(label="✅ Gotowe!", state="complete")
                    
                except Exception as e:
                    status.update(label="❌ Błąd!", state="error")
                    st.error(f"Wystąpił błąd: {e}")

    # Wyświetlanie wyniku (jeśli istnieje w sesji)
    if 'generated_avatar_url' in st.session_state:
        st.image(st.session_state['generated_avatar_url'], caption="Twój nowy awatar")
        
        st.success("👇 Ważne: Pobierz to zdjęcie na dysk. Będziesz go potrzebować w kolejnych krokach (do Strategii i Instagrama).")
        
        # Pobieranie
        try:
            img_data = requests.get(st.session_state['generated_avatar_url']).content
            st.download_button(
                label="📥 Pobierz Awatara (JPG)",
                data=img_data,
                file_name="moj_awatar.jpg",
                mime="image/jpeg"
            )
        except: pass