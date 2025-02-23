import requests

CLIENT_ID = "dc13d92d4de64452a21c970ed84f15e1"
CLIENT_SECRET = "599c8dbc06734107baa994260dd71dee"

# Get Spotify API Token manually
def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}
    
    response = requests.post(url, headers=headers, data=data, auth=(CLIENT_ID, CLIENT_SECRET))
    print("Token request status:", response.status_code)
    print("Token response text:", response.text)
    token_info = response.json()
    
    access_token = token_info.get("access_token")
    if not access_token:
        print("Failed to get access token:", token_info)
    return access_token

# Search for a track and fetch audio features
def search_spotify_track(title, artist):
    token = get_spotify_token()  # Get a fresh token

    if not token:
        return "No valid token retrieved."
    
    # Set the header in the required format
    headers = {"Authorization": "Bearer " + token}
    
    # Search for track
    search_url = "https://api.spotify.com/v1/search"
    search_params = {"q": f"{title} {artist}", "type": "track", "limit": 1}
    
    search_response = requests.get(search_url, headers=headers, params=search_params)
    # print("Search request status:", search_response.status_code)
    # print("Search response text:", search_response.text)
    
    if search_response.status_code != 200:
        return f"Error during track search: {search_response.status_code}"
    
    search_results = search_response.json()
    
    if search_results.get("tracks", {}).get("items"):
        track = search_results["tracks"]["items"][0]
        track_id = track["id"]

        # Get audio features for the track
        audio_features_url = f"https://api.spotify.com/v1/audio-analysis/{track_id}"
        audio_features_response = requests.get(audio_features_url, headers=headers)
        print("Audio features request status:", audio_features_response.status_code)
        print("Audio features response text:", audio_features_response.text)
        
        if audio_features_response.status_code != 200:
            return f"Error fetching audio features: {audio_features_response.status_code}"
        
        features = audio_features_response.json()
        return {
            "spotify_id": track_id,
            "spotify_url": track["external_urls"]["spotify"],
            "valence": features.get("valence"),
            "energy": features.get("energy")
        }
    return "No track found."

# Example usage:
result = search_spotify_track("Blinding Lights", "The Weeknd")
print(result)
