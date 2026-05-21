// Voice Navigation System
class VoiceNav {
    constructor() {
        console.log('Initializing VoiceNav...'); // Debug log
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.initializeSpeechRecognition();
    }

    initializeSpeechRecognition() {
        console.log('Initializing speech recognition...'); // Debug log
        if ('webkitSpeechRecognition' in window) {
            console.log('Speech recognition is supported'); // Debug log
            this.recognition = new webkitSpeechRecognition();
            this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.recognition.lang = 'en-US';

            this.recognition.onstart = () => {
                console.log('Speech recognition started'); // Debug log
            };

            this.recognition.onresult = (event) => {
                const command = event.results[event.results.length - 1][0].transcript.toLowerCase();
                console.log('Voice command received:', command); // Debug log
                this.processCommand(command);
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.speak('Error in speech recognition. Please try again.');
            };

            this.recognition.onend = () => {
                console.log('Speech recognition ended'); // Debug log
                if (this.isListening) {
                    console.log('Restarting speech recognition...'); // Debug log
                    this.recognition.start();
                }
            };
        } else {
            console.error('Speech recognition not supported');
            this.speak('Speech recognition is not supported in your browser.');
        }
    }

    startListening() {
        console.log('Starting voice navigation...'); // Debug log
        if (this.recognition) {
            try {
                this.recognition.start();
                this.isListening = true;
                this.speak('Voice navigation activated. How can I help you?');
                console.log('Voice navigation started successfully'); // Debug log
            } catch (error) {
                console.error('Error starting recognition:', error);
                this.speak('Error starting voice navigation. Please try again.');
            }
        } else {
            console.error('Speech recognition not initialized');
            this.speak('Voice navigation is not available. Please refresh the page and try again.');
        }
    }

    stopListening() {
        console.log('Stopping voice navigation...'); // Debug log
        if (this.recognition) {
            this.recognition.stop();
            this.isListening = false;
            this.speak('Voice navigation deactivated.');
            console.log('Voice navigation stopped successfully'); // Debug log
        }
    }

