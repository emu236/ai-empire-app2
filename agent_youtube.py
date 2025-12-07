# agent_youtube.py - Wersja Pancerna (yt-dlp)

import yt_dlp
import requests
from openai import OpenAI

def pobierz_transkrypcje(video_url):
    print(f"  [YouTube Agent] Analizuję wideo: {video_url}...")
    
    # Konfiguracja yt-dlp (tylko metadane, bez pobierania wideo)
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,      # Pobieraj też automatyczne
        'subtitleslangs': ['pl', 'en'], # Preferuj polskie, potem angielskie
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 1. Pobieramy informacje o filmie
            info = ydl.extract_info(video_url, download=False)
            
            # 2. Szukamy napisów
            subs = info.get('subtitles', {})
            auto_subs = info.get('automatic_captions', {})
            
            # Priorytety językowe: PL ręczne -> EN ręczne -> PL auto -> EN auto
            final_subs = None
            if 'pl' in subs: final_subs = subs['pl']
            elif 'en' in subs: final_subs = subs['en']
            elif 'pl' in auto_subs: final_subs = auto_subs['pl']
            elif 'en' in auto_subs: final_subs = auto_subs['en']
            
            if not final_subs:
                return None, "Nie znaleziono żadnych napisów (ani PL, ani EN) dla tego filmu."

            # 3. Wyciągamy URL do pliku z tekstem (szukamy formatu json3 lub vtt)
            sub_url = None
            for fmt in final_subs:
                if fmt.get('ext') == 'json3':
                    sub_url = fmt.get('url')
                    break
            if not sub_url:
                # Fallback - bierzemy pierwszy lepszy format
                sub_url = final_subs[0]['url']

            print(f"  [YouTube Agent] Pobieram tekst napisów z URL...")
            
            # 4. Pobieramy treść
            r = requests.get(sub_url)
            
            # Parsowanie JSON3 (YouTube'owy format napisów)
            if 'json3' in sub_url or 'json' in r.headers.get('Content-Type', ''):
                try:
                    data = r.json()
                    text_segments = []
                    # Wyciągamy czysty tekst z gąszcza JSONa
                    events = data.get('events', [])
                    for event in events:
                        segs = event.get('segs', [])
                        for seg in segs:
                            utf8 = seg.get('utf8', '')
                            if utf8 and utf8 != '\n':
                                text_segments.append(utf8)
                    
                    full_text = "".join(text_segments).replace('\n', ' ')
                    return full_text, None
                except:
                    return r.text, None # Zwracamy surowy tekst jak parsowanie zawiedzie
            else:
                # Jeśli to VTT/XML - GPT sobie z tym poradzi, zwracamy surowe
                return r.text, None

    except Exception as e:
        return None, f"Błąd yt-dlp: {str(e)}"

def repurpose_content(tekst_wideo, format_docelowy, klucz_api):
    client = OpenAI(api_key=klucz_api)
    
    prompty = {
        "Blog": "Napisz profesjonalny artykuł na bloga (SEO, nagłówki H2/H3) na podstawie poniższego tekstu. Dodaj wstęp i podsumowanie.",
        "Twitter": "Stwórz wiralowy wątek na Twittera (Thread, max 10 tweetów) z tego tekstu. Użyj emoji.",
        "LinkedIn": "Napisz angażujący post biznesowy na LinkedIn na podstawie tego tekstu. Styl storytelling.",
        "Newsletter": "Napisz e-mail do newslettera streszczający ten materiał. Zachęć do kliknięcia w wideo."
    }
    
    system_prompt = prompty.get(format_docelowy, "Streaszcz ten tekst.")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem content marketingu."},
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Treść wideo (może zawierać znaczniki czasu, ignoruj je): {tekst_wideo[:15000]}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Błąd AI: {e}"