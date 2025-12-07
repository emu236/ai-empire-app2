# pages/4_📺_YouTube_Repurposer.py

import streamlit as st
import os
from dotenv import load_dotenv
import time

# Import logiki
# Musimy dodać ścieżkę nadrzędną do path, żeby widzieć agenta z folderu głównego
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent_youtube import pobierz_transkrypcje, repurpose_content

# Konfiguracja
load_dotenv()
st.set_page_config(page_title="YouTube Repurposer", page_icon="📺", layout="wide")

if 'api_key' not in st.session_state: st.session_state.api_key = os.getenv("OPENAI_API_KEY")
if 'transkrypcja' not in st.session_state: st.session_state.transkrypcja = ""
if 'yt_url' not in st.session_state: st.session_state.yt_url = ""

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Ustawienia")
    api_key_input = st.text_input("Klucz OpenAI API", value=st.session_state.api_key, type="password")
    if api_key_input: st.session_state.api_key = api_key_input
    st.info("To narzędzie zamienia filmy z YouTube na posty, blogi i maile.")

# --- GŁÓWNY EKRAN ---
st.title("📺 YouTube Content Repurposer")
st.markdown("Wklej link do filmu, a AI zamieni go w gotowe treści do social media.")

url = st.text_input("Link do wideo na YouTube:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("📥 Pobierz treść"):
    if not url:
        st.warning("Wklej link!")
    else:
        with st.spinner("Pobieranie napisów z YouTube..."):
            tekst, blad = pobierz_transkrypcje(url)
            
            if blad:
                st.error(blad)
            else:
                st.session_state.transkrypcja = tekst
                st.session_state.yt_url = url
                st.success(f"Pobrano treść! Liczba znaków: {len(tekst)}")
                with st.expander("Pokaż surową transkrypcję"):
                    st.write(tekst)

# --- GENEROWANIE TREŚCI ---
if st.session_state.transkrypcja:
    st.divider()
    st.subheader("♻️ Wybierz format do wygenerowania")
    
    tabs = st.tabs(["📝 Artykuł Blogowy", "🐦 Wątek Twitter (X)", "💼 Post LinkedIn", "📧 Newsletter"])
    
    # BLOG
    with tabs[0]:
        if st.button("Generuj Blog Post"):
            with st.spinner("Pisanie artykułu SEO..."):
                wynik = repurpose_content(st.session_state.transkrypcja, "Blog", st.session_state.api_key)
                st.markdown(wynik)
                st.session_state.blog_result = wynik
    
    # TWITTER
    with tabs[1]:
        if st.button("Generuj Wątek (Thread)"):
            with st.spinner("Pisanie tweetów..."):
                wynik = repurpose_content(st.session_state.transkrypcja, "Twitter", st.session_state.api_key)
                st.markdown(wynik)
    
    # LINKEDIN
    with tabs[2]:
        if st.button("Generuj Post LinkedIn"):
            with st.spinner("Pisanie posta biznesowego..."):
                wynik = repurpose_content(st.session_state.transkrypcja, "LinkedIn", st.session_state.api_key)
                st.markdown(wynik)
                
    # NEWSLETTER
    with tabs[3]:
        if st.button("Generuj Newsletter"):
            with st.spinner("Pisanie maila..."):
                wynik = repurpose_content(st.session_state.transkrypcja, "Newsletter", st.session_state.api_key)
                st.markdown(wynik)