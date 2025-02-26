import os
import time
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import io
import warnings
warnings.filterwarnings('ignore')

class StreamlitSpeechProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.languages = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'ja': 'Japanese',
            'zh-CN': 'Chinese'
        }
        self.voice_speeds = {
            'slow': 0.5,
            'normal': 1.0,
            'fast': 1.5,
            'very_fast': 2.0
        }
        self.current_language = 'en'
        self.voice_speed = 'normal'
        self.output_dir = 'speech_outputs'

        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def text_to_speech(self, text, output_filename='output.mp3'):
        """Convert text to speech and save as MP3"""
        try:
            # Save with timestamp to prevent overwriting
            timestamp = int(time.time())
            filepath = f"{self.output_dir}/{timestamp}_{output_filename}"

            # Create TTS with selected language
            # For English, we can specify a female voice
            if self.current_language == 'en':
                tts = gTTS(text=text, lang=self.current_language, tld='com', slow=False)
            else:
                tts = gTTS(text=text, lang=self.current_language)

            tts.save(filepath)

            # Adjust speed if needed (using pydub)
            if self.voice_speed != 'normal':
                self._adjust_audio_speed(filepath)

            st.success(f"✅ Speech saved to {filepath}")

            # Return the file path for playback
            return filepath
        except Exception as e:
            st.error(f"❌ Error in text-to-speech conversion: {e}")
            return None

    def _adjust_audio_speed(self, filepath):
        """Adjust the speed of the generated audio file"""
        try:
            audio = AudioSegment.from_mp3(filepath)
            speed_factor = self.voice_speeds[self.voice_speed]

            # Create a new audio segment with adjusted speed
            # For speeding up, we need to adjust the frame rate
            adjusted_audio = audio._spawn(audio.raw_data, overrides={
                "frame_rate": int(audio.frame_rate * speed_factor)
            })
            adjusted_audio = adjusted_audio.set_frame_rate(audio.frame_rate)

            # Save the adjusted audio
            adjusted_audio.export(filepath, format="mp3")
            st.info(f"🔄 Audio speed adjusted to {self.voice_speed} ({speed_factor}x)")
        except Exception as e:
            st.error(f"❌ Error adjusting audio speed: {e}")

    def display_waveform(self, audio_path):
        """Generate a waveform for Streamlit display"""
        try:
            # Load audio file
            audio = AudioSegment.from_file(audio_path)
            audio_array = np.array(audio.get_array_of_samples())

            # Normalize for visualization
            audio_array = audio_array / np.max(np.abs(audio_array)) if np.max(np.abs(audio_array)) > 0 else audio_array

            # Create sample for x-axis (time)
            time_axis = np.linspace(0, len(audio_array) / audio.frame_rate, num=min(10000, len(audio_array)))

            # Downsample for better performance
            if len(audio_array) > 10000:
                factor = len(audio_array) // 10000
                audio_array = audio_array[::factor][:10000]

            # Create figure for Streamlit
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(time_axis[:len(audio_array)], audio_array, color='blue', alpha=0.7)
            ax.set_xlabel('Time (seconds)')
            ax.set_ylabel('Amplitude')
            ax.set_title('Audio Waveform')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()

            return fig
        except Exception as e:
            st.error(f"❌ Error displaying waveform: {e}")
            return None

    def speech_to_text(self, audio_file):
        """Convert speech to text from Streamlit uploaded file"""
        try:
            # Save uploaded file to temp location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_file.write(audio_file.getvalue())
                temp_filename = tmp_file.name

            st.info(f"🎧 Processing audio file...")

            # Convert to WAV if needed (e.g., if MP3)
            if audio_file.name.endswith('.mp3'):
                audio = AudioSegment.from_mp3(temp_filename)
                wav_filename = temp_filename.replace('.mp3', '.wav')
                audio.export(wav_filename, format='wav')
                temp_filename = wav_filename

            # Process the audio file
            with sr.AudioFile(temp_filename) as source:
                audio_data = self.recognizer.record(source)

            # Perform the recognition with specified language
            st.info("🔄 Converting speech to text...")
            transcription = self.recognizer.recognize_google(
                audio_data,
                language=self.current_language
            )

            # Clean up temporary file
            os.remove(temp_filename)

            st.success(f"📝 Transcription complete!")
            return transcription

        except sr.UnknownValueError:
            st.error("❌ Could not understand the audio.")
            return None
        except sr.RequestError as e:
            st.error(f"❌ Request error from Google Speech Recognition service: {e}")
            return None
        except Exception as e:
            st.error(f"❌ Error in speech-to-text conversion: {e}")
            return None

    def set_language(self, language_code):
        """Set the language for TTS and STT"""
        if language_code in self.languages:
            self.current_language = language_code
            st.info(f"🌐 Language set to {self.languages[language_code]} ({language_code})")
            return True
        else:
            st.error(f"❌ Unsupported language code: {language_code}")
            st.info(f"🌐 Available languages: {self.languages}")
            return False

    def set_voice_speed(self, speed):
        """Set the voice speed for TTS"""
        if speed in self.voice_speeds:
            self.voice_speed = speed
            st.info(f"⏩ Voice speed set to {speed} ({self.voice_speeds[speed]}x)")
            return True
        else:
            st.error(f"❌ Unsupported speed: {speed}")
            st.info(f"⏩ Available speeds: {list(self.voice_speeds.keys())}")
            return False

