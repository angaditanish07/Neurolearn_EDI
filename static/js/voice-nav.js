// Voice Navigation System (shared across all pages with dashboard navbar)
class VoiceNav {
    constructor() {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.initializeSpeechRecognition();
    }

    initializeSpeechRecognition() {
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SR) return;

        this.recognition = new SR();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';

        this.recognition.onresult = (event) => {
            const command = event.results[event.results.length - 1][0].transcript.toLowerCase().trim();
            this.processCommand(command);
        };

        this.recognition.onerror = () => {
            this.speak('Speech recognition error. Please try again.');
        };

        this.recognition.onend = () => {
            if (this.isListening) {
                try {
                    this.recognition.start();
                } catch (e) { /* ignore */ }
            }
        };
    }

    startListening() {
        if (!this.recognition) {
            this.speak('Speech recognition is not supported in your browser.');
            return;
        }
        try {
            this.recognition.start();
            this.isListening = true;
            this.speak('Voice navigation activated.');
        } catch (e) {
            this.speak('Error starting voice navigation.');
        }
    }

    stopListening() {
        if (this.recognition) {
            this.recognition.stop();
            this.isListening = false;
            this.speak('Voice navigation deactivated.');
        }
    }

    speak(text) {
        if (!this.synthesis || !text) return;
        this.synthesis.cancel();
        const u = new SpeechSynthesisUtterance(String(text).slice(0, 200));
        this.synthesis.speak(u);
    }

    processCommand(command) {
        if (command.includes('help')) {
            this.showHelp();
            return;
        }
        if (command.includes('bigger text') || command.includes('increase font')) {
            if (window.adjustTextSize) adjustTextSize(2);
            this.speak('Text size increased');
            return;
        }
        if (command.includes('smaller text') || command.includes('decrease font')) {
            if (window.adjustTextSize) adjustTextSize(-2);
            this.speak('Text size decreased');
            return;
        }
        if (command.includes('dyslexic')) {
            if (window.toggleDyslexicFont) toggleDyslexicFont();
            return;
        }
        if (command.includes('high contrast') || command.includes('contrast')) {
            if (window.toggleHighContrast) toggleHighContrast();
            return;
        }
        if (command.includes('read aloud') || command === 'read') {
            if (window.NeuroLearnA11y) NeuroLearnA11y.readMainContent();
            return;
        }

        if (command.includes('go to') || command.includes('open ')) {
            const dest = command.replace('go to', '').replace('open', '').trim();
            this.navigateTo(dest);
            return;
        }

        const routes = [
            ['interactive learning', '/interactive_learning'],
            ['dyslexia', '/dyslexia_screening'],
            ['screening', '/dyslexia_screening'],
            ['parent dashboard', '/parent/dashboard'],
            ['parent', '/parent/dashboard'],
            ['profile', '/profile'],
            ['settings', '/settings'],
            ['help', '/help'],
            ['home', '/'],
            ['login', '/login'],
        ];
        for (const [phrase, url] of routes) {
            if (command.includes(phrase)) {
                window.location.href = url;
                this.speak(`Going to ${phrase}`);
                return;
            }
        }

        this.speak('Command not recognized. Say help for options.');
    }

    navigateTo(destination) {
        const destinations = {
            home: '/',
            'interactive learning': '/interactive_learning',
            'dyslexia screening': '/dyslexia_screening',
            'dyslexia test': '/dyslexia_screening',
            profile: '/profile',
            settings: '/settings',
            help: '/help',
            'parent dashboard': '/parent/dashboard',
        };
        const key = destination.trim();
        if (destinations[key]) {
            window.location.href = destinations[key];
            this.speak(`Navigating to ${key}`);
        } else {
            this.speak(`Sorry, I could not find ${destination}`);
        }
    }

    showHelp() {
        this.speak(
            'Say: go to home, interactive learning, dyslexia screening, profile, settings, help, parent dashboard. ' +
            'Or: bigger text, smaller text, dyslexic font, high contrast, read aloud.'
        );
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (window.NeuroLearnVoiceNav) return;
    window.NeuroLearnVoiceNav = new VoiceNav();
});
