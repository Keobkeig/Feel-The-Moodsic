import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential, save_model, load_model
from tensorflow.keras.layers import Input, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import joblib

# Load dataset
# data = pd.read_csv("data/data_moods.csv")
data = pd.read_csv("data/SpotifyAudioFeaturesApril2019.csv")

# Select features and targets
features = ["danceability", "loudness", "tempo", "acousticness", "instrumentalness"]
X = data[features]
y = data[["valence", "energy"]]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Normalize features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Build the model with explicit Input layer
model = Sequential([
    Input(shape=(X_train.shape[1],)),  
    Dense(128, activation='relu'),
    Dropout(0.2),
    Dense(64, activation='relu'),
    Dense(32, activation='relu'),
    Dense(2, activation='linear')
])

# Compile the model
model.compile(optimizer=Adam(learning_rate=0.002), 
             loss='mse', 
             metrics=['mae'])

# Train the model
history = model.fit(X_train, y_train, 
                   epochs=100, 
                   batch_size=32, 
                   validation_split=0.1)

# Save model and scaler
model.save("mood_predictor.keras")  # New recommended .keras format
joblib.dump(scaler, "scaler.save")

# Load and use the model
def load_predictor(model_path="mood_predictor.keras", scaler_path="scaler.save"):
    model = load_model(model_path)
    scaler = joblib.load(scaler_path)
    return model, scaler

# Example usage
if __name__ == "__main__":
    # Load assets
    loaded_model, loaded_scaler = load_predictor()
    
    # sample input
    sample_input = pd.DataFrame([{
        "danceability": 0.75,
        "loudness": -5.2,
        "tempo": 120.5,
        "acousticness": 0.1,
        "instrumentalness": 0.05
    }])
    
    # Preprocess and predict
    scaled_input = loaded_scaler.transform(sample_input)
    prediction = loaded_model.predict(scaled_input)
    
    print(f"Valence: {prediction[0][0]:.2f}")
    print(f"Energy: {prediction[0][1]:.2f}")