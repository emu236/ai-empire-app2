# Agent: Codzienny Marketing
# Cel: Automatyczne publikowanie zaplanowanych treści na X (Twitter).

import pandas as pd
from datetime import datetime
import time
import schedule
import logging

# Importujemy naszych agentów do publikacji i grafiki
from agent_social import uruchom_agenta_social
from agent_grafik import uruchom_agenta_grafika
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler("marketing_automation.log", mode='a', encoding='utf-8'), logging.StreamHandler()])

def publikuj_zaplanowany_post():
    """
    Sprawdza plan, znajduje odpowiedni post na teraz i go publikuje.
    """
    try:
        df = pd.read_csv("plan_tresci.csv")
        teraz = datetime.now()
        
        # Znajdujemy post na dzisiaj (dzień miesiąca) i najbliższą minioną godzinę
        dzien_miesiaca = teraz.day
        aktualna_godzina = teraz.hour

        # Filtrujemy posty na dzisiaj
        posty_na_dzis = df[df['dzien'] == dzien_miesiaca]
        
        if posty_na_dzis.empty:
            logging.warning(f"Nie znaleziono zaplanowanych postów na dzień {dzien_miesiaca}.")
            return

        # Znajdujemy właściwy post do opublikowania
        post_do_publikacji = None
        for index, post in posty_na_dzis.iterrows():
            godzina_planowana = int(post['godzina'].split(':')[0])
            if godzina_planowana <= aktualna_godzina:
                post_do_publikacji = post
        
        if post_do_publikacji is None:
            logging.info("Jeszcze nie nadszedł czas na kolejny zaplanowany post.")
            return

        # Sprawdzamy, czy ten post nie był już dzisiaj opublikowany
        if os.path.exists(".ostatni_post.log"):
            with open(".ostatni_post.log", "r") as f:
                ostatni_log = f.read()
                if ostatni_log == f"{dzien_miesiaca}_{post_do_publikacji['godzina']}":
                    logging.info("Ten post został już dzisiaj opublikowany. Czekam na następny.")
                    return

        logging.info("Znaleziono nowy post do publikacji!")
        
        # --- Tu dzieje się magia ---
        tekst_posta = post_do_publikacji['tekst']
        
        # W przyszłości można tu zintegrować Agenta Grafika,
        # aby tworzył obraz na podstawie 'grafika_prompt'
        
        uruchom_agenta_social(tekst_posta)
        
        # Zapisujemy log, że ten post został opublikowany
        with open(".ostatni_post.log", "w") as f:
            f.write(f"{dzien_miesiaca}_{post_do_publikacji['godzina']}")
            
    except FileNotFoundError:
        logging.error("BŁĄD: Nie znaleziono pliku 'plan_tresci.csv'!")
    except Exception as e:
        logging.error(f"Wystąpił nieoczekiwany błąd: {e}")

if __name__ == '__main__':
    logging.info("--- AUTOMAT MARKETINGOWY: START ---")
    logging.info("Uruchamiam sprawdzanie co godzinę. Naciśnij Ctrl+C, aby zakończyć.")

    # Ustawiamy harmonogram: sprawdzaj plan co godzinę
    schedule.every().hour.at(":01").do(publikuj_zaplanowany_post)

    # Uruchomienie pętli harmonogramu
    while True:
        schedule.run_pending()
        time.sleep(60) # Czekaj 60 sekund przed kolejnym sprawdzeniem