🎵 AI Weather-Mood Predictor (University Project v1.0)
Progetto per l'esame di: Sistemi Intelligenti / Sviluppo Web Avanzato
Questo progetto è un'applicazione web sperimentale che utilizza l'Intelligenza Artificiale per analizzare il contesto meteorologico locale e suggerire una traccia musicale che si adatti all'atmosfera ("mood") del momento.

Il sistema integra API di terze parti per il recupero dei dati meteo, elaborazione del linguaggio naturale (LLM) per il suggerimento e generazione dinamica di link di ricerca musicale.

🛠️ Stack Tecnologico Richiesto
Linguaggio: Python 3.9+

Frontend: Streamlit (per una UI web reattiva e veloce)

LLM Backend: OpenAI API (Modello gpt-3.5-turbo o gpt-4o)

Weather Data: OpenWeatherMap API (per dati meteo reali)

Integrazione: Link di ricerca dinamica su Spotify

🚀 Istruzioni per l'implementazione (Task per l'AI)
Implementa il file app.py seguendo rigorosamente questa logica:

1. Configurazione Iniziale
Gestisci le API Key (OpenAI e OpenWeatherMap) tramite i "Secrets" di Streamlit (st.secrets) o un file .env.

Importa le librerie necessarie: streamlit, openai, requests.

2. Funzione: Recupero Meteo (get_weather)
Crea una funzione che accetta il nome di una città.

Interroga l'API di OpenWeatherMap per ottenere la descrizione del meteo (es. "nuvoloso", "pioggia leggera", "cielo sereno") e la temperatura.

3. Funzione: Suggerimento IA (get_ai_recommendation)
Invia un prompt all'API OpenAI strutturato così:

"Il meteo attuale a [Città] è [Descrizione Meteo] con una temperatura di [Gradi]°C. In base a questo contesto atmosferico, suggerisci una sola canzone (Titolo e Artista) che rifletta il mood della giornata. Rispondi esclusivamente nel formato: 'Titolo - Artista'. Non aggiungere commenti."

4. Interfaccia Utente (Streamlit)
Header: Titolo accattivante ("Weather-Mood AI Predictor") e un sottotitolo che richiami il progetto universitario.

Input: Una barra di ricerca di testo per inserire la città.

Azione: Un pulsante "Analizza Atmosfera".

Output: * Mostra un riquadro con i dati meteo correnti.

Mostra la canzone suggerita dall'IA con un font in evidenza.

Call to Action: Genera un pulsante o un link cliccabile che porti alla ricerca di quella canzone su Spotify (https://open.spotify.com/search/[Titolo+Artista]).

5. Gestione Errori
Se la città non viene trovata o le API falliscono, mostra un messaggio di errore pulito (st.error) invece del crash del codice.

📂 Struttura File suggerita
app.py (Il core dell'applicazione)

requirements.txt (Contenente: streamlit, openai, requests, python-dotenv)

.env (Per lo sviluppo locale - non caricare su GitHub)

📝 Note per il Testing
L'applicazione deve essere testata simulando diverse condizioni meteo per verificare la coerenza dei suggerimenti dell'IA (es. Jazz/Lo-fi per pioggia, Pop/Disco per sole).