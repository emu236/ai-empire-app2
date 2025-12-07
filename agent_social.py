# Agent 8: Social Media Manager
# Cel: Automatyczne publikowanie treści na X (Twitter).

import tweepy

# --- KONFIGURACJA X (TWITTER) API ---
# Wklej tutaj swoje 4 klucze z portalu deweloperskiego X
API_KEY = "Igq6to4uG4LnG2JdlcAyp7Gq1"
API_KEY_SECRET = "F3QrCSj980WdzDVFmP5bdopllyUI493shdigniyyNbcM71eC3z"
ACCESS_TOKEN = "1978373100623351808-jH9et2k3gFzdvOXV5Gd5zBoFKLTOZb"
ACCESS_TOKEN_SECRET = "5PlhSuC2l6Nm6I8M7ZXU9ZrVZPYMLGQYaOfp7luIPs4jr"
# ------------------------------------

def uruchom_agenta_social(tekst_posta: str):
    """
    Łączy się z API X i publikuje post o podanej treści.
    """
    if "TWOJ_API_KEY" in API_KEY:
        print("BŁĄD: Wklej swoje klucze API z X (Twittera) do pliku agent_social.py!")
        return

    try:
        # Uwierzytelnienie w API v2
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_KEY_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )

        print(f"  [Agent Social] Łączę się z X.com i publikuję posta...")
        
        # Publikowanie posta
        response = client.create_tweet(text=tekst_posta)
        
        print("  [Agent Social] SUKCES! Post został opublikowany.")
        print(f"  [Agent Social] ID posta: {response.data['id']}")
        
    except Exception as e:
        print(f"  [Agent Social] Wystąpił błąd podczas publikacji: {e}")

# Ten blok pozwala na samodzielne uruchomienie tego pliku do testów
if __name__ == '__main__':
    print("--- SOCIAL MEDIA MANAGER: START ---")
    
    # Przykładowy tekst posta. W przyszłości będziemy go pobierać z pliku od Agenta Marketera.
    przykladowy_post = "Automatyzuję swojego bota do publikowania w social mediach za pomocą AI i Pythona! 🚀 #AI #Python #Automatyzacja"
    
    uruchom_agenta_social(przykladowy_post)

    print("--- SOCIAL MEDIA MANAGER: ZAKOŃCZONO ---")