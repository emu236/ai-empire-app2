# agent_brain.py - Wersja "Pancerna" (Bez LangChain Chains)

import os
import shutil
# Importujemy tylko to, co jest stabilne i na pewno działa
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS

def zbuduj_indeks(pliki_pdf, klucz_api):
    """
    Tworzy bazę wiedzy z przesłanych plików PDF.
    """
    if not pliki_pdf:
        return None

    print("  [Brain] Przetwarzam dokumenty...")
    
    # 1. Zapisz pliki tymczasowo
    temp_dir = "temp_docs"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    wszystkie_dokumenty = []
    
    try:
        for plik in pliki_pdf:
            sciezka = os.path.join(temp_dir, plik.name)
            with open(sciezka, "wb") as f:
                f.write(plik.getbuffer())
                
            # Wczytaj PDF
            loader = PyPDFLoader(sciezka)
            docs = loader.load()
            wszystkie_dokumenty.extend(docs)
            
        # 2. Podziel tekst na kawałki
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(wszystkie_dokumenty)
        
        print(f"  [Brain] Stworzono {len(chunks)} fragmentów wiedzy.")

        # 3. Stwórz Embeddings i Bazę
        embeddings = OpenAIEmbeddings(api_key=klucz_api)
        vectorstore = FAISS.from_documents(chunks, embeddings)
        
        return vectorstore

    except Exception as e:
        print(f"  [Brain] Błąd budowania indeksu: {e}")
        return None
    finally:
        # Sprzątanie
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def zapytaj_baze(vectorstore, pytanie, klucz_api):
    """
    Zadaje pytanie do bazy wiedzy (Metoda ręczna - bez RetrievalQA).
    """
    try:
        # 1. Wyszukaj 3 najbardziej podobne fragmenty w bazie
        docs = vectorstore.similarity_search(pytanie, k=3)
        
        if not docs:
            return {'result': "Nie znalazłem informacji w dokumentach.", 'source_documents': []}

        # 2. Zbuduj kontekst (sklej fragmenty w jeden tekst)
        kontekst = "\n\n".join([f"FRAGMENT {i+1}: {d.page_content}" for i, d in enumerate(docs)])
        
        # 3. Wyślij zapytanie do GPT-4o z kontekstem
        llm = ChatOpenAI(model="gpt-4o", api_key=klucz_api, temperature=0)
        
        prompt = f"""
        Jesteś inteligentnym asystentem. Odpowiedz na pytanie użytkownika WYŁĄCZNIE na podstawie poniższego kontekstu.
        Jeśli w kontekście nie ma odpowiedzi, napisz "Nie wiem tego na podstawie dostarczonych dokumentów".

        --- KONTEKST Z DOKUMENTÓW ---
        {kontekst}
        --- KONIEC KONTEKSTU ---

        PYTANIE: {pytanie}
        """
        
        odpowiedz = llm.invoke(prompt)
        
        # 4. Zwróć wynik w formacie zgodnym z aplikacją
        return {
            'result': odpowiedz.content,
            'source_documents': docs
        }

    except Exception as e:
        return {'result': f"Błąd podczas pytania: {e}", 'source_documents': []}