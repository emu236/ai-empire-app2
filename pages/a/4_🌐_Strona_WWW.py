import streamlit as st
import db
from openai import OpenAI

st.set_page_config(page_title="Website Builder", page_icon="🌐", layout="wide")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⛔ Zaloguj się."); st.stop()

with st.sidebar:
    api_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.get('api_key', ''))
    if api_key: st.session_state.api_key = api_key
    current_credits = db.get_credits(st.session_state.username)
    st.metric("Kredyty", current_credits)

st.title("4. Generator Landing Page")
st.markdown("Stwórz stronę sprzedażową dla swojej postaci i jej produktów.")

# Pobieranie danych (z poprzednich kroków)
strategy = st.session_state.get('current_strategy', {
    'imie': 'Jan Kowalski', 'bio': 'Ekspert od wszystkiego', 'ebook_tytul': 'Super Poradnik'
})

col1, col2 = st.columns(2)
with col1:
    imie = st.text_input("Imię na stronie", strategy.get('imie'))
    naglowek = st.text_input("Nagłówek (Hero)", f"Odkryj sekret {strategy.get('nisza', 'sukcesu')}")
with col2:
    produkt = st.text_input("Nazwa Produktu", strategy.get('ebook_tytul'))
    cena = st.text_input("Cena", "49 PLN")

if st.button("🏗️ Zbuduj Stronę WWW (Koszt: 5 kredytów)", type="primary"):
    if current_credits < 5:
        st.error("Brak kredytów!")
    else:
        if not api_key: st.error("Podaj klucz API")
        else:
            db.deduct_credits(st.session_state.username, 5)
            
            # Prompt generujący kod HTML
            prompt = f"""
            Napisz kod jednego pliku HTML5 z wbudowanym CSS (Tailwind CSS via CDN).
            To ma być nowoczesny Landing Page dla Influencera.
            
            DANE:
            - Imię: {imie}
            - Bio: {strategy.get('bio')}
            - Nagłówek: {naglowek}
            - Produkt główny: {produkt}
            - Cena: {cena}
            
            SEKCJE:
            1. Hero Section (Ciemne tło, duży nagłówek, miejsce na zdjęcie po prawej).
            2. O mnie (Bio).
            3. Sekcja Produktowa (Opis e-booka, Cena, Przycisk 'Kup Teraz').
            4. Footer.
            
            Użyj placeholderów na zdjęcia (np. https://via.placeholder.com/400).
            Zwróć TYLKO kod HTML.
            """
            
            client = OpenAI(api_key=st.session_state.api_key)
            resp = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            html_code = resp.choices[0].message.content.replace("```html", "").replace("```", "")
            
            st.success("Strona wygenerowana!")
            st.download_button("📥 Pobierz index.html", html_code, "index.html", "text/html")
            st.components.v1.html(html_code, height=600, scrolling=True)