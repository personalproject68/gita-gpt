/* Gita Sarathi — Main App */

(function () {
    'use strict';

    // DOM refs
    const splash = document.getElementById('splash');
    const app = document.getElementById('app');
    const micBtn = document.getElementById('micBtn');
    const micStatus = document.getElementById('micStatus');
    const queryForm = document.getElementById('queryForm');
    const queryInput = document.getElementById('queryInput');
    const resultArea = document.getElementById('resultArea');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const shlokaResult = document.getElementById('shlokaResult');
    const amritList = document.getElementById('amritList');
    const journeyShloka = document.getElementById('journeyShloka');
    const navBtns = document.querySelectorAll('.nav-btn');

    const screens = {
        home: document.getElementById('homeScreen'),
        amrit: document.getElementById('amritScreen'),
        journey: document.getElementById('journeyScreen'),
    };

    // State
    let currentScreen = 'home';
    let amritData = null;
    let journeyLoaded = false;

    // === Splash (brief — don't make users wait) ===
    setTimeout(() => {
        splash.style.display = 'none';
        app.classList.remove('hidden');
        app.classList.add('visible');
    }, 800);

    // === Auto-hide header on scroll down, show on scroll up ===
    const header = document.querySelector('.header');
    let lastScrollY = 0;
    window.addEventListener('scroll', () => {
        const y = window.scrollY;
        if (y > 40) {
            header.classList.add('compact');
            header.classList.toggle('header-hidden', y > lastScrollY && y > 100);
        } else {
            header.classList.remove('compact', 'header-hidden');
        }
        lastScrollY = y;
    }, { passive: true });

    // === Navigation ===
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.screen;
            switchScreen(target);
        });
    });

    function switchScreen(name) {
        if (name === currentScreen) return;
        Object.values(screens).forEach(s => s.classList.add('hidden'));
        screens[name].classList.remove('hidden');
        screens[name].classList.add('active');
        navBtns.forEach(b => b.classList.toggle('active', b.dataset.screen === name));
        currentScreen = name;

        if (name === 'amrit' && !amritData) loadAmrit();
        if (name === 'journey' && !journeyLoaded) loadJourney();
    }

    // === Voice ===
    const voiceSupported = GitaVoice.init(
        (transcript) => {
            queryInput.value = transcript;
            handleQuery(transcript);
        },
        (status, data) => {
            switch (status) {
                case 'listening':
                    micBtn.classList.add('listening');
                    micStatus.textContent = 'सुन रहे हैं...';
                    break;
                case 'interim':
                    micStatus.textContent = data;
                    break;
                case 'stopped':
                    micBtn.classList.remove('listening');
                    micStatus.textContent = '';
                    break;
                case 'no-speech':
                    micBtn.classList.remove('listening');
                    micStatus.textContent = 'कुछ सुनाई नहीं दिया, फिर बोलें';
                    setTimeout(() => { micStatus.textContent = ''; }, 3000);
                    break;
                case 'not-allowed':
                    micBtn.classList.remove('listening');
                    micStatus.textContent = 'माइक की अनुमति दें';
                    break;
                case 'voice-unsupported':
                    micBtn.style.opacity = '0.5';
                    micStatus.textContent = 'इस ब्राउज़र में voice उपलब्ध नहीं';
                    break;
                case 'error':
                    micBtn.classList.remove('listening');
                    micStatus.textContent = 'कुछ गड़बड़ हुई, फिर कोशिश करें';
                    setTimeout(() => { micStatus.textContent = ''; }, 3000);
                    break;
            }
        }
    );

    micBtn.addEventListener('click', () => {
        if (voiceSupported) GitaVoice.toggle();
    });

    // === Text Query ===
    queryForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const q = queryInput.value.trim();
        if (q) handleQuery(q);
    });

    async function handleQuery(query) {
        showLoading();

        try {
            const data = await GitaAPI.ask(query);
            if (data.rate_limited) {
                showError(data.error);
                hideLoading();
                return;
            }
            if (data.filtered) {
                showError(data.message || 'कृपया अलग शब्दों में पूछें।');
                hideLoading();
                return;
            }
            showShloka(data);
        } catch (err) {
            showError('सर्वर से जुड़ नहीं पाए। कृपया फिर कोशिश करें।');
            hideLoading();
        }
    }

    function showLoading() {
        resultArea.classList.remove('hidden');
        loadingIndicator.classList.remove('hidden');
        shlokaResult.classList.add('hidden');
    }

    function hideLoading() {
        loadingIndicator.classList.add('hidden');
    }

    function showShloka(data) {
        hideLoading();
        if (!data.shlokas || data.shlokas.length === 0) {
            shlokaResult.innerHTML = `
                <div class="shloka-card">
                    <p class="shloka-meaning">कोई उपयुक्त श्लोक नहीं मिला। कृपया अलग शब्दों में पूछें।</p>
                </div>`;
            shlokaResult.classList.remove('hidden');
            return;
        }

        const s = data.shlokas[0];
        const parsed = formatInterpretation(data.interpretation || '');

        // Build share text
        const shareText = `📿 गीता ${s.shloka_id}\n\n${s.sanskrit}\n\n${s.hindi_meaning}\n\n— गीता सारथी 🙏\nhttps://www.gitasarathi.in`;
        const whatsappUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(shareText)}`;

        // Check if there are more shlokas to show
        const hasMore = data.shlokas && data.shlokas.length > 1;

        shlokaResult.innerHTML = `
            <div class="shloka-card">
                <div class="shloka-ref">गीता ${s.shloka_id}</div>
                <div class="shloka-sanskrit">${escapeHtml(s.sanskrit)}</div>
                <div class="shloka-meaning">${escapeHtml(s.hindi_meaning)}</div>
                <div class="shloka-interpretation">${renderInterpretation(parsed)}</div>
                <div class="shloka-footer">— गीता सारथी</div>
            </div>
            <div class="result-actions">
                <a href="${whatsappUrl}" target="_blank" rel="noopener" class="share-btn">भेजें ↗</a>
                ${hasMore ? '<button class="more-btn" id="showMoreBtn">और बताएं</button>' : ''}
                <button class="ask-another-btn" onclick="resetHome()">नया प्रश्न</button>
            </div>`;
        shlokaResult.classList.remove('hidden');

        // "और बताएं" — show next shloka from results
        if (hasMore) {
            let moreIndex = 1;
            const moreBtn = document.getElementById('showMoreBtn');
            moreBtn.addEventListener('click', () => {
                if (moreIndex >= data.shlokas.length) {
                    moreBtn.textContent = 'और श्लोक उपलब्ध नहीं';
                    moreBtn.disabled = true;
                    return;
                }
                const nextS = data.shlokas[moreIndex];
                // Use pre-fetched interpretation if available (no extra API call)
                const moreCard = document.createElement('div');
                moreCard.className = 'shloka-card more-card';
                moreCard.innerHTML = `
                    <div class="shloka-ref">गीता ${nextS.shloka_id}</div>
                    <div class="shloka-sanskrit">${escapeHtml(nextS.sanskrit)}</div>
                    <div class="shloka-meaning">${escapeHtml(nextS.hindi_meaning)}</div>
                    <div class="shloka-footer">— गीता सारथी</div>`;
                // Insert before the actions row
                const actionsRow = shlokaResult.querySelector('.result-actions');
                shlokaResult.insertBefore(moreCard, actionsRow);
                moreCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
                moreIndex++;
                if (moreIndex >= data.shlokas.length) {
                    moreBtn.textContent = 'और श्लोक उपलब्ध नहीं';
                    moreBtn.disabled = true;
                }
            });
        }

        // Scroll to result
        shlokaResult.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function formatInterpretation(text) {
        if (!text) return { shabdarth: '', bhavarth: '', guidance: '' };
        const parts = text.split('[SECTION]');
        if (parts.length >= 3) {
            return {
                shabdarth: parts[0].trim(),
                bhavarth: parts[1].trim(),
                guidance: parts[2].trim(),
            };
        }
        if (parts.length === 2) {
            return { shabdarth: parts[0].trim(), bhavarth: parts[1].trim(), guidance: '' };
        }
        return { shabdarth: '', bhavarth: text.trim(), guidance: '' };
    }

    function renderInterpretation(parsed) {
        let html = '';
        if (parsed.shabdarth) {
            html += `<div class="shloka-shabdarth"><div class="shabdarth-label">शब्दार्थ</div>${formatShabdarth(parsed.shabdarth)}</div>`;
        }
        if (parsed.bhavarth) {
            html += `<div class="shloka-bhavarth"><div class="bhavarth-label">भावार्थ</div>${escapeHtml(parsed.bhavarth)}</div>`;
        }
        if (parsed.guidance) {
            html += `<div class="shloka-guidance">${escapeHtml(parsed.guidance)}</div>`;
        }
        return html;
    }

    function formatShabdarth(text) {
        // Format "word = meaning | word = meaning" into a nice list
        const pairs = text.split('|').map(p => p.trim()).filter(Boolean);
        if (pairs.length > 1) {
            return '<div class="shabdarth-grid">' +
                pairs.map(p => `<span class="shabdarth-pair">${escapeHtml(p)}</span>`).join('') +
                '</div>';
        }
        return escapeHtml(text);
    }

    // === Amrit Shlokas ===
    async function loadAmrit() {
        amritList.innerHTML = '<div class="loading"><div class="loading-glow"></div></div>';
        try {
            amritData = await GitaAPI.getAmritShlokas();
            renderAmritList();
        } catch (err) {
            amritList.innerHTML = '<p style="text-align:center;color:var(--cream-dim)">लोड नहीं हो पाया</p>';
        }
    }

    function renderAmritList() {
        amritList.innerHTML = amritData.shlokas.map((s, i) => `
            <div class="amrit-card" data-index="${i}">
                <div class="amrit-card-ref">गीता ${s.shloka_id}</div>
                <div class="amrit-card-text">${escapeHtml(s.label)}</div>
            </div>
        `).join('');

        amritList.querySelectorAll('.amrit-card').forEach(card => {
            card.addEventListener('click', () => {
                const idx = parseInt(card.dataset.index);
                showAmritShloka(amritData.shlokas[idx]);
            });
        });
    }

    function showAmritShloka(s) {
        const parsed = formatInterpretation(s.interpretation || '');
        amritList.innerHTML = `
            <div class="amrit-expanded">
                <button class="amrit-back-btn" id="amritBack">&larr; अमृत श्लोक</button>
                <div class="shloka-card">
                    <div class="shloka-ref">गीता ${s.shloka_id}</div>
                    <div class="shloka-sanskrit">${escapeHtml(s.sanskrit)}</div>
                    <div class="shloka-meaning">${escapeHtml(s.hindi_meaning)}</div>
                    <div class="shloka-interpretation">${renderInterpretation(parsed)}</div>
                    <div class="shloka-footer">— गीता सारथी</div>
                </div>
            </div>`;
        document.getElementById('amritBack').addEventListener('click', renderAmritList);
    }

    // === Gita Journey ===
    const JOURNEY_TITLES = [
        { min: 0, title: 'जिज्ञासु' },
        { min: 50, title: 'साधक' },
        { min: 150, title: 'अभ्यासी' },
        { min: 300, title: 'योगी' },
        { min: 500, title: 'स्थितप्रज्ञ' },
        { min: 700, title: 'तत्त्वदर्शी' },
    ];

    function getJourneyPosition() {
        return parseInt(localStorage.getItem('gita_journey_pos') || '0', 10);
    }

    function setJourneyPosition(pos) {
        localStorage.setItem('gita_journey_pos', String(pos));
    }

    function getStreak() {
        const last = localStorage.getItem('gita_journey_last');
        const streak = parseInt(localStorage.getItem('gita_journey_streak') || '0', 10);
        const today = new Date().toISOString().slice(0, 10);
        if (last === today) return streak;
        const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
        if (last === yesterday) return streak; // not yet updated today
        return 0; // streak broken
    }

    function updateStreak() {
        const last = localStorage.getItem('gita_journey_last');
        const streak = parseInt(localStorage.getItem('gita_journey_streak') || '0', 10);
        const today = new Date().toISOString().slice(0, 10);
        if (last === today) return; // already counted today
        const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
        const newStreak = (last === yesterday) ? streak + 1 : 1;
        localStorage.setItem('gita_journey_streak', String(newStreak));
        localStorage.setItem('gita_journey_last', today);
    }

    function getTitle(pos) {
        let title = JOURNEY_TITLES[0].title;
        for (const t of JOURNEY_TITLES) {
            if (pos >= t.min) title = t.title;
        }
        return title;
    }

    async function loadJourney() {
        journeyShloka.innerHTML = '<div class="loading"><div class="loading-glow"></div></div>';
        try {
            const pos = getJourneyPosition();
            const data = await GitaAPI.getJourney(pos);
            journeyLoaded = true;
            renderJourney(data);
        } catch (err) {
            journeyShloka.innerHTML = '<p style="text-align:center;color:var(--cream-dim)">लोड नहीं हो पाया</p>';
        }
    }

    function renderJourney(data) {
        const pos = data.position;
        const total = data.total_shlokas;
        const pct = Math.round((pos / total) * 100);
        const streak = getStreak();

        // Update stats
        document.getElementById('journeyPercent').textContent = pct + '%';
        document.getElementById('journeyStreak').textContent = streak;
        document.getElementById('journeyTitle').textContent = getTitle(pos);
        document.getElementById('journeyProgressText').textContent = `${pos} / ${total} श्लोक`;
        document.getElementById('journeyProgressFill').style.width = pct + '%';

        // Chapter map
        const mapEl = document.getElementById('chapterMap');
        mapEl.innerHTML = '<div class="chapter-map-title">१८ अध्याय</div><div class="chapter-lamps">' +
            data.chapter_map.map(ch => {
                const done = pos > ch.last_pos;
                const current = pos >= ch.first_pos && pos <= ch.last_pos;
                const cls = done ? 'lamp lit' : (current ? 'lamp current' : 'lamp');
                return `<div class="${cls}" title="अ. ${ch.chapter} — ${ch.name}">
                    <div class="lamp-flame">${done ? '🪔' : (current ? '🔥' : '·')}</div>
                    <div class="lamp-num">${ch.chapter}</div>
                </div>`;
            }).join('') + '</div>';

        // Current shloka
        const s = data.shloka;
        const parsed = formatInterpretation(s.interpretation || '');
        const chInfo = data.chapter;

        let html = `
            <div class="journey-chapter-badge">
                अध्याय ${chInfo.number} — ${chInfo.name}
                <span class="chapter-progress-mini">${chInfo.shloka_in_chapter}/${chInfo.chapter_total}</span>
            </div>
            <div class="shloka-card">
                <div class="shloka-ref">गीता ${s.shloka_id}</div>
                <div class="shloka-sanskrit">${escapeHtml(s.sanskrit)}</div>
                <div class="shloka-meaning">${escapeHtml(s.hindi_meaning)}</div>
                <div class="shloka-interpretation">${renderInterpretation(parsed)}</div>
                <div class="shloka-footer">— गीता सारथी</div>
            </div>`;

        if (data.chapter_complete) {
            html += `<div class="chapter-milestone">
                <div class="milestone-icon">🪔</div>
                <div class="milestone-text">अध्याय ${chInfo.number} — ${chInfo.name} पूर्ण!</div>
            </div>`;
        }

        if (!data.journey_complete) {
            html += `<button class="journey-next-btn" id="journeyNextBtn">अगला श्लोक →</button>`;
        } else {
            html += `<div class="chapter-milestone">
                <div class="milestone-icon">🏆</div>
                <div class="milestone-text">सम्पूर्ण गीता यात्रा पूर्ण! जय श्री कृष्ण!</div>
            </div>`;
        }

        journeyShloka.innerHTML = html;

        // Next button
        const nextBtn = document.getElementById('journeyNextBtn');
        if (nextBtn) {
            nextBtn.addEventListener('click', async () => {
                const newPos = pos + 1;
                setJourneyPosition(newPos);
                updateStreak();
                nextBtn.disabled = true;
                nextBtn.textContent = '...';
                try {
                    const newData = await GitaAPI.getJourney(newPos);
                    renderJourney(newData);
                    journeyShloka.scrollIntoView({ behavior: 'smooth', block: 'start' });
                } catch (err) {
                    nextBtn.disabled = false;
                    nextBtn.textContent = 'अगला श्लोक →';
                }
            });
        }
    }

    // === Utilities ===
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function escapeAttr(text) {
        return text.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    function showError(msg) {
        const toast = document.createElement('div');
        toast.className = 'error-toast';
        toast.textContent = msg;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    // Global reset function
    window.resetHome = function () {
        queryInput.value = '';
        resultArea.classList.add('hidden');
        shlokaResult.classList.add('hidden');
        queryInput.focus();
    };

    // === Add to Home Screen ===
    let deferredPrompt = null;

    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        showInstallBanner();
    });

    function showInstallBanner() {
        // Don't show if already dismissed this session
        if (sessionStorage.getItem('a2hs-dismissed')) return;

        const banner = document.createElement('div');
        banner.className = 'install-banner';
        banner.innerHTML = `
            <div class="install-text">
                <strong>गीता सारथी</strong> को Home Screen पर जोड़ें
            </div>
            <div class="install-actions">
                <button class="install-btn" id="installBtn">जोड़ें</button>
                <button class="install-dismiss" id="installDismiss">बाद में</button>
            </div>
        `;
        document.body.appendChild(banner);

        document.getElementById('installBtn').addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const result = await deferredPrompt.userChoice;
                deferredPrompt = null;
            }
            banner.remove();
        });

        document.getElementById('installDismiss').addEventListener('click', () => {
            sessionStorage.setItem('a2hs-dismissed', '1');
            banner.remove();
        });
    }

    // === Service Worker Registration ===
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js').catch(() => {});
    }
})();
