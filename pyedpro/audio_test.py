#!/usr/bin/env python3

import sys
import os, time
import threading , queue
from array import array
import pyaudio

print("Loading Libs:", end = " "); sys.stdout.flush()

import whisper
import wave
import playsound

print("OK")

#import torch
#print("Cuda available:", torch.cuda.is_available())
#sys.exit(0)
#import intel_extension_for_pytorch as ipex

print("Loading model:", end = " "); sys.stdout.flush()
model = whisper.load_model("base")
#model = whisper.load_model("small")
#model = whisper.load_model("tiny", device = "xpu")
#model = whisper.load_model("tiny")

#model.eval()
#model = model.to('xpu')
#ipex.optimize(model)

print("OK")

FORMAT = pyaudio.paInt16
#FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 16000
#RATE = 40000
CHUNK = 1024
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "output.wav"
THRESH = 10000
USEFUL = 3
SILENCE_LEN = 10

def record_audio(stream):

    global qqq, xxx

    while True:
        on_flag = 0; off_flag = 0; sigcnt = 0
        frames = []

        if exitflag:
            break

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK, exception_on_overflow = False)
            snd_data = array('h', data)
            xxx = max(snd_data)
            #print("frame:" , i, xxx)
            if xxx > THRESH:
                on_flag += 1
                off_flag = 0
                sigcnt += 1
            else:
                off_flag += 1
                on_flag = 0

            if off_flag > SILENCE_LEN:
                if sigcnt > USEFUL:
                    qqq.put(frames)
                break

            frames.append(data)

# Silence warinings from ALSA
from ctypes import *

# From alsa-lib Git 3fd4ab9be0db7c7430ebd258f2717a976381715d
# $ grep -rn snd_lib_error_handler_t
# include/error.h:59:typedef void (*snd_lib_error_handler_t)(const char *file, int line, const char *function, int err, const char *fmt, ...) /* __attribute__ ((format (printf, 5, 6))) */;
# Define our error handler type
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
  #print ('message:', line)
  pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
asound = cdll.LoadLibrary('libasound.so')
# Set error handler
asound.snd_lib_error_set_handler(c_error_handler)

# ------------------------------------------------------------------------

def mainfunct():

    global qqq, exitflag

    exitflag = False
    qqq = queue.Queue()
    audio = pyaudio.PyAudio()

    #p = audio
    #for i in range(p.get_device_count()):
    #    dev = p.get_device_info_by_index(i)
    #    print((i,dev['name'],dev['maxInputChannels']))

    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=4
    )
    thh = threading.Thread(target=record_audio, args=[stream,])
    thh.daemon = True
    thh.start()

    sig = 0; was = 1

    while True:

        if was:
            print("Listening  ...", end = " "); sys.stdout.flush()
            was = 0

        frames = qqq.get()
        #print(len(frames))

        waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()

        #playsound.playsound("output.wav")

        #audio = whisper.pad_or_trim(whisper.load_audio("output.wav"))
        #ttt = whisper.transcribe(model, audio, task="translate", fp16=False)["text"]
        #print(ttt)
        sss = os.stat("output.wav")[6]
        print("Transcribing ...", sss / 1000, "kB")
        result = model.transcribe("output.wav", fp16=False, language='English')
        print("Result: '%s'" % result['text'])

        if 'exit program' in result['text'].lower():
            exitflag = True
            break

    #stream.stop_stream()
    #stream.close()
    #time.sleep(.5)
    #audio.terminate()

if __name__ == '__main__':

    mainfunct()

# EOF