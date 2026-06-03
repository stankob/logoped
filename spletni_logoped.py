# Stabilna in preverjena pretvorba besedila v govor (TTS) s pravim makedonskim glasom
def ustvari_pravilen_govor(tekst, jezik_koda):
    try:
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={tts_key}"
        
        payload = {
            "input": {"text": tekst},
            "voice": {
                "languageCode": jezik_koda,  # Zdaj neposredno uporabi mk-MK brez preklopa na sr-RS
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
