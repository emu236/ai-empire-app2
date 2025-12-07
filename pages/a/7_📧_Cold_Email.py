import streamlit as st
from openai import OpenAI

# --- Konfiguracja Strony ---
st.set_page_config(page_title="Generator Cold Email", page_icon="📧", layout="wide")

st.title("📧 Generator Ofert & Cold Email")
st.markdown("Zamień swój kod/produkt w sprzedaż. Wygeneruj skuteczne maile do klientów.")

# --- Pasek boczny ---
with st.sidebar:
    st.header("⚙️ Konfiguracja")
    api_key = st.text_input("OpenAI API Key", type="password")
    
    st.divider()
    framework = st.selectbox("Strategia Copywritingu", 
                             ["AIDA (Uwaga-Zainteresowanie-Pożądanie-Akcja)", 
                              "PAS (Problem-Agitacja-Rozwiązanie)", 
                              "Bezpośredni i Krótki"])
    
    tone = st.select_slider("Ton wiadomości", options=["Luźny", "Profesjonalny", "Agresywny sprzedażowo"])

# --- Funkcja Generująca ---
def generate_emails(product_name, audience, problem, solution, framework, tone, key):
    client = OpenAI(api_key=key)
    
    prompt = f"""
    Jesteś światowej klasy copywriterem B2B. Twoim zadaniem jest napisanie sekwencji Cold Email.
    
    SZCZEGÓŁY:
    - Produkt: {product_name}
    - Klient docelowy: {audience}
    - Problem klienta: {problem}
    - Nasze rozwiązanie: {solution}
    - Styl: {tone}
    - Framework: {framework}
    
    ZADANIE:
    Napisz 2 wiadomości:
    1. **E-mail otwierający** (Musi mieć chwytliwy temat, krótki wstęp i wezwanie do działania).
    2. **E-mail Follow-up** (Wysyłany 3 dni później, przypominający o wartości).
    
    Użyj formatowania Markdown. Oddziel maile wyraźną linią.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Błąd: {e}"

# --- Interfejs Główny ---

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Dane o Produkcie")
    st.info("Wklej tutaj informacje z 'Łowcy Nisz'.")
    
    product_name = st.text_input("Nazwa Twojego narzędzia/usługi", placeholder="Np. Auto-Fakturka 3000")
    audience = st.text_input("Do kogo piszemy?", placeholder="Np. Właściciele małych biur rachunkowych")
    
    problem = st.text_area("Jaki problem rozwiązujesz?", height=100, 
                           placeholder="Np. Tracą 5 godzin tygodniowo na przepisywanie danych z PDF do Excela.")
    
    solution = st.text_area("Jak Twoje narzędzie to naprawia?", height=100,
                            placeholder="Np. Skrypt automatycznie wyciąga dane i zapisuje w tabeli w 3 sekundy.")
    
    generate_btn = st.button("🚀 Napisz Ofertę Sprzedażową", type="primary", use_container_width=True)

with col2:
    st.subheader("📩 Gotowe Wiadomości")
    
    if generate_btn:
        if not api_key:
            st.error("Podaj klucz API w pasku bocznym.")
        elif not problem or not solution:
            st.warning("Uzupełnij opis problemu i rozwiązania.")
        else:
            with st.spinner("Copywriter pisze Twoje maile..."):
                email_content = generate_emails(product_name, audience, problem, solution, framework, tone, api_key)
                
                st.markdown(email_content)
                
                # Opcja pobrania
                st.download_button(
                    label="Pobierz treść maili (.txt)",
                    data=email_content,
                    file_name="cold_email_sequence.txt",
                    mime="text/plain"
                )