# Streamlit app
def main():
    st.title("🎙️ Speech Processing App")
    st.write("Convert text to speech and speech to text with various options.")

    # Initialize the processor
    processor = StreamlitSpeechProcessor()

    # Create tabs for different functionalities
    tab1, tab2 = st.tabs(["Text to Speech", "Speech to Text"])

    with tab1:
        st.header("Text to Speech Conversion")

        # Language selection
        language_code = st.selectbox(
            "Select Language:",
            options=list(processor.languages.keys()),
            format_func=lambda x: f"{processor.languages[x]} ({x})"
        )
        processor.set_language(language_code)

        # Voice speed selection
        voice_speed = st.select_slider(
            "Select Voice Speed:",
            options=list(processor.voice_speeds.keys()),
            value='normal'
        )
        processor.set_voice_speed(voice_speed)

        # Text input
        text_input = st.text_area("Enter the text to convert to speech:", height=150)

        # Process button
        if st.button("Generate Speech", key="generate_speech"):
            if text_input:
                st.info("🔄 Processing your text...")

                # Generate speech
                output_path = processor.text_to_speech(text_input)

                if output_path:
                    # Display waveform
                    waveform = processor.display_waveform(output_path)
                    if waveform:
                        st.pyplot(waveform)

                    # Audio player
                    st.subheader("🔊 Listen to the generated speech:")
                    st.audio(output_path)

                    # Download button
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="Download Audio",
                            data=file,
                            file_name=os.path.basename(output_path),
                            mime="audio/mp3"
                        )
            else:
                st.warning("⚠️ Please enter some text first.")

    with tab2:
        st.header("Speech to Text Conversion")

        # Language selection
        language_code = st.selectbox(
            "Select Language:",
            options=list(processor.languages.keys()),
            format_func=lambda x: f"{processor.languages[x]} ({x})",
            key="stt_language"
        )
        processor.set_language(language_code)

        # File uploader
        audio_file = st.file_uploader("Upload an audio file (WAV or MP3):", type=["wav", "mp3"])

        if audio_file:
            st.audio(audio_file)

            # Process button
            if st.button("Transcribe", key="transcribe_audio"):
                transcription = processor.speech_to_text(audio_file)

                if transcription:
                    st.subheader("📝 Transcription Result:")
                    st.write(transcription)

                    # Copy button using JavaScript
                    st.markdown("""
                    <div style="display: flex; justify-content: flex-end;">
                        <button onclick="navigator.clipboard.writeText(`{}`)">
                            Copy to clipboard
                        </button>
                    </div>
                    """.format(transcription), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
