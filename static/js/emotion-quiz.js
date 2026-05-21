/**
 * Adaptive MCQ quiz for Emotion Detection & Learning.
 * - Sad → easier immediately (from hard)
 * - Neutral for 5+ seconds on hard → easier
 * - Happy + correct answer → harder question
 */
window.EmotionQuiz = (function () {
    const NEUTRAL_DOWNGRADE_MS = 5000;

    const EASY_MCQS = [
        { question: 'What is 2 + 1?', options: ['2', '3', '4', '5'], correct: 1 },
        { question: 'How many sides does a triangle have?', options: ['2', '3', '4', '5'], correct: 1 },
        { question: 'Which letter comes after B?', options: ['A', 'C', 'D', 'E'], correct: 1 },
        { question: 'What color is the sky on a sunny day?', options: ['Green', 'Blue', 'Red', 'Purple'], correct: 1 },
        { question: 'How many days are in one week?', options: ['5', '6', '7', '8'], correct: 2 },
        { question: 'Spell the word for our star: S _ N', options: ['Son', 'Sun', 'Sin', 'San'], correct: 1 },
    ];

    const HARD_MCQS = [
        { question: 'What is 12 × 3?', options: ['24', '30', '36', '42'], correct: 2 },
        { question: 'Which planet is known as the Red Planet?', options: ['Venus', 'Mars', 'Jupiter', 'Saturn'], correct: 1 },
        { question: 'What is 48 ÷ 6?', options: ['6', '7', '8', '9'], correct: 2 },
        { question: 'Which fraction equals one half?', options: ['1/4', '2/4', '3/4', '1/3'], correct: 1 },
        { question: 'What is the capital of France?', options: ['London', 'Berlin', 'Paris', 'Rome'], correct: 2 },
        { question: 'How many centimeters are in one meter?', options: ['10', '50', '100', '1000'], correct: 2 },
    ];

    const state = {
        difficulty: 'easy',
        solved: false,
        current: null,
        lastEmotion: 'Neutral',
        usedEasy: new Set(),
        usedHard: new Set(),
        neutralSince: null,
    };

    function pickFromBank(bank, usedSet) {
        if (usedSet.size >= bank.length) usedSet.clear();
        let idx;
        do {
            idx = Math.floor(Math.random() * bank.length);
        } while (usedSet.has(idx) && usedSet.size < bank.length);
        usedSet.add(idx);
        return { ...bank[idx], id: `${state.difficulty}-${idx}-${Date.now()}` };
    }

    function loadQuestion(difficulty) {
        state.difficulty = difficulty;
        state.solved = false;
        state.current = pickFromBank(
            difficulty === 'hard' ? HARD_MCQS : EASY_MCQS,
            difficulty === 'hard' ? state.usedHard : state.usedEasy
        );
        return state.current;
    }

    function reset() {
        state.difficulty = 'easy';
        state.solved = false;
        state.current = null;
        state.lastEmotion = 'Neutral';
        state.usedEasy.clear();
        state.usedHard.clear();
        state.neutralSince = null;
    }

    function isHappy(emotion) {
        return emotion === 'Happy';
    }

    function downgradeToEasy() {
        state.neutralSince = null;
        if (state.difficulty === 'hard') {
            loadQuestion('easy');
            return true;
        }
        return false;
    }

    function getNeutralCountdownSec() {
        if (state.difficulty !== 'hard' || state.neutralSince == null) return null;
        const left = NEUTRAL_DOWNGRADE_MS - (Date.now() - state.neutralSince);
        return left > 0 ? Math.ceil(left / 1000) : 0;
    }

    /** Called on each emotion poll from the camera. */
    function onEmotionDetected(emotion) {
        state.lastEmotion = emotion;

        if (!state.current) {
            loadQuestion('easy');
            return { changed: true, reason: 'init', emotion };
        }

        if (emotion === 'Sad') {
            state.neutralSince = null;
            if (downgradeToEasy()) {
                return { changed: true, reason: 'easier', emotion, trigger: 'sad' };
            }
            return { changed: false, reason: 'stay_easy', emotion };
        }

        if (emotion === 'Neutral') {
            if (state.difficulty !== 'hard') {
                state.neutralSince = null;
                return { changed: false, reason: 'unchanged', emotion };
            }

            const now = Date.now();
            if (state.neutralSince == null) {
                state.neutralSince = now;
            }

            const elapsed = now - state.neutralSince;
            if (elapsed >= NEUTRAL_DOWNGRADE_MS) {
                downgradeToEasy();
                return {
                    changed: true,
                    reason: 'easier',
                    emotion,
                    trigger: 'neutral_5s',
                };
            }

            return {
                changed: false,
                reason: 'neutral_waiting',
                emotion,
                neutralSecondsLeft: getNeutralCountdownSec(),
            };
        }

        state.neutralSince = null;
        return { changed: false, reason: 'unchanged', emotion };
    }

    function onAnswer(selectedIndex) {
        if (!state.current) {
            return { correct: false, message: 'No question loaded.' };
        }

        const correct = selectedIndex === state.current.correct;
        if (!correct) {
            return { correct: false, message: 'Not quite — try again!', upgrade: false };
        }

        state.solved = true;

        if (isHappy(state.lastEmotion)) {
            loadQuestion('hard');
            state.neutralSince = null;
            return {
                correct: true,
                message: 'Correct! You look happy — here is a harder question.',
                upgrade: true,
                difficulty: 'hard',
            };
        }

        loadQuestion(state.difficulty);
        return {
            correct: true,
            message: 'Correct! Stay happy to unlock harder questions.',
            upgrade: false,
            difficulty: state.difficulty,
        };
    }

    function getState() {
        return {
            difficulty: state.difficulty,
            solved: state.solved,
            current: state.current,
            lastEmotion: state.lastEmotion,
            neutralSecondsLeft: getNeutralCountdownSec(),
        };
    }

    return {
        NEUTRAL_DOWNGRADE_MS,
        reset,
        loadQuestion,
        onEmotionDetected,
        onAnswer,
        getState,
        isHappy,
        getNeutralCountdownSec,
    };
})();
