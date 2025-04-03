document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    const languageSelect = document.getElementById('language-select');
    const scenarioSelect = document.getElementById('scenario-select');
    const startButton = document.getElementById('start-button');
    const quickDemoButton = document.getElementById('quick-demo-button');
    const resetButton = document.getElementById('reset-button');
    const chatbox = document.getElementById('chatbox');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    // Templates for cloning
    const aiResponseTemplate = document.querySelector('.ai-response-template');
    const userMessageTemplate = document.querySelector('.user-message-template');

    let currentLanguage = languageSelect.value;
    let currentLanguageName = languageSelect.options[languageSelect.selectedIndex]?.text || '';
    let currentScenario = scenarioSelect.value;
    let conversationHistory = [];

    // --- Event Listeners ---
    languageSelect.addEventListener('change', (e) => {
        currentLanguage = e.target.value;
        currentLanguageName = e.target.options[e.target.selectedIndex].text;
    });

    scenarioSelect.addEventListener('change', (e) => {
        currentScenario = e.target.value;
    });

    startButton.addEventListener('click', () => {
        if (!languageSelect.value || !scenarioSelect.value) {
            alert("Please select both a language and a scenario.");
            return;
        }
        startConversation();
    });

    quickDemoButton.addEventListener('click', () => {
        languageSelect.value = 'hi';
        scenarioSelect.value = 'general';
        currentLanguage = 'hi';
        currentLanguageName = 'Hindi (हिन्दी)';
        currentScenario = 'general';
        startConversation();
    });

    function startConversation() {
        conversationHistory = [];

        languageSelect.disabled = true;
        scenarioSelect.disabled = true;
        startButton.disabled = true;
        quickDemoButton.disabled = true;
        userInput.disabled = false;
        sendButton.disabled = false;
        resetButton.disabled = false;
        userInput.focus();

        resetButton.style.display = 'inline-block';

        chatbox.innerHTML = '';

        addMessageToChatbox('System', `Type your first message in English to begin practicing ${currentLanguageName}.`);
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    resetButton.addEventListener('click', resetConversation);

    // --- Functions ---

    function addMessageToChatbox(sender, data) {
        let messageElement;

        if (sender === 'User') {
            messageElement = userMessageTemplate.querySelector('.user-message').cloneNode(true);
            messageElement.querySelector('.user-message-text').textContent = data;
        } else if (sender === 'AI') {
            messageElement = aiResponseTemplate.querySelector('.ai-response').cloneNode(true);

            messageElement.querySelector('.original-en-text').textContent = data.ai_message || 'N/A';
            
            messageElement.querySelector('.translation-text').textContent = data.translation || 'N/A';
            messageElement.querySelector('.transliteration-text').textContent = data.transliteration || 'N/A';

            const audioPlayer = messageElement.querySelector('.audio-player');
            const audioSection = messageElement.querySelector('.audio-section');
            const audioErrorText = messageElement.querySelector('.audio-error');

            if (data.audio_base64 && !data.audio_base64.startsWith('Error:')) {
                try {
                    const byteCharacters = atob(data.audio_base64);
                    const byteNumbers = new Array(byteCharacters.length);
                    for (let i = 0; i < byteCharacters.length; i++) {
                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                    }
                    const byteArray = new Uint8Array(byteNumbers);
                    const audioBlob = new Blob([byteArray], { type: 'audio/wav' });
                    const audioUrl = URL.createObjectURL(audioBlob);
                    
                    audioPlayer.src = audioUrl;
                    audioPlayer.style.display = 'block';
                    if (audioErrorText) audioErrorText.style.display = 'none';
                    
                    audioPlayer.onended = () => {
                        URL.revokeObjectURL(audioUrl);
                    };

                } catch (e) {
                    console.error("Error processing base64 audio:", e);
                    if(audioSection) audioSection.style.display = 'block';
                    if(audioPlayer) audioPlayer.style.display = 'none';
                    if (audioErrorText) {
                        audioErrorText.textContent = 'Error playing audio.';
                        audioErrorText.style.display = 'block';
                    }
                }
            } else {
                if(audioSection) audioSection.style.display = 'block';
                if(audioPlayer) audioPlayer.style.display = 'none';
                if (audioErrorText) {
                    audioErrorText.textContent = data.audio_base64 || 'Audio not available.';
                    audioErrorText.style.display = 'block';
                }
            }
        } else {
            messageElement = document.createElement('div');
            messageElement.classList.add('response-block', 'system-message');
            messageElement.innerHTML = data;
        }

        chatbox.appendChild(messageElement);
        chatbox.scrollTop = chatbox.scrollHeight;
    }

    async function sendMessage() {
        const messageText = userInput.value.trim();
        if (!messageText) return;

        addMessageToChatbox('User', messageText);
        conversationHistory.push({ role: "user", content: messageText });
        console.log("History before sending:", JSON.stringify(conversationHistory));

        userInput.value = '';

        const thinkingIndicator = document.createElement('div');
        thinkingIndicator.classList.add('response-block', 'system-message', 'thinking');
        thinkingIndicator.innerHTML = `<p><i>AI is thinking...</i></p>`;
        chatbox.appendChild(thinkingIndicator);
        chatbox.scrollTop = chatbox.scrollHeight;

        sendButton.disabled = true;

        try {
            const response = await fetch('/api/converse', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: messageText,
                    language: currentLanguage,
                    scenario: currentScenario,
                    history: conversationHistory.slice(0, -1)
                }),
            });

            const thinkingMsg = chatbox.querySelector('.thinking');
            if (thinkingMsg) thinkingMsg.remove();

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: 'Failed to parse error response' }));
                conversationHistory.pop(); 
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data.ai_message && !data.ai_message.startsWith('Error:')) {
                 conversationHistory.push({ role: "assistant", content: data.ai_message });
                 console.log("History after receiving AI:", JSON.stringify(conversationHistory));
            } else {
                 conversationHistory.pop();
                 console.log("AI Error - History reverted:", JSON.stringify(conversationHistory));
            }
            addMessageToChatbox('AI', data);

        } catch (error) {
            console.error('Error sending message:', error);
            const thinkingMsg = chatbox.querySelector('.thinking');
            if (thinkingMsg) thinkingMsg.remove();
            if (conversationHistory.length > 0 && conversationHistory[conversationHistory.length - 1].role === 'user') {
                 conversationHistory.pop();
            }
            addMessageToChatbox('System', `Error: ${error.message}. Please try again.`);
        } finally {
            sendButton.disabled = false;
            userInput.focus();
        }
    }

    // Function to reset the conversation state
    function resetConversation() {
        conversationHistory = [];
        chatbox.innerHTML = '';

        addMessageToChatbox('System', 'Select language & scenario, or try the Quick Demo.');

        userInput.disabled = true;
        sendButton.disabled = true;
        resetButton.disabled = true;
        userInput.value = '';

        languageSelect.disabled = false;
        scenarioSelect.disabled = false;
        startButton.disabled = false;
        quickDemoButton.disabled = false;

        resetButton.style.display = 'none';

        languageSelect.value = '';
        scenarioSelect.value = '';
        currentLanguage = '';
        currentLanguageName = '';
        currentScenario = '';
    }

    // --- Dark Mode Logic ---
    const themeCheckbox = document.getElementById('theme-checkbox');

    // Function to set the theme
    function setTheme(themeName) {
        localStorage.setItem('theme', themeName);
        document.documentElement.setAttribute('data-theme', themeName);
    }

    // Function to toggle theme
    function toggleTheme() {
        if (localStorage.getItem('theme') === 'dark') {
            setTheme('light');
        } else {
            setTheme('dark');
        }
    }

    // Apply the saved theme on initial load
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        setTheme(savedTheme);
        if (savedTheme === 'dark') {
            themeCheckbox.checked = true;
        }
    } else {
        setTheme('light'); 
    }

    // Add event listener for the toggle switch
    themeCheckbox.addEventListener('change', toggleTheme);
    
    // --- Decorative Background Character Logic ---
    const backgroundCharElement = document.querySelector('.background-char');
    if (backgroundCharElement) {
        const indicChars = [
            'क', 'অ', 'અ', 'ਕ', 'ಅ', 'അ', 'क', 'ଓ', 'த', 'తె' // Hindi, Bengali, Gujarati, Punjabi, Kannada, Malayalam, Marathi, Odia, Tamil, Telugu
        ];
        let charIndex = Math.floor(Math.random() * indicChars.length);

        function changeBackgroundChar() {
            charIndex = (charIndex + 1) % indicChars.length;
            backgroundCharElement.style.opacity = 0; // Start fade out
            setTimeout(() => {
                backgroundCharElement.textContent = indicChars[charIndex];
                backgroundCharElement.style.opacity = 1; // Fade back in
            }, 400); // Match half of interval duration + CSS transition time
        }
        
        // Initial random character
        backgroundCharElement.textContent = indicChars[charIndex];
        backgroundCharElement.style.opacity = 1; // Make it visible initially
        backgroundCharElement.style.transition = 'opacity 0.4s ease-in-out'; // Add transition effect

        // Change character every few seconds
        setInterval(changeBackgroundChar, 2000); // Change every 2 seconds
    }

}); 