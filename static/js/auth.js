/* Gita Sarathi — Auth Module (Phone + OTP) */

const GitaAuth = {
    token: localStorage.getItem('gita_token') || null,

    isLoggedIn() { return !!this.token; },

    _headers() {
        const h = { 'Content-Type': 'application/json' };
        if (this.token) h['Authorization'] = 'Bearer ' + this.token;
        return h;
    },

    async sendOTP(phone) {
        const res = await fetch('/api/auth/send-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone }),
        });
        return res.json();
    },

    async verifyOTP(phone, otp) {
        const res = await fetch('/api/auth/verify-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, otp }),
        });
        const data = await res.json();
        if (data.success && data.token) {
            this.token = data.token;
            localStorage.setItem('gita_token', data.token);
            await this.syncJourney();
        }
        return data;
    },

    async syncJourney() {
        const pos = parseInt(localStorage.getItem('gita_journey_pos') || '0', 10);
        const streak = parseInt(localStorage.getItem('gita_journey_streak') || '0', 10);
        const lastDate = localStorage.getItem('gita_journey_last') || null;

        const res = await fetch('/api/auth/sync', {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify({
                journey_position: pos,
                journey_streak: streak,
                journey_last_date: lastDate,
            }),
        });
        const data = await res.json();
        if (data.success) {
            localStorage.setItem('gita_journey_pos', data.journey_position);
            localStorage.setItem('gita_journey_streak', data.journey_streak);
            if (data.journey_last_date) {
                localStorage.setItem('gita_journey_last', data.journey_last_date);
            }
        }
        return data;
    },

    async getMe() {
        try {
            const res = await fetch('/api/auth/me', { headers: this._headers() });
            const data = await res.json();
            if (!data.logged_in) {
                this.token = null;
                localStorage.removeItem('gita_token');
            }
            return data;
        } catch {
            return { logged_in: false };
        }
    },

    async logout() {
        try {
            await fetch('/api/auth/logout', {
                method: 'POST',
                headers: this._headers(),
            });
        } catch { /* ignore */ }
        this.token = null;
        localStorage.removeItem('gita_token');
    },

    // --- Login Modal UI ---

    showLoginModal() {
        const existing = document.getElementById('loginModal');
        if (existing) { existing.classList.remove('hidden'); return; }

        const modal = document.createElement('div');
        modal.id = 'loginModal';
        modal.className = 'login-modal';
        modal.innerHTML = `
            <div class="login-content">
                <button class="login-close" id="loginClose" aria-label="बंद करें">&times;</button>
                <div id="loginStep1">
                    <h3 class="login-title">लॉगिन करें</h3>
                    <p class="login-subtitle">अपनी यात्रा हर जगह सेव रखें</p>
                    <input type="tel" id="phoneInput" class="login-input" placeholder="मोबाइल नंबर" maxlength="10" inputmode="numeric" pattern="[0-9]*" autocomplete="tel">
                    <button id="sendOtpBtn" class="login-btn">OTP भेजें</button>
                    <div id="otpError" class="login-error hidden"></div>
                </div>
                <div id="loginStep2" class="hidden">
                    <h3 class="login-title">OTP डालें</h3>
                    <p class="login-subtitle" id="otpSentMsg"></p>
                    <input type="tel" id="otpInput" class="login-input" placeholder="4-अंक OTP" maxlength="6" inputmode="numeric" pattern="[0-9]*" autocomplete="one-time-code">
                    <button id="verifyOtpBtn" class="login-btn">पुष्टि करें</button>
                    <button id="resendOtpBtn" class="login-link hidden">OTP नहीं आया? फिर भेजें</button>
                    <div id="otpError2" class="login-error hidden"></div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        let currentPhone = '';

        // Close modal
        document.getElementById('loginClose').addEventListener('click', () => {
            modal.classList.add('hidden');
        });
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.add('hidden');
        });

        // Send OTP
        document.getElementById('sendOtpBtn').addEventListener('click', async () => {
            const phone = document.getElementById('phoneInput').value.trim();
            const errEl = document.getElementById('otpError');
            const btn = document.getElementById('sendOtpBtn');

            if (!phone || phone.length < 10) {
                errEl.textContent = '10 अंक का मोबाइल नंबर डालें';
                errEl.classList.remove('hidden');
                return;
            }

            btn.disabled = true;
            btn.textContent = 'भेज रहे हैं...';
            errEl.classList.add('hidden');

            const result = await GitaAuth.sendOTP(phone);
            if (result.success) {
                currentPhone = phone;
                document.getElementById('loginStep1').classList.add('hidden');
                document.getElementById('loginStep2').classList.remove('hidden');
                document.getElementById('otpSentMsg').textContent = `OTP भेजा गया ****${phone.slice(-4)} पर`;
                document.getElementById('otpInput').focus();

                // Show resend after 30s
                setTimeout(() => {
                    document.getElementById('resendOtpBtn').classList.remove('hidden');
                }, 30000);
            } else {
                errEl.textContent = result.error || 'कुछ गड़बड़ हुई';
                errEl.classList.remove('hidden');
            }
            btn.disabled = false;
            btn.textContent = 'OTP भेजें';
        });

        // Verify OTP
        document.getElementById('verifyOtpBtn').addEventListener('click', async () => {
            const otp = document.getElementById('otpInput').value.trim();
            const errEl = document.getElementById('otpError2');
            const btn = document.getElementById('verifyOtpBtn');

            if (!otp) {
                errEl.textContent = 'OTP डालें';
                errEl.classList.remove('hidden');
                return;
            }

            btn.disabled = true;
            btn.textContent = 'जांच रहे हैं...';
            errEl.classList.add('hidden');

            const result = await GitaAuth.verifyOTP(currentPhone, otp);
            if (result.success) {
                modal.classList.add('hidden');
                GitaAuth._updateUI(true);
                // Dispatch event so app.js can react
                window.dispatchEvent(new CustomEvent('gita-auth-change', { detail: { loggedIn: true } }));
            } else {
                errEl.textContent = result.error || 'गलत OTP';
                errEl.classList.remove('hidden');
            }
            btn.disabled = false;
            btn.textContent = 'पुष्टि करें';
        });

        // Resend OTP
        document.getElementById('resendOtpBtn').addEventListener('click', async () => {
            const btn = document.getElementById('resendOtpBtn');
            btn.classList.add('hidden');
            await GitaAuth.sendOTP(currentPhone);
            document.getElementById('otpSentMsg').textContent = `नया OTP भेजा गया ****${currentPhone.slice(-4)} पर`;
            setTimeout(() => btn.classList.remove('hidden'), 30000);
        });
    },

    _updateUI(loggedIn) {
        const profileBtn = document.getElementById('profileBtn');
        if (profileBtn) {
            profileBtn.textContent = loggedIn ? '👤' : 'लॉगिन';
            profileBtn.classList.toggle('logged-in', loggedIn);
        }
        // Also update journey login banner if visible
        const banner = document.getElementById('journeyLoginBanner');
        if (banner) banner.classList.toggle('hidden', loggedIn);
    },

    async init() {
        if (this.token) {
            const data = await this.getMe();
            this._updateUI(data.logged_in);
            if (data.logged_in) {
                await this.syncJourney();
            }
        }
    },
};
