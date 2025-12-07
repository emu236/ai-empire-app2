from openai import OpenAI

def uruchom_rezysera(pomysl_uzytkownika: str, styl: str, klucz_api: str) -> str:
    client = OpenAI(api_key=klucz_api)
    
    prompt = f"""
    Jesteś światowej klasy reżyserem filmowym i operatorem kamery (DoP). 
    Twoim zadaniem jest rozpisanie krótkiego pomysłu użytkownika na szczegółową, wizualną scenę wideo.
    
    POMYSŁ: "{pomysl_uzytkownika}"
    STYL: {styl}
    
    Opisz to w JEDNYM spójnym akapicie po ANGIELSKU. Skup się na:
    1. Oświetleniu (np. cinematic, neon, natural).
    2. Ruchu kamery (np. drone shot, pan, static).
    3. Wyglądzie obiektów i tła.
    4. Atmosferze.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are an expert film director."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"