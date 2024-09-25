import streamlit as st
import os
from datetime import datetime
import speech_recognition as sr
from pydub import AudioSegment
import json

# File path for the JSON file containing users data
USER_DATA_FILE = "users.json"
UPLOAD_DIR = "uploads"

# Create directory to save the audio files if not exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Function to validate login using JSON
def validate_login(mobile, password):
    try:
        # Load user data from JSON
        with open(USER_DATA_FILE, "r") as file:
            users = json.load(file)
        
        # Check if the user exists in the JSON data
        for user in users:
            if user['mobile'] == mobile and user['password'] == password:
                return True
        return False
    except Exception as e:
        st.error(f"Error loading user data: {e}")
        return False

# Function to convert speech to text in Hindi
def speech_to_text(audio_path):
    recognizer = sr.Recognizer()

    try:
        # Load the audio file into the recognizer
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)

        # Recognize speech using Google Web Speech API, specifying the language as Hindi
        text = recognizer.recognize_google(audio_data, language="hi-IN")
        return text
    except sr.UnknownValueError:
        return "Could not understand the audio"
    except sr.RequestError:
        return "Could not request results from the speech recognition service"

# Function to handle audio file conversion
def convert_to_wav(uploaded_audio):
    audio_format = uploaded_audio.name.split(".")[-1].lower()
    audio_path = os.path.join(UPLOAD_DIR, uploaded_audio.name)
    
    # Save the uploaded file to disk
    with open(audio_path, "wb") as f:
        f.write(uploaded_audio.getbuffer())

    # Convert to WAV if the file is not already in WAV format
    if audio_format != "wav":
        sound = AudioSegment.from_file(audio_path)
        wav_path = os.path.join(UPLOAD_DIR, uploaded_audio.name.split(".")[0] + ".wav")
        sound.export(wav_path, format="wav")
        return wav_path
    return audio_path

# Login Form
def login():
    st.title("User Login")

    # Get user input
    mobile = st.text_input("Mobile Number", max_chars=10, key="mobile")
    password = st.text_input("Password", type="password", max_chars=6, key="password")
    
    # Handle login button click
    if st.button("Login"):
        if validate_login(int(mobile), int(password)):
            st.session_state['authenticated'] = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid mobile number or password")

# Workflow Form after Login
def workflow():
    st.title("Workflow: Upload Food and System Condition")

    # Time selection
    time_of_day = st.selectbox("Select Time of Day", ["Morning", "Afternoon", "Evening", "Night"])

    # Upload voice recording about food intake
    uploaded_voice = st.file_uploader("Upload voice recording related to food intake", type=["wav", "mp3", "ogg", "m4a"])

    # Upload system condition details (e.g., a text file or a recorded message)
    uploaded_condition = st.file_uploader("Upload file with system condition", type=["txt", "docx", "wav", "mp3", "ogg", "m4a"])

    # Store text to edit for both food and system condition
    extracted_text = None
    extracted_condition_text = None

    if uploaded_voice is not None:
        # Convert the audio file to WAV and extract text for food intake
        audio_path = convert_to_wav(uploaded_voice)
        extracted_text = speech_to_text(audio_path)

        st.subheader("Extracted Text from Voice Recording (in Hindi) - Food Intake:")
        # Editable text area for food intake
        food_text = st.text_area("Edit extracted text for food intake:", value=extracted_text)

    if uploaded_condition is not None:
        # Convert the audio file to WAV and extract text for system condition
        condition_audio_path = convert_to_wav(uploaded_condition)
        extracted_condition_text = speech_to_text(condition_audio_path)

        st.subheader("Extracted Text from Voice Recording (in Hindi) - System Condition:")
        # Editable text area for system condition
        condition_text = st.text_area("Edit extracted text for system condition:", value=extracted_condition_text)

    if st.button("Submit"):
        if uploaded_voice is not None and uploaded_condition is not None:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

            # Save voice file
            voice_filename = f"{timestamp}_voice_{uploaded_voice.name}"
            voice_file_path = os.path.join(UPLOAD_DIR, voice_filename)
            with open(voice_file_path, "wb") as f:
                f.write(uploaded_voice.getbuffer())

            # Save condition file
            condition_filename = f"{timestamp}_condition_{uploaded_condition.name}"
            condition_file_path = os.path.join(UPLOAD_DIR, condition_filename)
            with open(condition_file_path, "wb") as f:
                f.write(uploaded_condition.getbuffer())

            # Show success message and the final edited text
            st.success(f"Files uploaded successfully! ({voice_filename}, {condition_filename})")
            st.subheader("Final Submitted Text for Food Intake:")
            st.write(food_text)
            st.subheader("Final Submitted Text for System Condition:")
            st.write(condition_text)
        else:
            st.error("Please upload both the voice recording and system condition files.")

# Main function to handle login and workflow
def main():
    # Check if user is authenticated
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if not st.session_state['authenticated']:
        login()
    else:
        workflow()

# Run the app
if __name__ == "__main__":
    main()
