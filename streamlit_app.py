import streamlit as st
import random
import qrcode
from io import BytesIO

# --- CONFIGURAZIONE GIOCO ---
WORDS = ["Pizza", "Colosseo", "Astronauta", "Chitarra", "Gatto", "Internet"]

st.set_page_config(page_title="L'Impostore", layout="centered")

# --- LOGICA DI BACKEND (Simulata) ---
# In una versione reale, useresti un database. Qui usiamo la sessione locale.
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        "word": random.choice(WORDS),
        "imposter_id": random.randint(0, 5), # Esempio per 6 giocatori
        "active": False
    }

def reset_game():
    st.session_state.game_state["word"] = random.choice(WORDS)
    st.session_state.game_state["imposter_id"] = random.randint(0, 10)
    st.session_state.game_state["active"] = True

# --- INTERFACCIA ---
st.title("🕵️ L'Impostore")

# Generazione QR Code (Puntalo all'URL del tuo sito una volta pubblicato)
url = "https://blank-app-5j19v4hfo1b.streamlit.app/" # Cambia questo dopo il deploy
img = qrcode.make(url)
buf = BytesIO()
img.save(buf)
st.image(buf, caption="Inquadra per far entrare gli amici!", width=200)

st.divider()

# Input per il giocatore
player_name = st.text_input("Inserisci il tuo nome")
player_slot = st.number_input("Scegli un numero di sedia (0-10)", min_value=0, max_value=10, step=1)

if st.button("Scopri il tuo Ruolo"):
    if player_slot == st.session_state.game_state["imposter_id"]:
        st.error("SEI L'IMPOSTORE! 🎭")
        st.write("Cerca di capire la parola dagli indizi degli altri.")
    else:
        st.success(f"SEI UN INNOCENTE. La parola segreta è: **{st.session_state.game_state['word']}**")

st.divider()

# Bottone Admin per resettare
if st.button("🔄 Rigenera Ruoli / Nuova Partita"):
    reset_game()
    st.warning("Partita resettata! Tutti devono premere di nuovo 'Scopri il tuo Ruolo'.")