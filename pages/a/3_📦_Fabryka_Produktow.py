import streamlit as st
import db
from openai import OpenAI
import json
import os
from io import BytesIO

# --- KONFIGURACJA ---
st.set_page_config(page_title="Fabryka Produktów", page_icon="📦", layout="wide")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⛔ Zaloguj się na stronie głównej."); st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Konfiguracja")
    api_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.get('api_key', ''))
    if api_key: st.session_state.api_key = api_key
    
    current_credits = db.get_credits(st.session_state.username)
    st.metric("Twoje Kredyty", current_credits)

# --- DANE ZE STRATEGII ---
strategy = st.session_state.get('current_strategy', {
    'ebook_tytul': 'Przykładowy Tytuł', 
    'spis_tresci_ebook': ['Rozdział 1', 'Rozdział 2'],
    'pomysl_podcast': 'Przykładowy Podcast',
    'pomysl_planner': 'Przykładowy Planner'
})

# --- UI GŁÓWNE ---
st.title("📦 Fabryka Produktów Cyfrowych")
st.markdown("Wybierz produkt, który chcesz stworzyć na podstawie swojej Strategii.")

c1, c2, c3 = st.columns(3)

# === KAFELEK 1: E-BOOK (PRZEKIEROWANIE) ===
with c1:
    st.info("📚 **E-book Premium**")
    st.write(f"Tytuł: *{strategy.get('ebook_tytul')}*")
    st.write("Użyj swojego zaawansowanego generatora (Agenci, Grafika, PDF).")
    
    if st.button("➡️ Przejdź do Kreatora E-booków"):
        # 1. Przygotowujemy dane dla tamtego modułu
        # Formatujemy spis treści z listy na string (jeśli trzeba) lub odwrotnie, 
        # w zależności co przyjmuje Twój moduł Ebooki.py (v9.0 używa JSON w 'prospekt_data')
        
        chapters = strategy.get('spis_tresci_ebook', [])
        if isinstance(chapters, str):
            chapters = chapters.split('\n')
            
        # Wstrzykujemy dane do sesji, z której korzysta 1_📚_Ebooki.py
        st.session_state['temat_roboczy'] = strategy.get('ebook_tytul')
        
        # Symulujemy, że etap planowania (Architekt) jest już zrobiony
        st.session_state['prospekt_data'] = {
            "Tytul": strategy.get('ebook_tytul'),
            "Cel_Ebooka": "Edukacja i budowanie autorytetu w niszy " + strategy.get('nisza', ''),
            "Kluczowa_Obietnica_USP": "Praktyczna wiedza w pigułce",
            "Spis_Tresci": chapters
        }
        st.session_state['etap'] = 1 # Przeskakujemy od razu do edycji planu
        
        # 2. Przekierowanie
        st.switch_page("pages/1_📚_Ebooki.py")

# === KAFELEK 2: PODCAST (LOKALNIE) ===
with c2:
    st.warning("🎙️ **Podcast AI**")
    st.write(f"Seria: *{strategy.get('pomysl_podcast')}*")
    st.write("Wygeneruj scenariusz i audio.")
    
    # Tutaj możemy zostawić prostą logikę lub też przekierować, jeśli masz osobny plik Podcast
    # Zakładam, że robimy to tutaj lub przekierowujemy do Podcast.py jeśli istnieje.
    # Jeśli masz plik 'pages/3_🎙️_Podcast.py' (lub podobny), lepiej przekierować:
    
    if st.button("➡️ Przejdź do Studia Podcast"):
        # Przekazujemy temat
        st.session_state['podcast_topic_idea'] = strategy.get('pomysl_podcast')
        # Sprawdź dokładną nazwę pliku w swoim folderze pages!
        try:
            st.switch_page("pages/3_🎙️_Podcast.py") 
        except:
            st.error("Nie znaleziono pliku pages/3_🎙️_Podcast.py. Sprawdź nazwę.")

# === KAFELEK 3: PLANNER (LOKALNIE) ===
with c3:
    st.success("✅ **Planner / Checklista**")
    st.write(f"Temat: *{strategy.get('pomysl_planner')}*")
    
    # Generator plannerów jest prosty, więc może zostać tutaj (lub w osobnym pliku)
    if st.button("🛠️ Generuj Planner tutaj"):
        if current_credits < 3:
            st.error("Brak kredytów.")
        else:
            with st.spinner("Projektowanie..."):
                # Prosta logika generowania (ta co była wcześniej)
                client = OpenAI(api_key=st.session_state.api_key)
                prompt = f"Stwórz planner PDF (treść markdown). Temat: {strategy.get('pomysl_planner')}."
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role":"user", "content":prompt}])
                content = res.choices[0].message.content
                
                db.deduct_credits(st.session_state.username, 3)
                st.session_state['generated_planner'] = content
                st.rerun()

# Wyświetlenie wyniku Plannera (jeśli wygenerowano w tym widoku)
if 'generated_planner' in st.session_state:
    st.divider()
    st.subheader("Twój Planner")
    st.markdown(st.session_state['generated_planner'])
    st.download_button("Pobierz (.md)", st.session_state['generated_planner'], "planner.md")