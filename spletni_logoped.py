# Funkcija za Googlovo profesionalno pretvorbo besedila v govor (TTS) - Samodejna izbira glasu
def ustvari_pravilen_govor(tekst, jezik_koda, glas_ime):
    try:
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={tts_key}"
        payload = {
            "input": {"text": tekst},
            # Googlu podava samo kodo jezika (npr. sl-SI), ime glasu pa izpustiva, da sam izbere aktivnega
            "voice": {"languageCode": jezik_koda},
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
