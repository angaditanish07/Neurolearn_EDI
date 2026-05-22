/**
 * Global accessibility helpers (navbar + all pages).
 */
(function () {
    'use strict';

    const STORAGE_KEY = 'nl_settings';

    const UI_SELECTORS_TO_SKIP = [
        'button',
        'input',
        'select',
        'textarea',
        'script',
        'style',
        'nav',
        '.nav-bar',
        '.dashboard-nav',
        '.voice-controls',
        '.voice-controls-global',
        '.status-indicator',
        '.sr-only',
        '.path-read-btn',
        '.icon',
        '[aria-hidden="true"]',
        '[data-skip-read-aloud]',
    ].join(', ');

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
        el.setAttribute('role', 'status');
        el.setAttribute('aria-live', 'polite');
        el.className = 'sr-only';
        el.setAttribute('data-skip-read-aloud', 'true');
        el.textContent = message;
        document.body.appendChild(el);
        setTimeout(() => el.remove(), 800);
    }

    /** Remove emojis and symbols TTS often reads aloud (🔊, 🎯, etc.). */
    function sanitizeSpeechText(text) {
        let t = String(text || '');
        try {
            t = t.replace(/\p{Extended_Pictographic}/gu, '');
        } catch (e) {
            // Fallback for older engines without Unicode property escapes
            t = t.replace(/(?:[\u2700-\u27BF]|[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|[\u2011-\u26FF]|\uD83E[\uDD00-\uDDFF])/g, '');
        }
        t = t.replace(/[\uFE00-\uFE0F\u200D\u20E3]/g, '');
        t = t.replace(/🔊\s*Read Aloud/gi, '');
        t = t.replace(/Read Aloud/gi, '');
        t = t.replace(/Reading\.\.\./gi, '');
        t = t.replace(/\s+/g, ' ').trim();
        return t;
    }

    /** Strip UI chrome so we never read "Read Aloud", nav labels, or button names. */
    function extractReadableText(root) {
        if (!root) return '';
        const clone = root.cloneNode(true);
        clone.querySelectorAll(UI_SELECTORS_TO_SKIP).forEach((node) => node.remove());
        return sanitizeSpeechText(clone.textContent || '');
    }

    /**
     * Pick a real TTS voice — skip Windows device names like "Speakers (High volume)".
     */
    function pickSafeVoice() {
        const voices = window.speechSynthesis.getVoices();
        if (!voices.length) return null;

        const badName = /speaker|volume|audio device|realtek|high definition|headphone|bluetooth|hdmi|display/i;

        const good = voices.filter(
            (v) =>
                v.lang &&
                v.lang.startsWith('en') &&
                !badName.test(v.name) &&
                v.name.length < 80
        );

        const prefer = good.find((v) => /google|zira|david|mark|aria|jenny|guy|samantha|microsoft/i.test(v.name));
        return prefer || good[0] || null;
    }

    function isScreeningPage() {
        return (
            document.body.dataset.screeningPage === '1' ||
            window.location.pathname === '/dyslexia_screening' ||
            window.location.pathname.endsWith('/dyslexia_screening')
        );
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
            if (isScreeningPage()) {
                document.body.classList.remove('dyslexic-font');
            } else {
                document.body.classList.toggle('dyslexic-font', this.state.dyslexicFont);
            }
            document.body.classList.toggle('high-contrast', this.state.highContrast);
            document.documentElement.style.fontSize = `${this.state.fontSize}px`;
        },

        toggleDyslexicFont() {
            if (isScreeningPage()) {
                document.body.classList.remove('dyslexic-font');
                announceChange('Dyslexic font is off during screening for accurate results');
                return;
            }
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
            announceChange(`Auto read aloud ${this.state.readAloud ? 'on' : 'off'}`);
            return this.state.readAloud;
        },

        sanitizeSpeechText(text) {
            return sanitizeSpeechText(text);
        },

        speakNow(text, maxLen) {
            const cleaned = sanitizeSpeechText(text);
            if (!cleaned || !window.speechSynthesis) {
                if (!window.speechSynthesis) {
                    announceChange('Read aloud is not supported in this browser');
                }
                return;
            }

            window.speechSynthesis.cancel();

            const u = new SpeechSynthesisUtterance(cleaned.slice(0, maxLen || 1200));
            u.rate = 0.95;
            u.pitch = 1;
            u.volume = 1;
            u.lang = 'en-US';

            const voice = pickSafeVoice();
            if (voice) {
                u.voice = voice;
            }

            window.speechSynthesis.speak(u);
        },

        stopSpeaking() {
            if (window.speechSynthesis) {
                window.speechSynthesis.cancel();
            }
        },

        speakText(text) {
            if (!this.state.readAloud) return;
            this.speakNow(text, 500);
        },

        readElement(target) {
            let el = null;
            if (typeof target === 'string') {
                el = document.getElementById(target) || document.querySelector(target);
            } else if (target && target.nodeType === 1) {
                el = target;
            }
            if (!el) {
                announceChange('Could not find text to read');
                return;
            }
            const text = extractReadableText(el);
            if (!text) {
                announceChange('No text to read in this section');
                return;
            }
            this.speakNow(text);
        },

        readMainContent() {
            const main = document.querySelector(
                'main.main-content, .main-content, main[role="main"], main, .parent-container, .auth-card'
            );
            if (!main) {
                announceChange('No content found to read');
                return;
            }
            const text = extractReadableText(main);
            if (text) {
                this.speakNow(text);
            }
        },

        readVisibleSection() {
            const sections = document.querySelectorAll('.section');
            for (const section of sections) {
                const rect = section.getBoundingClientRect();
                if (rect.top <= window.innerHeight * 0.55 && rect.bottom >= window.innerHeight * 0.25) {
                    const text = extractReadableText(section);
                    if (text) {
                        this.speakNow(text);
                    }
                    return;
                }
            }
            if (sections.length) {
                const text = extractReadableText(sections[0]);
                if (text) {
                    this.speakNow(text);
                }
            } else {
                this.readMainContent();
            }
        },

        readPageAloud() {
            this.stopSpeaking();
            if (document.querySelector('.section')) {
                this.readVisibleSection();
            } else {
                this.readMainContent();
            }
        },
    };

    NeuroLearnA11y.applyAll();

    function wireReadAloudButton() {
        const btn = document.getElementById('readAloudBtn');
        if (!btn || btn.dataset.nlReadWired) return;
        btn.dataset.nlReadWired = '1';
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            NeuroLearnA11y.readPageAloud();
        });
    }

    window.toggleDyslexicFont = () => NeuroLearnA11y.toggleDyslexicFont();
    window.toggleHighContrast = () => NeuroLearnA11y.toggleHighContrast();
    window.adjustTextSize = (d) => NeuroLearnA11y.adjustTextSize(d);
    window.toggleReadAloud = () => NeuroLearnA11y.toggleReadAloud();
    window.readPageAloud = () => NeuroLearnA11y.readPageAloud();
    window.readSection = (sectionId) => NeuroLearnA11y.readElement(sectionId);
    window.speakText = (text) => NeuroLearnA11y.speakText(text);
    window.announceChange = announceChange;

    document.addEventListener('DOMContentLoaded', () => {
        wireReadAloudButton();
        if (window.speechSynthesis) {
            window.speechSynthesis.getVoices();
        }
    });

    if (window.speechSynthesis) {
        window.speechSynthesis.onvoiceschanged = () => {
            window.speechSynthesis.getVoices();
        };
    }
})();
