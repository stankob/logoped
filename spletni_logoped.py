import streamlit as st
from google import genai
import speech_recognition as sr
import os
import difflib  # Za analizo podobnosti besedil
from streamlit_mic_recorder import mic_recorder

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

# Prikaže lep gumb z ikono mikrofona neposredno v brskalniku
avdio_posnetek = mic_recorder(start_prompt="Klikni in govori", stop_prompt="Zaustavi snemanje", key="logoped_mic")

if avdio_posnetek:
    # Ko uporabnik konča, vzamemo zvočne bajte
    zvočni_bajti = avdio_posnetek['bytes']

    # Shranimo jih v datoteko za SpeechRecognition
    with open("posnetek.wav", "wb") as f:
        f.write(zvočni_bajti)

    # Preberemo z recognizerjem
    with sr.AudioFile("posnetek.wav") as vir_datoteke:
        avdio_podatki = sr.Recognizer().record(vir_datoteke)
        # Tukaj naprej teče vaša nespremenjena logika (npr. recognizer.recognize_google...)

    # Preberemo z recognizerjem
    with sr.AudioFile("posnetek.wav") as vir_datoteke:
        avdio_podatki = sr.Recognizer().record(vir_datoteke)
    # Tukaj naprej teče vaša nespremenjena logika (npr. recognizer.recognize_google...)
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
