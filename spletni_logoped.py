import streamlit as st
from streamlit_mic_recorder import mic_recorder
from google import genai
from google.genai import types

# 1. Samodejno branje skritega API ključa iz nastavitev strežnika
try:
    gemini_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Napaka: API ključ ni nastavljen v Streamlit Secrets. Prosimo, uredite nastavitve aplikacije.")
    st.stop()

# 2. Izbira jezika v stranskem meniju (Sidebar)
jezik = st.sidebar.radio("Izberite jezik / Odaberite jezik:", ("Slovenščina", "Hrvatski"))

# 3. Nastavitev besedil glede na izbrani jezik
if jezik == "Slovenščina":
    naslov = "Pametni AI Logopedski Asistent"
    podnaslov = "Aplikacija za preverjanje pravilnosti izgovarjave s pomočjo umetne inteligence."
    podnaslov_naloga = "Naloga za pacienta:"
    navodilo_branje = "Prosim, jasno preberite naslednji stavek:"
    stavek_default = "Riba raca rak, hitro teče v potok."
    navodilo_gumb = "Kliknite spodnji gumb, izgovorite stavek in ko zaključite, kliknite 'Zaustavi snemanje'."
    gumb_start = "🎤 Klikni in govori"
    gumb_stop = "🛑 Zaustavi snemanje"
    uspeh_posneto = "🤖 Uspešno posneto!"
    ai_naslov = "Logopedska analiza umetne inteligence:"
    ai_potek = "Umetna inteligenca posluša posnetek in analizira izgovarjavo..."
    
    # Navodilo za Gemini v slovenščini
    prompt_za_ai = (
        "Deluješ kot strokovni logoped. Pacient je dobil nalogo, da glasno in jasno prebere "
        "naslednji stavek: '{stavek}'. "
        "Tvoja naloga je, da poslušaš priloženi zvočni posnetek pacienta in izvedeš naslednje korake:\n"
        "1. Natančno zapiši besedilo, ki ga slišiš v posnetku.\n"
        "2. Oceni pravilnost in natančnost izgovarjave glasov v slovenščini (izpostavi npr. napačne glasove, izpuščene črke).\n"
        "3. Podaj kratko, spodbudno logopedsko oceno in koristen nasvet za izboljšanje.\n\n"
        "Odgovori izključno v slovenskem jeziku."
    )
else:
    # Hrvaški prevodi
    naslov = "Pametni AI Logopedski Asistent"
    podnaslov = "Aplikacija za provjeru pravilnosti izgovora pomoću umjetne inteligencije."
    podnaslov_naloga = "Zadatak za pacijenta:"
    navodilo_branje = "Molim, jasno pročitajte sljedeću rečenicu:"
    stavek_default = "Na vrh brda vrba mrda."
    navodilo_gumb = "Kliknite gumb ispod, izgovorite rečenicu i kada završite, kliknite 'Zaustavi snimanje'."
    gumb_start = "🎤 Klikni i govori"
    gumb_stop = "🛑 Zaustavi snimanje"
    uspeh_posneto = "🤖 Uspješno snimljeno!"
    ai_naslov = "Logopedska analiza umjetne inteligencije:"
    ai_potek = "Umjetna inteligencija sluša snimku i analizira izgovor..."
    
    # Navodilo za Gemini v hrvaščini
    prompt_za_ai = (
        "Djeluješ kao stručni logoped. Pacijent je dobio zadatak da glasno i jasno pročita "
        "sljedeću rečenicu: '{stavek}'. "
        "Tvoj zadatak je da poslušaš priloženu zvučnu snimku pacijenta i izvedeš sljedeće korake:\n"
        "1. Točno zapiši tekst koji čuješ u snimci.\n"
        "2. Procijeni pravilnost i točnost izgovora glasova na hrvatskom jeziku (istakni npr. pogrešne glasove, izostavljena slova).\n"
        "3. Podaj kratku, ohrabrujuću logopedsku ocjenu i koristan savjet za poboljšanje.\n\n"
        "Odgovori isključivo na hrvatskom jeziku."
    )

# 4. Izris vmesnika na strani
st.title(naslov)
st.write(podnaslov)

# Shranjevanje stavka v sejo glede na jezik
if 'trenutni_jezik' not in st.session_state or st.session_state.trenutni_jezik != jezik:
    st.session_state.trenutni_jezik = jezik
    st.session_state.stavek = stavek_default

st.subheader(podnaslov_naloga)
st.info(f"{navodilo_branje} **\"{st.session_state.stavek}\"**")

st.write("---")
st.write(navodilo_gumb)

# 5. Spletni snemalnik zvoka
avdio_posnetek = mic_recorder(
    start_prompt=gumb_start, 
    stop_prompt=gumb_stop, 
    key="logoped_mic"
)

if avdio_posnetek:
    zvočni_bajti = avdio_posnetek['bytes']
    st.success(uspeh_posneto)
    
    st.write("---")
    st.subheader(ai_naslov)
    
    with st.spinner(ai_potek):
        try:
            # Povezava na Gemini API
            client = genai.Client(api_key=gemini_key)
            
            # Vstavimo trenutni stavek v navodilo
            končni_prompt = prompt_za_ai.format(stavek=st.session_state.stavek)

            # Pošljemo zvok in navodilo modelu
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_bytes(
                        data=bytes(zvočni_bajti),
                        mime_type='audio/wav',
                    ),
                    končni_prompt
                ]
            )
            
            # Izpis končnega rezultata analize
            st.write(response.text)

        except Exception as e:
            if jezik == "Slovenščina":
                st.error(f"Prišlo je do napake pri komunikaciji z Gemini AI: {e}")
            else:
                st.error(f"Došlo je do pogreške u komunikaciji s Gemini AI: {e}")
