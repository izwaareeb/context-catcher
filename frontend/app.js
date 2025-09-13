// Context Catcher Frontend Application
class ContextCatcher {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.isRecording = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSystemStatus();
        this.startPeriodicUpdates();
    }

    bindEvents() {
        // Main action buttons
        document.getElementById('yesterdayBtn').addEventListener('click', () => this.handleYesterday());
        document.getElementById('todayBtn').addEventListener('click', () => this.handleToday());
        document.getElementById('commandBtn').addEventListener('click', () => this.openCommandModal());

        // Modal events
        document.getElementById('closeModal').addEventListener('click', () => this.closeCommandModal());
        document.getElementById('cancelBtn').addEventListener('click', () => this.closeCommandModal());
        document.getElementById('executeBtn').addEventListener('click', () => this.executeCommand());
        document.getElementById('voiceBtn').addEventListener('click', () => this.toggleVoiceRecording());

        // Response close
        document.getElementById('closeResponse').addEventListener('click', () => this.closeResponse());

        // Example command clicks
        document.querySelectorAll('.example-cmd').forEach(cmd => {
            cmd.addEventListener('click', (e) => {
                document.getElementById('commandInput').value = e.target.textContent.replace(/"/g, '');
            });
        });

        // Enter key in command input
        document.getElementById('commandInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.executeCommand();
            }
        });

        // Close modal on outside click
        document.getElementById('commandModal').addEventListener('click', (e) => {
            if (e.target.id === 'commandModal') {
                this.closeCommandModal();
            }
        });
    }

    async handleYesterday() {
        this.showLoading();
        try {
            const response = await this.makeRequest('/briefing/yesterday');
            this.showResponse('Yesterday\'s Recap', response.text);
        } catch (error) {
            this.showError('Failed to get yesterday\'s recap');
        } finally {
            this.hideLoading();
        }
    }

    async handleToday() {
        this.showLoading();
        try {
            const response = await this.makeRequest('/briefing/today');
            this.showResponse('Today\'s Plan', response.text);
        } catch (error) {
            this.showError('Failed to get today\'s plan');
        } finally {
            this.hideLoading();
        }
    }

    openCommandModal() {
        document.getElementById('commandModal').style.display = 'block';
        document.getElementById('commandInput').focus();
    }

    closeCommandModal() {
        document.getElementById('commandModal').style.display = 'none';
        document.getElementById('commandInput').value = '';
        this.stopVoiceRecording();
    }

    async executeCommand() {
        const command = document.getElementById('commandInput').value.trim();
        if (!command) return;

        this.showLoading();
        try {
            const response = await this.makeRequest('/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command: command })
            });
            
            this.closeCommandModal();
            this.showResponse('Command Result', response.result);
        } catch (error) {
            this.showError('Failed to execute command');
        } finally {
            this.hideLoading();
        }
    }

    toggleVoiceRecording() {
        if (this.isRecording) {
            this.stopVoiceRecording();
        } else {
            this.startVoiceRecording();
        }
    }

    startVoiceRecording() {
        this.isRecording = true;
        const voiceBtn = document.getElementById('voiceBtn');
        voiceBtn.classList.add('recording');
        voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
        
        // Simulate voice recording (in real implementation, use Web Speech API)
        setTimeout(() => {
            this.stopVoiceRecording();
            // Simulate voice input
            document.getElementById('commandInput').value = 'Open Gmail';
        }, 2000);
    }

    stopVoiceRecording() {
        this.isRecording = false;
        const voiceBtn = document.getElementById('voiceBtn');
        voiceBtn.classList.remove('recording');
        voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
    }

    showResponse(title, content) {
        const responseContainer = document.getElementById('responseContainer');
        const responseContent = document.getElementById('responseContent');
        
        responseContent.innerHTML = `
            <div class="response-title">${title}</div>
            <div class="response-text">${content}</div>
        `;
        
        responseContainer.style.display = 'block';
        responseContainer.scrollIntoView({ behavior: 'smooth' });
    }

    showError(message) {
        this.showResponse('Error', `<div style="color: #ff4757;">${message}</div>`);
    }

    closeResponse() {
        document.getElementById('responseContainer').style.display = 'none';
    }

    showLoading() {
        document.getElementById('loadingOverlay').style.display = 'block';
    }

    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }

    async makeRequest(endpoint, options = {}) {
        const url = `${this.apiBaseUrl}${endpoint}`;
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const response = await fetch(url, { ...defaultOptions, ...options });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }

    async loadSystemStatus() {
        try {
            const status = await this.makeRequest('/status');
            this.updateStats(status);
        } catch (error) {
            console.error('Failed to load system status:', error);
        }
    }

    updateStats(status) {
        // Update quick stats (mock data for demo)
        document.getElementById('emailCount').textContent = Math.floor(Math.random() * 10) + 1;
        document.getElementById('slackCount').textContent = Math.floor(Math.random() * 20) + 5;
        document.getElementById('taskCount').textContent = Math.floor(Math.random() * 8) + 2;
        document.getElementById('meetingCount').textContent = Math.floor(Math.random() * 5) + 1;
    }

    startPeriodicUpdates() {
        // Update stats every 30 seconds
        setInterval(() => {
            this.loadSystemStatus();
        }, 30000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ContextCatcher();
});

// Add some demo functionality
document.addEventListener('DOMContentLoaded', () => {
    // Simulate real-time updates
    setInterval(() => {
        const stats = document.querySelectorAll('.stat-number');
        stats.forEach(stat => {
            const currentValue = parseInt(stat.textContent);
            const change = Math.floor(Math.random() * 3) - 1; // -1, 0, or 1
            const newValue = Math.max(0, currentValue + change);
            stat.textContent = newValue;
        });
    }, 10000);
});