import os
from boto3 import Session
from contextlib import closing
from pydub import AudioSegment
import simpleaudio as sa


os.makedirs('./audio', exist_ok=True)
polly = Session().client('polly')


def encode_filename(text):
    ret = ''

    for c in text:
        if not c.isalnum():
            ret += '_'

        else:
            ret += c

    return ret


def speak(text):
    filename = encode_filename(text)
    filepath_wav = os.path.join('./audio/', f'{filename}.wav')

    if not os.path.exists(filepath_wav):
        response = polly.synthesize_speech(Text=text, OutputFormat='mp3',
                                           VoiceId='Joanna')

        if 'AudioStream' not in response:
            return

        with closing(response['AudioStream']) as stream:
            filepath_mp3 = os.path.join('./audio/', f'{filename}.mp3')
            with open(filepath_mp3, 'wb') as file:
                file.write(stream.read())

        mp3 = AudioSegment.from_mp3(filepath_mp3)
        mp3.export(filepath_wav, format='wav')

    wav_obj = sa.WaveObject.from_wave_file(filepath_wav)
    play_obj = wav_obj.play()
    play_obj.wait_done()
