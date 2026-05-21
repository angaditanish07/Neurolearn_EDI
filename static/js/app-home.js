/** Home page: load user progress and wire UI */
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
        const streakEl = document.querySelector('.progress-section .stat-card .stat-number');
        const cards = document.querySelectorAll('.progress-section .stat-card .stat-number');
        if (cards[0]) cards[0].textContent = `${s.streak || 0} Days`;
        if (cards[1]) cards[1].textContent = `${s.lessons_completed || 0}`;
        if (cards[2]) cards[2].textContent = `${s.skills_mastered || 0}`;

        const pp = s.path_progress || {};
        const pathBars = document.querySelectorAll('.paths-section .progress');
        if (pathBars[0]) pathBars[0].style.width = `${pp.interactive || 0}%`;
        if (pathBars[1]) pathBars[1].style.width = `${pp.dyslexia || 0}%`;
        if (pathBars[2]) pathBars[2].style.width = `${pp.games || 0}%`;

        window.state = window.state || {};
        window.state.userProgress = {
            streak: s.streak,
            lessonsCompleted: s.lessons_completed,
            skillsMastered: s.skills_mastered,
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
});
