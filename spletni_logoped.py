import streamlit as st
from google import genai
import speech_recognition as sr
import os
import difflib  # Za analizo podobnosti besedil

# 1. NASTAVITEV SPLETNE STRANI
st.set_page_config(page_title="Pametni AI Logoped", page_icon="🧠", layout="centered")

st.title("🧠 Pametni AI Logopedski Asistent")
st.write("Različica z mehko logiko primerjave (odpušča drobne šume in nepopolno izgovorjavo).")

# 2. VARNOST IN API KLJUČ
if os.path.exists("gemini_api_key.txt"):
    with open("gemini_api_key.txt", "r") as f:
        api_key = f.read().strip()
elif "gemini_api_key" in st.secrets:
    api_key = st.secrets["gemini_api_key"]
else:
    api_key = st.text_input("Vnesi svoj Gemini API ključ:", type="password")

if not api_key:
    st.warning("Za delovanje vnesite Google Gemini API ključ.")
    st.stop()

client = genai.Client(api_key=api_key)

# 3. NASTAVITVE ZA LOGOPEDA
st.sidebar.header("🎛️ Nastavitve")
glas = st.sidebar.selectbox("Glas za vadbo:", ["R", "Š", "Č", "Ž", "Z", "S", "L"])
tema = st.sidebar.text_input("Tema nalog:", "vesolje")

if "stavek" not in st.session_state:
    st.session_state.stavek = "--- Klikni gumb za generiranje naloge ---"

if st.sidebar.button("🤖 AI Generiraj nalogo"):
    sistemski_prompt = (
        f"Deluješ kot strokovni logopedski asistent za slovenski jezik. "
        f"Ustvari natanko EN kratek, preprost stavek primeren za otroka starosti 5-7 let. "
        f"Stavek mora intenzivno trenirati glas '{glas}' (čim več besed s to črko). "
        f"Vsebina mora biti strogo povezana z motivom: '{tema}'. "
        f"Vrni IZKLUČNO le stavek, napisan z VELIKIMI ČRKAMI, brez pik in narekovajev."
    )
    with st.spinner("AI razmišlja..."):
        try:
            odgovor = client.models.generate_content(model='gemini-2.5-flash', contents=sistemski_prompt)
            st.session_state.stavek = odgovor.text.strip().upper()
        except Exception as e:
            st.error(f"Napaka pri povezavi z AI: {e}")

# 4. OSREDNJI VIZUALNI ZASLON ZA OTROKA
st.markdown("### 📖 Otrok naj glasno prebere:")
st.info(f"## {st.session_state.stavek}")

# 5. MIKROFON IN SNEMANJE ZVOKA Z MEHKO LOGIKO
st.markdown("### 🎤 Poslušanje")
if st.button("▶️ KLIKNI IN GOVORI"):
    prepoznavalnik = sr.Recognizer()
    
    # Maksimalno prilagojeni tajmingi za specifičen ali počasen govor
    prepoznavalnik.pause_threshold = 2.5  
    prepoznavalnik.energy_threshold = 300  # Bolj občutljiv mikrofon za tišji govor
    
    with sr.Microphone() as vir_zvoka:
        st.warning("🔊 Mikrofon posluša... Govorite sproščeno.")
        try:
            prepoznavalnik.adjust_for_ambient_noise(vir_zvoka, duration=0.8)
            posneti_zvok = prepoznavalnik.listen(vir_zvoka, timeout=10, phrase_time_limit=12)
            st.text("🔍 Analiziram posnetek...")
            
            izgovorjeno = prepoznavalnik.recognize_google(posneti_zvok, language="sl-SI").upper()
            if izgovorjeno.endswith('.'):
                izgovorjeno = izgovorjeno[:-1]
                
            st.markdown(f"Računalnik je slišal: **{izgovorjeno}**")
            
            # RAČUNANJE PODOBNOSTI (Fuzzy matching)
            # Razmerje vrne vrednost med 0.0 in 1.0 (npr. 0.85 pomeni 85% uemanje)
            stopnja_ujemanja = difflib.SequenceMatcher(None, st.session_state.stavek, izgovorjeno).ratio()
            procenti = int(stopnja_ujemanja * 100)
            
            st.write(f"Natančnost izgovorjave: **{procenti}%**")
            
            # MEHKA MEJA: Če je uemanje nad 70%, priznamo kot uspeh!
            if stopnja_ujemanja >= 0.70:
                st.success(f"🌟 ODLIČNO! Uspešno opravljena vaja! ({procenti}% uemanje) 🌟")
                st.balloons()
            else:
                st.error("💪 Blizu je bilo! Poskusimo še enkrat, bolj glasno in razločno.")
                st.write("Namig: Poskusite vsako besedo izgovoriti nekoliko bolj poudarjeno.")
                
        except sr.WaitTimeoutError:
            st.error("Čas je potekel. Program ni zaznal začetka govora.")
        except sr.UnknownValueError:
            st.error("Sistem ni uspel pretvoriti zvoka v besedilo. Poskusite govoriti bližje mikrofonu.")
        except Exception as e:
            st.error("Težava z mikrofonom.")