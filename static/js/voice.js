/* Gita Sarathi — Voice Input (Web Speech API) */

const GitaVoice = {
    recognition: null,
    isListening: false,
    onResult: null,
    onStatus: null,

    init(onResult, onStatus) {
        this.onResult = onResult;
        this.onStatus = onStatus;

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            this.onStatus('voice-unsupported');
            return false;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.lang = 'hi-IN';
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.maxAlternatives = 1;

        this.recognition.onstart = () => {
            this.isListening = true;
            this.onStatus('listening');
        };

        this.recognition.onresult = (event) => {
            let transcript = '';
            let isFinal = false;
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    isFinal = true;
                }
            }
            if (isFinal && transcript.trim()) {
                this.onResult(transcript.trim());
            } else if (transcript.trim()) {
                this.onStatus('interim', transcript.trim());
            }
        };

        this.recognition.onerror = (event) => {
            this.isListening = false;
            if (event.error === 'no-speech') {
                this.onStatus('no-speech');
            } else if (event.error === 'not-allowed') {
                this.onStatus('not-allowed');
            } else {
                this.onStatus('error');
            }
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.onStatus('stopped');
        };

        return true;
    },

    toggle() {
        if (!this.recognition) return;
        if (this.isListening) {
            this.recognition.stop();
        } else {
            this.recognition.start();
        }
    },

    isSupported() {
        return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
    }
};
