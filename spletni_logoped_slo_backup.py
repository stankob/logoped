import streamlit as st
from streamlit_mic_recorder import mic_recorder
from google import genai
from google.genai import types

# 1. Nastavitev naslova aplikacije
st.title("Pametni AI Logopedski Asistent")
st.write("Aplikacija za preverjanje pravilnosti izgovarjave s pomočjo umetne inteligence.")

# Samodejno preberemo skriti API ključ iz nastavitev strežnika
try:
    gemini_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Napaka: API ključ ni nastavljen v Streamlit Secrets. Prosimo, uredite nastavitve aplikacije.")
    st.stop()

# Pobuda za uporabnika (stavek, ki ga mora ponoviti)
if 'stavek' not in st.session_state:
    st.session_state.stavek = "Riba raca rak, hitro teče v potok."

st.subheader("Naloga za pacienta:")
st.info(f"Prosim, jasno preberite naslednji stavek: **\"{st.session_state.stavek}\"**")

st.write("---")
st.write("Kliknite spodnji gumb, izgovorite stavek in ko zaključite, kliknite 'Zaustavi snemanje'.")

# 2. Spletni snemalnik zvoka
avdio_posnetek = mic_recorder(
    start_prompt="🎤 Klikni in govori", 
    stop_prompt="🛑 Zaustavi snemanje", 
    key="logoped_mic"
)

if avdio_posnetek:
    zvočni_bajti = avdio_posnetek['bytes']

    st.success("🤖 Uspešno posneto!")
    
    # 3. Podrobna AI analiza neposredno iz ZVOKA z modelom Gemini
    st.write("---")
    st.subheader("Logopedska analiza umetne inteligence:")
    
    with st.spinner("Umetna inteligenca posluša posnetek in analizira izgovarjavo..."):
        try:
            # Povezava na Gemini API s samodejno prebranim ključem
            client = genai.Client(api_key=gemini_key)
            
            # Pripravimo navodilo za AI
            navodilo_za_ai = (
                f"Deluješ kot strokovni logoped. Pacient je dobil nalogo, da glasno in jasno prebere "
                f"naslednji stavek: '{st.session_state.stavek}'. "
                f"Tvoja naloga is, da poslušaš priloženi zvočni posnetek pacienta in izvedeš naslednje korake:\n"
                f"1. Natančno zapiši besedilo, ki ga slišiš v posnetku.\n"
                f"2. Oceni pravilnost in natančnost izgovarjave glasov v slovenščini (izpostavi npr. napačne glasove, izpuščene črke).\n"
                f"3. Podaj kratko, spodbudno logopedsko oceno in koristen nasvet za izboljšanje.\n\n"
                f"Odgovori izključno v slovenskem jeziku."
            )

            # Pošljemo vsebino modelu
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_bytes(
                        data=bytes(zvočni_bajti),
                        mime_type='audio/wav',
                    ),
                    navodilo_za_ai
                ]
            )
            
            # Izpis končnega rezultata
            st.write(response.text)

        except Exception as e:
            st.error(f"Prišlo je do napake pri komunikaciji z Gemini AI: {e}")
