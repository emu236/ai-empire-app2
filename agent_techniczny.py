from openai import OpenAI

def uruchom_technika(opis_rezysera: str, proporcje: str, klucz_api: str) -> str:
    client = OpenAI(api_key=klucz_api)
    
    prompt = f"""
    Jesteś inżynierem promptów wideo (Video Prompt Engineer) dla modeli Veo, Sora i Runway.
    Przekształć opis reżysera w idealny techniczny prompt.
    
    OPIS: "{opis_rezysera}"
    PROPORCJE: {proporcje}
    
    Zasady:
    1. Zacznij od rodzaju ujęcia (np. "Wide shot of...", "Drone footage of...").
    2. Zachowaj najważniejsze detale wizualne.
    3. Dodaj na końcu tagi jakości: "4k, highly detailed, photorealistic, cinematic lighting, 60fps".
    4. Zwróć TYLKO gotowy prompt w języku angielskim.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are an AI Video Prompt Expert."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"