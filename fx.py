from pedalboard import load_plugin, Pedalboard, Limiter, Plugin
from pedalboard.io import AudioFile
import numpy as np
import openai
import re
import os
import streamlit as st

openai.api_key = os.getenv('KEY_PT')

#########
## Audio I/O ##
#########

def set_input(f_name = '/content/drive/MyDrive/Pedalboard Experiment/Dry Guitar.wav'):
    """
    Takes in an audio file as a file-path string, returns an AudioFile object.
    Use this method to select and sample the input file for processing.

    Parameters:
        f_name (str): Valid file path pointing to the "dry" audio.

    Returns:
        audio: AudioFile object that can be processed and exported via pedalboard.io
    """
    with AudioFile(f_name) as f:
        audio = f.read(f.frames)
    return audio
  
def write_output(input_audio, f_name, p_board, samplerate = 44100):
    """
    Takes in an AudioFile object, a valid path name, a Pedalboard object and
    (optionally) a desired sample rate. Applies the Pedalboard effects to
    the audio and exports it to the specified path name.

    Parameters:
        input_audio (AudioFile): Object representing dry audio for processing.
        f_name (str): File path specifying the output destination for processed or "wet" audio.
        p_board (Pedalboard): Object representing effects chain to be applied.
        samplerate (float): Sampling rate to be used for the export.

    Returns:
        effected (AudioFile): Object containing processed or "wet" audio.
    """
    effected = p_board(input_audio, samplerate)
    with AudioFile(f_name, 'w', samplerate, effected.shape[0]) as f:
        f.write(effected)
    return effected

#########
## Pedalboard Management ##
#########

vst_plugin_path = "/Library/Audio/Plug-Ins/Components/Archetype Cory Wong.component"

def jazz(arch_instance, x = 0.5):
    arch_instance.amp_type = "The Clean Machine"
    arch_instance.the_80s_active = "Active"
    arch_instance.the_fourth_position_active = "Inactive"
    arch_instance.the_clean_machine_treble = 0.2
    arch_instance.the_clean_machine_bass = 0.4
    return arch_instance
    
def reverb(arch_instance):
    arch_instance.the_wash_mode = "Reverb"
    arch_instance.the_wash_dry_wet = 0.2
    return arch_instance
    
def overdrive(arch_instance, x = 0.5):
    arch_instance.amp_type = "The Amp Snob"
    arch_instance.the_fourth_position_active = "Active"
    arch_instance.the_fourth_position_compression = 0.6
    arch_instance.the_big_rig_active = "Active"
    arch_instance.the_big_rig_drive = max(0.8 * x, 0.8)
    return arch_instance

def tube_drive(arch_instance, x = 0.5):
    arch_instance.amp_type = "The Amp Snob"
    arch_instance.the_fourth_position_active = "Active"
    arch_instance.the_fourth_position_compression = 0.4
    arch_instance.the_big_rig_active = "Active"
    arch_instance.the_big_rig_drive = 0.3
    arch_instance.the_tuber_active = "Active"
    arch_instance.the_tuber_drive = max(0.8 * x, 0.8)
    return arch_instance


#########
## OOP Implementation of Generated Pedal ##
#########

system_prompt = "I am a user entering text prompts related to guitar tones. Respond in exactly this format: 'FX: ..., Val: ...%, Reverb: [T/F]', where FX is one from [Jazz Chorus, Overdrive, Tube Screamer], Val is ."
fx_match = {"Jazz Chorus": jazz, "Overdrive": overdrive, "Tube Screamer": tube_drive}

class BoardGenerator:
    def __init__(self, input_text):
        self.arch = load_plugin(vst_plugin_path)
        self.input_text = input_text
        self.weights = self.get_weights()
        self.board = self.make_board()

    def get_weights(self):
        user_token = self.input_text
        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_token}
        ],
        max_tokens = 40
        )
        response = completion.choices[0].message["content"]
        self.gpt_response = response
        print("user token: " + str(user_token) + " || gpt response: " + str(response))
        return self.extract_values(response)

    def make_board(self):
        self.arch = fx_match[self.weights["FX"]](self.arch, self.weights["Value"]/100)
        if self.weights["Reverb"] == "T":
            self.arch = reverb(self.arch)
        return Pedalboard([self.arch])

    def extract_values(self, input_string):
        fx_pattern = r"FX:\s*([\w\s]+),"
        val_pattern = r"Val:\s*(\d+)%,"
        reverb_pattern = r"Reverb:\s*([TF])"

        fx = re.search(fx_pattern, input_string)
        val = re.search(val_pattern, input_string)
        reverb = re.search(reverb_pattern, input_string)
        return {"FX": fx.group(1), "Value": int(val.group(1)), "Reverb": reverb.group(1)}