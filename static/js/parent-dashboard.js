let selectedChildId = null;
let refreshTimer = null;

function formatRelativeTime(iso) {
    if (!iso) return 'Never';
    const d = new Date(iso);
    const diff = Date.now() - d.getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'Just now';
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    if (days < 7) return `${days}d ago`;
    return d.toLocaleDateString();
}

function riskClass(level) {
    if (level == null) return 'risk-medium';
    if (level <= 0) return 'risk-low';
    if (level === 1) return 'risk-medium';
    return 'risk-high';
}

function riskLabel(level) {
    if (level == null) return 'No data';
    const labels = ['Low concern', 'Moderate', 'Higher concern'];
    return labels[level] || 'Unknown';
}

async function init() {
    const me = await NeuroLearnAuth.me();
    if (!me.success || me.user.role !== 'parent') {
        window.location.href = '/login?next=/parent/dashboard';
        return;
    }
    document.getElementById('parentName').textContent =
        `Welcome, ${me.user.display_name} — live progress for linked learners`;

    document.getElementById('linkBtn').onclick = linkChild;
    document.getElementById('notifyBtn').onclick = notifyVideo;
    await loadChildren();

    refreshTimer = setInterval(() => {
        if (selectedChildId) selectChild(selectedChildId, true);
        else loadChildren(true);
    }, 30000);
}

async function linkChild() {
    document.getElementById('msg').textContent = '';
    document.getElementById('err').textContent = '';
    const code = document.getElementById('linkCode').value.trim();
    const res = await fetch('/api/parent/link-child', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ link_code: code }),
    });
    const data = await res.json();
    if (!data.success) {
        document.getElementById('err').textContent = data.error || 'Link failed';
        return;
    }
    document.getElementById('msg').textContent = data.message || 'Child linked!';
    document.getElementById('linkCode').value = '';
    await loadChildren();
}

async function loadChildren(silent) {
    const res = await fetch('/api/parent/children');
    const data = await res.json();
    const el = document.getElementById('childrenList');
    if (!data.success || !data.children.length) {
        el.innerHTML = '<p class="empty-state">No children linked yet. Enter a link code above.</p>';
        document.getElementById('detailPanel').hidden = true;
        return;
    }

    el.innerHTML = data.children.map((c) => {
        const s = c.summary || {};
        const pct = s.latest_screening?.overall_score != null
            ? Math.round(s.latest_screening.overall_score * 100)
            : null;
        const pathPct = s.path_progress?.interactive || 0;
        return `<div class="child-card" data-id="${c.id}">
            <strong>${c.display_name}</strong>
            <p style="margin:0.25rem 0;color:#64748b;">@${c.username}</p>
            <p>🔥 Streak: <strong>${s.streak || 0}</strong> days</p>
            <p>Screening: <strong>${pct != null ? pct + '%' : '—'}</strong></p>
            <p>Last active: ${formatRelativeTime(s.last_active)}</p>
            <div class="mini-bar"><div class="mini-bar-fill" style="width:${pathPct}%"></div></div>
        </div>`;
    }).join('');

    el.querySelectorAll('.child-card').forEach((card) => {
        card.onclick = () => selectChild(parseInt(card.dataset.id, 10));
    });

    if (!silent && data.children.length === 1) {
        selectChild(data.children[0].id);
    } else if (selectedChildId) {
        const still = data.children.find((c) => c.id === selectedChildId);
        if (still) selectChild(selectedChildId, true);
    }
}

async function selectChild(childId, silent) {
    selectedChildId = childId;
    document.querySelectorAll('.child-card').forEach((c) => {
        c.classList.toggle('active', parseInt(c.dataset.id, 10) === childId);
    });

    const res = await fetch(`/api/parent/child/${childId}/summary`);
    const data = await res.json();
    if (!data.success) return;

    document.getElementById('detailPanel').hidden = false;
    document.getElementById('detailTitle').textContent =
        `${data.child.display_name}'s live progress`;

    const summary = data.summary || {};
    const activity = data.activity || {};
    const paths = summary.path_progress || {};

    renderStats(summary, activity);
    renderPathProgress(paths);
    renderScreeningChart(data.history || []);
    renderComponentScores(summary);
    renderActivityBreakdown(activity.breakdown || {});
    renderTimeline(activity.timeline || []);
    renderRecommendations(summary);
}

