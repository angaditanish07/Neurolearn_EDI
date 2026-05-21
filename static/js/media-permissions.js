/**
 * Camera/microphone require a secure context (HTTPS or localhost).
 * http://192.168.x.x will NOT work in Chrome/Edge.
 */
window.NeuroLearnMedia = {
    isSecureContext() {
        return window.isSecureContext === true;
    },

    localUrls(port) {
        const p = port || (location.port || '8080');
        return [
            `http://localhost:${p}${location.pathname}`,
            `https://localhost:${p}${location.pathname}`,
        ];
    },

    insecureReason() {
        if (this.isSecureContext()) return null;
        const host = location.hostname;
        if (host === 'localhost' || host === '127.0.0.1') {
            return null;
        }
        if (/^\d+\.\d+\.\d+\.\d+$/.test(host)) {
            return (
                'You opened NeuroLearn via a network IP over HTTP (' + location.origin + '). ' +
                'Browsers block camera and microphone on non-secure sites.'
            );
        }
        return 'This page is not served over HTTPS. Camera and microphone are blocked.';
    },

    async getUserMedia(constraints) {
        const reason = this.insecureReason();
        if (reason) {
            const err = new Error(reason);
            err.code = 'INSECURE_CONTEXT';
            throw err;
        }
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error('Camera/microphone API is not available in this browser.');
        }
        return navigator.mediaDevices.getUserMedia(constraints);
    },

    showBlockedUI(containerId) {
        const reason = this.insecureReason();
        if (!reason) return false;

        const el = document.getElementById(containerId || 'mediaSecurityBanner');
        if (!el) return true;

        const port = location.port || '8080';
        el.style.display = 'block';
        el.hidden = false;
        el.innerHTML = `
            <strong>Camera &amp; microphone blocked (site not secure)</strong>
            <p>${reason}</p>
            <p><strong>Fix on this PC:</strong> use one of these URLs instead:</p>
            <ul>
                <li><a href="http://localhost:${port}/interactive_learning">http://localhost:${port}/interactive_learning</a></li>
                <li>Or enable HTTPS: set <code>USE_HTTPS=1</code> in <code>.env</code> and restart the server, then open <code>https://${location.hostname}:${port}</code> (accept the security warning).</li>
            </ul>
        `;
        return true;
    },

    alertCameraError(err) {
        const reason = this.insecureReason();
        if (reason || (err && err.code === 'INSECURE_CONTEXT')) {
            const port = location.port || '8080';
            alert(
                'Camera/microphone need a secure connection.\n\n' +
                'On this computer, open:\n' +
                `  http://localhost:${port}/interactive_learning\n\n` +
                'Do NOT use http://192.168.x.x unless you enable USE_HTTPS=1 in .env and use https://...'
            );
            return;
        }
        alert(
            'Could not access camera/microphone.\n\n' +
            (err && err.message ? err.message : 'Check browser permissions for this site.')
        );
    },
};
