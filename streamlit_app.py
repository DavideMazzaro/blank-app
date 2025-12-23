import streamlit as st
import json
import os
import random
import qrcode
from io import BytesIO

# --- CONFIGURAZIONE ---
ROOMS_DIR = "rooms"
if not os.path.exists(ROOMS_DIR):
    os.makedirs(ROOMS_DIR)

WORDS = ["Pizza", "Parigi", "Smartphone", "Harry Potter", "Calcio", "Vampiro", "Internet", "Treno"]

# --- GESTIONE DATI STANZA ---
def get_room_path(room_id):
    return os.path.join(ROOMS_DIR, f"{room_id}.json")

def load_state(room_id):
    path = get_room_path(room_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"players": {}, "word": "", "imposter": "", "status": "LOBBY"}

def save_state(room_id, state):
    with open(get_room_path(room_id), "w") as f:
        json.dump(state, f)

# --- LOGICA URL E QR ---
st.set_page_config(page_title="L'Impostore", layout="centered")

# Recupera il room_id dall'URL (es. ?room=ABCD)
query_params = st.query_params
room_id = query_params.get("room")

if not room_id:
    st.title("🕵️ Crea una Nuova Stanza")
    new_room = st.text_input("Inserisci un nome per la stanza (es. 'serata-pizza'):").strip()
    if st.button("Crea Stanza"):
        if new_room:
            st.query_params["room"] = new_room
            st.rerun()
    st.stop()

# --- INTERFACCIA STANZA ---
st.title(f"🕵️ Stanza: {room_id}")
state = load_state(room_id)

# Generazione QR Code dinamico con room_id
base_url = "https://blank-app-5j19v4hfo1b.streamlit.app" # SOSTITUISCI CON IL TUO URL DOPO IL DEPLOY
room_url = f"{base_url}/?room={room_id}"

qr = qrcode.make(room_url)
buf = BytesIO()
qr.save(buf)
st.image(buf, width=150, caption="Inquadra per far entrare gli amici in questa stanza")

st.divider()

# --- GESTIONE GIOCATORE ---
name = st.text_input("Il tuo Nome:").strip()

if name:
    if name not in state["players"]:
        state["players"][name] = False
        save_state(room_id, state)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ SONO PRONTO"):
            state["players"][name] = True
            save_state(room_id, state)
            st.rerun()
    with col2:
        if st.button("❌ NON PRONTO"):
            state["players"][name] = False
            save_state(room_id, state)
            st.rerun()

# --- STATO DELLA STANZA ---
st.subheader("Giocatori")
ready_count = 0
for p, ready in state["players"].items():
    icon = "✅" if ready else "⏳"
    st.write(f"{icon} {p}")
    if ready: ready_count += 1

# --- AVVIO GIOCO ---
if state["status"] == "LOBBY":
    if ready_count >= 3 and ready_count == len(state["players"]):
        if st.button("🚀 INIZIA PARTITA"):
            state["word"] = random.choice(WORDS)
            state["imposter"] = random.choice(list(state["players"].keys()))
            state["status"] = "PLAYING"
            save_state(room_id, state)
            st.rerun()
    elif len(state["players"]) < 3:
        st.info("In attesa di almeno 3 giocatori...")

# --- RUOLI ---
if state["status"] == "PLAYING":
    st.success("Partita in corso!")
    if name in state["players"]:
        if st.button("👁️ SCOPRI IL TUO RUOLO"):
            if name == state["imposter"]:
                st.error("🎭 SEI L'IMPOSTORE!")
                st.write("Non conosci la parola. Ascolta gli altri e sopravvivi!")
            else:
                st.info(f"INNOCENTE. La parola è: **{state['word']}**")
    
    if st.button("🔄 NUOVA PARTITA / RESET"):
        # Resetta la stanza ma mantiene i giocatori (mettendoli a "non pronto")
        for p in state["players"]: state["players"][p] = False
        state["status"] = "LOBBY"
        state["word"] = ""
        state["imposter"] = ""
        save_state(room_id, state)
        st.rerun()

# Tasto per cambiare stanza
if st.button("🚪 Esci dalla stanza"):
    st.query_params.clear()
    st.rerun()