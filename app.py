import streamlit as st
import openai
import requests
import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env se presente (per sviluppo locale)
load_dotenv()

# Configurazione API Keys
# Tenta di recuperare le chiavi da st.secrets (deploy) o variabili d'ambiente (locale)
# La sintassi st.secrets.get() è più robusta per evitare KeyError
XAI_API_KEY = st.secrets.get("XAI_API_KEY") or os.getenv("XAI_API_KEY")
OPENWEATHER_API_KEY = st.secrets.get("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")

if not XAI_API_KEY:
    st.error("Errore: Chiave API Grok (xAI) non configurata!")

if not OPENWEATHER_API_KEY:
    st.error("Errore: Chiave API OpenWeatherMap non configurata!")

# Configura il client per Grok (xAI) usando la libreria OpenAI
if XAI_API_KEY:
    openai.api_key = XAI_API_KEY
    openai.base_url = "https://api.x.ai/v1"

def get_weather(city):
    """
    Recupera i dati meteo per una data città utilizzando OpenWeatherMap API.
    Restituisce una tupla (descrizione, temperatura) o (None, None) in caso di errore.
    """
    if not OPENWEATHER_API_KEY:
        st.error("Chiave API OpenWeatherMap mancante. Configurala in .env o secrets.")
        return None, None

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric", # Per ottenere la temperatura in Celsius
        "lang": "it"       # Risposte in italiano
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status() # Solleva un'eccezione per codici di stato 4xx/5xx
        data = response.json()
        
        weather_desc = data['weather'][0]['description']
        temp = data['main']['temp']
        
        return weather_desc, temp
    except requests.exceptions.HTTPError as err:
        if response.status_code == 404:
            st.error(f"Città '{city}' non trovata. Controlla il nome e riprova.")
        else:
            st.error(f"Errore API Meteo: {err}")
        return None, None
    except Exception as e:
        st.error(f"Si è verificato un errore durante il recupero del meteo: {e}")
        return None, None

def get_ai_recommendation(city, weather_desc, temp):
    """
    Utilizza Grok (xAI) per suggerire una canzone basata sul meteo.
    """
    if not XAI_API_KEY:
        st.error("Chiave API Grok (xAI) mancante. Configurala in .env o secrets.")
        return None

    prompt = (
        f"Il meteo attuale a {city} è '{weather_desc}' con una temperatura di {temp:.1f}°C. "
        "In base a questo contesto atmosferico, suggerisci una sola canzone (Titolo e Artista) "
        "che rifletta il mood della giornata. Rispondi esclusivamente nel formato: 'Titolo - Artista'. "
        "Non aggiungere commenti, virgolette o altro testo."
    )

    try:
        # Implementazione compatibile con client OpenAI configurato per Grok
        from openai import OpenAI
        client = OpenAI(
            api_key=XAI_API_KEY,
            base_url="https://api.x.ai/v1"
        )
        
        response = client.chat.completions.create(
            model="grok-2-latest", # Modello Grok
            messages=[
                {"role": "system", "content": "Sei un esperto curatore musicale sensibile al meteo."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=50
        )
        
        suggestion = response.choices[0].message.content.strip()
        return suggestion
        
    except Exception as e:
        st.error(f"Errore durante la comunicazione con l'IA (Grok): {e}")
        return None

# --- Interfaccia Streamlit ---

st.set_page_config(page_title="Weather-Mood AI", page_icon="🎵")

st.title("🎵 Weather-Mood AI Predictor")
st.subheader("Progetto Universitario: Sistemi Intelligenti / Sviluppo Web Avanzato")
st.markdown("Scopri la colonna sonora perfetta per il tempo fuori dalla tua finestra!")

# Verifica preliminare delle chiavi
if not XAI_API_KEY or "inserisci_qui" in XAI_API_KEY:
    st.warning("⚠️ Grok (xAI) API Key non configurata. Impostala nel file .env o nei secrets.")
if not OPENWEATHER_API_KEY or "inserisci_qui" in OPENWEATHER_API_KEY:
    st.warning("⚠️ OpenWeatherMap API Key non configurata. Impostala nel file .env o nei secrets.")

# Input
col1, col2 = st.columns([3, 1])
with col1:
    city = st.text_input("Inserisci il nome della tua città", placeholder="Es. Roma, Milano, New York...")
with col2:
    # Piccolo hack per allineare il bottone verticalmente con l'input
    st.write("") 
    st.write("")
    analyze_btn = st.button("Analizza Atmosfera")

if analyze_btn and city:
    with st.spinner('Controllo il meteo e consulto l\'Oracolo Musicale...'):
        # 1. Recupero Meteo
        weather_desc, temp = get_weather(city)
        
        if weather_desc is not None:
            # Mostra info meteo
            st.info(f"📍 **Meteo a {city}**: {weather_desc.capitalize()}, {temp:.1f}°C")
            
            # 2. Suggerimento IA
            song_suggestion = get_ai_recommendation(city, weather_desc, temp)
            
            if song_suggestion:
                # Pulizia stringa se necessario (rimozione virgolette residue)
                song_suggestion = song_suggestion.replace('"', '').replace("'", "")
                
                st.success("🎶 L'IA ha scelto per te:")
                st.markdown(f"<h2 style='text-align: center; color: #1DB954;'>{song_suggestion}</h2>", unsafe_allow_html=True)
                
                # 3. Link Spotify
                # Codifica URL per caratteri speciali
                import urllib.parse
                query_encoded = urllib.parse.quote(song_suggestion)
                spotify_url = f"https://open.spotify.com/search/{query_encoded}"
                
                st.markdown(f"""
                <div style="text-align: center; margin-top: 20px;">
                    <a href="{spotify_url}" target="_blank" style="text-decoration: none;">
                        <button style="
                            background-color: #1DB954;
                            color: white;
                            padding: 12px 24px;
                            border: none;
                            border-radius: 25px;
                            font-weight: bold;
                            font-size: 16px;
                            cursor: pointer;
                            transition: transform 0.2s;
                        " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                            🎧 Ascolta su Spotify
                        </button>
                    </a>
                </div>
                """, unsafe_allow_html=True)

elif analyze_btn and not city:
    st.warning("Per favore, inserisci il nome di una città.")

# Footer
st.markdown("---")
st.caption("Powered by Streamlit, Grok (xAI) & OpenWeatherMap")
