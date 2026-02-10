/* Gita Sarathi — API Module */

const GitaAPI = {
    BASE: '',

    async ask(query) {
        const res = await fetch(`${this.BASE}/ask?q=${encodeURIComponent(query)}`);
        // 429 (rate limit) and filtered responses return valid JSON
        if (res.status === 429 || res.ok) return res.json();
        throw new Error('Server error');
    },

    async getAmritShlokas() {
        const res = await fetch(`${this.BASE}/api/amrit`);
        if (!res.ok) throw new Error('Server error');
        return res.json();
    },

    async getTopics() {
        const res = await fetch(`${this.BASE}/api/topics`);
        if (!res.ok) throw new Error('Server error');
        return res.json();
    },

    async getJourney(position) {
        const res = await fetch(`${this.BASE}/api/journey?pos=${position}`);
        if (!res.ok) throw new Error('Server error');
        return res.json();
    },

    async getShloka(shlokaId) {
        const res = await fetch(`${this.BASE}/shloka/${shlokaId}`);
        if (!res.ok) throw new Error('Server error');
        return res.json();
    },
};
