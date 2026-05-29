import streamlit as st
import speech_recognition as r_api  # uvoženo pod r_api za jasnost
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
import difflib
from google import genai
from google.genai import types

# 1. Nastavitev naslova aplikacije
st.title("Pametni AI Logopedski Asistent")
st.write("Aplikacija za preverjanje pravilnosti izgovarjave s pomočjo umetne inteligence.")

# 2. Vnos API ključa na strani (zaradi varnosti v oblaku)
gemini_key = st.text_input("Vpišite vaš Google Gemini API ključ:", type="password")

if not gemini_key:
    st.warning("Za delovanje aplikacije prosim vpišite svoj Gemini API ključ.")
else:
    # Pobuda za uporabnika (stavek, ki ga mora ponoviti)
    if 'stavek' not in st.session_state:
        st.session_state.stavek = "Riba raca rak, hitro teče v potok."

    st.subheader("Naloga za pacienta:")
    st.info(f"Prosim, jasno preberite naslednji stavek: **\"{st.session_state.stavek}\"**")

    st.write("---")
    st.write("Kliknite spodnji gumb, izgovorite stavek in ko zaključite, kliknite 'Zaustavi snemanje'.")

    # 3. Spletni snemalnik zvoka
    avdio_posnetek = mic_recorder(
        start_prompt="🎤 Klikni in govori", 
        stop_prompt="🛑 Zaustavi snemanje", 
        key="logoped_mic"
    )

    if avdio_posnetek:
        # Pridobivanje posnetih bajtov
        zvočni_bajti = avdio_posnetek['bytes']

        # Shranjevanje v začasno datoteko na strežniku
        with open("posnetek.wav", "wb") as f:
            f.write(zvočni_bajti)

        # Prepoznavanje govora z uporabo SpeechRecognition
        recognizer = sr.Recognizer()
        
        try:
            with sr.AudioFile("posnetek.wav") as vir_datoteke:
                avdio_podatki = recognizer.record(vir_datoteke)
            
            # Pretvorba zvoka v tekst preko Google prepoznave (za slovenščino)
            izgovorjeno = recognizer.recognize_google(avdio_podatki, language="sl-SI")
            
            st.success("🤖 Uspešno posneto in prepoznano!")
            st.write(f"**Prepoznano besedilo:** {izgovorjeno}")

            # 4. Izračun stopnje ujemanja (Mehka logika / SequenceMatcher)
            stopnja_ujemanja = difflib.SequenceMatcher(None, st.session_state.stavek.lower(), izgovorjeno.lower()).ratio()
            procent_ujemanja = int(stopnja_ujemanja * 100)
            
            st.write(f"**Natančnost izgovarjave (mehka logika):** {procent_ujemanja}%")

            # 5. Podrobna AI analiza z modelom Gemini
            st.write("---")
            st.subheader("Logopedska analiza umetne inteligence:")
            
            with st.spinner("Umetna inteligenca analizira vaš posnetek..."):
                # Povezava na Gemini API z vpisanim ključem
                client = genai.Client(api_key=gemini_key)
                
                navodilo_za_ai = (
                    f"Deluješ kot strokovni logoped. Pacient je moral prebrati stavek: '{st.session_state.stavek}'. "
                    f"Sistem za prepoznavo govora je zaznal, da je pacient dejansko izgovoril: '{izgovorjeno}'. "
                    f"Matematična stopnja ujemanja je {procent_ujemanja}%. "
                    f"Napiši kratko, spodbudno logopedsko oceno v slovenščini. Izpostavi morebitne napake pri "
                    f"izgovarjavi glasov (npr. napačne črke, izpuščeni glasovi) in podaj kratek nasvet za vajo."
                )

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=navodilo_za_ai,
                )
                
                # Izpis AI rezultata
                st.write(response.text)

        except sr.UnknownValueError:
            st.error("Žal sistem ni uspel razločiti besed. Prosimo, poskusite znova in govorite nekoliko bolj glasno in razločno.")
        except sr.RequestError as e:
            st.error(f"Težava s povezavo do storitve za prepoznavo govora: {e}")
        except Exception as e:
            st.error(f"Prišlo je do nepričakovane napake pri analizi: {e}")
