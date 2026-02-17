/**
 * NeuroCognitive AI - Professional Edition
 * Robust State Management & Data Pipeline v3.5.1
 */

class ProfessionalAssessmentApp {
    constructor() {
        // State
        this.sessionId = localStorage.getItem('mmse_session_id');
        this.userProfile = JSON.parse(localStorage.getItem('mmse_user_profile') || 'null');
        this.totalQuestions = 0;
        this.currentIdx = 0;
        this.qStartTime = null;
        this.timerInterval = null;
        this.charts = {};

        // DOM Elements
        this.views = {
            home: document.getElementById('homeView'),
            login: document.getElementById('loginView'),
            assessment: document.getElementById('assessmentView'),
            results: document.getElementById('resultsView')
        };

        this.elements = {
            startBtn: document.getElementById('startBtn'),
            loginForm: document.getElementById('loginForm'),
            submitBtn: document.getElementById('submitBtn'),
            userInput: document.getElementById('userInput'),
            qText: document.getElementById('qText'),
            qDomain: document.getElementById('qDomain'),
            qTimer: document.getElementById('qTimer'),
            progressBar: document.getElementById('progressBar'),
            progressText: document.getElementById('progressText'),
            specialContent: document.getElementById('specialContent'),
            feedbackToast: document.getElementById('feedbackToast'),
            headerStatus: document.getElementById('headerStatus'),
            displayPatientName: document.getElementById('displayPatientName'),
            resPatientName: document.getElementById('resPatientName'),
            listenBtn: document.getElementById('listenBtn'),
            speakBtn: document.getElementById('speakBtn'),
            downloadReportBtn: document.getElementById('downloadReport')
        };

        this.init();
    }

