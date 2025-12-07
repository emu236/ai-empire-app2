# Home.py - CENTRUM DOWODZENIA (DASHBOARD + LANDING PAGE)

import streamlit as st
import database as db
import stripe_agent
import time
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

# --- KONFIGURACJA ---
load_dotenv()
st.set_page_config(page_title="AI Empire", page_icon="👑", layout="wide")

# Ścieżki
PATH_TO_PDF = "public/prezent.pdf" 
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Baza
db.init_db()

# --- STAN APLIKACJI ---
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'user_tier' not in st.session_state: st.session_state.user_tier = "Free"
if 'username' not in st.session_state: st.session_state.username = ""
if 'email' not in st.session_state: st.session_state.email = ""
if 'credits' not in st.session_state: st.session_state.credits = 0
if 'is_admin' not in st.session_state: st.session_state.is_admin = False

# ==============================================================================
# 🎨 CUSTOM CSS
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        padding-top: 5rem;
        padding-bottom: 5rem;
    }

    .hero-title {
        background: linear-gradient(90deg, #FF4B4B 0%, #7038FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 10px;
        line-height: 1.2;
        padding-top: 20px;
    }

    .hero-subtitle {
        font-size: 1.2rem;
        text-align: center;
        color: #B0B0B0;
        margin-bottom: 40px;
        font-weight: 400;
    }

    .feature-card {
        background-color: #1E1E1E;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #333;
        height: 100%;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        border-color: #FF4B4B;
        box-shadow: 0 10px 30px rgba(255, 75, 75, 0.1);
    }

    .feature-card h3 { color: #FFFFFF; font-size: 1.3rem; margin-bottom: 10px; }
    .feature-card p { color: #AAAAAA; font-size: 0.9rem; line-height: 1.5; }

    .price-card {
        background-color: #121212;
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #444;
        text-align: center;
        position: relative;
    }

    .price-card.premium {
        border: 2px solid #FFD700;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.1);
    }
    
    .price-amount {
        font-size: 2.5rem;
        font-weight: 800;
        color: #FFF;
        margin: 10px 0;
    }

    .badge {
        background-color: #FFD700;
        color: #000;
        padding: 5px 10px;
        border-radius: 10px;
        font-size: 0.8rem;
        font-weight: bold;
        position: absolute;
        top: -10px;
        right: 20px;
    }

    .footer {
        text-align: center;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #333;
        color: #666;
        font-size: 0.8rem;
    }
    
    .footer a { color: #888; text-decoration: none; }
    .footer a:hover { color: #FFF; }

</style>
""", unsafe_allow_html=True)

# --- FUNKCJE LOGICZNE ---
def perform_login(user, tier, admin_status, email, credits):
    st.session_state.authenticated = True
    st.session_state.username = user
    st.session_state.user_tier = tier
    st.session_state.is_admin = bool(admin_status)
    st.session_state.email = email
    st.session_state.credits = credits

def send_lead_magnet(receiver_email, name):
    if not os.path.exists(PATH_TO_PDF): return False, "Brak pliku PDF na serwerze."
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = receiver_email
        msg['Subject'] = f"🎁 {name}, Twój Plan Działania AI"
        body = f"Cześć {name}!\n\nDziękujemy za pobranie poradnika. Znajdziesz go w załączniku.\n\nPozdrawiamy,\nZespół AI Empire"
        msg.attach(MIMEText(body, 'plain'))
        with open(PATH_TO_PDF, "rb") as f:
            part = MIMEApplication(f.read(), Name="Poradnik_AI.pdf")
        part['Content-Disposition'] = 'attachment; filename="Poradnik_AI.pdf"'
        msg.attach(part)
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True, "Wysłano"
    except Exception as e:
        return False, str(e)

# 🚨 LOGIKA PŁATNOŚCI (STRIPE RETURN)
query_params = st.query_params
if "session_id" in query_params:
    session_id = query_params["session_id"]
    st.query_params.clear()
    with st.spinner("Autoryzacja płatności..."):
        result = stripe_agent.verify_payment(session_id)
        if result["verified"]:
            user = result["username"]
            
            # A. Zmiana pakietu
            if result["type"] == "subscription":
                new_tier = result["value"]
                db.update_user_tier(user, new_tier)
                st.balloons()
                st.success(f"🎉 Płatność udana! Witaj w pakiecie {new_tier}.")
            
            # B. Doładowanie kredytów
            elif result["type"] == "credits":
                amount = int(result["value"])
                db.add_user_credits(user, amount)
                st.balloons()
                st.success(f"🎉 Doładowano {amount} kredytów!")

            # Auto-login po płatności
            user_data = db.get_user_details(user)
            if user_data:
                perform_login(user, user_data['tier'], user_data['is_admin'], user_data['email'], user_data['credits'])
                time.sleep(2)
                st.rerun()
        else:
            st.error("Błąd płatności.")

# ==============================================================================
# WIDOK 1: UŻYTKOWNIK ZALOGOWANY (DASHBOARD)
# ==============================================================================
if st.session_state.authenticated:
    st.title(f"Witaj, {st.session_state.username}!")
    
    # Kafelki statusu
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        st.info(f"💎 Twój Pakiet: **{st.session_state.user_tier}**")
    with c2:
        credits = db.get_user_credits(st.session_state.username)
        st.session_state.credits = credits
        st.success(f"⚡ Dostępne Kredyty: **{credits}**")
    with c3:
        if st.button("Wyloguj", use_container_width=True):
            st.session_state.authenticated = False; st.rerun()
            
    st.divider()
    
    # --- ZAKŁADKI GŁÓWNE ---
    tab_home, tab_shop, tab_profile = st.tabs(["🚀 Centrum Dowodzenia", "⚡ Doładuj Kredyty", "👤 Mój Profil"])

    # TAB 1: NARZĘDZIA
    with tab_home:
        if st.session_state.user_tier == "Premium" or st.session_state.is_admin:
            st.markdown("### 🧰 Twoje Centrum Dowodzenia")
            
            # Rząd 1
            row1 = st.columns(3)
            with row1[0]:
                if st.button("📚 Fabryka Ebooków", use_container_width=True): st.switch_page("pages/2_🏭_Fabryka_Contentu.py")
            with row1[1]:
                if st.button("🎥 Studio Awatarów", use_container_width=True): st.switch_page("pages/8_🎥_Studio_Awatarow.py")
            with row1[2]:
                if st.button("🎙️ Inteligentny Dyktafon", use_container_width=True): st.switch_page("pages/5_🎤_Inteligentny_Dyktafon.py")
            
            st.write("")
            
            # Rząd 2
            row2 = st.columns(3)
            with row2[0]:
                if st.button("🕵️ Łowca Nisz", use_container_width=True): st.switch_page("pages/6_🕵️_Lowca_Nisz.py")
            with row2[1]:
                if st.button("📧 Cold Email B2B", use_container_width=True): st.switch_page("pages/3_📧_Cold_Email.py")
            with row2[2]:
                if st.button("📺 YouTube Repurposer", use_container_width=True): st.switch_page("pages/7_📺_YouTube_Repurposer.py")
            
            st.write("")
            
            # Rząd 3 (NOWY - DODATKI)
            row3 = st.columns(3)
            with row3[0]:
                if st.button("🎨 Karykaturzysta AI", use_container_width=True): st.switch_page("pages/9_🎨_Karykaturzysta_AI.py")
            with row3[1]:
                # Dodajemy przycisk do trenera
                if st.button("🏋️ Agent Trener", use_container_width=True): st.switch_page("pages/10_🏋️_Agent_Trener.py")
            with row3[2]:
                st.info("🔜 Więcej narzędzi wkrótce!")
            
        else:
            st.warning("⚠️ Twój pakiet jest ograniczony. Odblokuj pełną moc AI poniżej.")
            # Tutaj można dać ograniczone menu dla Basic/Standard
            st.markdown("### Dostępne dla Ciebie:")
            if st.button("📚 Fabryka Ebooków (Tekst)", use_container_width=True): st.switch_page("pages/2_🏭_Fabryka_Contentu.py")

    # TAB 2: SKLEP KREDYTÓW
    with tab_shop:
        st.subheader("Brakuje mocy? Dokup kredyty.")
        c_s1, c_s2, c_s3 = st.columns(3)
        with c_s1:
            st.markdown('<div class="price-card"><h4>Starter</h4><div class="price-big">29 zł</div><p>50 Kredytów</p></div>', unsafe_allow_html=True)
            url = stripe_agent.create_checkout_session("Small", "credits", st.session_state.email, st.session_state.username)
            if url: st.link_button("Kup 50 ⚡", url, use_container_width=True)
        with c_s2:
            st.markdown('<div class="price-card highlight"><h4>Power</h4><div class="price-big">99 zł</div><p>200 Kredytów</p></div>', unsafe_allow_html=True)
            url = stripe_agent.create_checkout_session("Medium", "credits", st.session_state.email, st.session_state.username)
            if url: st.link_button("Kup 200 ⚡", url, type="primary", use_container_width=True)
        with c_s3:
            st.markdown('<div class="price-card"><h4>Tycoon</h4><div class="price-big">399 zł</div><p>1000 Kredytów</p></div>', unsafe_allow_html=True)
            url = stripe_agent.create_checkout_session("Large", "credits", st.session_state.email, st.session_state.username)
            if url: st.link_button("Kup 1000 ⚡", url, use_container_width=True)

    # TAB 3: PROFIL
    with tab_profile:
        col_p1, col_p2 = st.columns([1, 2])
        with col_p1:
            st.markdown("### Twoje Dane")
            st.text_input("Login", value=st.session_state.username, disabled=True)
            st.text_input("Email", value=st.session_state.email, disabled=True)
            st.text_input("Aktywny Plan", value=st.session_state.user_tier, disabled=True)
        with col_p2:
            st.markdown("### Zmień Plan")
            cp1, cp2, cp3 = st.columns(3)
            with cp1:
                st.caption("Basic (10 Kredytów/mc)")
                if st.session_state.user_tier == "Basic": st.button("Obecny", disabled=True, key="pb")
                else:
                    u = stripe_agent.create_checkout_session("Basic", "subscription", st.session_state.email, st.session_state.username)
                    if u: st.link_button("Basic (49zł)", u)
            with cp2:
                st.caption("Standard (30 Kredytów/mc)")
                if st.session_state.user_tier == "Standard": st.button("Obecny", disabled=True, key="ps")
                else:
                    u = stripe_agent.create_checkout_session("Standard", "subscription", st.session_state.email, st.session_state.username)
                    if u: st.link_button("Standard (99zł)", u)
            with cp3:
                st.caption("Premium (100 Kredytów/mc)")
                if st.session_state.user_tier == "Premium": st.button("Obecny", disabled=True, key="pp")
                else:
                    u = stripe_agent.create_checkout_session("Premium", "subscription", st.session_state.email, st.session_state.username)
                    if u: st.link_button("Premium (199zł)", u)

# ==============================================================================
# WIDOK 2: LANDING PAGE (DLA GOŚCI)
# ==============================================================================
else:
    c_hero1, c_hero2, c_hero3 = st.columns([1, 8, 1])
    with c_hero2:
        st.markdown('<div class="hero-title">Zbuduj Imperium Contentu z AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-subtitle">Generuj e-booki, audiobooki i wideo w 15 minut.<br>Jedna platforma do automatyzacji Twojego biznesu online.</div>', unsafe_allow_html=True)
        
        bt1, bt2, bt3 = st.columns([1, 1, 1])
        with bt2:
            st.button("🚀 DOŁĄCZ TERAZ (Start Gratis)", type="primary", use_container_width=True, on_click=lambda: st.write("👇 Formularz rejestracji jest na dole!"))

    st.write(""); st.write("")

    st.subheader("🛠️ Co potrafi ten system?")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="feature-card"><h3>📚 Fabryka E-booków</h3><p>Wpisz temat, a AI napisze całą książkę, rozdział po rozdziale.</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="feature-card"><h3>🎥 Studio Awatarów</h3><p>Wgraj swoje zdjęcie, wpisz tekst i otrzymaj profesjonalne wideo.</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="feature-card"><h3>🎙️ Audio & Podcast</h3><p>Zamień tekst w audiobooka lub wygeneruj dwuosobowy podcast.</p></div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="feature-card"><h3>🏋️ Agent Trener</h3><p>Osobisty plan treningowy i dieta, żebyś miał siłę na biznes.</p></div>', unsafe_allow_html=True)

    st.divider()

    col_lead1, col_lead2 = st.columns([1, 1])
    with col_lead1:
        st.subheader("🎁 Odbierz Darmowy Raport")
        st.markdown("**Nie wiesz jak zacząć?** Pobierz nasz przewodnik: *'7 Sposobów na Zarabianie z AI'*.")
        
    with col_lead2:
        with st.form("landing_lead_form", border=True):
            st.write("Wpisz email, aby odebrać PDF:")
            lm_name = st.text_input("Imię")
            lm_email = st.text_input("E-mail")
            lm_zgoda = st.checkbox("Zgadzam się na politykę prywatności.")
            
            if st.form_submit_button("📩 Wyślij mi PDF", type="secondary", use_container_width=True):
                if not lm_name or not lm_email or not lm_zgoda: st.error("Uzupełnij dane.")
                else:
                    with st.spinner("Wysyłanie..."):
                        success, msg = send_lead_magnet(lm_email, lm_name)
                        if success: st.success("Wysłano! Sprawdź skrzynkę."); st.balloons()
                        else: st.error(f"Błąd: {msg}")

    st.divider()

    st.subheader("🔐 Panel Logowania / Rejestracji")
    tab_login, tab_reg = st.tabs(["Zaloguj się", "Załóż Konto (3 Kredyty Gratis)"])
    
    with tab_login:
        with st.form("login_main"):
            c_l1, c_l2 = st.columns(2)
            l_user = c_l1.text_input("Login")
            l_pass = c_l2.text_input("Hasło", type="password")
            if st.form_submit_button("Zaloguj się", type="primary", use_container_width=True):
                s, t, a, e, c = db.check_login(l_user, l_pass)
                if s: perform_login(l_user, t, a, e, c); st.rerun()
                else: st.error("Błędne dane.")

    with tab_reg:
        with st.form("register_main"):
            c_r1, c_r2 = st.columns(2)
            r_user = c_r1.text_input("Wybierz Login")
            r_email = c_r2.text_input("Twój Email")
            r_pass = c_r1.text_input("Hasło", type="password")
            r_pass2 = c_r2.text_input("Powtórz Hasło", type="password")
            r_zgoda = st.checkbox("Akceptuję Regulamin serwisu.")
            if st.form_submit_button("Załóż Konto i Odbierz 3 Kredyty", type="primary", use_container_width=True):
                if r_pass != r_pass2: st.error("Hasła się różnią.")
                elif not r_zgoda: st.error("Zaakceptuj regulamin.")
                else:
                    ok, info = db.create_user(r_user, r_email, r_pass)
                    if ok: st.success("Konto założone! Zaloguj się w zakładce obok."); st.balloons()
                    else: st.error(info)

    st.markdown("""<div class="footer">© 2025 AI Empire Builder Inc. Wszystkie prawa zastrzeżone.<br><a href="/Polityka_Prywatnosci" target="_blank">Polityka Prywatności</a> | <a href="/Polityka_Prywatnosci" target="_blank">Regulamin</a></div>""", unsafe_allow_html=True)