    speak(text) {
        console.log('Speaking:', text); // Debug log
        if (this.synthesis) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            this.synthesis.speak(utterance);
        } else {
            console.error('Speech synthesis not available');
        }
    }

    processCommand(command) {
        console.log('Processing command:', command); // Debug log

        // Navigation commands
        if (command.includes('go to')) {
            const destination = command.replace('go to', '').trim();
            console.log('Navigating to:', destination); // Debug log
            this.navigateTo(destination);
        }
        // Feature activation commands
        else if (command.includes('start')) {
            const feature = command.replace('start', '').trim();
            console.log('Starting feature:', feature); // Debug log
            this.startFeature(feature);
        }
        // Feature deactivation commands
        else if (command.includes('stop')) {
            const feature = command.replace('stop', '').trim();
            console.log('Stopping feature:', feature); // Debug log
            this.stopFeature(feature);
        }
        // Help command
        else if (command.includes('help')) {
            console.log('Showing help'); // Debug log
            this.showHelp();
        }
        // Text size commands
        else if (command.includes('bigger text')) {
            console.log('Increasing text size'); // Debug log
            this.increaseTextSize();
        }
        else if (command.includes('smaller text')) {
            console.log('Decreasing text size'); // Debug log
            this.decreaseTextSize();
        }
        // Navigation commands without "go to"
        else if (command.includes('interactive learning')) {
            console.log('Navigating to interactive learning'); // Debug log
            this.navigateTo('interactive learning');
        }
        else if (command.includes('dyslexia test') || command.includes('dyslexia screening')) {
            console.log('Navigating to dyslexia screening'); // Debug log
            this.navigateTo('dyslexia screening');
        }
        else if (command.includes('home')) {
            console.log('Navigating to home'); // Debug log
            this.navigateTo('home');
        }
        else if (command.includes('profile')) {
            console.log('Navigating to profile'); // Debug log
            this.navigateTo('profile');
        }
        else if (command.includes('settings')) {
            console.log('Navigating to settings'); // Debug log
            this.navigateTo('settings');
        }
        else {
            console.log('Command not recognized:', command); // Debug log
            this.speak('Command not recognized. Say help for available commands.');
        }
    }

    navigateTo(destination) {
        const destinations = {
            'home': '/',
            'interactive learning': '/interactive_learning',
            'dyslexia screening': '/dyslexia_screening',
            'take dyslexia test': '/dyslexia_screening',
            'start dyslexia test': '/dyslexia_screening',
            'profile': '/profile',
            'settings': '/settings'
        };

        if (destinations[destination]) {
            window.location.href = destinations[destination];
            this.speak(`Navigating to ${destination}`);
        } else {
            this.speak(`Sorry, I couldn't find ${destination}`);
        }
    }

    startFeature(feature) {
        const features = {
            'camera': () => {
                const video = document.querySelector('video');
                if (video) {
                    video.play();
                    this.speak('Camera started');
                }
            },
            'recording': () => {
                const recordButton = document.querySelector('.btn-record');
                if (recordButton) {
                    recordButton.click();
                    this.speak('Recording started');
                }
            },
            'emotion detection': () => {
                const emotionButton = document.querySelector('.btn-emotion');
                if (emotionButton) {
                    emotionButton.click();
                    this.speak('Emotion detection started');
                }
            }
        };

        if (features[feature]) {
            features[feature]();
        } else {
            this.speak(`Feature ${feature} not found`);
        }
    }

    stopFeature(feature) {
        const features = {
            'camera': () => {
                const video = document.querySelector('video');
                if (video) {
                    video.pause();
                    this.speak('Camera stopped');
                }
            },
            'recording': () => {
                const recordButton = document.querySelector('.btn-record');
                if (recordButton) {
                    recordButton.click();
                    this.speak('Recording stopped');
                }
            },
            'emotion detection': () => {
                const emotionButton = document.querySelector('.btn-emotion');
                if (emotionButton) {
                    emotionButton.click();
                    this.speak('Emotion detection stopped');
                }
            }
        };

        if (features[feature]) {
            features[feature]();
        } else {
            this.speak(`Feature ${feature} not found`);
        }
    }

    increaseTextSize() {
        const body = document.body;
        const currentSize = window.getComputedStyle(body).fontSize;
        const newSize = parseFloat(currentSize) + 2;
        body.style.fontSize = `${newSize}px`;
        this.speak('Text size increased');
    }

    decreaseTextSize() {
        const body = document.body;
        const currentSize = window.getComputedStyle(body).fontSize;
        const newSize = Math.max(parseFloat(currentSize) - 2, 8);
        body.style.fontSize = `${newSize}px`;
        this.speak('Text size decreased');
    }

    showHelp() {
        const helpText = `
            Available voice commands:
            - "Go to [page name]" - Navigate to different pages
            - "Start [feature name]" - Start a feature (camera, recording, emotion detection)
            - "Stop [feature name]" - Stop a feature
            - "Bigger text" - Increase text size
            - "Smaller text" - Decrease text size
            - "Help" - Show this help message
            
            Example commands:
            - "Go to interactive learning"
            - "Go to dyslexia screening"
            - "Start camera"
            - "Stop recording"
            - "Bigger text"
            - "Smaller text"
        `;
        this.speak(helpText);
    }
}

// Initialize voice navigation when the page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing voice navigation...'); // Debug log
    
    // Create voice navigation instance
    const voiceNav = new VoiceNav();
    
    // Add voice navigation toggle button
    const voiceButton = document.createElement('button');
    voiceButton.id = 'voice-nav-toggle';
    voiceButton.className = 'btn btn-purple';
    voiceButton.innerHTML = '<i class="fas fa-microphone"></i> Voice Navigation';
    voiceButton.onclick = () => {
        console.log('Voice button clicked'); // Debug log
        if (voiceNav.isListening) {
            voiceNav.stopListening();
            voiceButton.classList.remove('active');
        } else {
            voiceNav.startListening();
            voiceButton.classList.add('active');
        }
    };
    
    // Add button to navigation
    const navContainer = document.querySelector('.nav-container');
    if (navContainer) {
        console.log('Adding voice button to nav container'); // Debug log
        navContainer.appendChild(voiceButton);
    } else {
        console.log('Nav container not found, adding voice button to body'); // Debug log
        document.body.appendChild(voiceButton);
    }

    // Add voice navigation styles
    const style = document.createElement('style');
    style.textContent = `
        #voice-nav-toggle {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            padding: 10px 20px;
            border-radius: 25px;
            background: var(--primary-gradient);
            color: white;
            border: none;
            cursor: pointer;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        #voice-nav-toggle:hover {
            transform: scale(1.05);
        }
        #voice-nav-toggle.active {
            background: var(--error-color);
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
    `;
    document.head.appendChild(style);
    
    console.log('Voice navigation initialization complete'); // Debug log
}); 