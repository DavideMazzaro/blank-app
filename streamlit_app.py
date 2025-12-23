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

# --- UI DESIGN (DARK THEME & MOBILE OPTIMIZED) ---
st.markdown("""
    <style>
    /* Sfondo e font generale */
    .stApp { background-color: #1e1e1e; color: #ffffff; }
    
    /* Header barra superiore */
    .header-bar {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 0px; border-bottom: 1px solid #333; margin-bottom: 20px;
    }

    /* Badge Giocatori */
    .player-badge { 
        display: inline-block; padding: 10px 18px; margin: 5px; 
        border-radius: 12px; background: #2d2d2d; border: 1px solid #444;
        font-weight: 500; color: #e0e0e0;
    }
    .badge-ready { border-color: #00ff88; color: #00ff88; }

    /* Card del Ruolo */
    .role-card-container {
        background: #2d2d2d; border-radius: 20px; padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center;
        border: 1px solid #444; margin-top: 15px;
    }
    .inner-word-box {
        background: rgba(0,0,0,0.2); border-radius: 15px;
        padding: 20px; margin-top: 15px;
    }

    /* Bottoni */
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.8em; 
        font-weight: 600; transition: 0.3s; border: none;
    }
    
    /* Personalizzazione Switch (Toggle) */
    .stCheckbox label { font-size: 18px !important; color: #bbb !important; }
    
    /* Popover menu */
    div[data-testid="stPopover"] > button {
        background-color: #333 !important; color: white !important; border-radius: 50% !important;
        width: 45px !important; height: 45px !important; padding: 0 !important;
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
    st.markdown("<h1 style='text-align: center;'>🕵️ L'Impostore</h1>", unsafe_allow_html=True)
    new_room = st.text_input("Nome della Stanza", placeholder="es: serata-amici").strip()
    if st.button("CREA STANZA", type="primary"):
        if new_room:
            st.query_params["room"] = new_room
            st.rerun()
    st.stop()

state = load_state(room_id)

# --- HEADER UI ---
st.markdown(f"""
    <div class='header-bar'>
        <div style='font-size: 1.2em; font-weight: bold;'>Stanza: <span style='color:#00ff88;'>{room_id}</span></div>
    </div>
    """, unsafe_allow_html=True)

col_inv, col_set, col_ref = st.columns([1, 1, 1])
with col_inv:
    with st.popover("📲"):
        base_url = "https://blank-app-5j19v4hfo1b.streamlit.app"
        qr_url = f"{base_url}/?room={room_id}"
        qr = qrcode.make(qr_url)
        buf = BytesIO()
        qr.save(buf)
        st.image(buf, use_container_width=True)
        st.caption("Fai scannerizzare questo codice")

with col_set:
    with st.popover("⚙️"):
        st.write("### Lista Parole")
        new_word = st.text_input("Aggiungi parola")
        if st.button("Aggiungi"):
            if new_word and new_word not in state["word_list"]:
                state["word_list"].append(new_word)
                save_state(room_id, state)
                st.rerun()
        if st.button("Reset Default"):
            state["word_list"] = DEFAULT_WORDS
            save_state(room_id, state)
            st.rerun()

with col_ref:
    if st.button("🔄"): st.rerun()

st.divider()

# --- LOGIN / GESTIONE GIOCATORE ---
if "my_name" not in st.session_state:
    st.markdown("### 🚪 Entra nel gioco")
    name = st.text_input("Inserisci il tuo nome").strip()
    if st.button("PARTECIPA", type="primary"):
        if name:
            st.session_state.my_name = name
            state["players"][name] = False
            save_state(room_id, state)
            st.rerun()
else:
    my_name = st.session_state.my_name
    
    # Lista Giocatori (UI Badge)
    st.markdown("### 👥 Giocatori")
    badges_html = "<div style='margin-bottom: 20px;'>"
    ready_count = 0
    for p, ready in state["players"].items():
        status_class = "badge-ready" if ready else ""
        icon = "✅" if ready else "⏳"
        badges_html += f"<span class='player-badge {status_class}'>{icon} {p}</span>"
        if ready: ready_count += 1
    badges_html += "</div>"
    st.markdown(badges_html, unsafe_allow_html=True)
    
    # Logica Lobby
    if state["status"] == "LOBBY":
        is_ready = state["players"].get(my_name, False)
        if not is_ready:
            if st.button("👍 SONO PRONTO", type="primary"):
                state["players"][my_name] = True
                save_state(room_id, state)
                st.rerun()
        else:
            st.success("Sei pronto! Aspettiamo gli altri...")
            if st.button("❌ ANNULLA"):
                state["players"][my_name] = False
                save_state(room_id, state)
                st.rerun()

        if len(state["players"]) >= 3 and ready_count == len(state["players"]):
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 INIZIA PARTITA", type="primary"):
                state["word"] = random.choice(state["word_list"])
                state["imposter"] = random.choice(list(state["players"].keys()))
                state["status"] = "PLAYING"
                save_state(room_id, state)
                st.rerun()

    # --- SCHERMATA GIOCO ---
    if state["status"] == "PLAYING":
        st.markdown("### 🔍 Ruolo Segreto")
        
        # Switch migliorato visivamente
        reveal = st.toggle("Svela il mio ruolo ora")
        
        if reveal:
            if my_name == state["imposter"]:
                st.markdown("""
                    <div class='role-card-container' style='border-top: 5px solid #ff4b4b;'>
                        <h1 style='color: #ff4b4b; margin:0;'>🎭 IMPOSTORE</h1>
                        <div class='inner-word-box'>
                            <p style='color: #bbb;'>Non conosci la parola segreta.<br>Ascolta gli indizi e confondi gli altri!</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='role-card-container' style='border-top: 5px solid #00ff88;'>
                        <h1 style='color: #00ff88; margin:0;'>👑 INNOCENTE</h1>
                        <div class='inner-word-box'>
                            <p style='color: #bbb; margin-bottom: 5px;'>La parola segreta è:</p>
                            <h2 style='font-size: 42px; margin:0; letter-spacing: 2px;'>{state['word'].upper()}</h2>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Attiva lo switch per vedere il tuo ruolo in segreto.")

        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🔄 FINE PARTITA / RESET"):
            for p in state["players"]: state["players"][p] = False
            state["status"] = "LOBBY"
            save_state(room_id, state)
            st.rerun()

    if st.button("🚪 Esci dalla Stanza", use_container_width=True):
        st.query_params.clear()
        st.session_state.clear()
        st.rerun()