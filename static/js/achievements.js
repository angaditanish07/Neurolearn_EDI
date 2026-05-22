/**
 * Achievement unlock popup and rendering helpers.
 */
window.NeuroLearnAchievements = (function () {
    function ensureModal() {
        let modal = document.getElementById('achievementModal');
        if (modal) return modal;

        modal = document.createElement('div');
        modal.id = 'achievementModal';
        modal.className = 'achievement-modal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.hidden = true;
        modal.innerHTML = `
            <div class="achievement-modal-backdrop"></div>
            <div class="achievement-modal-card">
                <button type="button" class="achievement-modal-close" aria-label="Close">&times;</button>
                <div class="achievement-modal-icon" id="achievementModalIcon"></div>
                <h2 id="achievementModalTitle">Achievement unlocked!</h2>
                <p id="achievementModalDesc"></p>
                <button type="button" class="btn btn-purple" id="achievementModalOk">Awesome!</button>
            </div>`;
        document.body.appendChild(modal);

        const close = () => { modal.hidden = true; };
        modal.querySelector('.achievement-modal-backdrop').onclick = close;
        modal.querySelector('.achievement-modal-close').onclick = close;
        modal.querySelector('#achievementModalOk').onclick = close;
        return modal;
    }

    function showUnlock(achievement) {
        if (!achievement) return;
        const modal = ensureModal();
        document.getElementById('achievementModalIcon').textContent = achievement.icon || '🏆';
        document.getElementById('achievementModalTitle').textContent = achievement.title || 'Achievement unlocked!';
        document.getElementById('achievementModalDesc').textContent =
            achievement.description || 'You completed a new milestone.';
        modal.hidden = false;
        if (window.announceChange) {
            window.announceChange(`Achievement unlocked: ${achievement.title}`);
        }
    }

    function showQueue(achievements) {
        if (!achievements || !achievements.length) return;
        let i = 0;
        const next = () => {
            if (i >= achievements.length) return;
            showUnlock(achievements[i]);
            i += 1;
            const modal = document.getElementById('achievementModal');
            const btn = modal && modal.querySelector('#achievementModalOk');
            if (btn) {
                const handler = () => {
                    btn.removeEventListener('click', handler);
                    modal.hidden = true;
                    setTimeout(next, 400);
                };
                btn.addEventListener('click', handler);
            }
        };
        next();
    }

    function renderGrid(container, achievements) {
        if (!container) return;
        const unlocked = (achievements || []).filter((a) => a.unlocked);
        if (!unlocked.length) {
            container.innerHTML = '<p class="achievements-empty">Complete learning activities to earn achievements!</p>';
            return;
        }
        const recent = unlocked.slice(0, 6);
        container.innerHTML = recent.map((a) => `
            <div class="achievement" title="${a.description || ''}">
                <span class="achievement-icon">${a.icon || '🏆'}</span>
                <p>${a.title}</p>
            </div>`).join('');
    }

    return { showUnlock, showQueue, renderGrid };
})();
