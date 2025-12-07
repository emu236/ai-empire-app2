# agent_dataviz.py - GENERATOR WYKRESÓW BIZNESOWYCH
import matplotlib.pyplot as plt
import matplotlib
import json
import os
from openai import OpenAI

# Ustawienie backendu "Agg" jest konieczne dla serwerów/Streamlit (bez okienek)
matplotlib.use('Agg')

def generuj_wykres(temat_rozdzialu, api_key, output_folder, filename):
    client = OpenAI(api_key=api_key)
    
    # 1. AI wymyśla dane do wykresu
    prompt = f"""
    Jesteś analitykiem danych. Tworzysz wsad do e-booka biznesowego.
    Temat rozdziału: "{temat_rozdzialu}".
    
    Twoim zadaniem jest wymyślić WIARYGODNE dane statystyczne pasujące do tego tematu i zwrócić je w formacie JSON.
    Wybierz najlepszy typ wykresu: 'bar' (słupkowy - porównania), 'line' (liniowy - trendy w czasie) lub 'pie' (kołowy - udziały).
    
    Zwróć TYLKO czysty JSON w formacie:
    {{
        "type": "bar", 
        "title": "Tytuł Wykresu",
        "xlabel": "Oś X",
        "ylabel": "Oś Y",
        "data": {{ "Etykieta1": 10, "Etykieta2": 25, "Etykieta3": 15 }}
    }}
    Nie dodawaj żadnych komentarzy, tylko JSON.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        
        data_str = response.choices[0].message.content
        data = json.loads(data_str)
        
        # 2. Rysowanie wykresu (Matplotlib)
        plt.figure(figsize=(10, 6))
        
        # Styl biznesowy
        plt.style.use('bmh') # Czysty styl
        colors = ['#4c72b0', '#55a868', '#c44e52', '#8172b2', '#ccb974', '#64b5cd']
        
        values = list(data['data'].values())
        labels = list(data['data'].keys())
        
        if data['type'] == 'line':
            plt.plot(labels, values, marker='o', linestyle='-', color='#2c3e50', linewidth=2)
            plt.grid(True, linestyle='--', alpha=0.7)
            
        elif data['type'] == 'pie':
            plt.pie(labels=labels, x=values, autopct='%1.1f%%', startangle=140, colors=colors)
            
        else: # Domyślnie BAR (Słupkowy)
            plt.bar(labels, values, color=colors[:len(labels)])
            plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Opisy
        plt.title(data.get('title', 'Wykres'), fontsize=16, fontweight='bold', pad=20)
        if data['type'] != 'pie':
            plt.xlabel(data.get('xlabel', ''), fontsize=12)
            plt.ylabel(data.get('ylabel', ''), fontsize=12)
            
        plt.tight_layout()
        
        # 3. Zapis do pliku
        filepath = os.path.join(output_folder, f"{filename}.png")
        plt.savefig(filepath, dpi=300)
        plt.close() # Ważne: zamykamy wykres, żeby nie zjadł pamięci
        
        return filepath

    except Exception as e:
        print(f"Błąd DataViz: {e}")
        return None