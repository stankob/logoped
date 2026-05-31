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

# Dinamična in varna pretvorba besedila v govor (TTS) brez trdno kodiranih imen glasov
def ustvari_pravilen_govor(tekst, jezik_koda):
    try:
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={tts_key}"
        
        # Googlu pošljemo le kodo jezika in nevtralen/ženski spol. 
        # Sistem bo samodejno izbral edini aktivni delujoči glas za to regijo.
        payload = {
            "input": {"text": tekst},
            "voice": {
                "languageCode": jezik_koda,
                "ssmlGender": "FEMALE"
            },
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

# 2. Stranski meni: Izbira jezikov in ciljne skupine
st.sidebar.header("Nastavitve / Postavke / Settings")
jezik = st.sidebar.radio(
    "Izberite jezik / Odaberite jezik / Изберете јазик:", 
    ("Slovenščina", "Hrvatski", "Srpski", "Bosanski", "Македонски")
)
skupina = st.sidebar.radio(
    "Komu je namenjena ocena? / Kome je namijenjena ocjena? / За кого е проценката?", 
    ("Logoped (Strokovno)", "Otrok (Igrivo / Za djecu)")
)

# 3. Nastavitev lokalizacije in ISO jezikovnih kod za vsak jezik
if jezik == "Slovenščina":
    naslov, podnaslov = "Pametni AI Logopedski Asistent", "Aplikacija za preverjanje pravilnosti izgovarjave s pomočjo umetne inteligence."
    label_vnos, stavek_default = "Uredite ali vpišite poljuben stavek za pacienta:", "Riba raca rak, hitro teče v potok."
    podnaslov_naloga, gumb_poslusaj = "Naloga za pacienta:", "🔊 Poslušaj pravilno izgovarjavo"
    navodilo_gumb, gumb_start, gumb_stop = "Kliknite spodnji gumb, izgovorite stavek in ko zaključite, kliknite 'Zaustavi snemanje'.", "🎤 Klikni in govori", "🛑 Zaustavi snemanje"
    uspeh_posneto, ai_naslov, ai_potek = "🤖 Uspešno posneto!", "Analiza izgovarjave:", "Umetna inteligenca posluša posnetek..."
    
    tts_lang = "sl-SI"
    
    prompt_za_ai = (
        "Deluješ kot strokovni logoped. Pacient je dobil nalogo, da glasno in jasno prebere stavek: '{stavek}'. Poslušaj posnetek in: 1. Natančno zapiši besedilo, ki ga slišiš. 2. Strokovno oceni pravilnost izgovarjave glasov v slovenščini (uporabi logopedsko terminologijo). 3. Podaj strokovno oceno in koristen nasvet za rehabilitacijo. Odgovori izključno v slovenskem jeziku, resno in strokovno."
        if skupina == "Logoped (Strokovno)" else
        "Deluješ kot prijazen, topel in igriv logopedski asistent, ki govori neposredno z OTROKOM v ti-obliki.  Otrok je poskusil prebrati stavek: '{stavek}'. Poslušaj posnetek in: 1. Pohvali otroka za trud z veliko navdušenja in emojiji (🌟, 🏆, 🐸). 2. Na preprost, pravljičen način mu povej, če je kakšen glas 'ponagajal'. 3. Podaj mu preprosto, zabavno igrico ali trik za trening. Odgovori v slovenščini."
    )

elif jezik == "Hrvatski":
    naslov, podnaslov = "Pametni AI Logopedski Asistent", "Aplikacija za provjeru pravilnosti izgovora pomoću umjetne inteligencije."
    label_vnos, stavek_default = "Uredite ili upišite proizvoljnu rečenicu za pacijenta:", "Na vrh brda vrba mrda."
    podnaslov_naloga, gumb_poslusaj = "Zadatak za pacijenta:", "🔊 Poslušaj pravilan izgovor"
    navodilo_gumb, gumb_start, gumb_stop = "Kliknite gumb ispod, izgovorite rečenicu i kada završite, kliknite 'Zaustavi snimanje'.", "🎤 Klikni i govori", "🛑 Zaustavi snimanje"
    uspeh_posneto, ai_naslov, ai_potek = "🤖 Uspješno snimljeno!", "Analiza izgovora:", "Umjetna inteligencija sluša snimku..."
    
    tts_lang = "hr-HR"
    
    prompt_za_ai = (
        "Djeluješ kao stručni logoped. Pacijent je dobio zadatak da glasno i jasno pročita rečenicu: '{stavek}'. Poslušaj snimku i: 1. Točno zapiši tekst koji čuješ. 2. Stručno procijeni pravilnost izgovora glasova na hrvatskom jeziku. 3. Podaj stručnu ocjenu i koristan savjet za rehabilitaciju. Odgovori izključivo na hrvatskom jeziku."
        if skupina == "Logoped (Strokovno)" else
        "Djeluješ kao drag, topao i razigran logopedski asistent koji govori izravno DJETETU (u ti-obliku). Dijete je pokušalo pročitati rečenicu: '{stavek}'. Poslušaj snimku i: 1. Pohvali dijete za trud s puno entuzijazma i koristi emojije (🌟, 🚀, 🦁). 2. Na vrlo jednostavan način reci mu ako ga je neki glas 'pobijedio'. 3. Daj mu jednu jednostavnu, zabavnu igricu za vježbu. Odgovori na hrvatskom jeziku."
    )

elif jezik == "Srpski":
    naslov, podnaslov = "Pametni AI Logopedski Asistent", "Aplikacija za proveru pravilnosti izgovora pomoću veštačke inteligencije."
    label_vnos, stavek_default = "Uredite ili upišite željenu rečenicu za pacijenta:", "Četiri čavčića na čončiću čučeći ćaskaju."
    podnaslov_naloga, gumb_poslusaj = "Zadatak za pacijenta:", "🔊 Poslušaj pravilan izgovor"
    navodilo_gumb, gumb_start, gumb_stop = "Kliknite dugme ispod, izgovorite rečenicu i kada završite, kliknite 'Zaustavi snimanje'.", "🎤 Klikni i govori", "🛑 Zaustavi snimanje"
    uspeh_posneto, ai_naslov, ai_potek = "🤖 Uspešno snimljeno!", "Analiza izgovora:", "Veštačka inteligencija sluša snimak..."
    
    tts_lang = "sr-RS"
    
    prompt_za_ai = (
        "Deluješ kao stručni logoped. Pacijent je dobio zadatak da glasno i jasno pročita rečenicu: '{stavek}'. Poslušaj snimak i: 1. Tačno zapiši tekst koji čuješ. 2. Stručno proceni pravilnost izgovora glasova na srpskom jeziku. 3. Podaj savet za vežbanje. Odgovori stručno na srpskom jeziku."
        if skupina == "Logoped (Strokovno)" else
        "Deluješ kao blag, topao i zabavan logopedski asistent koji priča direktno sa DETETOM (u ti-formi). Dete je pokušalo da pročita: '{stavek}'. Poslušaj snimak i: 1. Puno ga pohvali uz sjajne emojije (🌟, 🐼, 🎯). 2. Na simpatičan način mu kaži ako mu je neki glas 'pobegao'. 3. Daj mu jednu laku igricu za kućno vežbanje tog glasa. Odgovori na srpskom jeziku."
    )

elif jezik == "Bosanski":
    naslov, podnaslov = "Pametni AI Logopedski Asistent", "Aplikacija za provjeru pravilnosti izgovora pomoću vještačke inteligencije."
    label_vnos, stavek_default = "Uredite ili upišite željenu rečenicu za pacijenta:", "Miš uz pušku, miš niz pušku."
    podnaslov_naloga, gumb_poslusaj = "Zadatak za pacijenta:", "🔊 Poslušaj pravilan izgovor"
    navodilo_gumb, gumb_start, gumb_stop = "Kliknite dugme ispod, izgovorite rečenicu i kada završite, kliknite 'Zaustavi snimanje'.", "🎤 Klikni i govori", "🛑 Zaustavi snimanje"
    uspeh_posneto, ai_naslov, ai_potek = "🤖 Uspješno snimljeno!", "Analiza izgovora:", "Vještačka inteligencija sluša snimak..."
    
    # Bosanski gladko koristi skupno regionalno govorečo bazo
    tts_lang = "hr-HR"
    
    prompt_za_ai = (
        "Djeluješ kao stručni logoped. Pacient je dobio zadatak da glasno i jasno pročita rečenicu: '{stavek}'. Poslušaj snimak i: 1. Tačno zapiši tekst koji čuješ. 2. Stručno procijeni artikulaciju glasova u bosanskom jeziku. 3. Daj preporuku za terapiju. Odgovori u potpunosti na bosanskom jeziku."
        if skupina == "Logoped (Strokovno)" else
        "Djeluješ kao srdačan i zabavan logopedski pomoćnik koji priča direktno sa DJETETOM (u ti-obliku). Dijete je pokušalo pročitati rečenicu: '{stavek}'. Poslušaj snimak i: 1. Pohvali dječiji trud uz emojije (⭐, 🦄, ⚽). 2. Kroz igru mu objasni ako mu je neki glas 'odletio'. 3. Predloži mu zabavnu vježbicu. Odgovori ohrabrujuće na bosanskom jeziku."
    )

else:  # Македонски
    naslov, podnaslov = "Паметен АИ Логопедски Асистент", "Апликација за проверка на правилноста на изговорот со помош на вештачка интелигенција."
    label_vnos, stavek_default = "Уреди ја или внеси саканата реченица за пациентот:", "Петар плете пет пати по три прти."
    podnaslov_naloga, gumb_poslusaj = "Задача за пациентот:", "🔊 Слушни го правилниот изговор"
    navodilo_gumb, gumb_start, gumb_stop = "Кликнете на копчето подолу, изговорете ја реченицата и кога ќе завршите, кликнете 'Запрете го снимањето'.", "🎤 Кликни и зборувај", "🛑 Запрете го снимањето"
    uspeh_posneto, ai_naslov, ai_potek = "🤖 Успешно снимено!", "Анализа на изговорот:", "Вештачката интелигенција ја слуша снимката..."
    
    tts_lang = "mk-MK"
    
    prompt_za_ai = (
        "Делуваш како стручен логопед. Пациентот имаше задача гласно и јасно да ја прочита реченицата: '{stavek}'. Слушни ја снимката и: 1. Точно запиши го текстот што го слушаш. 2. Стручно процени ја правилноста на изговорот на гласовите на македонски јазик (фонетска анализа). 3. Дај совет за рехабилитација. Одговори исклучиво на македонски јазик, сериозно и стручно."
        if skupina == "Logoped (Strokovno)" else
        "Делуваш како прекрасен, топол и забавен логопедски асистент кој зборува директно со ДЕТЕТО (во ти-форма). Детето се обиде да прочита: '{stavek}'. Слушни ја снимката и: 1. Силно пофали го со многу ентузијазам и емотикони (🌟, 🚀, 🎨). 2. На многу едноставен начин кажи му ако некое гласче му 'побегнало'. 3. Дај му забавна игричка како да го извежба тоа гласче дома. Одговори охрабрувачки на македонски јазик."
    )

# 4. Izris vmesnika na strani
st.title(naslov)
st.write(podnaslov)
st.write("---")

vpisani_stavek = st.text_input(label_vnos, value=stavek_default)

st.subheader(podnaslov_naloga)
st.info(f"**\"{vpisani_stavek}\"**")

if st.button(gumb_poslusaj):
    with st.spinner("Generiranje..."):
        # Klic sedaj vsebuje le besedilo in ISO kodo jezika
        avdio_podatki = ustvari_pravilen_govor(vpisani_stavek, tts_lang)
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
            st.error(f"Napaka / Грешка: {e}")
