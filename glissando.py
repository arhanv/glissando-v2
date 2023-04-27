#########
## Imports ##
#########
from pedalboard import load_plugin,Plugin, Limiter
from pedalboard.io import AudioFile
import streamlit as st
import fx

ranger = iter(range(1, 31))
samples = {"A": "/samples/B Minor 120bpm (Melody 17).wav", "B": "/samples/C Major 80bpm (Melody 23).wav"}

#########
## Streamlit App Begins ##
#########

# Defining some Streamlit variables
st.session_state.format = None
format_selected = None
disable_submit = False
user_query = None
user_upload = None

# Header
st.title("Glissando")
st.write("This functional demo generates guitar effects based on text descriptions provided by the user. Select one of the provided samples or upload your own file to get started!")

# Streamlit forms begin here
with st.form("format_selection"):
    st.write("Would you like to upload your own audio?")
    st.session_state.format = st.radio(
        label = "Select an option to begin:",
        options=["Upload my own file", "Use a sample file"],
        horizontal=True
        )
    format_selected = st.form_submit_button("Continue")
with st.form("audio_in"):
    st.write("Demo (v2.0)")
    if st.session_state.format == "Upload my own file":
        user_upload = st.file_uploader("Upload Audio", type=['wav', 'mp3'], help="You can select any .wav or .mp3 audio files from your computer for processing. This app is currently optimized for raw (unprocessed) guitar tracks.")
    else:
        a, b = st.columns(2)
        with a:
            st.caption("Sample A")
            st.audio(samples["A"])
        with b:
            st.caption("Sample B")
            st.audio(samples["B"])
        st.session_state.sample_option = st.radio("Choose sample: ", ["A", "B"], horizontal=True)
        if st.session_state.sample_option == "A":
            user_upload = samples["A"]
        else:
            user_upload = samples["B"]
    user_query = st.text_input(label = "Describe your effect:")
    st.caption("Hint: Try something like 'crunchy hendrix lead' or 'warm jazz' or 'steve lacy chorus effect'")
    # Every form must have a submit button. 
    if not (user_upload or user_query):
        disable_submit = True
    submitted = st.form_submit_button("Process Audio", disabled=disable_submit, help="Upload a file and enter text into the box to get started!")
    st.write("")

if submitted:
    pedal = fx.BoardGenerator(user_query)
    audio_obj = fx.set_input(user_upload)
    effected = fx.write_output(audio_obj, "user_output.wav", pedal.board)
    st.audio(f"user_output.wav")
    st.download_button("Download this file!", data = "audio/wav", file_name="user_output.wav")