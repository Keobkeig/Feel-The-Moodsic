import asyncio
import sounddevice as sd
from scipy.io.wavfile import write
from shazamio import Shazam
import json

# Configuration
RECORD_DURATION = 10  # seconds
SAMPLE_RATE = 8000

def record_audio(filename='recording.wav'):
    """Record audio from microphone"""
    print("Recording...")
    try:
        # Get default input device
        device_info = sd.query_devices(kind='input')
        channels = min(2, device_info['max_input_channels'])
        
        # Record audio
        audio = sd.rec(int(RECORD_DURATION * SAMPLE_RATE),
                      samplerate=SAMPLE_RATE,
                      channels=channels)
        sd.wait()
        write(filename, SAMPLE_RATE, audio)
        return filename
    except Exception as e:
        print(f"Recording failed: {str(e)}")
        return None

async def recognize(filename):
    """Use Shazam to recognize the recorded audio"""
    try:
        shazam = Shazam()
        result = await shazam.recognize(filename) #this is json result, convert to json
        result = json.loads(result)
        print(result) 
        return result
    except Exception as e:
        print(f"Recognition error: {e}")
        return None

async def main():
    while True:
        input("\nPress Enter to start recording...")
        filename = record_audio()
        
        if filename:
            print("Analyzing audio...")
            track = await recognize(filename)
            
            if track and hasattr(track, 'title'):
                print(f"\n🎵 Identified Track: {track.title}")
                print(f"🎤 Artist: {track.subtitle}")
                print(f"🔗 URL: {track.url}")
            else:
                print("No song recognized")

if __name__ == "__main__":
    asyncio.run(main())