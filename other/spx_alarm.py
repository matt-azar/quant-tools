from binaries import *
from time import sleep
from datetime import datetime
import sounddevice as sd
from os import system

sd.default.device = "pulse"

def alarm():
    for _ in range(10):
        duration = 1.0              # Duration in seconds
        frequency = 440.0           # Frequency in Hertz (A4)
        amplitude = 0.2             # Volume (0.0 to 1.0)
        samplerate = 44100 // 2     # Samples per second
        t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
        waveform = amplitude * np.sin(2 * np.pi * frequency * t)
        sd.play(waveform, samplerate=samplerate, blocksize=2048, latency='high')
        sd.sleep(2000)

warn_price = 5930
period = input("Period (default 5): ")
if period == "":
    period = 5
else:
    period = int(period)

while(1):
    system('clear')
    
    now = datetime.now()    
    print(f"{now:%T}\n")
    
    print('S&P 500')
    try:
        print(f"{(p:=price('^GSPC')):,.2f}\n")
        if p < warn_price:
            alarm()
    except Exception as e:
        print("[Failed to retrieve price.]\n")
        print(e)

    sleep(period)
