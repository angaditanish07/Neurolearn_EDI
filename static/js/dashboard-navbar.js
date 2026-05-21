/**
 * Dashboard navbar: auth links, active route, voice + read-aloud buttons.
 */
(function () {
    'use strict';

    function setActiveNavLink() {
        const path = window.location.pathname;
        const map = {
            '/': 'home',
            '/interactive_learning': 'interactive',
            '/dyslexia_screening': 'screening',
            '/help': 'help',
            '/parent/dashboard': 'parent',
            '/profile': 'profile',
            '/settings': 'settings',
            '/login': 'login',
            '/register': 'register',
        };
        let key = map[path];
        if (!key && path.startsWith('/parent')) key = 'parent';

        document.querySelectorAll('.nav-menu-links a[data-nav]').forEach((a) => {
            a.classList.toggle('active', a.getAttribute('data-nav') === key);
        });
    }

    async function loadNavUser() {
        const nav = document.getElementById('authNav');
        if (!nav) return;

        try {
            const res = await fetch('/api/me');
            const data = await res.json();
            const parentLink = document.getElementById('navParentLink');

            if (data.success) {
                const u = data.user;
                if (parentLink) {
                    parentLink.style.display = u.role === 'parent' ? '' : 'none';
                }
                nav.innerHTML = `
                    <span>Hi, ${u.display_name}</span>
                    <a href="/profile">Profile</a>
                    <a href="/settings">Settings</a>
                    <a href="#" id="navLogout">Logout</a>`;
                document.getElementById('navLogout')?.addEventListener('click', (e) => {
                    e.preventDefault();
                    if (window.NeuroLearnAuth) {
                        NeuroLearnAuth.logout();
                    } else {
                        fetch('/api/logout', { method: 'POST' }).then(() => {
                            window.location.href = '/login';
                        });
                    }
                });
            } else {
                if (parentLink) parentLink.style.display = 'none';
                nav.innerHTML = `
                    <a href="/login">Login</a>
                    <a href="/register">Register</a>`;
            }
        } catch (e) {
            console.warn('Nav user load failed', e);
        }
    }

    function wireVoiceButtons() {
        const voiceBtn = document.getElementById('voiceNavBtn');
        const readBtn = document.getElementById('readAloudBtn');

        if (voiceBtn && window.NeuroLearnVoiceNav) {
            voiceBtn.addEventListener('click', () => {
                const vn = window.NeuroLearnVoiceNav;
                if (vn.isListening) {
                    vn.stopListening();
                    voiceBtn.classList.remove('active');
                } else {
                    vn.startListening();
                    voiceBtn.classList.add('active');
                }
            });
        }

        if (readBtn) {
            readBtn.addEventListener('click', () => {
                if (window.NeuroLearnA11y) {
                    NeuroLearnA11y.readMainContent();
                }
            });
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        document.body.classList.add('has-dashboard-nav');
        setActiveNavLink();
        loadNavUser();
        wireVoiceButtons();
    });

    window.NeuroLearnNavbar = { loadNavUser, setActiveNavLink };
})();
