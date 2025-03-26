import streamlit as st
import google.generativeai as genai
from PIL import Image
import speech_recognition as sr
from dotenv import load_dotenv
import os
import time

load_dotenv()
api_key = os.getenv("YOUR_API_KEY")

if not api_key:
    st.error("Помилка: API ключ не встановлений. Вкажіть змінну середовища YOUR_API_KEY.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash-exp-image-generation')

languages = {
    "Українська": "uk-UA",
    "Англійська": "en-US",
    "Німецька": "de-DE",
    "Іспанська": "es-ES",
    "Французька": "fr-FR",
}

selected_language = st.selectbox("Виберіть мову", list(languages.keys()))

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎙️ Говоріть...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language=languages[selected_language])
        st.write(f"✅ Ви сказали: {text}")
        return text
    except sr.UnknownValueError:
        st.write("⚠️ Не вдалося розпізнати мову.")
        return None
    except sr.RequestError as e:
        st.write(f"❌ Помилка сервісу Google Speech Recognition: {e}")
        return None

image_source = st.radio("Виберіть джерело зображення", ("Завантажити файл", "Використовувати камеру"))

image = None
if image_source == "Завантажити файл":
    uploaded_file = st.file_uploader("Завантажте зображення", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="📷 Завантажене зображення", use_container_width=True)

elif image_source == "Використовувати камеру":
    picture = st.camera_input("📸 Зробіть фото")
    if picture:
        image = Image.open(picture)
        st.image(image, caption="📷 Зображення з камери", use_container_width=True)

if image:
    input_option = st.radio("Виберіть спосіб введення запитання", ("📝 Ввести текст", "🎙️ Записати запитання"))

    question = None
    if input_option == "📝 Ввести текст":
        question = st.text_input("Введіть ваше запитання")
    else:
        if st.button("🎤 Записати запитання"):
            question = recognize_speech()

    if question:
        st.write("⏳ Генерується відповідь...")
        response_stream = model.generate_content([question, image], stream=True)

        st.write("📜 **Відповідь:**")
        placeholder = st.empty()

        response_text = ""
        for chunk in response_stream:
            response_text += chunk.text
            placeholder.write(response_text)
            time.sleep(0.1)