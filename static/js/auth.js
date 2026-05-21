/**
 * NeuroLearn auth helpers
 */
window.NeuroLearnAuth = {
    async me() {
        const res = await fetch('/api/me');
        return res.json();
    },
    async logout() {
        await fetch('/api/logout', { method: 'POST' });
        window.location.href = '/login';
    },
    async requireAuth(redirectToLogin = true) {
        const data = await this.me();
        if (!data.success && redirectToLogin) {
            const next = encodeURIComponent(window.location.pathname);
            window.location.href = `/login?next=${next}`;
            return null;
        }
        return data.success ? data.user : null;
    },
};
