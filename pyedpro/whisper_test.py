#!/usr/bin/env python3

import signal, os, time, sys, subprocess, platform, socket, requests
import ctypes, datetime, sqlite3, warnings, threading, httpx
import json
import select

import whisper

model = whisper.load_model("base")
print("loaded model")
result = model.transcribe("audio.mp3")
print("result:", result)
#print(result["text"])