    init() {
        console.log("Initializing App...");

        // Navigation
        if (this.elements.startBtn) {
            this.elements.startBtn.addEventListener('click', () => {
                console.log("Start clicked, switching to login");
                this.switchView('login');
            });
        }

        if (this.elements.loginForm) {
            this.elements.loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin();
            });
        }

        // Assessment Actions
        if (this.elements.submitBtn) {
            this.elements.submitBtn.addEventListener('click', () => this.submitAnswer());
        }

        if (this.elements.userInput) {
            this.elements.userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.submitAnswer();
            });
        }

        // Voice
        if (this.elements.listenBtn) {
            this.elements.listenBtn.addEventListener('click', () => this.speakText(this.elements.qText.innerText));
        }
        if (this.elements.speakBtn) {
            this.elements.speakBtn.addEventListener('click', () => this.listenToUser());
        }

        // Report
        if (this.elements.downloadReportBtn) {
            this.elements.downloadReportBtn.addEventListener('click', () => {
                if (this.sessionId) window.location.href = `/api/report/${this.sessionId}`;
            });
        }

        console.log("App Ready. SessionID:", this.sessionId);
    }

    async handleLogin() {
        const nameInput = document.getElementById('userName');
        const ageInput = document.getElementById('userAge');
        const emailInput = document.getElementById('userEmail');

        if (!nameInput || !ageInput || !emailInput) {
            this.showToast("Form elements missing.");
            return;
        }

        const profile = {
            name: nameInput.value,
            age: parseInt(ageInput.value),
            email: emailInput.value
        };

        try {
            this.updateStatus("Registering Patient...");
            this.showLoading(true);

            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(profile)
            });

            if (!response.ok) throw new Error("Login failed");

            const data = await response.json();

            this.sessionId = data.session_id;
            this.userProfile = profile;

            // Persist
            localStorage.setItem('mmse_session_id', this.sessionId);
            localStorage.setItem('mmse_user_profile', JSON.stringify(profile));

            if (this.elements.displayPatientName) {
                this.elements.displayPatientName.innerText = profile.name;
            }

            await this.startAssessment();
        } catch (error) {
            console.error("Login failed:", error);
            this.showToast("Connection Error: " + error.message);
        } finally {
            this.showLoading(false);
            this.resetStatus();
        }
    }

    async startAssessment() {
        try {
            const response = await fetch(`/api/start/${this.sessionId}`);
            if (!response.ok) throw new Error("Assessment start failed");

            const data = await response.json();

            this.totalQuestions = data.total_questions;
            this.renderQuestion(data.first_question, 0, this.totalQuestions);
            this.switchView('assessment');
            this.updateStatus("Assessment Active", true);
        } catch (error) {
            console.error("Failed to start:", error);
            this.showToast("Error starting assessment.");
        }
    }

    renderQuestion(question, idx, total) {
        if (!question) return;

        this.currentIdx = idx;
        this.qStartTime = Date.now();

        // Text
        if (this.elements.qText) {
            this.elements.qText.classList.remove('fade-in');
            void this.elements.qText.offsetWidth;
            this.elements.qText.classList.add('fade-in');
            this.elements.qText.innerText = question.text;
        }

        if (this.elements.qDomain) this.elements.qDomain.innerText = question.domain;
        if (this.elements.progressText) {
            this.elements.progressText.innerText = `Domain: ${question.domain} | ${idx + 1} of ${total}`;
        }
        if (this.elements.progressBar) {
            this.elements.progressBar.style.width = `${((idx + 1) / total) * 100}%`;
        }

        // Special Content
        if (this.elements.specialContent) {
            this.elements.specialContent.innerHTML = '';
            if (question.content && Array.isArray(question.content)) {
                question.content.forEach(word => {
                    const span = document.createElement('span');
                    span.className = 'mem-word fade-in';
                    span.innerText = word;
                    this.elements.specialContent.appendChild(span);
                });
            }
        }

        // Input
        if (this.elements.userInput && this.elements.submitBtn) {
            if (question.input_type === 'button') {
                this.elements.userInput.style.display = 'none';
                this.elements.submitBtn.innerText = question.button_text || "Confirm & Continue";
            } else {
                this.elements.userInput.style.display = 'block';
                this.elements.userInput.value = '';
                this.elements.submitBtn.innerHTML = 'Continue <span class="arrow">→</span>';
                this.elements.userInput.focus();
            }
        }

        this.startTimer();
    }

    async submitAnswer() {
        const userInput = (this.elements.userInput ? this.elements.userInput.value : "") || "CONFIRMED";
        const duration = (Date.now() - this.qStartTime) / 1000;

        try {
            this.showLoading(true);
            const response = await fetch('/api/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    question_id: 'auto',
                    user_input: userInput,
                    duration: duration
                })
            });

            if (!response.ok) throw new Error("Submission failed");
            const data = await response.json();

            this.showToast(`${data.status}: ${data.feedback}`);

            if (data.is_completed) {
                await this.completeAssessment();
            } else if (data.next_question) {
                this.renderQuestion(data.next_question, this.currentIdx + 1, this.totalQuestions);
            }
        } catch (error) {
            console.error("Submission failed:", error);
            this.showToast("System Error during submission.");
        } finally {
            this.showLoading(false);
        }
    }

    async completeAssessment() {
        this.stopTimer();
        this.updateStatus("Processing Diagnostics...");
        this.switchView('results');

        try {
            console.log("Fetching results for session:", this.sessionId);
            const response = await fetch(`/api/results/${this.sessionId}`);
            if (!response.ok) throw new Error("Results fetch failed");

            const data = await response.json();
            console.log("CRITICAL: Diagnostics Received:", data);
            this.renderResults(data);
            this.updateStatus("Clinical Review Ready", true);
        } catch (error) {
            console.error("Failed to fetch results:", error);
            this.showToast("Diagnostic analysis failed.");
            this.resetStatus();
        }
    }

    renderResults(data) {
        console.log("Rendering results dashboard");

        // 1. Defend Personalization
        if (this.elements.resPatientName) {
            this.elements.resPatientName.innerText = this.userProfile ? this.userProfile.name : "Anonymous Patient";
        }

        // 2. Score Visualization
        try {
            const totalScore = data.total_score || 0;
            const scorePct = Math.min(100, Math.max(0, (totalScore / 30) * 100));
            const scoreEl = document.getElementById('totalScore');
            const scorePath = document.getElementById('scorePath');

            if (scoreEl) scoreEl.innerText = totalScore.toFixed(1);
            if (scorePath) scorePath.style.strokeDasharray = `${scorePct}, 100`;
        } catch (e) { console.error("Score render error:", e); }

        // 3. AI Insights
        try {
            const pred = data.disease_prediction || {};
            const setVal = (id, val) => {
                const el = document.getElementById(id);
                if (el) el.innerText = val || "---";
            };

            setVal('diseaseType', pred.disease_type);
            setVal('severityStage', pred.severity);
            setVal('clinicalNote', pred.interpretation);
            setVal('confText', pred.confidence ? `${pred.confidence.toFixed(1)}%` : "---");

            const confBar = document.getElementById('confBarFill');
            if (confBar) confBar.style.width = `${pred.confidence || 0}%`;
        } catch (e) { console.error("Prediction render error:", e); }

        // 4. Behavioral Metrics
        try {
            const meta = data.typing_summary || {};
            const setVal = (id, val) => {
                const el = document.getElementById(id);
                if (el) el.innerText = val;
            };

            setVal('avgWpm', Math.round(meta.avg_speed_wpm || 0));
            setVal('errorRate', `${(meta.error_rate || 0).toFixed(1)}%`);
            setVal('consistency', `${Math.round(meta.consistency_score || 0)}%`);
        } catch (e) { console.error("Metrics render error:", e); }

        // 5. Response Analytics Log
        try {
            const log = document.getElementById('responseLog');
            if (log && data.responses) {
                log.innerHTML = data.responses.map(r => `
                    <div class="log-item fade-in">
                        <div class="log-top">
                            <h5>${r.question_text || "Question"}</h5>
                            <span class="log-badge badge-${(r.status || "Unknown").toLowerCase()}">${r.status || "---"}</span>
                        </div>
                        <div class="log-answer">"${r.user_answer || "No response"}"</div>
                        <div class="log-meta">
                            <strong>AI Feedback:</strong> ${r.feedback || "Processed"} | 
                            <strong>Time:</strong> ${(r.time_taken || 0).toFixed(1)}s
                        </div>
                    </div>
                `).join('');
            }
        } catch (e) { console.error("Log render error:", e); }

        // 6. Charts
        try {
            if (typeof Chart !== 'undefined') {
                this.renderCharts(data);
            } else {
                console.error("Chart.js not loaded");
            }
        } catch (e) { console.error("Chart render error:", e); }
    }

    renderCharts(data) {
        // Destroy old
        Object.values(this.charts).forEach(c => { if (c) c.destroy(); });

        // Radar
        try {
            const domainScores = {};
            (data.responses || []).forEach(r => {
                if (!domainScores[r.domain]) domainScores[r.domain] = { earned: 0, max: 0 };
                domainScores[r.domain].earned += (r.earned || 0);
                domainScores[r.domain].max += (r.max_points || 1);
            });

            const labels = Object.keys(domainScores);
            const values = labels.map(l => (domainScores[l].earned / domainScores[l].max) * 100);

            const ctxRadar = document.getElementById('radarChart');
            if (ctxRadar && labels.length > 0) {
                this.charts.radar = new Chart(ctxRadar, {
                    type: 'radar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Clinical Strength (%)',
                            data: values,
                            backgroundColor: 'rgba(13, 148, 136, 0.15)',
                            borderColor: '#0d9488',
                            borderWidth: 2,
                            pointBackgroundColor: '#0d9488'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            r: { min: 0, max: 100, ticks: { display: false } }
                        },
                        plugins: { legend: { display: false } }
                    }
                });
            }
        } catch (e) { console.error("Radar crash:", e); }

        // Line
        try {
            const speeds = (data.responses || []).map(r => (r.typing_metrics || {}).wpm || 0);
            const steps = speeds.map((_, i) => i + 1);

            const ctxLine = document.getElementById('typingChart');
            if (ctxLine && speeds.length > 0) {
                this.charts.line = new Chart(ctxLine, {
                    type: 'line',
                    data: {
                        labels: steps,
                        datasets: [{
                            label: 'Velocity',
                            data: speeds,
                            borderColor: '#d97706',
                            backgroundColor: 'rgba(217, 119, 6, 0.1)',
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: { x: { display: false }, y: { beginAtZero: true } }
                    }
                });
            }
        } catch (e) { console.error("Line crash:", e); }
    }

    // Tools
    switchView(viewName) {
        Object.keys(this.views).forEach(v => {
            if (this.views[v]) {
                this.views[v].classList.toggle('active', v === viewName);
            }
        });
        window.scrollTo(0, 0);
    }

    updateStatus(text, withDot = false) {
        if (!this.elements.headerStatus) return;
        const dot = withDot ? '<span class="status-dot"></span> ' : '';
        this.elements.headerStatus.innerHTML = dot + text;
    }

    resetStatus() {
        this.updateStatus("System Online", true);
    }

    startTimer() {
        this.stopTimer();
        let seconds = 0;
        this.timerInterval = setInterval(() => {
            seconds++;
            const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
            const secs = (seconds % 60).toString().padStart(2, '0');
            if (this.elements.qTimer) this.elements.qTimer.innerText = `${mins}:${secs}`;
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) clearInterval(this.timerInterval);
    }

    showToast(message) {
        if (!this.elements.feedbackToast) return;
        this.elements.feedbackToast.innerText = message;
        this.elements.feedbackToast.classList.add('active');
        setTimeout(() => this.elements.feedbackToast.classList.remove('active'), 5000);
    }

    showLoading(isLoading) {
        if (!this.elements.submitBtn) return;
        this.elements.submitBtn.disabled = isLoading;
        this.elements.submitBtn.style.opacity = isLoading ? '0.5' : '1';
    }

    speakText(text) {
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        const ut = new SpeechSynthesisUtterance(text);
        ut.rate = 0.95;
        window.speechSynthesis.speak(ut);
    }

    listenToUser() {
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRec) {
            this.showToast("Voice capture not available.");
            return;
        }
        const rec = new SpeechRec();
        if (this.elements.speakBtn) this.elements.speakBtn.innerText = "⏳";
        rec.onresult = (e) => {
            if (this.elements.userInput) this.elements.userInput.value = e.results[0][0].transcript;
            if (this.elements.speakBtn) this.elements.speakBtn.innerText = "🎤";
        };
        rec.onerror = () => { if (this.elements.speakBtn) this.elements.speakBtn.innerText = "🎤"; };
        rec.start();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new ProfessionalAssessmentApp();
});
