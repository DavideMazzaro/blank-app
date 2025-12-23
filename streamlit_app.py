import streamlit as st
import json
import os
import random
import qrcode
from io import BytesIO

# --- CONFIGURAZIONE STORAGE ---
ROOMS_DIR = "rooms"
if not os.path.exists(ROOMS_DIR):
    os.makedirs(ROOMS_DIR)

DEFAULT_WORDS = ["Pizza", "Parigi", "Smartphone", "Harry Potter", "Calcio", "Vampiro", "Internet", "Treno"]

# --- STILE CSS MOBILE OPTIMIZED ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.5em; 
        font-size: 16px; text-transform: uppercase; letter-spacing: 1px;
    }
    .player-badge { 
        display: inline-block; padding: 8px 15px; margin: 4px; 
        border-radius: 50px; background: white; border: 2px solid #007bff;
        font-weight: bold; color: #007bff;
    }
    .role-card {
        padding: 30px; border-radius: 20px; text-align: center;
        margin: 20px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI CORE ---
def load_state(room_id):
    path = os.path.join(ROOMS_DIR, f"{room_id}.json")
    if os.path.exists(path):
        with open(path, "r") as f: return json.load(f)
    return {"players": {}, "word": "", "imposter": "", "status": "LOBBY", "word_list": DEFAULT_WORDS}

def save_state(room_id, state):
    with open(os.path.join(ROOMS_DIR, f"{room_id}.json"), "w") as f:
        json.dump(state, f)

# --- GESTIONE URL ---
room_id = st.query_params.get("room")

if not room_id:
    st.title("🕵️ Crea Stanza")
    new_room = st.text_input("Nome della Stanza", placeholder="es: festa-luca").strip()
    if st.button("CREA ORA"):
        if new_room:
            st.query_params["room"] = new_room
            st.rerun()
    st.stop()

# Caricamento stato
state = load_state(room_id)

# --- INTERFACCIA ---
st.title(f"Stanza: {room_id}")

# 1. MENU INVITO E SETTINGS (NASCOSTI)
col_inv, col_set = st.columns(2)
with col_inv:
    with st.popover("📲 Invita"):
        base_url = "https://blank-app-5j19v4hfo1b.streamlit.app"
        qr_url = f"{base_url}/?room={room_id}"
        qr = qrcode.make(qr_url)
        buf = BytesIO()
        qr.save(buf)
        st.image(buf, use_container_width=True)
        st.code(qr_url)

with col_set:
    with st.popover("⚙️ Parole"):
        st.write("### Personalizza Parole")
        new_word = st.text_input("Aggiungi parola")
        if st.button("Aggiungi"):
            if new_word and new_word not in state["word_list"]:
                state["word_list"].append(new_word)
                save_state(room_id, state)
                st.rerun()
        st.write("Lista attuale:", ", ".join(state["word_list"]))
        if st.button("Reset Parole"):
            state["word_list"] = DEFAULT_WORDS
            save_state(room_id, state)
            st.rerun()

st.divider()

# 2. LOGIN / GESTIONE GIOCATORE
if "my_name" not in st.session_state:
    name = st.text_input("Il tuo nome").strip()
    if st.button("ENTRA NELLA STANZA"):
        if name:
            st.session_state.my_name = name
            state["players"][name] = False
            save_state(room_id, state)
            st.rerun()
else:
    my_name = st.session_state.my_name
    
    # Lista Giocatori (UI Badge)
    st.write("### 👥 Giocatori")
    ready_count = 0
    p_cols = st.columns(1)
    badges_html = ""
    for p, ready in state["players"].items():
        icon = "✅" if ready else "⏳"
        badges_html += f"<span class='player-badge'>{icon} {p}</span>"
        if ready: ready_count += 1
    st.markdown(badges_html, unsafe_allow_html=True)
    
    st.write("---")

    # Stato Pronto
    if state["status"] == "LOBBY":
        is_ready = state["players"].get(my_name, False)
        if not is_ready:
            if st.button("👍 SONO PRONTO"):
                state["players"][my_name] = True
                save_state(room_id, state)
                st.rerun()
        else:
            st.info("Attesa altri giocatori...")
            if st.button("❌ NON PRONTO"):
                state["players"][my_name] = False
                save_state(room_id, state)
                st.rerun()

        # Avvio Partita
        if len(state["players"]) >= 3 and ready_count == len(state["players"]):
            if st.button("🚀 INIZIA PARTITA", type="primary"):
                state["word"] = random.choice(state["word_list"])
                state["imposter"] = random.choice(list(state["players"].keys()))
                state["status"] = "PLAYING"
                save_state(room_id, state)
                st.rerun()

    # 3. GIOCO IN CORSO
    if state["status"] == "PLAYING":
        st.markdown("### 🔍 Ruolo Segreto")
        reveal = st.toggle("Svela il mio ruolo")
        
        if reveal:
            if my_name == state["imposter"]:
                st.markdown("""
                    <div class='role-card' style='background-color: #dc3545; color: white;'>
                        <h1>🎭 IMPOSTORE</h1>
                        <p>Non conosci la parola! Ascolta gli altri e bluffa.</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='role-card' style='background-color: #28a745; color: white;'>
                        <h1>😇 INNOCENTE</h1>
                        <p>La parola segreta è:</p>
                        <h2 style='font-size: 40px;'>{state['word']}</h2>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Attiva lo switch sopra per vedere chi sei (occhio a chi ti sta vicino!)")

        if st.button("🔄 NUOVA PARTITA / RESET"):
            for p in state["players"]: state["players"][p] = False
            state["status"] = "LOBBY"
            save_state(room_id, state)
            st.rerun()

# 4. BOTTONE AGGIORNA (Per vedere chi si aggiunge o se la partita inizia)
if st.button("🔄 AGGIORNA STATO STANZA"):
    st.rerun()