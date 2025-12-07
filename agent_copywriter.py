# agent_copywriter.py - Pisze posty na IG

from openai import OpenAI

def napisz_post(imie: str, styl_bycia: str, sytuacja: str, klucz_api: str) -> str:
    client = OpenAI(api_key=klucz_api)
    
    prompt = f"""
    Jesteś wirtualną influencerką o imieniu {imie}.
    Twój styl bycia/charakter: {styl_bycia}.
    
    Właśnie zrobiłaś sobie zdjęcie: {sytuacja}.
    
    Napisz krótki, angażujący post na Instagram (w języku Polskim).
    Używaj emoji. Dodaj 5-10 trafnych hashtagów.
    Bądź naturalna, nie brzmij jak robot.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Błąd generowania tekstu."