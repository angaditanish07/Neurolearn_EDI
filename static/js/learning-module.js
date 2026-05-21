/**
 * Shared helpers for Interactive Learning modules.
 */
window.LearningModule = {
    close() {
        const video = document.getElementById('videoElement');
        const videoContainer = document.querySelector('.video-container');
        const feedbackContainer = document.querySelector('.feedback-container');
        const modulesGrid = document.querySelector('.modules-grid');
        const activeBar = document.getElementById('moduleActiveBar');

        if (video && video.srcObject) {
            video.srcObject.getTracks().forEach((t) => t.stop());
            video.srcObject = null;
        }
        if (videoContainer) {
            videoContainer.style.display = 'none';
        }
        if (feedbackContainer) {
            feedbackContainer.style.display = 'none';
        }

        const fingerFb = document.querySelector('.finger-count-feedback');
        if (fingerFb) {
            fingerFb.style.display = 'none';
        }

        const drawing = document.querySelector('.drawing-container');
        if (drawing) {
            drawing.style.display = 'none';
        }

        const gameContainer = document.getElementById('gameContainer');
        if (gameContainer) {
            gameContainer.style.display = 'none';
        }
        const gamesModal = document.getElementById('gamesModal');
        if (gamesModal) {
            gamesModal.style.display = 'none';
        }

        const faceLabels = document.querySelector('.organ-labels');
        if (faceLabels) {
            faceLabels.remove();
        }

        const questionContainer = document.querySelector('.question-container');
        if (questionContainer) {
            questionContainer.innerHTML = '';
        }
        const emotionFeedback = document.querySelector('.emotion-feedback');
        if (emotionFeedback) {
            emotionFeedback.textContent = '';
        }

        if (window.EmotionQuiz) {
            EmotionQuiz.reset();
        }

        if (typeof window.onLearningModuleClose === 'function') {
            window.onLearningModuleClose();
        }

        if (modulesGrid) {
            modulesGrid.style.display = 'grid';
        }
        if (activeBar) {
            activeBar.style.display = 'none';
        }
    },

    showActiveBar(label) {
        const modulesGrid = document.querySelector('.modules-grid');
        const activeBar = document.getElementById('moduleActiveBar');
        const title = document.getElementById('moduleActiveTitle');
        if (modulesGrid) {
            modulesGrid.style.display = 'none';
        }
        if (activeBar) {
            activeBar.style.display = 'flex';
        }
        if (title && label) {
            title.textContent = label;
        }
    },
};
