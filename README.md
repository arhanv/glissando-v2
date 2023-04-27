# glissando-v2

A Python-based demo for guitar tone generation based on natural language input from the user. GUI based on `streamlit`, DSP implements `pedalboard` and Neural DSP's Archetype VST.

File Architecture:
- `glissando.py`: Streamlit web app that enables the user to upload an audio file and enter their query text.
- `fx.py`: Script containing object-oriented implementations of the parsing and FX generation methods. Requires an `openai` API key to execute.

Here is a [video demonstration](https://youtu.be/fDsuukaGOp0) for the current version of the app.
