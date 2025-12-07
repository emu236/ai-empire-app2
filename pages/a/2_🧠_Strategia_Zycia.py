import streamlit as st
import db
from openai import OpenAI
import base64
import json
import os

# --- KONFIGURACJA ---
st.set_page_config(page_title="Strategia Marki", page_icon="🧠", layout="wide")

# --- ZABEZPIECZENIA ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⛔ Zaloguj się na stronie głównej.")
    st.stop()

# --- SIDEBAR I KLUCZE ---
with st.sidebar:
    st.header("⚙️ Konfiguracja")
    api_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.get('api_key', ''))
    if api_key: st.session_state.api_key = api_key

# --- LOGIKA KREDYTÓW ---
COST = 2
current_credits = db.get_credits(st.session_state.username)

# --- FUNKCJE ---
def analyze_avatar_strategy(uploaded_file, niche_hint, key):
    client = OpenAI(api_key=key)
    base64_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    
    # ZMODYFIKOWANY PROMPT (BEZPIECZNY DLA FILTRÓW)
    prompt = f"""
    To jest fikcyjna postać wygenerowana przez AI (CGI character). 
    Jesteś ekspertem od storytellingu i marketingu.
    
    Twoje zadanie: Stwórz dla tej FIKCYJNEJ postaci tożsamość i plan biznesowy.
    Analizuj cechy wizualne (styl, ubiór) jako wskazówki do jej osobowości.
    
    Sugestia użytkownika (jeśli jest): {niche_hint}
    
    Wygeneruj odpowiedź w formacie JSON z polami:
    {{
        "imie": "Imię i Nazwisko (pasujące do wyglądu)",
        "nisza": "Konkretna nisza (np. Joga twarzy, Krypto, Ogrodnictwo)",
        "bio": "Krótkie BIO na Instagram (max 150 znaków)",
        "historia": "Storytelling - krótka historia postaci (3 zdania)",
        "grupa_docelowa": "Opis idealnego klienta",
        "pomysl_ebook": "Chwytliwy tytuł E-booka",
        "spis_tresci_ebook": ["Rozdział 1...", "Rozdział 2...", "Rozdział 3...", "Rozdział 4...", "Rozdział 5..."],
        "pomysl_podcast": "Tytuł Podcastu",
        "pomysl_planner": "Tytuł Checklisty PDF"
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ],
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        
        # ZABEZPIECZENIE PRZED PUSTĄ ODPOWIEDZIĄ
        if not content:
            return {"error": "AI odmówiło analizy zdjęcia (Filtr Bezpieczeństwa). Spróbuj innego zdjęcia."}
            
        return json.loads(content)
        
    except Exception as e:
        return {"error": f"Błąd techniczny: {str(e)}"}

# --- UI ---
st.title("2. Strategia i Dusza Postaci")
st.markdown(f"Wgraj awatara z kroku 1. AI wymyśli resztę. **Koszt: {COST} kredyty**.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Dane wejściowe")
    uploaded_file = st.file_uploader("Wgraj zdjęcie awatara (JPG/PNG)", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        st.image(uploaded_file, width=200, caption="Twój Awatar")
    
    niche_hint = st.text_input("Masz pomysł na branżę? (Opcjonalne)", placeholder="np. Joga, Krypto, Gotowanie...")
    
    generate_btn = st.button("🚀 Generuj Strategię", type="primary")

with col2:
    st.subheader("Wynik Strategiczny")
    
    if generate_btn:
        if not st.session_state.get('api_key'):
            st.error("Podaj klucz API OpenAI!")
        elif not uploaded_file:
            st.error("Musisz wgrać zdjęcie!")
        elif current_credits < COST:
            st.error("Brak środków na koncie! Doładuj w Home.")
        else:
            with st.status("Analiza psychologiczna i rynkowa...", expanded=True):
                # Najpierw analiza, potem pobranie kredytów (żeby nie pobierać za błędy)
                strategy_data = analyze_avatar_strategy(uploaded_file, niche_hint, st.session_state.api_key)
                
                if "error" in strategy_data:
                    st.error(strategy_data['error'])
                else:
                    db.deduct_credits(st.session_state.username, COST)
                    st.session_state['current_strategy'] = strategy_data
                    st.success("Strategia gotowa! (Pobrano kredyty)")

    # Wyświetlanie wyników z sesji
    if 'current_strategy' in st.session_state:
        s = st.session_state['current_strategy']
        
        st.header(f"👤 {s.get('imie', 'Nieznany')}")
        st.info(f"🎯 **Nisza:** {s.get('nisza', 'Ogólna')}")
        
        st.markdown(f"**Bio na Insta:**\n> {s.get('bio', '')}")
        
        with st.expander("📖 Przeczytaj Historię Postaci (Storytelling)", expanded=True):
            st.write(s.get('historia', ''))
            st.write(f"**Target:** {s.get('grupa_docelowa', '')}")

        st.divider()
        st.subheader("💰 Produkty do stworzenia (Krok 3)")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.success("📚 E-BOOK")
            st.write(f"**{s.get('pomysl_ebook', '')}**")
        with c2:
            st.warning("🎙️ PODCAST")
            st.write(f"**{s.get('pomysl_podcast', '')}**")
        with c3:
            st.info("✅ PLANNER")
            st.write(f"**{s.get('pomysl_planner', '')}**")
            
        st.caption("Dane te zostały zapisane. Przejdź teraz do 'Fabryki Produktów', aby je wygenerować.")