function renderStats(summary, activity) {
    const latest = summary.latest_screening;
    const scorePct = latest?.overall_score != null
        ? Math.round(latest.overall_score * 100)
        : '—';

    document.getElementById('statsRow').innerHTML = `
        <div class="stat-pill"><div class="stat-value">${summary.streak || 0}</div><div class="stat-label">Day streak</div></div>
        <div class="stat-pill"><div class="stat-value">${activity.events_this_week || 0}</div><div class="stat-label">Activities this week</div></div>
        <div class="stat-pill"><div class="stat-value">${summary.lessons_completed || 0}</div><div class="stat-label">Lessons done</div></div>
        <div class="stat-pill"><div class="stat-value">${scorePct}${scorePct !== '—' ? '%' : ''}</div><div class="stat-label">Latest screening</div></div>
        <div class="stat-pill"><div class="stat-value" style="font-size:1rem;">${formatRelativeTime(activity.last_active)}</div><div class="stat-label">Last active</div></div>
    `;
}

function renderPathProgress(paths) {
    const interactive = paths.interactive?.percent ?? paths.interactive ?? 0;
    const dyslexia = paths.dyslexia?.percent ?? paths.dyslexia ?? 0;
    const games = paths.games?.percent ?? paths.games ?? 0;

    const extra = (p) => {
        if (typeof p === 'object' && p !== null) {
            const parts = [];
            if (p.emotion_sessions) parts.push(`${p.emotion_sessions} emotion`);
            if (p.finger_sessions) parts.push(`${p.finger_sessions} fingers`);
            if (p.screenings_done) parts.push(`${p.screenings_done} screening(s)`);
            if (p.sessions) parts.push(`${p.sessions} sessions`);
            return parts.length ? `<small style="color:#64748b">${parts.join(' · ')}</small>` : '';
        }
        return '';
    };

    document.getElementById('pathProgress').innerHTML = `
        <div class="path-card-dash">
            <h4>Interactive learning</h4>
            <div class="bar-track"><div class="bar-fill interactive" style="width:0%" data-w="${interactive}"></div></div>
            <p><strong>${interactive}%</strong> ${extra(paths.interactive)}</p>
        </div>
        <div class="path-card-dash">
            <h4>Dyslexia screening</h4>
            <div class="bar-track"><div class="bar-fill dyslexia" style="width:0%" data-w="${dyslexia}"></div></div>
            <p><strong>${dyslexia}%</strong> ${extra(paths.dyslexia)}</p>
        </div>
        <div class="path-card-dash">
            <h4>Games & practice</h4>
            <div class="bar-track"><div class="bar-fill games" style="width:0%" data-w="${games}"></div></div>
            <p><strong>${games}%</strong> ${extra(paths.games)}</p>
        </div>
    `;

    requestAnimationFrame(() => {
        document.querySelectorAll('#pathProgress .bar-fill').forEach((bar) => {
            bar.style.width = `${bar.dataset.w}%`;
        });
    });
}

