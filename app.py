import streamlit as st
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Google Translator", page_icon="🌍")

st.title("🌍 Google Translator")

languages = {
    "English": "en",
    "Hindi": "hi",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese": "zh-CN",
    "Arabic": "ar",
    "Russian": "ru"
}

text = st.text_area("Enter text")

target = st.selectbox("Translate to", list(languages.keys()))

if st.button("Translate"):
    if text.strip():
        try:
            translated = GoogleTranslator(
                source="auto",
                target=languages[target]
            ).translate(text)

            st.success("Translation")
            st.write(translated)

        except Exception as e:
            st.error(str(e))