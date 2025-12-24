import streamlit as st
import json
import os
import random
import qrcode
from io import BytesIO
from faker import Faker

# --- INIZIALIZZAZIONE FAKER ---
fake = Faker('it_IT')

# --- CONFIGURAZIONE STORAGE ---
ROOMS_DIR = "rooms"
if not os.path.exists(ROOMS_DIR):
    os.makedirs(ROOMS_DIR)

# Funzione per generare una lista di parole casuali sempre diverse
def generate_random_words(n=20):
    categories = [
        lambda: fake.city(),
        lambda: fake.job(),
        lambda: fake.color_name(),
        lambda: fake.word().capitalize(),
        lambda: fake.first_name()
    ]
    words = []
    for _ in range(n):
        words.append(random.choice(categories)())
    return list(set(words)) # Rimuove eventuali duplicati

# --- UI DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #1e1e1e; color: #ffffff; }
    .header-bar { display: flex; justify-content: space-between; align-items: center; padding: 10px 0px; border-bottom: 1px solid #333; margin-bottom: 20px; }
    .player-badge { display: inline-block; padding: 10px 18px; margin: 5px; border-radius: 12px; background: #2d2d2d; border: 1px solid #444; font-weight: 500; color: #e0e0e0; }
    .badge-ready { border-color: #00ff88; color: #00ff88; box-shadow: 0 0 5px #00ff88; }
    .role-card-container { background: #2d2d2d; border-radius: 20px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center; border: 1px solid #444; margin-top: 15px; }
    .inner-word-box { background: #1a2e1f; border-radius: 15px; padding: 25px; margin-top: 15px; border: 1px solid #2d5a3c; }
    .inner-imposter-box { background: #2e1a1a; border-radius: 15px; padding: 25px; margin-top: 15px; border: 1px solid #5a2d2d; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.8em; font-weight: 600; border: none; }
    div[data-testid="stPopover"] > button { background-color: #333 !important; color: white !important; border-radius: 50% !important; width: 45px !important; height: 45px !important; padding: 0 !important; border: 1px solid #555 !important; }
    </style>
    """, unsafe_allow_html=True)

def load_state(room_id):
    path = os.path.join(ROOMS_DIR, f"{room_id}.json")
    if os.path.exists(path):
        try:
            with open(path, "r") as f: return json.load(f)
        except: pass
    return {"players": {}, "word": "", "imposter": "", "status": "LOBBY", "word_list":  [
    "casa", "scuola", "auto", "libro", "amico", "gatto", "cane", "bicicletta", "albero", "mela", 
    "tavolo", "sedia", "telefono", "finestra", "porta", "cielo", "sole", "pioggia", "giorno", "notte", 
    "acqua", "fuoco", "strada", "montagna", "mare", "spiaggia", "fiume", "lago", "foresta", "giardino", 
    "città", "paese", "villaggio", "pianta", "fiore", "banco", "zaino", "penna", "matita", "gomma", 
    "cartella", "professore", "studente", "lezione", "compito", "esame", "viaggio", "vacanza", "lavoro"
]
}

def save_state(room_id, state):
    with open(os.path.join(ROOMS_DIR, f"{room_id}.json"), "w") as f:
        json.dump(state, f)

# --- GESTIONE URL ---
room_id = st.query_params.get("room")
if not room_id:
    st.markdown("<h1 style='text-align: center; color: #00ff88;'>🕵️ L'Impostore</h1>", unsafe_allow_html=True)
    new_room = st.text_input("Nome della Stanza", placeholder="es: serata-amici").strip()
    if st.button("CREA STANZA", type="primary"):
        if new_room:
            st.query_params["room"] = new_room
            st.rerun()
    st.stop()

state = load_state(room_id)

# --- HEADER ---
st.markdown(f"<div class='header-bar'><div style='font-size: 1.2em; font-weight: bold;'>Stanza: <span style='color:#00ff88;'>{room_id}</span></div></div>", unsafe_allow_html=True)

col_inv, col_set, col_ref = st.columns([1, 1, 1])
with col_inv:
    with st.popover("📲"):
        base_url = "https://blank-app-5j19v4hfo1b.streamlit.app"
        qr_url = f"{base_url}/?room={room_id}"
        qr = qrcode.make(qr_url)
        buf = BytesIO()
        qr.save(buf)
        st.image(buf, width='stretch')
        st.caption("Fai inquadrare per entrare")

with col_set:
    with st.popover("⚙️"):
        st.write("### Gestione Parole")
        if st.button("🎲 Rigenera lista casuale"):
            state["word_list"] =  [
    "casa", "scuola", "auto", "libro", "amico", "gatto", "cane", "bicicletta", "albero", "mela", 
    "tavolo", "sedia", "telefono", "finestra", "porta", "cielo", "sole", "pioggia", "giorno", "notte", 
    "acqua", "fuoco", "strada", "montagna", "mare", "spiaggia", "fiume", "lago", "foresta", "giardino", 
    "città", "paese", "villaggio", "pianta", "fiore", "banco", "zaino", "penna", "matita", "gomma", 
    "cartella", "professore", "studente", "lezione", "compito", "esame", "viaggio", "vacanza", "lavoro"
]

            save_state(room_id, state)
            st.rerun()
        new_word = st.text_input("Aggiungi parola manuale")
        if st.button("Aggiungi"):
            if new_word and new_word not in state["word_list"]:
                state["word_list"].append(new_word)
                save_state(room_id, state)
                st.rerun()
        st.write("Lista attuale:", ", ".join(state["word_list"]))

with col_ref:
    if st.button("🔄"): st.rerun()

st.divider()

# --- LOGIN ---
if "my_name" not in st.session_state:
    st.markdown("### 🚪 Chi sei?")
    name = st.text_input("Nome").strip()
    if st.button("PARTECIPA", type="primary"):
        if name:
            st.session_state.my_name = name
            state["players"][name] = False
            save_state(room_id, state)
            st.rerun()
else:
    my_name = st.session_state.my_name
    
    st.markdown("### 👥 Giocatori")
    badges_html = "<div>"
    ready_count = 0
    for p, ready in state["players"].items():
        status_class = "badge-ready" if ready else ""
        icon = "✅" if ready else "⏳"
        badges_html += f"<span class='player-badge {status_class}'>{icon} {p}</span>"
        if ready: ready_count += 1
    badges_html += "</div>"
    st.markdown(badges_html, unsafe_allow_html=True)
    
    if state["status"] == "LOBBY":
        is_ready = state["players"].get(my_name, False)
        if not is_ready:
            if st.button("👍 SONO PRONTO", type="primary"):
                state["players"][my_name] = True
                save_state(room_id, state)
                st.rerun()
        else:
            st.success("Sei pronto! In attesa degli altri...")
            if st.button("❌ ANNULLA"):
                state["players"][my_name] = False
                save_state(room_id, state)
                st.rerun()

        if len(state["players"]) >= 3 and ready_count == len(state["players"]):
            if st.button("🚀 INIZIA NUOVO TURNO", type="primary"):
                # Prende una parola casuale dalla lista generata da Faker
                state["word"] = random.choice(state["word_list"])
                state["imposter"] = random.choice(list(state["players"].keys()))
                state["status"] = "PLAYING"
                for p in state["players"]: state["players"][p] = False
                save_state(room_id, state)
                st.rerun()

    # --- IN GIOCO ---
    if state["status"] == "PLAYING":
        st.markdown("### 🔍 Ruolo Segreto")
        reveal = st.toggle("Svela il mio ruolo")
        
        if reveal:
            if my_name == state["imposter"]:
                st.markdown("""
                    <div class='role-card-container' style='border-top: 5px solid #ff4b4b;'>
                        <h1 style='color: #ff4b4b; margin:0;'>🎭 SEI L'IMPOSTORE</h1>
                        <div class='inner-imposter-box'>
                            <p style='color: #ffaaaa;'>Fingi di conoscere la parola!</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='role-card-container' style='border-top: 5px solid #00ff88;'>
                        <h1 style='color: #00ff88; margin:0;'>👑 INNOCENTE</h1>
                        <div class='inner-word-box'>
                            <p style='color: #aaffcc; margin-bottom: 5px;'>La parola è:</p>
                            <h2 style='font-size: 40px; margin:0; color: white;'>{state['word'].upper()}</h2>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='height: 120px; display: flex; align-items: center; justify-content: center; background: #2d2d2d; border-radius: 20px; border: 1px dashed #555; color: #888;'>Usa lo switch per vedere chi sei</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🏁 FINE TURNO (NUOVA PARTITA)", type="primary"):
            state["status"] = "LOBBY"
            state["word"] = ""
            state["imposter"] = ""
            # Rigeneriamo anche la lista per il prossimo turno così è sempre fresca
            state["word_list"] =  [
    "casa", "scuola", "auto", "libro", "amico", "gatto", "cane", "bicicletta", "albero", "mela", 
    "tavolo", "sedia", "telefono", "finestra", "porta", "cielo", "sole", "pioggia", "giorno", "notte", 
    "acqua", "fuoco", "strada", "montagna", "mare", "spiaggia", "fiume", "lago", "foresta", "giardino", 
    "città", "paese", "villaggio", "pianta", "fiore", "banco", "zaino", "penna", "matita", "gomma", 
    "cartella", "professore", "studente", "lezione", "compito", "esame", "viaggio", "vacanza", "lavoro"
]

            for p in state["players"]: state["players"][p] = False
            save_state(room_id, state)
            st.rerun()

    if st.button("🚪 Esci dalla Stanza", width='stretch'):
        st.query_params.clear()
        st.session_state.clear()
        st.rerun()