function renderScreeningChart(history) {
    const el = document.getElementById('screeningChart');
    if (!history.length) {
        el.innerHTML = '<p class="empty-state">No screenings yet — encourage your child to complete the dyslexia screening.</p>';
        return;
    }

    const ordered = [...history].reverse().slice(-8);
    const max = Math.max(...ordered.map((h) => h.overall_score || 0), 0.01);

    el.innerHTML = ordered.map((h, i) => {
        const pct = Math.round((h.overall_score || 0) * 100);
        const hpx = Math.max(8, Math.round(((h.overall_score || 0) / max) * 100));
        const label = h.created_at
            ? new Date(h.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
            : `#${i + 1}`;
        return `<div class="chart-bar-wrap" title="${pct}%">
            <div class="chart-bar" style="height:${hpx}px"></div>
            <span>${label}</span>
            <span><strong>${pct}%</strong></span>
        </div>`;
    }).join('');
}

function renderComponentScores(summary) {
    const cs = summary.component_scores ||
        summary.latest_screening?.component_scores || {};
    const risk = summary.latest_screening?.risk_level;
    const el = document.getElementById('detailScores');

    if (!Object.keys(cs).length) {
        el.innerHTML = '<p class="empty-state">No skill scores yet — complete a screening first.</p>';
        return;
    }

    let html = `<p>Risk level: <span class="risk-badge ${riskClass(risk)}">${riskLabel(risk)}</span></p>`;
    html += Object.entries(cs).map(([k, v]) => {
        const pct = Math.round((v || 0) * 100);
        return `<div style="margin-top:0.75rem;">
            <strong style="text-transform:capitalize;">${k.replace(/_/g, ' ')}</strong> ${pct}%
            <div class="score-bar"><div class="score-fill" style="width:0%" data-w="${pct}"></div></div>
        </div>`;
    }).join('');

    el.innerHTML = html;
    requestAnimationFrame(() => {
        el.querySelectorAll('.score-fill').forEach((bar) => {
            bar.style.width = `${bar.dataset.w}%`;
        });
    });
}

function renderActivityBreakdown(breakdown) {
    const el = document.getElementById('activityBreakdown');
    const entries = Object.entries(breakdown);
    if (!entries.length) {
        el.innerHTML = '<p class="empty-state">No activity recorded yet.</p>';
        return;
    }

    const max = Math.max(...entries.map(([, c]) => c), 1);
    const labels = {
        dyslexia_screening: 'Dyslexia screening',
        interactive_emotion: 'Emotion learning',
        interactive_fingers: 'Finger counting',
        module_visit: 'Module visits',
        feedback: 'Feedback',
    };

    el.innerHTML = entries
        .sort((a, b) => b[1] - a[1])
        .map(([type, count]) => {
            const pct = Math.round((count / max) * 100);
            return `<div class="activity-row">
                <span>${labels[type] || type}</span>
                <div class="act-bar"><div class="act-fill" style="width:0%" data-w="${pct}"></div></div>
                <strong>${count}</strong>
            </div>`;
        }).join('');

    requestAnimationFrame(() => {
        el.querySelectorAll('.act-fill').forEach((bar) => {
            bar.style.width = `${bar.dataset.w}%`;
        });
    });
}

function renderTimeline(timeline) {
    const el = document.getElementById('activityTimeline');
    if (!timeline.length) {
        el.innerHTML = '<p class="empty-state">Activity will appear here as your child uses NeuroLearn.</p>';
        return;
    }

    el.innerHTML = timeline.map((item) => {
        const when = item.at ? new Date(item.at).toLocaleString() : '';
        let detail = '';
        if (item.payload?.emotion) detail = ` — ${item.payload.emotion}`;
        if (item.payload?.total_fingers != null) detail = ` — ${item.payload.total_fingers} fingers`;
        if (item.payload?.overall_score != null) {
            detail = ` — score ${Math.round(item.payload.overall_score * 100)}%`;
        }
        return `<div class="timeline-item">
            <strong>${item.label || item.type}</strong>${detail}
            <time>${when}</time>
        </div>`;
    }).join('');
}

function renderRecommendations(summary) {
    const recs = summary.recommendations ||
        summary.latest_screening?.recommendations || [];
    document.getElementById('detailRecs').innerHTML = recs.length
        ? recs.map((r) => `<li>${r}</li>`).join('')
        : '<li>Complete a dyslexia screening to get personalized suggestions.</li>';
}

async function notifyVideo() {
    if (!selectedChildId) return;
    const res = await fetch('/notify_parent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'video_call_request', child_id: selectedChildId }),
    });
    const data = await res.json();
    alert(data.success ? 'Video check-in request sent.' : (data.error || 'Failed'));
}

document.addEventListener('DOMContentLoaded', init);
