import streamlit as st
import requests
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Chiavi API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Configura Gemini con la chiave API
genai.configure(api_key=GEMINI_API_KEY)


def get_youtube_video(query: str) -> str:
    """
    Cerca su YouTube il video corrispondente alla query
    e restituisce il link completo.
    """
    print(f"DEBUG: Cerco su YouTube: {query}") # Debug
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "key": YOUTUBE_API_KEY,
        "maxResults": 1,
        "type": "video"
    }
    
    try:
        response = requests.get(search_url, params=params)
        print(f"DEBUG: YouTube Status Code: {response.status_code}") # Debug
        
        if response.status_code == 200:
            data = response.json()
            if "items" in data and len(data["items"]) > 0:
                video_id = data["items"][0]["id"]["videoId"]
                link = f"https://www.youtube.com/watch?v={video_id}"
                print(f"DEBUG: Video trovato: {link}") # Debug
                return link
            else:
                print("DEBUG: Nessun video trovato nella risposta.")
        else:
            print(f"DEBUG: Errore API YouTube: {response.text}")
    except Exception as e:
        print(f"DEBUG: Eccezione durante ricerca YouTube: {e}")
            
    return None


def get_weather(city: str) -> dict:
    """
    Chiede il meteo corrente a OpenWeather per la città indicata.
    Restituisce un dizionario con descrizione, temperatura e nome città,
    oppure None in caso di errore.
    """
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},it&limit=1&appid={OPENWEATHER_API_KEY}"
    geo_res = requests.get(geo_url).json()

    if geo_res:
        lat = geo_res[0]['lat']
        lon = geo_res[0]['lon']
    
        # 2. Usa le coordinate per il meteo
        weather_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "it",
        }
        response = requests.get(weather_url, params=params)

        if response.status_code != 200:
            return None

        data = response.json()
        print("Dati meteo ricevuti:", data)  # Debug: stampa i dati ricevuti da OpenWeather
        # Estrai solo le info utili
        weather_info = {
            "city": data["name"],
            "description": data["weather"][0]["description"],
            "temp": data["main"]["temp"],
            "icon": data["weather"][0]["icon"],
        }
        return weather_info
    
    return None


def get_song_from_gemini(weather_description: str, city: str, temp: float) -> str:
    """
    Chiede a Gemini di suggerire una canzone adatta al meteo.
    Restituisce solo Titolo e Artista.
    """
    prompt = (
        f"Il meteo attuale a {city} è: {weather_description}, con una temperatura di {temp}°C. "
        "Suggerisci UNA sola canzone (titolo e artista) che si adatti perfettamente a questo meteo. "
        "Rispondi SOLO con il titolo e l'artista, nel seguente formato esatto:\n"
        "Canzone: TITOLO - ARTISTA"
    )

    # Usa il modello Gemini
    model = genai.GenerativeModel('gemini-flash-latest')
    response = model.generate_content(prompt)
    print("Gemini ha risposto:", response.text)  # Debug: stampa la risposta di Gemini
    return response.text


# ───────────────────────── UI STREAMLIT ─────────────────────────

# Configurazione pagina
st.set_page_config(page_title="WeatherSong 🎵", page_icon="🌤️")

st.title("🌤️ WeatherSong 🎵")
st.markdown("Inserisci una città e ti suggerirò una canzone adatta al meteo con il video YouTube!")

# Input utente
city = st.text_input("📍 Inserisci la tua città", placeholder="es. Roma")

if st.button("🔍 Cerca canzone"):
    if not city.strip():
        st.warning("Per favore inserisci il nome di una città.")
    else:
        # Mostra spinner mentre carica
        with st.spinner("Recupero il meteo..."):
            weather = get_weather(city.strip())

        if weather is None:
            st.error("❌ Città non trovata. Controlla il nome e riprova.")
        else:
            # Mostra il meteo
            st.subheader(f"Meteo a {weather['city']}")
            # Icona meteo da OpenWeather
            icon_url = f"https://openweathermap.org/img/wn/{weather['icon']}@2x.png"
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(icon_url, width=80)
            with col2:
                st.metric("Temperatura", f"{weather['temp']}°C")
                st.write(f"**Condizioni:** {weather['description'].capitalize()}")

            # Chiedi la canzone a Gemini
            with st.spinner("Cerco la canzone perfetta..."):
                gemini_response = get_song_from_gemini(
                    weather["description"], weather["city"], weather["temp"]
                )
            
            # Parsing della risposta - Rimuove prefissi comuni e markdown
            clean_response = gemini_response.replace("**", "").replace("*", "").strip()
            if "Canzone:" in clean_response:
                song_title = clean_response.split("Canzone:")[1].strip()
            else:
                song_title = clean_response

            print(f"DEBUG: Titolo estratto per YouTube: {song_title}") # Debug
            
            # Cerca su YouTube
            youtube_link = None
            if song_title:
                with st.spinner(f"Cerco il video per '{song_title}'..."):
                    youtube_link = get_youtube_video(song_title)

            st.divider()
            st.subheader("🎵 Canzone consigliata")
            
            if song_title:
                st.write(f"**{song_title}**")
            else:
                st.write(gemini_response)

            if youtube_link:
                st.link_button("📺 Ascolta su YouTube", youtube_link)
                st.video(youtube_link) # Mostra anche il player integrato se possibile
