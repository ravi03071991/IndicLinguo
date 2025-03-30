import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import requests # Placeholder for Sarvam API calls
from mistralai import Mistral # Ensure this is the correct import
import base64

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys safely from environment variables
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY") # Get Mistral key

# --- Initialize API Clients ---

# Check Sarvam key
if not SARVAM_API_KEY:
    print("Warning: SARVAM_API_KEY not found in environment variables.")
    # Handle missing key appropriately

# Initialize Mistral client
mistral_client = None
if MISTRAL_API_KEY:
    mistral_client = Mistral(api_key=MISTRAL_API_KEY)
    MISTRAL_MODEL = "mistral-large-latest" # Or choose another model
else:
    print("Warning: MISTRAL_API_KEY not found. Role-playing will be disabled.")

# Sarvam API endpoints and Headers
TRANSLATION_API_URL = "https://api.sarvam.ai/translate"
# TODO: Confirm exact header format needed by Sarvam API
SARVAM_HEADERS = {
    "Content-Type": "application/json",
    "api-subscription-key": SARVAM_API_KEY # Assuming Bearer token auth
}
TRANSLITERATION_API_URL = "https://api.sarvam.ai/transliterate"
TTS_API_URL = "https://api.sarvam.ai/text-to-speech"

# Configure Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Mapping from frontend language codes to Sarvam API codes
LANGUAGE_MAP = {
    'en': 'en-IN',
    'hi': 'hi-IN',
    'bn': 'bn-IN',
    'gu': 'gu-IN',
    'kn': 'kn-IN',
    'ml': 'ml-IN',
    'mr': 'mr-IN',
    'od': 'od-IN',
    'pa': 'pa-IN',
    'ta': 'ta-IN',
    'te': 'te-IN',
}

# --- Routes ---

@app.route('/')
def index():
    """Serves the main HTML file."""
    # Note: We configure static_folder to point to 'frontend',
    # so Flask will automatically look for 'index.html' in 'frontend'.
    # However, explicitly sending it ensures clarity.
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def send_static(path):
    """Serves static files (CSS, JS, images) from the frontend folder."""
    return send_from_directory(app.static_folder, path)

