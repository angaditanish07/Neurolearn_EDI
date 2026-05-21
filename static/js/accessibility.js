/**
 * Global accessibility helpers (navbar + all pages).
 */
(function () {
    'use strict';

    const STORAGE_KEY = 'nl_settings';

    function loadSettings() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
        } catch (e) {
            return {};
        }
    }

    function saveSettings() {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(window.NeuroLearnA11y.state));
    }

    function announceChange(message) {
        const el = document.createElement('div');
        el.setAttribute('role', 'alert');
        el.setAttribute('aria-live', 'polite');
        el.className = 'sr-only';
        el.textContent = message;
        document.body.appendChild(el);
        setTimeout(() => el.remove(), 1200);
    }

    const saved = loadSettings();
    window.NeuroLearnA11y = {
        state: {
            dyslexicFont: !!saved.dyslexicFont,
            highContrast: !!saved.highContrast,
            fontSize: saved.fontSize || 16,
            readAloud: !!saved.readAloud,
        },

        applyAll() {
            document.body.classList.toggle('dyslexic-font', this.state.dyslexicFont);
            document.body.classList.toggle('high-contrast', this.state.highContrast);
            document.documentElement.style.fontSize = `${this.state.fontSize}px`;
        },

        toggleDyslexicFont() {
            this.state.dyslexicFont = !this.state.dyslexicFont;
            document.body.classList.toggle('dyslexic-font', this.state.dyslexicFont);
            saveSettings();
            announceChange(`Dyslexic friendly font ${this.state.dyslexicFont ? 'enabled' : 'disabled'}`);
        },

        toggleHighContrast() {
            this.state.highContrast = !this.state.highContrast;
            document.body.classList.toggle('high-contrast', this.state.highContrast);
            saveSettings();
            announceChange(`High contrast ${this.state.highContrast ? 'enabled' : 'disabled'}`);
        },

        adjustTextSize(delta) {
            const minSize = 12;
            const maxSize = 28;
            this.state.fontSize = Math.max(minSize, Math.min(maxSize, this.state.fontSize + delta));
            document.documentElement.style.fontSize = `${this.state.fontSize}px`;
            saveSettings();
            announceChange(`Text size ${this.state.fontSize}px`);
        },

        toggleReadAloud() {
            this.state.readAloud = !this.state.readAloud;
            saveSettings();
            announceChange(`Read aloud ${this.state.readAloud ? 'enabled' : 'disabled'}`);
            return this.state.readAloud;
        },

        speakText(text) {
            if (!this.state.readAloud || !text || !window.speechSynthesis) return;
            window.speechSynthesis.cancel();
            const u = new SpeechSynthesisUtterance(String(text).slice(0, 500));
            u.rate = 0.95;
            window.speechSynthesis.speak(u);
        },

        readMainContent() {
            const main = document.querySelector('main, .main-content, .container, .auth-card');
            if (main) {
                this.speakText(main.innerText.replace(/\s+/g, ' ').trim().slice(0, 800));
            }
        },
    };

    NeuroLearnA11y.applyAll();

    window.toggleDyslexicFont = () => NeuroLearnA11y.toggleDyslexicFont();
    window.toggleHighContrast = () => NeuroLearnA11y.toggleHighContrast();
    window.adjustTextSize = (d) => NeuroLearnA11y.adjustTextSize(d);
    window.toggleReadAloud = () => NeuroLearnA11y.toggleReadAloud();
    window.announceChange = announceChange;
})();
