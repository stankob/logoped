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

# 2. Stranski meni: Izbira jezika in ciljne skupine
st.sidebar.header("Nastavitve / Postavke")
jezik = st.sidebar.radio("Izberite jezik / Odaberite jezik:", ("Slovenščina", "Hrvatski"))
skupina = st.sidebar.radio("Komu je namenjena ocena? / Kome je namijenjena ocjena?", ("Logoped (Strokovno)", "Otrok (Igrivo / Za djecu)"))

# 3. Nastavitev besedil glede na jezik in skupino
if jezik == "Slovenščina":
    naslov = "Pametni AI Logopedski Asistent"
    podnaslov = "Aplikacija za preverjanje pravilnosti izgovarjave s pomočjo umetne inteligence."
    label_vnos = "Uredite ali vpišite poljuben stavek za pacienta:"
    stavek_default = "Riba raca rak, hitro teče v potok."
    podnaslov_naloga = "Naloga za pacienta:"
    navodilo_gumb = "Kliknite spodnji gumb, izgovorite stavek in ko zaključite, kliknite 'Zaustavi snemanje'."
    gumb_start = "🎤 Klikni in govori"
    gumb_stop = "🛑 Zaustavi snemanje"
    uspeh_posneto = "🤖 Uspešno posneto!"
    ai_naslov = "Analiza izgovarjave:"
    ai_potek = "Umetna inteligenca posluša posnetek..."
    
    if skupina == "Logoped (Strokovno)":
        prompt_za_ai = (
            "Deluješ kot strokovni logoped. Pacient je dobil nalogo, da glasno in jasno prebere "
            "naslednji stavek: '{stavek}'. Poslušaj posnetek in izvedi naslednje korake:\n"
            "1. Natančno zapiši besedilo, ki ga slišiš.\n"
            "2. Strokovno oceni pravilnost izgovarjave glasov v slovenščini (uporabi logopedsko terminologijo).\n"
            "3. Podaj strokovno oceno in koristen nasvet za rehabilitacijo.\n\n"
            "Odgovori izključno v slovenskem jeziku, resno in strokovno."
        )
    else: # Za otroke
        prompt_za_ai = (
            "Deluješ kot prijazen, topel in igriv logopedski asistent, ki govori neposredno z OTROKOM. "
            "Otrok je poskusil prebrati stavek: '{stavek}'. Poslušaj posnetek in:\n"
            "1. Pohvali otroka za trud z veliko navdušenja in uporabljaj emojije (npr. 🌟, 🏆, 🐸).\n"
            "2. Na zelo preprost, pravljičen in igriv način mu povej, če je kakšen glas 'ponagajal' ali se skril (npr. namesto težkih izrazov reci 'jeziček je malce zaspal').\n"
            "3. Podaj mu eno preprosto, zabavno igrico ali trik (npr. oponašanje motorja, pihanje balonov), kako lahko ta glas natrenira.\n\n"
            "Odgovori izključno v slovenskem jeziku. Govoriti moraš neposredno otroku (v ti-obliki), jezik mora biti preprost, izjemno spodbuden in poln topline."
        )
else:
    # Hrvaški prevodi
    naslov = "Pametni AI Logopedski Asistent"
    podnaslov = "Aplikacija za provjeru pravilnosti izgovora pomoću umjetne inteligencije."
    label_vnos = "Uredite ili upišite proizvoljnu rečenicu za pacijenta:"
    stavek_default = "Na vrh brda vrba mrda."
    podnaslov_naloga = "Zadatak za pacijenta:"
    navodilo_gumb = "Kliknite gumb ispod, izgovorite rečenicu i kada završite, kliknite 'Zaustavi snimanje'."
    gumb_start = "🎤 Klikni i govori"
    gumb_stop = "🛑 Zaustavi snimanje"
    uspeh_posneto = "🤖 Uspješno snimljeno!"
    ai_naslov = "Analiza izgovora:"
    ai_potek = "Umjetna inteligencija sluša snimku..."
    
    if skupina == "Logoped (Strokovno)":
        prompt_za_ai = (
            "Djeluješ kao stručni logoped. Pacijent je dobio zadatak da glasno i jasno pročita "
            "sljedeću rečenicu: '{stavek}'. Poslušaj snimku i izvedi sljedeće korake:\n"
            "1. Točno zapiši tekst koji čuješ.\n"
            "2. Stručno procijeni pravilnost izgovora glasova na hrvatskom jeziku (koristi logopedsku terminologiju).\n"
            "3. Podaj stručnu ocjenu i koristan savjet za rehabilitaciju.\n\n"
            "Odgovori isključivo na hrvatskom jeziku, ozbiljno i stručno."
        )
    else: # Za otroke
        prompt_za_ai = (
            "Djeluješ kao drag, topao i razigran logopedski asistent koji govori izravno DJETETU. "
            "Dijete je pokušalo pročitati rečenicu: '{stavek}'. Poslušaj snimku i:\n"
            "1. Pohvali dijete za trud s puno entuzijazma i koristi emojije (npr. 🌟, 🚀, 🦁).\n"
            "2. Na vrlo jednostavan, bajkovit i zabavan način reci mu ako ga je neki glas 'pobijedio' ili se sakrio (npr. 'jezičić je malo zaspao').\n"
            "3. Daj mu jednu jednostavnu, zabavnu igricu ili trik kako može vježbati taj glas.\n\n"
            "Odgovori isključivo na hrvatskom jeziku. Govori izravno djetetu (u ti-obliku), jezik mora biti jednostavan, iznimno ohrabrujuć i pun topline."
        )

# 4. Izris vmesnika na strani
st.title(naslov)
st.write(podnaslov)
st.write("---")

vpisani_stavek = st.text_input(label_vnos, value=stavek_default)

st.subheader(podnaslov_naloga)
st.info(f"**\"{vpisani_stavek}\"**")

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
            client = genai.Client(api_key=gemini_key)
            končni_prompt = prompt_za_ai.format(stavek=vpisani_stavek)

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
            st.write(response.text)

        except Exception as e:
            if jezik == "Slovenščina":
                st.error(f"Prišlo je do napake: {e}")
            else:
                st.error(f"Došlo je do pogreške: {e}")
