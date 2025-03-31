# IndicLinguo: Indian Language Learning Buddy

Meet Linguo — your buddy for learning Indian languages through conversational practice, powered by MistralAI and SarvamAI.

> **Note:** Currently supports practice in 10 Indian languages: Hindi, Bengali, Gujarati, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, and Telugu.

## ✨ Features

*   **Conversational Practice:** Engage in role-playing scenarios (e.g., restaurant, hotel) to practice speaking.
*   **10 Indian Languages:** Supports learning 10 different Indian languages (e.g., Telugu, Hindi, Tamil, Kannada).
*   **MistralAI LLMs:** Uses MistralAI for generating conversational responses.
*   **Translation & Transliteration:** Provides translations and transliterations of the AI's responses (powered by SarvamAI).
*   **Text-to-Speech:** Hear the pronunciation of the translated responses (powered by SarvamAI).

## 📋 Prerequisites

*   **Python 3.8+**
*   **pip** (Python package installer)
*   **MistralAI API Key:** Get one from [Mistral AI](https://console.mistral.ai/api-keys).
*   **SarvamAI API Key:** Get one from [Sarvam AI](https://dashboard.sarvam.ai/admin).

## ⚙️ Setup

1.  **Clone the Repository:**
    ```bash
    git clone http://github.com/ravi03071991/IndicLinguo
    cd IndicLinguo
    ```

2.  **Backend Setup:**
    *   Navigate to the backend directory:
        ```bash
        cd backend
        ```
    *   Create a virtual environment (recommended):
        ```bash
        python3 -m venv venv
        source venv/bin/activate # On Windows use `venv\Scripts\activate`
        ```
    *   Install required Python packages:
        ```bash
        pip install -r requirements.txt
        ```
    *   Create a `.env` file in the `backend` directory:
        ```
        SARVAM_API_KEY='YOUR_SARVAM_API_KEY'
        MISTRAL_API_KEY='YOUR_MISTRAL_API_KEY'
        ```
        Replace `YOUR_SARVAM_API_KEY` and `YOUR_MISTRAL_API_KEY` with your actual keys.

3.  **Frontend Setup:**
    *   No specific build steps are required for the frontend as it's plain HTML, CSS, and JavaScript.

## ▶️ Running the Application

1.  **Start the Backend Server:**
    *   Make sure you are in the `backend` directory and your virtual environment is activated.
    *   Run the Flask application:
        ```bash
        flask run
        ```
        *Alternatively, you can run `python app.py`.*
    *   The backend server will typically start on `http://127.0.0.1:5000`.

2.  **Access the Frontend:**
    *   Open your web browser and navigate to `http://127.0.0.1:5000`.
    *   The application interface should load.

## 🚀 How to Use

1.  **Select Language:** Choose the Indian language you want to practice from the dropdown menu.
2.  **Select Scenario:** Pick a conversational scenario (e.g., General, Restaurant, Hotel) from the dropdown.
3.  **Start Conversation:** Click the "Start Conversation" button.
4.  **Interact:** Type your messages in English in the input box at the bottom and press Enter or click the Send button.
5.  **View Response:** The AI's response will appear, along with:
    *   **Translation:** The AI's response translated into your selected language.
    *   **Transliteration:** The transliterated response into your selected language.
    *   **Audio:** An audio version to hear the pronunciation of the translation.
6.  **Quick Demo:** Use the "Quick Demo" button for a pre-filled example conversation.
7.  **Theme:** Use the toggle switch in the top-right corner to switch between light and dark modes.

## 🛠️ Technologies Used

*   **Backend:** Python, Flask, MistralAI API, SarvamAI API (Translation, Transliteration, TTS)
*   **Frontend:** HTML, CSS, JavaScript
*   **AI Models:** Mistral Large (via API), Sarvam AI Models (via API)
