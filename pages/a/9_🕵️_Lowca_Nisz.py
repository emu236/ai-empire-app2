import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS

# --- Konfiguracja Strony ---
st.set_page_config(page_title="Łowca Nisz & Generator MVP", page_icon="🕵️", layout="wide")

st.title("🕵️ Łowca Nisz & Cyfrowy Software House")
st.markdown("Krok 1: Znajdź pomysł. Krok 2: Niech AI napisze dla Ciebie kod tej aplikacji.")

# --- Pasek boczny ---
with st.sidebar:
    st.header("⚙️ Konfiguracja")
    api_key = st.text_input("OpenAI API Key", type="password")
    
    st.divider()
    st.info("💡 **Instrukcja:**\n1. Wpisz branżę i znajdź problemy.\n2. Wybierz najlepszy pomysł z listy.\n3. Wklej go w sekcji 'Budowa' i wygeneruj kod.")

# --- Funkcje Logiczne ---
def search_web(query):
    """Szuka problemów w sieci"""
    try:
        results = DDGS().text(query, max_results=5)
        context = ""
        for r in results:
            context += f"- {r['title']}: {r['body']}\n"
        return context
    except Exception as e:
        return f"Błąd wyszukiwania: {e}"

def generate_business_ideas(niche, search_context, key):
    """Generuje listę pomysłów"""
    client = OpenAI(api_key=key)
    prompt = f"""
    Analizujesz branżę: {niche}.
    Problemy z sieci: {search_context}
    
    Wypisz 3 konkretne pomysły na automatyzacje (Micro-SaaS lub skrypty Python), które rozwiążą te problemy.
    Opisz je tak, abym mógł jeden z nich wybrać do zaprogramowania.
    
    Format dla każdego pomysłu:
    ### [Nazwa Pomysłu]
    **Opis:** Co to robi?
    **Technologia:** Jak to zadziała (np. Python + Pandas + API).
    **Potencjał:** Dlaczego klient za to zapłaci?
    ---
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def generate_mvp_code(idea_description, key):
    """Pisze kod dla wybranego pomysłu"""
    client = OpenAI(api_key=key)
    prompt = f"""
    Jesteś Senior Python Developerem. Twój cel: Napisać działający prototyp (MVP) dla poniższego pomysłu.
    
    POMYSŁ:
    {idea_description}
    
    WYMAGANIA:
    1. Kod ma być w Pythonie.
    2. Jeśli to prosta automatyzacja, zrób skrypt konsolowy.
    3. Jeśli wymaga interfejsu, użyj biblioteki 'streamlit'.
    4. Kod musi być kompletny (zawierać importy).
    5. Dodaj komentarze wyjaśniające jak to uruchomić.
    6. Nie używaj placeholderów typu "tutaj wpisz kod", napisz przykładową logikę.
    
    Wygeneruj TYLKO kod w bloku markdown.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content

# --- Interfejs Użytkownika ---

# Tab 1: Wyszukiwanie, Tab 2: Budowanie
tab1, tab2 = st.tabs(["🔍 Krok 1: Znajdź Pomysł", "🏗️ Krok 2: Zbuduj Aplikację"])

with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        target_niche = st.text_input("Jaka branża?", "Agencje Marketingowe")
        search_btn = st.button("🔍 Szukaj Pomysłów", use_container_width=True)
    
    with col2:
        if search_btn:
            if not api_key:
                st.error("Podaj klucz API w pasku bocznym.")
            else:
                with st.spinner("Przeszukuję internet i analizuję bóle klientów..."):
                    web_data = search_web(f"biggest pain points challenges {target_niche} 2024 automation")
                    ideas = generate_business_ideas(target_niche, web_data, api_key)
                    
                    st.success("Znaleziono potencjalne żyły złota!")
                    st.markdown(ideas)
                    st.session_state['generated_ideas'] = ideas # Zapisz w pamięci
                    st.info("👉 Skopiuj opis wybranego pomysłu i przejdź do zakładki 'Zbuduj Aplikację'.")

with tab2:
    st.header("🏗️ Cyfrowy Software House")
    st.write("Wklej tutaj opis pomysłu, który wygenerowałeś w poprzednim kroku (lub wpisz własny).")
    
    # Jeśli mamy coś w pamięci, podpowiedz użytkownikowi
    default_text = ""
    if 'generated_ideas' in st.session_state:
        st.caption("Poniżej możesz wkleić jeden z pomysłów z poprzedniej zakładki.")
    
    chosen_idea = st.text_area("Opis aplikacji do stworzenia", height=150, placeholder="Np. Skrypt, który bierze plik Excel z adresami e-mail i sprawdza czy są poprawne...")
    
    build_btn = st.button("🛠️ Napisz Kod Aplikacji", type="primary")
    
    if build_btn:
        if not api_key:
            st.error("Podaj klucz API.")
        elif not chosen_idea:
            st.warning("Musisz wpisać co mam zbudować.")
        else:
            with st.spinner("Piszę kod... To może chwilę potrwać (jestem w trybie Senior Dev 🤓)"):
                code_result = generate_mvp_code(chosen_idea, api_key)
                
                st.subheader("💾 Twój Gotowy Kod")
                st.code(code_result, language='python')
                
                st.success("Kod wygenerowany! Skopiuj go do nowego pliku .py i uruchom.")
                
                # Opcja pobrania
                st.download_button(
                    label="Pobierz plik .py",
                    data=code_result.replace("```python", "").replace("```", ""),
                    file_name="moj_automat.py",
                    mime="text/x-python"
                )