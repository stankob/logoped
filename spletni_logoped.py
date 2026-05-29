import streamlit as st
from streamlit_mic_recorder import mic_recorder
import difflib
from google import genai
from google.genai import types

# 1. Nastavitev naslova aplikacije
st.title("Pametni AI Logopedski Asistent")
st.write("Aplikacija za preverjanje pravilnosti izgovarjave s pomočjo umetne inteligence.")

# 2. Vnos API ključa na strani
gemini_key = st.text_input("Vpišite vaš Google Gemini API ključ:", type="password")

if not gemini_key:
    st.warning("Za delovanje aplikacije prosim vpišite svoj Gemini API ključ.")
else:
    # Pobuda za uporabnika
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
        zvočni_bajti = avdio_posnetek['bytes']
        tip_posnetka = avdio_posnetek['sample_rate'] # pomaga določiti strukturo

        st.success("🤖 Uspešno posneto!")
        
        # 4. Podrobna AI analiza neposredno iz ZVOKA z modelom Gemini
        st.write("---")
        st.subheader("Logopedska analiza umetne inteligence:")
        
        with st.spinner("Umetna inteligenca posluša posnetek in analizira izgovarjavo..."):
            try:
                # Povezava na Gemini API
                client = genai.Client(api_key=gemini_key)
                
                # Pripravimo navodilo za AI
                navodilo_za_ai = (
                    f"Deluješ kot strokovni logoped. Pacient je dobil nalogo, da glasno in jasno prebere "
                    f"naslednji stavek: '{st.session_state.stavek}'. "
                    f"Tvoja naloga je, da poslušaš priloženi zvočni posnetek pacienta in izvedeš naslednje korake:\n"
                    f"1. Natančno zapiši besedilo, ki ga slišiš v posnetku (Prepoznano besedilo).\n"
                    f"2. Oceni pravilnost in natančnost izgovarjave glasov v slovenščini (izpostavi npr. napačne glasove, rljanje, izpuščene črke).\n"
                    f"3. Podaj kratko, spodbudno logopedsko oceno in koristen nasvet ali vajo za izboljšanje.\n\n"
                    f"Prosim, bodi strukturiran in odgovori v slovenščini."
                )

                # Gemini sprejme surove zvočne bajte ne glede na format (mp3, wav, webm...)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[
                        types.Part.from_bytes(
                            data=zvočni_bajti,
                            mime_type='audio/wav', # Gemini bo sam zaznal dejanski format
                        ),
                        navodilo_za_ai
                    ]
                )
                
                # Izpis končnega rezultata
                st.write(response.text)

            except Exception as e:
                st.error(f"Prišlo je do napake pri komunikaciji z Gemini AI: {e}")
