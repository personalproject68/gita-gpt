/* GitaGPT — API Module */

const GitaAPI = {
    BASE: '',

    async ask(query) {
        const res = await fetch(`${this.BASE}/ask?q=${encodeURIComponent(query)}`);
        if (!res.ok) throw new Error('Server error');
        return res.json();
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
