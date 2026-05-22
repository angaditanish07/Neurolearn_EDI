/** Home page: load user progress, achievements, and wire UI */
async function loadUserProgress() {
    try {
        const res = await fetch('/api/progress/summary');
        const data = await res.json();
        if (!data.success) return;

        if (data.role === 'parent') {
            window.location.href = '/parent/dashboard';
            return;
        }

        const s = data.summary || {};
        const cards = document.querySelectorAll('.progress-section .stat-card .stat-number');
        if (cards[0]) cards[0].textContent = `${s.streak || 0} Days`;
        if (cards[1]) cards[1].textContent = `${s.lessons_completed || 0}`;
        if (cards[2]) cards[2].textContent = `${s.skills_mastered || 0}`;

        const pp = s.path_progress || {};
        document.querySelectorAll('.paths-section .progress[data-path]').forEach((bar) => {
            const key = bar.getAttribute('data-path');
            if (key && pp[key] != null) bar.style.width = `${pp[key]}%`;
        });

        const screeningCard = document.getElementById('screeningPathDesc');
        if (screeningCard && (s.screening_count || 0) > 0) {
            const pct = pp.dyslexia || 0;
            const latest = s.latest_screening;
            const scoreTxt = latest && latest.overall_score != null
                ? ` Latest score: ${Math.round(latest.overall_score * 100)}%.`
                : '';
            screeningCard.textContent = `Screening completed (${s.screening_count}×). Progress ${pct}%.${scoreTxt}`;
        }

        if (window.NeuroLearnAchievements) {
            NeuroLearnAchievements.renderGrid(
                document.getElementById('achievementsGrid'),
                data.achievements || []
            );
            if (data.new_achievements && data.new_achievements.length) {
                NeuroLearnAchievements.showQueue(data.new_achievements);
            }
        }

        window.state = window.state || {};
        window.state.userProgress = {
            streak: s.streak,
            lessonsCompleted: s.lessons_completed,
            skillsMastered: s.skills_mastered,
            screeningCount: s.screening_count,
        };
    } catch (e) {
        console.warn('Progress load failed', e);
    }
}

async function loadNavUser() {
    const res = await fetch('/api/me');
    const data = await res.json();
    const nav = document.getElementById('authNav');
    if (!nav) return;
    if (data.success) {
        nav.innerHTML = `
            <span>Hi, ${data.user.display_name}</span>
            <a href="/profile">Profile</a>
            <a href="#" id="navLogout">Logout</a>`;
        document.getElementById('navLogout')?.addEventListener('click', (e) => {
            e.preventDefault();
            NeuroLearnAuth.logout();
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadUserProgress();
    loadNavUser();

    const pending = sessionStorage.getItem('nl_pending_achievements');
    if (pending && window.NeuroLearnAchievements) {
        try {
            const list = JSON.parse(pending);
            if (list.length) NeuroLearnAchievements.showQueue(list);
        } catch (e) { /* ignore */ }
        sessionStorage.removeItem('nl_pending_achievements');
    }
});
