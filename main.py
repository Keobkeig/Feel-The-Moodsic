import asyncio
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import cv2
from shazamio import Shazam 
import pandas as pd
from tensorflow.keras.models import load_model
import joblib
import serial
import colormap
import time
import argparse

# Configuration
RECORD_DURATION = 5  # seconds
IMAGE_SIZE = 400

parser = argparse.ArgumentParser(description="Music Mood Visualizer")
parser.add_argument('--arduino', action='store_true', help='Enable Arduino hardware integration')
args = parser.parse_args()
ENABLE_ARDUINO = args.arduino

if ENABLE_ARDUINO:
    try:
        ser = serial.Serial('/dev/tty.usbmodem1101', 9600, timeout=1)
        time.sleep(2)
        print("[Arduino] Serial connection established")    
    except Exception as e:
        print(f"[Arduino] Failed to initialize serial connection: {e}")
        ENABLE_ARDUINO = False


genre_features = {
    'Afrobeats': [0.85, 0.92, 0.88, 0.15, 0.25],  
    'Alternative': [0.40, 0.55, 0.45, 0.75, 0.65],  
    'Country': [0.75, 0.50, 0.55, 0.85, 0.45],     
    'Classical': [0.25, 0.25, 0.20, 0.98, 0.99], 
    'Dance': [0.95, 0.97, 0.93, 0.05, 0.75],       
    'Electronic': [0.65, 0.85, 0.75, 0.20, 0.95],
    'Electronica': [0.68, 0.88, 0.78, 0.18, 0.92],   
    'Film, TV & Stage': [0.30, 0.45, 0.35, 0.95, 0.85],  
    'French Pop': [0.72, 0.58, 0.68, 0.48, 0.42],  
    'Hip-Hop': [0.70, 0.80, 0.78, 0.30, 0.15], 
    'Hip-Hop/Rap': [0.72, 0.82, 0.80, 0.28, 0.12],
    'House': [0.82, 0.88, 0.92, 0.18, 0.82],       
    'Indie Rock': [0.45, 0.50, 0.55, 0.70, 0.75],
    'J-Pop': [0.78, 0.83, 0.85, 0.28, 0.33],
    'K-Pop': [0.78, 0.83, 0.85, 0.28, 0.33],       
    'Latin': [0.88, 0.92, 0.86, 0.38, 0.52],      
    'Música Mexicana': [0.73, 0.63, 0.69, 0.58, 0.55],
    'MandoPop': [0.80, 0.85, 0.82, 0.30, 0.25],
    'Pop': [0.83, 0.87, 0.83, 0.35, 0.20],         
    'Rap': [0.75, 0.85, 0.80, 0.25, 0.10],
    'R&B/Soul': [0.55, 0.50, 0.58, 0.72, 0.38],    
    'Reggae/Dancehall': [0.68, 0.65, 0.67, 0.55, 0.48],  
    'Rock': [0.52, 0.75, 0.62, 0.60, 0.63],         
    'Singer/Songwriter': [0.38, 0.28, 0.32, 0.92, 0.42], 
    'Worldwide': [0.69, 0.62, 0.70, 0.50, 0.72],   
    'Jazz': [0.48, 0.38, 0.42, 0.83, 0.97]         
}

# Load the model and scaler
model = load_model("mood_predictor.keras")
scaler = joblib.load("scaler.save")

# Prepare the genre features
genre_df = pd.DataFrame(genre_features).T
genre_df.columns = ["danceability", "loudness", "tempo", "acousticness", "instrumentalness"]
required_features = ["danceability", "loudness", "tempo", "acousticness", "instrumentalness"]
genre_df = genre_df[required_features]
scaled_input = scaler.transform(genre_df)

# Running the prediction model and storing the results
predictions = model.predict(scaled_input)

genre_predictions = {
    genre: {
        "valence": float(predictions[i][0]),
        "energy": float(predictions[i][1])
    }
    for i, genre in enumerate(genre_features.keys())
}

def record_audio(filename='recording.wav', duration=RECORD_DURATION, samplerate=44100):
    '''
    Record audio from the default input device and save it to a WAV file.
    '''
    print("Recording...")
    try:
        default_input = sd.query_devices(kind='input')
        print(f"Using input device: {default_input['name']}")
        channels = min(2, default_input['max_input_channels'])
        
        recording = sd.rec(int(duration * samplerate),
                          samplerate=samplerate,
                          channels=channels,
                          device=sd.default.device[0])
        sd.wait()
        write(filename, samplerate, recording)
        return filename
    except Exception as e:
        print(f"Recording failed: {str(e)}")
        return None

async def recognize_song_shazam(filename):
    try:
        shazam = Shazam()
        result = await shazam.recognize(filename)
        return result
    except Exception as e:
        print(f"Shazam error: {e}")
        return None
        
def display_results(track_info, soft_valence, soft_energy):
    display_map = cv2.imread("colormap.png")
    
    # Map emotions to the image
    h, w, _ = display_map.shape
    y_center, x_center = int(h / 2), int(w / 2)
    y = y_center - int((h/2) * soft_energy)
    x = x_center + int((w/2) * soft_valence)
    radius = 20

    # Get the median color in the selected region
    color = np.median(display_map[y-2:y+2, x-2:x+2], axis=0).mean(axis=0)
    r, g, b = int(color[0]), int(color[1]), int(color[2])

    # Draw the selected point on the map
    display_map = cv2.circle(display_map, (x, y), radius, (r, g, b), -1)
    display_map = cv2.circle(display_map, (x, y), radius, (255, 255, 255), 2)
    cv2.imshow('Music Recognition', display_map)
    cv2.waitKey(5000)

    if ENABLE_ARDUINO:
        try:
            ser.write(f"{r},{g},{b}\n".encode())
            ser.write(f"{track_info['title']}\n{track_info['artist']}\n".encode())
            print(f"Sent RGB ({r}, {g}, {b}) and song info to Arduino")
        except Exception as e:
            print(f"[Arduino] Communication failed: {e}")

    print(f"Track: {track_info['title']} by {track_info['artist']}")
    time.sleep(0.05) # small delay
    

async def main():
    cv2.namedWindow('Music Recognition', cv2.WINDOW_NORMAL)
    
    while True:
        enter = input("\nPress Enter to start recording...")
        
        if enter == 'q':
            break

        filename = record_audio()
        
        if filename:
            print("Analyzing audio...")
            result = await recognize_song_shazam(filename)
            # if not ser.is_open:
            #     ser.open()
            if result and 'track' in result:
                track_info = {
                    'title': result['track']['title'],
                    'artist': result['track']['subtitle'],
                    'url': result['track']['url'],
                    'genre': result['track']['genres']['primary'] if 'genres' in result['track'] else 'Unknown'
                }
                print(f"\nIdentified: {track_info['title']} by {track_info['artist']}")
                print(f"Genre: {track_info['genre']}")
                #print(f"More info: {track_info['url']}")

                genre = track_info['genre']
                energy = genre_predictions[genre]['energy']
                valence = genre_predictions[genre]['valence']
                energy, valence = interpolate(valence, energy)
                display_results(track_info, valence, energy)
                if ENABLE_ARDUINO and ser.is_open:
                    ser.close()
            else:
                print("No song recognized")
    
def interpolate(valence, energy):
    # Interpolate between emotions from 0-1 range to -1-1 range
    x = (2 * valence) - 1
    y = (2 * energy) - 1   
    return x, y

if __name__ == "__main__":
    asyncio.run(main())