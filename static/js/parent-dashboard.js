let selectedChildId = null;

async function init() {
    const me = await NeuroLearnAuth.me();
    if (!me.success || me.user.role !== 'parent') {
        window.location.href = '/login';
        return;
    }
    document.getElementById('parentName').textContent = ` — ${me.user.display_name}`;
    document.getElementById('linkBtn').onclick = linkChild;
    document.getElementById('notifyBtn').onclick = notifyVideo;
    await loadChildren();
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

async function loadChildren() {
    const res = await fetch('/api/parent/children');
    const data = await res.json();
    const el = document.getElementById('childrenList');
    if (!data.success || !data.children.length) {
        el.innerHTML = '<p>No children linked yet. Enter a link code above.</p>';
        document.getElementById('detailPanel').hidden = true;
        return;
    }
    el.innerHTML = data.children.map((c) => {
        const score = c.summary?.latest_screening?.overall_score;
        const pct = score != null ? Math.round(score * 100) : '—';
        return `<div class="child-card" data-id="${c.id}">
            <strong>${c.display_name}</strong>
            <p>@${c.username}</p>
            <p>Latest score: ${pct}%</p>
            <p>Streak: ${c.summary?.streak || 0} days</p>
        </div>`;
    }).join('');
    el.querySelectorAll('.child-card').forEach((card) => {
        card.onclick = () => selectChild(parseInt(card.dataset.id, 10));
    });
    if (data.children.length === 1) {
        selectChild(data.children[0].id);
    }
}

async function selectChild(childId) {
    selectedChildId = childId;
    document.querySelectorAll('.child-card').forEach((c) => {
        c.classList.toggle('active', parseInt(c.dataset.id, 10) === childId);
    });
    const res = await fetch(`/api/parent/child/${childId}/summary`);
    const data = await res.json();
    if (!data.success) return;

    document.getElementById('detailPanel').hidden = false;
    document.getElementById('detailTitle').textContent =
        `${data.child.display_name}'s progress`;

    const cs = data.summary?.component_scores ||
        data.summary?.latest_screening?.component_scores || {};
    const scoresEl = document.getElementById('detailScores');
    if (!Object.keys(cs).length) {
        scoresEl.innerHTML = '<p>No screening completed yet.</p>';
    } else {
        scoresEl.innerHTML = Object.entries(cs).map(([k, v]) => {
            const pct = Math.round((v || 0) * 100);
            return `<div><strong>${k.replace(/_/g, ' ')}</strong> ${pct}%
                <div class="score-bar"><div class="score-fill" style="width:${pct}%"></div></div></div>`;
        }).join('');
    }

    const recs = data.summary?.recommendations ||
        data.summary?.latest_screening?.recommendations || [];
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
