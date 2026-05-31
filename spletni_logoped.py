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

# Stabilna in preverjena pretvorba besedila v govor (TTS) z regionalnim preklopom
def ustvari_pravilen_govor(tekst, jezik_koda):
    try:
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={tts_key}"
        
        # Regionalni preklop za makedonščino zaradi stabilnosti API klienta
        iskani_jezik = "sr-RS" if jezik_koda == "mk-MK" else jezik_koda
        
        payload = {
            "input": {"text": tekst},
            "voice": {
                "languageCode": iskani_jezik,
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

# 2. Stranski meni: Izbira jezikov (dodana angleščina) in ciljne skupine
st.sidebar.header("Nastavitve / Postavke / Settings")
jezik = st.sidebar.radio(
    "Izberite jezik / Odaberite jezik / Изберете јазик / Select language:", 
    ("Slovenščina", "Hrvatski", "Srpski", "Bosanski", "Македонски", "English")
)
skupina = st.sidebar.radio(
    "Komu je namenjena ocena? / Kome je namijenjena ocjena? / За кого е проценката? / Audience:", 
    ("Logoped (Strokovno)", "Starš (Enostavno / Za roditelje)", "Otrok (Igrivo / Za djecu)")
)

# 3. Nastavitev lokalizacije in ISO jezikovnih kod za vsak jezik
if jezik == "Slovenščina":
    naslov, podnaslov = "Pametni AI Logopedski Asistent", "Aplikacija za preverjanje pravilnosti izgovarjave s pomočjo umetne inteligence."
    label_vnos, stavek_default = "Uredite ali vpišite poljuben stavek oz. glas za pacienta:", "Riba raca rak, hitro teče v potok."
    podnaslov_naloga, gumb_poslusaj = "Naloga za pacienta:", "🔊 Poslušaj pravilno izgovarjavo"
    navodilo_gumb, gumb_start, gumb_stop = "Kliknite spodnji gumb, izgovorite stavek in ko zaključite, kliknite 'Zaustavi snemanje'.", "🎤 Klikni in govori", "🛑 Zaustavi snemanje"
    uspeh_posneto, ai_naslov, ai_potek = "🤖 Uspešno posneto!", "Analiza izgovarjave:", "Umetna inteligenca posluša posnetek..."
    tts_lang = "sl-SI"
    
    if skupina == "Logoped (Strokovno)":
        prompt_za_ai = "Deluješ kot strokovni logoped. Pacient je dobil nalogo, da glasno in jasno izgovori: '{stavek}'. Poslušaj posnetek in: 1. Natančno zapiši besedilo, ki ga slišiš. 2. Strokovno oceni pravilnost izgovarjave glasov v slovenščini (uporabi logopedsko terminologijo). 3. Podaj strokovno oceno in koristen nasvet za rehabilitacijo. Odgovori izključno v slovenskem jeziku, resno in strokovno."
    elif skupina == "Starš (Enostavno / Za roditelje)":
        prompt_za_ai = "Deluješ kot prijazen, spodbuden logopedski svetovalec, ki govori z STARŠI otroka.  Otrok je poskusil izgovoriti: '{stavek}'. Poslušaj posnetek in: 1. Na zelo preprost način, BREZ zapletenih strokovnih izrazov, staršem razloži, kako dobro je otrok izgovoril ciljni glas ali besedo. 2. Jasno izpostavi, kje se je zataknilo (npr. če je glas izpustil ali zamenjal). 3. Podaj jim 2 praktčna, vsakodnevna nasveta, kako lahko to napako z otrokom popravljata in vadita doma med igro. Odgovori toplo in razumljivo v slovenščini."
    else:
        prompt_za_ai = "Deluješ kot prijazen, topel in igriv logopedski asistent, ki govori neposredno z OTROKOM v ti-obliki.  Otrok je poskusil prebrati stavek: '{stavek}'. Poslušaj posnetek in: 1. Pohvali otroka za trud z veliko navdušenja in emojiji (🌟, 🏆, 🐸). 2. Na preprost, pravljičen način mu povej, če je kakšen glas 'ponagajal'. 3. Podaj mu preprosto, zabavno igrico ali trik za trening. Odgovori v slovenščini."

elif jezik == "Hrvatski":
    naslov, podnaslov = "Pametni AI Logopedski Asistent", "Aplikacija za provjeru pravilnosti izgovora pomoću umjetne inteligencije."
    label_vnos, stavek_default = "Uredite ili upišite proizvoljnu rečenicu ili glas za pacijenta:", "Na vrh brda vrba mrda."
    podnaslov_naloga, gumb_poslusaj = "Zadatak za pacijenta:", "🔊 Poslušaj pravilan izgovor"
    navodilo_gumb, gumb_start, gumb_stop = "Kliknite gumb ispod, izgovorite rečenicu i kada završite, kliknite 'Zaustavi snimanje'.", "🎤 Klikni i govori", "🛑 Zaustavi snimanje"
    uspeh_posneto, ai_naslov, ai_potek = "🤖 Uspješno snimljeno!", "Analiza izgovora:", "Umjetna inteligencija sluša snimku..."
    tts_lang = "hr-HR"
    
    if skupina == "Logoped (Strokovno)":
        prompt_za_ai = "Djeluješ kao stručni logoped. Pacijent je dobio zadatak da glasno i jasno pročita rečenicu: '{stavek}'. Poslušaj snimku i: 1. Točno zapiši tekst koji čuješ. 2. Stručno procijeni pravilnost izgovora glasova na hrvatskom jeziku. 3. Podaj stručnu ocjenu i koristan savjet za rehabilitaciju. Odgovori izključivo na hrvatskom jeziku."
    elif skupina == "Starš (Enostavno / Za roditelje)":
        prompt_za_ai = "Djeluješ kao srdačan logopedski savjetnik koji razgovara s RODITELJIMA djeteta. Dijete je pokušalo izgovoriti: '{stavek}'. Poslušaj snimku i: 1. Na vrlo jednostavan način, BEZ kompliciranih stručnih izraza, objasni roditeljima koliko je dobro dijete izgovorilo zadani glas ili riječ. 2. Jasno ukaži gdje je nastao problem (npr. ako je glas zamijenjen drugim). 3. Daj im 2 praktična savjeta kako mogu vježbati kroz svakodnevnu igru kod kuće. Odgovori na hrvatskom jeziku."
    else:
        prompt_za_ai = "Djeluješ kao drag, topao i razigran logopedski asistent koji govori izravno DJETETU (u ti-obliku). Dijete je pokušalo pročitati rečenicu: '{stavek}'. Poslušaj snimku i: 1. Pohvali dijete za trud s puno entuzijazma i koristi emojije (🌟, 🚀, 🦁). 2. Na vrlo jednostavan način reci mu ako ga je neki glas 'pobijedio'. 3. Daj mu jednu jednostavnu, zabavnu igricu za vježbu. Odgovori na hrvatskom jeziku."

elif jezik == "Srpski":
    naslov, podnaslov = "Pametni AI Logopedski Asistent", "Aplikacija za proveru pravilnosti izgovora pomoću veštačke inteligencije."
    label_vnos, stavek_default = "Uredite ili upišite željenu rečenicu ili glas za pacijenta:", "Četiri čavčića na čončiću čučeći ćaskaju."
    podnaslov_naloga, gumb_poslusaj = "Zadatak za pacijenta:", "🔊 Poslušaj pravilan izgovor"
    navodilo_gumb, gumb_start, gumb_stop = "Kliknite dugme ispod, izgovorite rečenicu i kada završite, kliknite 'Zaustavi snimanje'.", "🎤 Klikni i govori", "🛑 Zaustavi snimanje"
    uspeh_posneto, ai_naslov, ai_potek = "🤖 Uspešno snimljeno!", "Analiza izgovora:", "Veštačka inteligencija sluša snimak..."
    tts_lang = "sr-RS"
    
    if skupina == "Logoped (Strokovno)":
        prompt_za_ai = "Deluješ kao stručni logoped. Pacijent je dobio zadatak da glasno i jasno pročita rečenicu: '{stavek}'. Poslušaj snimak i: 1. Tačno zapiši tekst koji čuješ. 2. Stručno proceni pravilnost izgovora glasova na srpskom jeziku. 3. Podaj savet za vežbanje. Odgovori stručno na srpskom jeziku."
    elif skupina == "Starš (Enostavno / Za roditelje)":
        prompt_za_ai = "Deluješ kao blag i iskusan logopedski savetnik koji se obraća RODITELJIMA. Dete je pokušalo da izgovori: '{stavek}'. Poslušaj snimak i: 1. Na jednostavan i jasan način, BEZ teških medicinskih izraza, objasni roditeljima kako je dete izgovorilo glas ili reč. 2. Jasno ukaži na to šta treba popraviti (npr. ako je glas 'progutan'). 3. Predloži 2 zabavne i jednostavne vežbe koje mogu raditi kod kuće kroz igru. Odgovori toplo na srpskom jeziku."
    else:
        prompt_za_ai = "Deluješ kao blag, topao i zabavan logopedski asistent koji priča direktno sa DETETOM (u ti-formi). Dete je pokušalo da pročita: '{stavek}'. Poslušaj snimak i: 1. Puno ga pohvali uz sjajne emojije (🌟, 🐼, 🎯). 2. Na simpatičan način mu kaži ako mu je neki glas 'pobegao'. 3. Daj mu jednu laku igricu za kućno vežbanje tog glasa. Odgovori na srpskom jeziku."

elif jezik == "Bosanski":
    naslov, podnaslov = "Pametni AI Logopedski Asistent", "Aplikacija za provjeru pravilnosti izgovora pomoću vještačke inteligencije."
    label_vnos, stavek_default = "Uredite ili upišite željenu rečenicu ili glas za pacijenta:", "Miš uz pušku, miš niz pušku."
    podnaslov_naloga, gumb_poslusaj = "Zadatak za pacijenta:", "🔊 Poslušaj pravilan izgovor"
    navodilo_gumb, gumb_start, gumb_stop = "Kliknite dugme ispod, izgovorite rečenicu i kada završite, kliknite 'Zaustavi snimanje'.", "🎤 Klikni i govori", "🛑 Zaustavi snimanje"
    uspeh_posneto, ai_naslov, ai_potek = "🤖 Uspješno snimljeno!", "Analiza izgovora:", "Vještačka inteligencija sluša snimak..."
    tts_lang = "hr-HR"
    
    if skupina == "Logoped (Strokovno)":
        prompt_za_ai = "Djeluješ kao stručni logoped. Pacient je dobio zadatak da glasno i jasno pročita rečenicu: '{stavek}'. Poslušaj snimak i: 1. Tačno zapiši tekst koji čuješ. 2. Stručno procijeni artikulaciju glasova u bosanskom jeziku. 3. Daj preporuku za terapiju. Odgovori u potpunosti na bosanskom jeziku."
    elif skupina == "Starš (Enostavno / Za roditelje)":
        prompt_za_ai = "Djeluješ kao srdačan logopedski savjetnik koji razgovara sa RODITELJIMA djeteta. Dijete je izgovorilo: '{stavek}'. Poslušaj snimak i: 1. Na sasvim jednostavan način, BEZ komplikovanih logopedskih izraza, pojasni roditeljima kako je dijete izgovorilo zadati glas ili riječ. 2. Jasno ukaži gdje je zapelo (npr. ako je glas izgovoren nepravilno). 3. Ponudi 2 jednostavna savjeta kako da to vježbaju kroz svakodnevne aktivnosti kod kuće. Odgovori na bosanskom jeziku."
    else:
        prompt_za_ai = "Djeluješ kao srdačan i zabavan logopedski pomoćnik koji priča direktno sa DJETETOM (u ti-obliku). Dijete je pokušalo pročitati rečenicu: '{stavek}'. Poslušaj snimak i: 1. Pohvali dječiji trud uz emojije (⭐, 🦄, ⚽). 2. Kroz igru mu objasni ako mu je neki glas 'odletio'. 3. Predloži mu zabavnu vježbicu. Odgovori ohrabrujuće na bosanskom jeziku."

elif jezik == "Македонски":
    naslov, podnaslov = "Паметен АИ Логопедски Асистент", "Апликација за проверка на правилноста на изговорот со помош на вештачка интелигенција."
    label_vnos, stavek_default = "Уреди ја или внеси саканата реченица или глас за пациентот:", "Петар плете пет пати по три прти."
    podnaslov_naloga, gumb_poslusaj = "Задача за пациентот:", "🔊 Слушни го правилниот изговор"
    navodilo_gumb, gumb_start, gumb_stop = "Кликнете на копчето подолу, изговорете ја реченицата и кога ќе завршите, кликнете 'Запрете го снимањето'.", "🎤 Кликни и зборувај", "🛑 Запрете го снимањето"
    uspeh_posneto, ai_naslov, ai_potek = "🤖 Успешно снимено!", "Анализа на изговорот:", "Вештачката интелигенција ја слуша снимката..."
    tts_lang = "mk-MK"
    
    if skupina == "Logoped (Strokovno)":
        prompt_za_ai = "Делуваш како стручен логопед. Пациентот имаше задача гласно и јасно да ја прочита реченицата: '{stavek}'. Слушни ја снимката и: 1. Точно запиши го текстот што го слушаш. 2. Стручно процени ја правилноста на изговорот на гласовите на македонски јазик (фонетска анализа). 3. Дај совет за рехабилитација. Одговори исклучиво на македонски јазик, сериозно и стручно."
    elif skupina == "Starš (Enostavno / Za roditelje)":
        prompt_za_ai = "Делуваш како пријателски логопедски советник кој разговара со РОДИТЕЛИТЕ. Детето се обиде да изговори: '{stavek}'. Слушни ја снимката и: 1. На едноставен начин, БЕЗ тешки стручни термини, објасни им на родителите како детето го изговорило гласот или зборот. 2. Јасно посочи каде имало потешкотии. 3. Дај им 2 практични и забавни совети како да вежбаат дома преку игра. Одговори на македонски јазик."
    else:
        prompt_za_ai = "Делуваш како прекрасен, топол и забавен логопедски асистент кој зборува директно со ДЕТЕТО (во ти-форма). Детето се обиде да прочита: '{stavek}'. Слушни ја снимката и: 1. Силно пофали го со многу ентузијазам и емотикони (🌟, 🚀, 🎨). 2. На многу едноставен начин кажи му ако некое гласче му 'побегнало'. 3. Дај му забавна игричка како да го извежба тоа гласче дома. Одговори охрабрувачки на македонски јазик."

else:  # English (NOVO)
    naslov, podnaslov = "Smart AI Speech Therapy Assistant", "An AI-powered application for evaluating and improving pronunciation accuracy."
    label_vnos, stavek_default = "Edit or type a custom sentence or sound for the patient:", "The quick brown fox jumps over the lazy dog."
    podnaslov_naloga, gumb_poslusaj = "Task for the patient:", "🔊 Listen to correct pronunciation"
    navodilo_gumb, gumb_start, gumb_stop = "Click the button below, speak the sentence clearly, and click 'Stop recording' when finished.", "🎤 Click and Speak", "🛑 Stop recording"
    uspeh_posneto, ai_naslov, ai_potek = "🤖 Successfully recorded!", "Pronunciation Analysis:", "AI is evaluating the audio..."
    tts_lang = "en-US"
    
    if skupina == "Logoped (Strokovno)":
        prompt_za_ai = "You are a professional speech-language pathologist (SLP). The patient was tasked with reading aloud: '{stavek}'. Listen to the audio and: 1. Provide an accurate transcription of what you hear. 2. Clinically evaluate phoneme articulation and pronunciation accuracy using standard speech therapy terminology. 3. Provide professional recommendations and corrective exercises. Respond professionally and strictly in English."
    elif skupina == "Starš (Enostavno / Za roditelje)":
        prompt_za_ai = "You are a friendly and encouraging speech therapy consultant speaking directly to the child's PARENTS. The child tried to say: '{stavek}'. Listen to the audio and: 1. Explain how well the child pronounced the target sound or word in a very simple way, completely WITHOUT complicated medical jargon. 2. Clearly highlight where they struggled (e.g., missing or substituted sounds). 3. Provide 2 practical, fun tips or daily activities they can do at home to practice together. Respond warmly in English."
    else:
        prompt_za_ai = "You are a kind, warm, and playful AI speech assistant speaking directly to the CHILD in the 'you' form. The child tried to read: '{stavek}'. Listen to the audio and: 1. Praise the child's effort with great enthusiasm and lots of fun emojis (🌟, 🏆, 🐸). 2. Explain in a simple, friendly, fairytale-like way if a sound 'tricked' them. 3. Give them 1 fun little game or trick to practice that sound at home. Respond in English."

# 4. Izris vmesnika na strani
st.title(naslov)
st.write(podnaslov)
st.write("---")

vpisani_stavek = st.text_input(label_vnos, value=stavek_default)

st.subheader(podnaslov_naloga)
st.info(f"**\"{vpisani_stavek}\"**")

if st.button(gumb_poslusaj):
    with st.spinner("Generiranje..."):
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
            st.error(f"Napaka / Error: {e}")
