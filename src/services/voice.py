import streamlit as st
import io


def convert_bytes_to_mp3(audio_bytes):
    buffer = io.BytesIO(audio_bytes)
    buffer.name = "audio_file.mp3"

    return buffer


def transcribe_audio_file(audio_file, client):

    transcription = client.audio.transcriptions.create(
        model="whisper-1", file=audio_file
    )

    return transcription


# Voice recognition functionality
def process_voice_command(command):
    st.session_state.messages.append({"role": "user", "content": command})
