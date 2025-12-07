import streamlit as st
import os
from openai import OpenAI
import base64
import json

# --- Konfiguracja Strony ---
st.set_page_config(page_title="AI Strategy Brain", page_icon="🧠", layout="wide")

st.title("🧠 Mózg Strategii & Marki Osobistej")
st.markdown("Krok 2: Wgraj zdjęcie swojej postaci. AI stworzy dla niej **historię, niszę i produkt do sprzedaży**.")

# --- Pasek boczny ---
with st.sidebar:
    st.header("⚙️ Konfiguracja")
    api_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.get('api_key', ''))
    if api_key: st.session_state.api_key = api_key

    st.info("💡 Ten moduł łączy wygląd postaci z pomysłem na biznes. To serce Twojej 'Agencji AI'.")

# --- Funkcje ---
def analyze_and_strategize(uploaded_file, niche_hint, key):
    client = OpenAI(api_key=key)
    
    # Kodowanie obrazu
    base64_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    
    prompt = f"""
    Jesteś ekspertem od brandingu i marketingu cyfrowego.
    Oto zdjęcie wirtualnego influencera.
    
    Twoje zadanie to stworzyć dla tej postaci kompletną tożsamość i plan biznesowy.
    
    Sugestia użytkownika (jeśli jest): {niche_hint}
    
    Wygeneruj odpowiedź w formacie JSON z polami:
    1. "imie": Imię i nazwisko (pasujące do wyglądu).
    2. "bio": Krótkie bio na Instagram (z emoji).
    3. "historia": Krótka, chwytliwa historia (storytelling) - kim jest, co przeszła, dlaczego uczy innych.
    4. "nisza": W jakiej branży działa (np. Biohacking, Krypto, Joga twarzy).
    5. "ebook_tytul": Chwytliwy tytuł e-booka, którego sprzedaje.
    6. "ebook_spis": Lista 5 rozdziałów tego e-booka (jako tekst).
    7. "styl_wizualny": Opis stylu zdjęć, który pasuje do tej marki (do użycia w generatorze zdjęć).
    """

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
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

# --- Interfejs Główny ---

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Wgraj Awatara")
    uploaded_file = st.file_uploader("Zdjęcie postaci (z modułu Influencer)", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Twoja Gwiazda", width=250)
        
    niche_hint = st.text_input("Sugestia branży (opcjonalne)", placeholder="np. Zdrowe odżywianie, Finanse, Moda...")
    
    generate_btn = st.button("🚀 Stwórz Strategię i Produkt", type="primary")

with col2:
    st.subheader("2. Strategia Biznesowa")
    
    if generate_btn and uploaded_file:
        if not st.session_state.get('api_key'):
            st.error("Podaj klucz API OpenAI.")
        else:
            with st.spinner("Analizuję psychologię postaci i trendy rynkowe..."):
                try:
                    strategy = analyze_and_strategize(uploaded_file, niche_hint, st.session_state.api_key)
                    st.session_state.strategy_result = strategy
                    st.success("Strategia gotowa!")
                except Exception as e:
                    st.error(f"Błąd: {e}")

    # Wyświetlanie wyników
    if 'strategy_result' in st.session_state:
        s = st.session_state.strategy_result
        
        st.markdown(f"### 👤 {s.get('imie', 'Nieznany')}")
        st.info(f"**Nisza:** {s.get('nisza')}")
        st.text_area("Bio na Instagram:", s.get('bio'), height=100)
        
        with st.expander("📖 Przeczytaj Historię (Storytelling)"):
            st.write(s.get('historia'))
            
        st.divider()
        st.subheader("💰 Produkt Cyfrowy (E-book)")
        st.markdown("Skopiuj te dane do modułu **'Fabryka E-booków'**:")
        
        col_copy1, col_copy2 = st.columns(2)
        with col_copy1:
            st.text_input("Tytuł E-booka:", s.get('ebook_tytul'))
        with col_copy2:
            st.text_area("Spis Treści (Rozdziały):", "\n".join(s.get('ebook_spis', [])) if isinstance(s.get('ebook_spis'), list) else s.get('ebook_spis'), height=150)
            
        st.divider()
        st.markdown("### 🎨 Styl Marki")
        st.caption("Użyj tego opisu w 'Fabryce Influencerów' jako 'Charakter/Vibe':")
        st.code(s.get('styl_wizualny'))