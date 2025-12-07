# pages/2_🎁_Odbierz_Prezent.py - WERSJA FINALNA (NAPRAWIONY LINK)
import streamlit as st
import smtplib
import pandas as pd
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

# --- KONFIGURACJA ---
load_dotenv()
st.set_page_config(page_title="Odbierz Darmowy E-book", page_icon="🎁", layout="centered")

# Ustawienia maila (z pliku .env)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Ścieżki
PATH_TO_PDF = "public/prezent.pdf" 
DATABASE_FILE = "subscribers.csv"

# --- FUNKCJE (Backend) ---
def send_email_with_attachment(receiver_email, name, pdf_path):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = receiver_email
    msg['Subject'] = f"🎁 Cześć {name}, Twój E-book jest tutaj!"

    body = f"""
    Cześć {name}!

    Dziękuję za dołączenie do newslettera AI Empire!
    
    Zgodnie z umową, w załączniku przesyłam Twój darmowy E-book.
    Mam nadzieję, że wiedza w nim zawarta pomoże Ci w rozwoju.
    
    Pozdrawiam,
    Twój Zespół AI
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        with open(pdf_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(pdf_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
        msg.attach(part)
    except FileNotFoundError:
        return False, "Błąd serwera: brak pliku PDF."

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True, "Wysłano"
    except Exception as e:
        return False, str(e)

def save_subscriber(name, email):
    # Tworzymy plik CSV, jeśli nie istnieje
    if not os.path.exists(DATABASE_FILE):
        df = pd.DataFrame(columns=["Imie", "Email", "Data", "Zgoda_Regulamin", "IP_Hash"])
        df.to_csv(DATABASE_FILE, index=False)
    
    # Zapisujemy rekord
    new_data = pd.DataFrame([[name, email, pd.Timestamp.now(), True, "N/A"]], 
                            columns=["Imie", "Email", "Data", "Zgoda_Regulamin", "IP_Hash"])
    new_data.to_csv(DATABASE_FILE, mode='a', header=False, index=False)

# --- STYLIZACJA (CSS) ---
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    .legal-text {font-size: 0.8rem; color: #888; margin-top: 10px; margin-bottom: 10px;}
    a {text-decoration: underline; color: #FF4B4B; font-weight: bold;}
    a:hover {color: #FF0000;}
</style>
""", unsafe_allow_html=True)

# --- LANDING PAGE ---
st.image("https://placehold.co/600x200?text=Zbuduj+Imperium+AI", use_container_width=True)
st.title("🚀 Odbierz swój Plan Działania")
st.markdown("### Dołącz do newslettera i odbierz E-booka jako prezent powitalny.")
st.write("Wpisz swoje dane, a materiały trafią na Twoją skrzynkę w ciągu minuty.")

with st.form("landing_form"):
    imie = st.text_input("Twoje Imię")
    email = st.text_input("Twój Adres Email")
    
    st.markdown("---")
    
    # --- SEKCJA PRAWNA ---
    # Link: href="Polityka_Prywatnosci" zadziała, jeśli plik nazywa się "3_Polityka_Prywatnosci.py"
    # Target="_blank" otwiera w nowym oknie
    st.markdown("""
    <p class="legal-text">
        Administratorem Twoich danych jest: <strong>[TUTAJ WPISZ SWOJE IMIĘ I NAZWISKO / FIRMĘ]</strong>. 
        Szczegóły dotyczące przetwarzania danych oraz Regulamin usługi znajdziesz w 
        <a href="Polityka_Prywatnosci" target="_blank">Polityce Prywatności i Regulaminie</a>.
    </p>
    """, unsafe_allow_html=True)
    
    zgoda = st.checkbox("✅ Zamawiam newsletter AI Empire i odbieram darmowego E-booka. Akceptuję Regulamin i wiem, że mogę wypisać się w każdej chwili.")
    # ---------------------

    submit_btn = st.form_submit_button("📩 Odbierz E-booka", type="primary")

    if submit_btn:
        if not imie or not email:
            st.error("⚠️ Uzupełnij imię i adres email.")
        elif "@" not in email or "." not in email:
            st.warning("⚠️ Podaj poprawny adres email.")
        elif not zgoda:
            st.error("⛔ Musisz zaakceptować zasady (wymóg prawny), aby otrzymać materiały.")
        else:
            if not os.path.exists(PATH_TO_PDF):
                st.error("⚠️ Błąd techniczny: Brak pliku PDF (public/prezent.pdf).")
            else:
                with st.spinner("Przetwarzanie zamówienia..."):
                    save_subscriber(imie, email)
                    success, msg = send_email_with_attachment(email, imie, PATH_TO_PDF)
                    
                    if success:
                        st.balloons()
                        st.success(f"Sukces! 🎁 E-book został wysłany na adres: {email}")
                        st.info("Nie widzisz maila? Sprawdź folder SPAM lub Oferty.")
                    else:
                        st.error(f"Wystąpił błąd przy wysyłce: {msg}")

st.divider()
st.markdown('<div style="text-align: center; color: grey; font-size: 0.8em;">Copyright © 2025 AI Empire Builder</div>', unsafe_allow_html=True)