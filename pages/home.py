# Home.py - BRAMKA LOGOWANIA I SUBSKRYPCJI
import streamlit as st

st.set_page_config(page_title="AI Empire - Logowanie", page_icon="👑", layout="centered")

# Inicjalizacja stanu (jeśli nie istnieje)
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_tier' not in st.session_state:
    st.session_state.user_tier = "Free"  # Opcje: Free, Basic, Standard, Premium

# --- FUNKCJA LOGOWANIA (MOCKUP) ---
def login(username, password):
    # W prawdziwej aplikacji tutaj łączysz się z bazą danych
    if username == "admin" and password == "admin":
        st.session_state.authenticated = True
        # Tutaj normalnie pobrałbyś info o subskrypcji z bazy danych
        # Na potrzeby testów - nie ustawiamy tieru tutaj, użytkownik wybierze go niżej
        st.rerun()
    else:
        st.error("Błędny login lub hasło")

# --- UI: JEŚLI ZALOGOWANY ---
if st.session_state.authenticated:
    st.title(f"Witaj w Panelu, {st.session_state.get('username', 'Admin')}!")
    
    st.info(f"Twój obecny pakiet: **{st.session_state.user_tier}**")
    
    st.subheader("Zarządzaj Subskrypcją (Symulacja Płatności)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🥉 BASIC")
        st.write("✅ Tylko E-booki (Tekst/PDF)")
        st.write("❌ Audiobooki")
        st.write("❌ Marketing")
        if st.button("Wybierz Basic"):
            st.session_state.user_tier = "Basic"
            st.rerun()

    with col2:
        st.markdown("### 🥈 STANDARD")
        st.write("✅ E-booki")
        st.write("✅ **Audiobooki**")
        st.write("❌ Marketing")
        if st.button("Wybierz Standard"):
            st.session_state.user_tier = "Standard"
            st.rerun()

    with col3:
        st.markdown("### 🥇 PREMIUM")
        st.write("✅ E-booki")
        st.write("✅ Audiobooki")
        st.write("✅ **Podcast & Cold Email**")
        if st.button("Wybierz Premium"):
            st.session_state.user_tier = "Premium"
            st.rerun()

    st.divider()
    st.success("👈 Przejdź do narzędzi w menu po lewej stronie.")
    
    if st.button("Wyloguj"):
        st.session_state.authenticated = False
        st.session_state.user_tier = "Free"
        st.rerun()

# --- UI: JEŚLI NIEZALOGOWANY ---
else:
    st.title("👑 AI Empire Builder")
    st.markdown("Zaloguj się, aby uzyskać dostęp do narzędzi.")
    
    with st.form("login_form"):
        user = st.text_input("Login", "admin")
        passwd = st.text_input("Hasło", type="password", value="admin")
        submit = st.form_submit_button("Zaloguj się")
        
        if submit:
            login(user, passwd)
            
    st.markdown("---")
    st.markdown("Nie masz konta? [Odbierz darmowy E-book i zobacz próbkę](/Odbierz_Prezent)")