import streamlit as st
from streamlit_mic_recorder import mic_recorder
from google import genai
from google.genai import types
import requests

# 1. Branje skritih API ključev iz nastavitev strežnika (Secrets)
try:
    gemini_key = st.secrets["GEMINI_API_KEY"]
    tts_key = st.secrets.get("TTS_API_KEY", gemini_key)
except Exception:
    st.error("Napaka: Ključi niso pravilno nastavljeni v Streamlit Secrets. Prosimo, uredite nastavitve.")
    st.stop()

# Funkcija za Googlovo profesionalno pretvorbo besedila v govor (TTS)
def ustvari_pravilen_govor(tekst, jezik_koda, glas_ime):
    try:
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={tts_key}"
        payload = {
            "input": {"text": tekst},
            "voice": {"languageCode": jezik_koda, "name": glas_ime},
            "audioConfig": {"audioEncoding": "MP3"}
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            import base64
            audio_content = response.json().get("audioContent", "")
            return base64.b64decode(audio_content)
        else:
            st.error(f"Google TTS napaka: {response.text}")
            return None
    except Exception as e:
        st.error(f"Napaka pri sintezi govora: {e}")
        return None

# 2. Stranski meni: Izbira jezika in ciljne skupine
st.sidebar.header("Nastavitve / Postavke")
jezik = st.sidebar.radio("Izberite jezik / Odaberite jezik:", ("Slovenščina", "Hrvatski"))
skupina = st.sidebar.radio("Komu je namenjena ocena? / Kome je namijenjena ocjena?", ("Logoped (Strokovno)", "Otrok (Igrivo / Za djecu)"))

# 3. Nastavitev besedil in glasov glede na jezik in skupino
if jezik == "Slovenščina":
    naslov = "Pametni AI Logopedski Asistent"
    podnaslov = "Aplikacija za preverjanje pravilnosti izgovarjave s pomočjo umetne inteligence."
    label_vnos = "Uredite ali vpišite poljuben stavek za pacienta:"
    stavek_default = "Riba raca rak, hitro teče v potok."
    podnaslov_naloga = "Naloga za pacienta:"
    gumb_poslusaj = "🔊 Poslušaj pravilno izgovarjavo"
    navodilo_gumb = "Kliknite spodnji gumb, izgovorite stavek in ko zaključite, kliknite 'Zaustavi snemanje'."
    gumb_start = "🎤 Klikni in govori"
    gumb_stop = "🛑 Zaustavi snemanje"
    uspeh_posneto = "🤖 Uspešno posneto!"
    ai_naslov = "Analiza izgovarjave:"
    ai_potek = "Umetna inteligenca posluša posnetek..."
    
    # Popravljen uradni slovenski glas
    tts_lang, tts_voice = "sl-SI", "sl-SI-Standard-A"
    
    if skupina == "Logoped (Strokovno)":
        prompt_za_ai = (
            "Deluješ kot strokovni logoped. Pacient je dobil nalogo, da glasno in jasno prebere "
            "naslednji stavek: '{stavek}'. Poslušaj posnetek in izvedi naslednje korake:\n"
            "1. Natančno zapiši besedilo, ki ga slišiš.\n"
            "2. Strokovno oceni pravilnost izgovarjave glasov v slovenščini (uporabi logopedsko terminologijo).\n"
            "3. Podaj strokovno oceno in koristen nasvet za rehabilitacijo.\n\n"
            "Odgovori izključno v slovenskem jeziku, resno in strokovno."
        )
    else:
        prompt_za_ai = (
            "Deluješ kot prijazen, topel in igriv logopedski asistent, ki govori neposredno z OTROKOM. "
            "Otrok je poskusil prebrati stavek: '{stavek}'. Poslušaj posnetek in:\n"
            "1. Pohvali otroka za trud z veliko navdušenja in uporabljaj emojije (npr. 🌟, 🏆, 🐸).\n"
            "2. Na zelo preprost, pravljičen in igriv način mu povej, če je kakšen glas 'ponagajal' (npr. 'jeziček je malce zaspal').\n"
            "3. Podaj mu eno preprosto, zabavno igrico ali trik, kako lahko ta glas natrenira.\n\n"
            "Odgovori izključno v slovenskem jeziku. Govori neposredno otroku (v ti-obliki), izjemno spodbudno."
        )
else:
    naslov = "Pametni AI Logopedski Asistent"
    podnaslov = "Aplikacija za provjeru pravilnosti izgovora pomoću umjetne inteligencije."
    label_vnos = "Uredite ili upišite proizvoljnu rečenicu za pacijenta:"
    stavek_default = "Na vrh brda vrba mrda."
    podnaslov_naloga = "Zadatak za pacijenta:"
    gumb_poslusaj = "🔊 Poslušaj pravilan izgovor"
    navodilo_gumb = "Kliknite gumb ispod, izgovorite rečenicu i kada završite, kliknite 'Zaustavi snimanje'."
    gumb_start = "🎤 Klikni i govori"
    gumb_stop = "🛑 Zaustavi snimanje"
    uspeh_posneto = "🤖 Uspješno snimljeno!"
    ai_naslov = "Analiza izgovora:"
    ai_potek = "Umjetna inteligencija sluša snimku..."
    
    # Popravljen uradni hrvaški glas
    tts_lang, tts_voice = "hr-HR", "hr-HR-Standard-A"
    
    if skupina == "Logoped (Strokovno)":
        prompt_za_ai = (
            "Djeluješ kao stručni logoped. Pacijent je dobio zadatak da glasno i jasno pročitati "
            "sljedeću rečenicu: '{stavek}'. Poslušaj snimku i izvedi sljedeće korake:\n"
            "1. Točno zapiši tekst koji čuješ.\n"
            "2. Stručno procijeni pravilnost izgovora glasova na hrvatskom jeziku.\n"
            "3. Podaj stručnu ocjenu i koristan savjet za rehabilitaciju.\n\n"
            "Odgovori isključivo na hrvatskom jeziku, ozbiljno i stručno."
        )
    else:
        prompt_za_ai = (
            "Djeluješ kao drag, topao i razigran logopedski asistent koji govori izravno DJETETU. "
            "Dijete je pokušalo pročitati rečenicu: '{stavek}'. Poslušaj snimku i:\n"
            "1. Pohvali dijete za trud s puno entuzijazma i koristi emojije (npr. 🌟, 🚀, 🦁).\n"
            "2. Na vrlo jednostavan način reci mu ako ga je neki glas 'pobijedio' (npr. 'jezičić je malo zaspao').\n"
            "3. Daj mu jednu jednostavnu, zabavnu igricu ili trik kako može vježbati taj glas.\n\n"
            "Odgovori isključivo na hrvatskom jeziku. Govori izravno djetetu (u ti-obliku), ohrabrujuć."
        )

# 4. Izris vmesnika na strani
st.title(naslov)
st.write(podnaslov)
st.write("---")

vpisani_stavek = st.text_input(label_vnos, value=stavek_default)

st.subheader(podnaslov_naloga)
st.info(f"**\"{vpisani_stavek}\"**")

if st.button(gumb_poslusaj):
    with st.spinner("Generiranje čistega govora..."):
        avdio_podatki = ustvari_pravilen_govor(vpisani_stavek, tts_lang, tts_voice)
        if avdio_podatki:
            st.audio(avdio_podatki, format="audio/mp3")

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
