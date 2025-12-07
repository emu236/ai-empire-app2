# pages/8_🧠_Second_Brain.py

import streamlit as st
import os
from dotenv import load_dotenv

# Import logiki (ścieżka do głównego folderu)
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent_brain import zbuduj_indeks, zapytaj_baze

# Konfiguracja
load_dotenv()
st.set_page_config(page_title="AI Second Brain", page_icon="🧠", layout="wide")

if 'api_key' not in st.session_state: st.session_state.api_key = os.getenv("OPENAI_API_KEY")
if 'vectorstore' not in st.session_state: st.session_state.vectorstore = None
if 'historia_czatu' not in st.session_state: st.session_state.historia_czatu = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Baza Wiedzy")
    api_key_input = st.text_input("Klucz OpenAI API", value=st.session_state.api_key, type="password")
    if api_key_input: st.session_state.api_key = api_key_input
    
    st.divider()
    st.write("### 📂 Wgraj Dokumenty")
    uploaded_files = st.file_uploader("Wybierz pliki PDF", type=["pdf"], accept_multiple_files=True)
    
    if st.button("🔄 Przetwórz i Zbuduj Bazę"):
        if not uploaded_files:
            st.warning("Najpierw wgraj pliki!")
        else:
            with st.status("Budowanie Twojego Drugiego Mózgu...", expanded=True) as status:
                st.write("Czytanie PDF-ów...")
                st.write("Dzielenie na fragmenty...")
                st.write("Tworzenie bazy wektorowej...")
                
                vs = zbuduj_indeks(uploaded_files, st.session_state.api_key)
                st.session_state.vectorstore = vs
                
                status.update(label="✅ Baza Gotowa!", state="complete", expanded=False)
                st.success(f"Zindeksowano {len(uploaded_files)} plików.")

# --- GŁÓWNY EKRAN ---
st.title("🧠 Twój Drugi Mózg (RAG)")
st.markdown("Wgraj dokumenty po lewej stronie i zadawaj pytania na ich podstawie.")

# Wyświetlanie czatu
for msg in st.session_state.historia_czatu:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Pole na pytanie
pytanie = st.chat_input("O co chcesz zapytać swoje dokumenty?")

if pytanie:
    if not st.session_state.vectorstore:
        st.error("Najpierw musisz zbudować bazę wiedzy (Wgraj pliki w panelu bocznym)!")
    else:
        # Wyświetl pytanie użytkownika
        with st.chat_message("user"):
            st.markdown(pytanie)
        st.session_state.historia_czatu.append({"role": "user", "content": pytanie})

        # Generuj odpowiedź
        with st.chat_message("assistant"):
            with st.spinner("Szukam w dokumentach..."):
                wynik = zapytaj_baze(st.session_state.vectorstore, pytanie, st.session_state.api_key)
                odpowiedz_tekst = wynik['result']
                zrodla = wynik['source_documents']
                
                st.markdown(odpowiedz_tekst)
                
                # Pokaż źródła (dla wiarygodności)
                with st.expander("📚 Źródła (Skąd to wiem?)"):
                    for doc in zrodla:
                        st.caption(f"📄 {os.path.basename(doc.metadata['source'])} (Fragment: {doc.page_content[:100]}...)")

        st.session_state.historia_czatu.append({"role": "assistant", "content": odpowiedz_tekst})