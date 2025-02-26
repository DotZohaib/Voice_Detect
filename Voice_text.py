import streamlit as st
# import speech_recognition as sr
# from gtts import gTTS
import os
import tempfile
from io import BytesIO
import base64

# Set page configuration
st.set_page_config(
    page_title="Voice Conversion App",
    page_icon="🔊",
    layout="centered"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .title {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .stAudio {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown("<h1 class='title'>📝🔊 Text-to-Speech & Speech-to-Text App</h1>", unsafe_allow_html=True)
st.markdown("Convert your text to a female voice or upload audio to convert to text.")

# Create tabs for different functionalities
tab1, tab2 = st.tabs(["Text to Speech", "Speech to Text"])

# Text to Speech tab
with tab1:
    st.subheader("Text to Speech Conversion")
    
    # Text input
    user_text = st.text_area("Enter the text you want to convert to speech:", height=150)
    
    # Language selection
    language = st.selectbox("Select language:", ["English (en)", "Spanish (es)", "French (fr)", "German (de)"])
    language_code = language.split("(")[1].split(")")[0]
    
    # Voice gender (always female as per requirement)
    st.write("Voice gender: Female")
    
    # Generate button
    if st.button("Generate Audio") and user_text:
        with st.spinner("Generating audio..."):
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                # Generate the audio file with female voice
                tts = gTTS(text=user_text, lang=language_code, slow=False)
                tts.save(fp.name)
                
                # Read the audio file
                with open(fp.name, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                
                # Display audio player
                st.audio(audio_bytes, format='audio/mp3')
                
                # Create a download button
                b64 = base64.b64encode(audio_bytes).decode()
                href = f'<a href="data:audio/mp3;base64,{b64}" download="speech.mp3">Download audio file</a>'
                st.markdown(href, unsafe_allow_html=True)
                
                # Clean up the temp file
                os.unlink(fp.name)
    
    # Sample text options
    st.subheader("Sample Texts")
    sample_texts = {
        "Greeting": "Hello! Welcome to the text to speech conversion app. I hope you're having a wonderful day!",
        "Weather Report": "Today will be mostly sunny with a high of 75 degrees. Expect some light clouds in the afternoon with a slight chance of rain in the evening.",
        "Recipe Instructions": "Add two cups of flour to a mixing bowl. Slowly pour in one cup of milk while stirring. Mix until you achieve a smooth consistency."
    }
    
    sample_choice = st.selectbox("Choose a sample text:", list(sample_texts.keys()))
    if st.button("Use Sample"):
        st.session_state.user_text = sample_texts[sample_choice]
        st.experimental_rerun()

# Speech to Text tab
with tab2:
    st.subheader("Speech to Text Conversion")
    
    # File uploader for audio
    uploaded_file = st.file_uploader("Upload an audio file (WAV, MP3, etc.)", type=['wav', 'mp3', 'ogg'])
    
    if uploaded_file is not None:
        # Display the uploaded audio file
        st.audio(uploaded_file, format=f'audio/{uploaded_file.name.split(".")[-1]}')
        
        # Process the file when the button is clicked
        if st.button("Convert to Text"):
            with st.spinner("Converting audio to text..."):
                # Save the uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{uploaded_file.name.split(".")[-1]}') as fp:
                    fp.write(uploaded_file.getvalue())
                    temp_filename = fp.name
                
                try:
                    # Initialize recognizer
                    r = sr.Recognizer()
                    
                    # Convert the audio to wav if it's not already
                    if not temp_filename.endswith('.wav'):
                        # You might need additional libraries like pydub here
                        # For simplicity, we'll just handle WAV files in this example
                        st.warning("For best results, please upload a WAV file recorded at 16kHz.")
                    
                    # Load the audio file
                    with sr.AudioFile(temp_filename) as source:
                        # Read the audio data
                        audio_data = r.record(source)
                        
                        # Recognize speech using Google's speech recognition
                        text = r.recognize_google(audio_data)
                        
                        # Display the result
                        st.subheader("Transcription Result:")
                        st.markdown(f'<div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6;">{text}</div>', unsafe_allow_html=True)
                        
                        # Add a button to copy the text
                        st.text_area("Copy text:", text, height=150)
                except Exception as e:
                    st.error(f"Error in speech recognition: {str(e)}")
                    st.info("Try uploading a clearer audio file or check if the file format is supported.")
                
                # Clean up
                os.unlink(temp_filename)
    
    # Option to record directly
    st.subheader("Or Record Audio Directly")
    st.warning("Note: Recording directly in the browser requires microphone permissions and may not work in all browsers.")
    st.markdown("""
    To record audio directly:
    1. Click the "Start Recording" button below
    2. Allow microphone access if prompted
    3. Speak clearly into your microphone
    4. Click "Stop Recording" when finished
    """)
    
    # Recording buttons (Note: This is a placeholder as direct recording requires JavaScript which is limited in Streamlit)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Recording"):
            st.info("Recording... (This is a placeholder - actual recording requires JavaScript implementation)")
    with col2:
        if st.button("Stop Recording"):
            st.info("Recording stopped. (This is a placeholder)")
            st.markdown("For a fully functional recording feature, you would need to use Streamlit components or integrate with JavaScript.")

# Show app information
st.markdown("---")
st.markdown("""
### About this app
This application uses:
- Google Text-to-Speech (gTTS) for converting text to speech
- SpeechRecognition library for converting speech to text
- Streamlit for the web interface

For best results when uploading audio:
- Use WAV format
- Ensure clear audio with minimal background noise
- Speak clearly and at a moderate pace
""")