@app.route('/api/converse', methods=['POST'])
def converse():
    """Handles the user's message and returns AI response with translation, etc."""
    # Check for API keys early
    if not SARVAM_API_KEY:
        return jsonify({"error": "Sarvam API key not configured"}), 500
    if not mistral_client: # Check if Mistral client was initialized
        return jsonify({"error": "Mistral API key not configured or client failed to initialize"}), 500

    try:
        data = request.get_json()
        user_message = data.get('message')
        language_code_short = data.get('language', 'te') # e.g., 'te'
        scenario = data.get('scenario', 'general') # Default scenario
        # Get history from request - Expects a list of {"role": "user/assistant", "content": "..."}
        conversation_history = data.get('history', []) 

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Basic validation for history format (optional but good practice)
        if not isinstance(conversation_history, list):
             return jsonify({"error": "Invalid history format, expected a list"}), 400
        for item in conversation_history:
             if not isinstance(item, dict) or 'role' not in item or 'content' not in item:
                 return jsonify({"error": "Invalid history item format"}), 400

        # Get the full language code for the Sarvam API
        target_language_code_api = LANGUAGE_MAP.get(language_code_short)

        print(f"Target language code: {target_language_code_api}")
        if not target_language_code_api:
            return jsonify({"error": f"Unsupported language code: {language_code_short}"}), 400

        # --- Core Logic ---

        # 1. Generate Role-playing response using Mistral
        ai_response_text = "Error: Role-playing response generation failed."
        try:
            # Define system prompt based on scenario
            scenario_prompts = {
                "general": "You are a helpful language practice partner. Keep your responses concise and conversational. Always keep responses short and make sure responses are specific to indian audience and culture.",
                "medical": "You are a helpful pharmacist in India. Respond to the customer\'s query politely and clearly. Always keep responses short and make sure responses are specific to indian audience and culture.",
                "restaurant": "You are a waiter in an Indian restaurant taking an order. Be polite and confirm the order. Always keep responses short and make sure responses are specific to indian audience and culture.",
                "hotel": "You are a hotel receptionist in India handling check-in or guest requests. Be polite and helpful. Always keep responses short and make sure responses are specific to indian audience and culture.",
                "support": "You are a customer support agent for a generic service in India. Be polite and try to resolve the issue concisely. Always keep responses short and make sure responses are specific to indian audience and culture."
            }
            system_prompt = scenario_prompts.get(scenario, scenario_prompts["general"])

            # Construct messages for Mistral API using dictionaries
            # Start with the system prompt
            messages = [{"role": "system", "content": system_prompt}]
            # Add the conversation history received from the frontend
            messages.extend(conversation_history)
            # Add the latest user message
            messages.append({"role": "user", "content": user_message})

            print(f"Sending to Mistral: {messages}") # Log the messages being sent

            # Use client.chat.complete as per current documentation
            chat_response = mistral_client.chat.complete(
                model=MISTRAL_MODEL,
                messages=messages
            )

            if chat_response.choices:
                ai_response_text = chat_response.choices[0].message.content
            else:
                 print("Mistral API returned no choices.")
                 # Keep the default error message

        except Exception as mistral_err:
             print(f"Mistral API error: {mistral_err}")
             # Keep the default error message

        # 2. Call Sarvam Translation API (using the ai_response_text from Mistral)
        translation = "Error: Translation failed"
        # Only attempt translation if Mistral response is not an error
        if ai_response_text and not ai_response_text.startswith("Error:"):
            try:
                payload = {
                    "input": ai_response_text,
                    "source_language_code": "en-IN", # Assuming Mistral response is English
                    "target_language_code": target_language_code_api,
                }
                api_response = requests.request("POST", TRANSLATION_API_URL, json=payload, headers=SARVAM_HEADERS)
                response_json = api_response.json()
                translation = response_json.get('translated_text', 'Error: Could not parse translation')

            except requests.exceptions.RequestException as req_err:
                print(f"Translation API request error: {req_err}")
            except Exception as json_err:
                 print(f"Translation API JSON parsing error: {json_err}")
                 print(f"Raw response: {api_response.text if 'api_response' in locals() else 'N/A'}")
        elif ai_response_text.startswith("Error:"):
            translation = "Error: Cannot translate due to role-play failure."

        # 3. Call Sarvam Transliteration API
        transliteration = "Error: Transliteration failed"
        # Only attempt if translation succeeded
        if translation and not translation.startswith("Error:"):
            try:
                payload = {
                    "input": translation,
                    "source_language_code": target_language_code_api,
                    "target_language_code": "en-IN",
                }
                api_response_transl = requests.post(TRANSLITERATION_API_URL, json=payload, headers=SARVAM_HEADERS)
                api_response_transl.raise_for_status()
                response_json_transl = api_response_transl.json()
                transliteration = response_json_transl.get('transliterated_text', 'Error: Could not parse transliteration')

            except requests.exceptions.RequestException as req_err:
                print(f"Transliteration API request error: {req_err}")
            except Exception as json_err:
                 print(f"Transliteration API JSON parsing error: {json_err}")
                 print(f"Raw response: {api_response_transl.text if 'api_response_transl' in locals() else 'N/A'}")
        elif translation.startswith("Error:"):
             transliteration = "Error: Cannot transliterate due to previous failure."

        # 4. Call Sarvam TTS API
        audio_base64_data = None # Initialize variable for base64 audio
        # Only attempt TTS if translation succeeded
        if translation and not translation.startswith("Error:"):
            try:
                payload = {
                    "inputs": [translation],
                    "target_language_code": target_language_code_api,
                    "speaker": "meera"
                }
                tts_headers = SARVAM_HEADERS.copy()
                api_response_tts = requests.post(TTS_API_URL, json=payload, headers=tts_headers)
                print("api_response_tts.status_code",api_response_tts.status_code)
                
                if api_response_tts.status_code == 200:
                    response_body_tts = api_response_tts.json()
                    if response_body_tts.get("audios") and len(response_body_tts["audios"]) > 0:
                        # Get the base64 encoded audio string directly
                        audio_base64_data = response_body_tts["audios"][0]
                        print("Successfully received base64 audio data.")
                    else:
                         print(f"TTS API response missing 'audios' field or it's empty. Response: {api_response_tts.text[:200]}")
                         audio_base64_data = "Error: TTS failed - No audio data in response"
                else:
                     print(f"TTS API error. Status: {api_response_tts.status_code}. Response: {api_response_tts.text[:200]}")
                     audio_base64_data = f"Error: TTS failed - Status {api_response_tts.status_code}"

            except requests.exceptions.RequestException as req_err:
                print(f"TTS API request error: {req_err}")
                audio_base64_data = "Error: TTS request failed"
            except Exception as e:
                 print(f"Error processing TTS response: {e}")
                 audio_base64_data = "Error: TTS processing failed"
        else:
             # If translation failed, set the audio error message
             audio_base64_data = "Error: Cannot generate audio due to previous failure."

        # --- Construct Response ---
        response_data = {
            "ai_message": ai_response_text, # The original English response from Mistral
            "translation": translation,
            "transliteration": transliteration,
            "audio_base64": audio_base64_data # Return base64 data instead of path
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Error in /api/converse: {e}")
        # Log the full traceback for debugging
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An unexpected error occurred processing your request."}), 500

# --- Run the App ---

if __name__ == '__main__':
    # Removed debug=True, host is okay for local testing but Gunicorn handles host/port in prod
    app.run(port=5001) 