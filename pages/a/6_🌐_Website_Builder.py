# pages/6_🌐_Website_Builder.py

import streamlit as st
import os
from dotenv import load_dotenv

# Import logiki (dodajemy ścieżkę do głównego folderu)
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent_webdev import generuj_landing_page

# Konfiguracja
load_dotenv()
st.set_page_config(page_title="AI Website Builder", page_icon="🌐", layout="wide")

if 'api_key' not in st.session_state: st.session_state.api_key = os.getenv("OPENAI_API_KEY")
if 'wygenerowany_html' not in st.session_state: st.session_state.wygenerowany_html = ""

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Ustawienia")
    api_key_input = st.text_input("Klucz OpenAI API", value=st.session_state.api_key, type="password")
    if api_key_input: st.session_state.api_key = api_key_input
    st.info("To narzędzie tworzy kompletne Landing Page (HTML) dla Twoich produktów.")

# --- GŁÓWNY EKRAN ---
st.title("🌐 AI Website Builder")
st.markdown("Stwórz profesjonalną stronę sprzedażową w 30 sekund.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Dane Produktu")
    
    # Przycisk do zaciągnięcia danych z generatora E-booków
    if st.button("📥 Załaduj dane z ostatniego projektu e-booka"):
        if 'prospekt_data' in st.session_state and st.session_state.prospekt_data:
            dane = st.session_state.prospekt_data
            st.session_state.web_tytul = dane.get('Tytul', '')
            st.session_state.web_usp = dane.get('Kluczowa_Obietnica_USP', '')
            st.session_state.web_target = dane.get('Segment_Docelowy', '')
            st.session_state.web_rozdzialy = "\n".join(dane.get('Spis_Tresci', []))
            st.success("Załadowano dane!")
            st.rerun()
        else:
            st.warning("Brak danych w pamięci. Stwórz najpierw e-booka lub wpisz ręcznie.")

    # Formularz (wypełniony automatycznie lub ręcznie)
    with st.form("web_form"):
        tytul = st.text_input("Tytuł Produktu", value=st.session_state.get('web_tytul', ''))
        usp = st.text_area("Główna Obietnica (USP)", value=st.session_state.get('web_usp', ''), height=70)
        target = st.text_input("Dla kogo to jest?", value=st.session_state.get('web_target', ''))
        
        rozdzialy_raw = st.text_area("Główne moduły/rozdziały (każdy w nowej linii)", 
                                     value=st.session_state.get('web_rozdzialy', ''), height=150)
        
        generuj = st.form_submit_button("🚀 Generuj Stronę WWW")

if generuj:
    if not tytul or not usp:
        st.error("Podaj przynajmniej Tytuł i USP!")
    else:
        lista_rozdzialow = [r.strip() for r in rozdzialy_raw.split('\n') if r.strip()]
        
        with st.status("Budowanie strony...", expanded=True) as status:
            st.write("👨‍💻 Copywriter pisze teksty sprzedażowe...")
            st.write("🎨 Designer układa sekcje w Tailwind CSS...")
            
            html_code = generuj_landing_page(tytul, usp, target, lista_rozdzialow, st.session_state.api_key)
            st.session_state.wygenerowany_html = html_code
            
            status.update(label="✅ Strona gotowa!", state="complete", expanded=False)

# --- WYNIK ---
with col2:
    st.subheader("2. Podgląd i Kod")
    
    if st.session_state.wygenerowany_html:
        tab_preview, tab_code = st.tabs(["👁️ Podgląd", "💻 Kod Źródłowy"])
        
        with tab_preview:
            # Renderowanie HTML w ramce (iframe)
            st.components.v1.html(st.session_state.wygenerowany_html, height=600, scrolling=True)
            
        with tab_code:
            st.code(st.session_state.wygenerowany_html, language="html")
            
        st.divider()
        # Przycisk pobierania
        st.download_button(
            label="⬇️ Pobierz plik index.html",
            data=st.session_state.wygenerowany_html,
            file_name="index.html",
            mime="text/html"
        )
    else:
        st.info("Wypełnij formularz po lewej, aby zobaczyć wynik.")