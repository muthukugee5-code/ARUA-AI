/**
 * ARUA AI - IBM Watson Integration
 * Chatbot widget, prompt analysis, and image classification UI
 */

var Watson = {
  chatOpen: false,
  chatSessionId: null,
  messages: [],

  /**
   * Analyze a prompt using Watson NLP
   */
  async analyzePrompt(prompt) {
    try {
      const result = await API.post('/watson/analyze', { prompt });
      return result;
    } catch (err) {
      console.error('Watson analyze error:', err);
      return null;
    }
  },

  /**
   * Enhance a prompt using Watson NLP
   */
  async enhancePrompt(prompt) {
    try {
      const result = await API.post('/watson/enhance', { prompt });
      return result;
    } catch (err) {
      console.error('Watson enhance error:', err);
      return null;
    }
  },

  /**
   * Classify an image using Watson Visual Recognition
   */
  async classifyImage(imageUrl) {
    try {
      const result = await API.post('/watson/classify', { image_url: imageUrl });
      return result;
    } catch (err) {
      console.error('Watson classify error:', err);
      return null;
    }
  },

  /**
   * Send a chat message to Watson Assistant
   */
  async chat(message) {
    try {
      const payload = { message };
      if (this.chatSessionId) payload.session_id = this.chatSessionId;
      const result = await API.post('/watson/chat', payload);
      if (result?.session_id) this.chatSessionId = result.session_id;
      return result;
    } catch (err) {
      console.error('Watson chat error:', err);
      return null;
    }
  },

  /**
   * Inline Watson Insights Panel HTML
   */
  renderInsightsPanel(analysis) {
    if (!analysis) return '';
    const styles = (analysis.detected_styles || []).map(s =>
      `<span class="badge badge-primary" style="font-size:0.7rem;text-transform:capitalize">${s}</span>`
    ).join(' ');
    const suggestions = (analysis.enhancement_suggestions || []).map(s =>
      `<li style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:4px">💡 ${s}</li>`
    ).join('');
    return `
      <div style="background:rgba(220,38,38,0.05);border:1px solid rgba(220,38,38,0.15);border-radius:12px;padding:16px;margin-top:12px">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
          <img src="assets/logo-icon.svg" style="width:20px;height:20px">
          <span style="font-weight:700;font-size:0.85rem">IBM Watson Insights</span>
          <span class="badge badge-primary" style="font-size:0.6rem;margin-left:auto">${analysis.complexity || 'N/A'}</span>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">${styles}</div>
        <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-bottom:8px">
          <div style="font-size:0.75rem;color:var(--text-muted)">📝 ${analysis.word_count || 0} words</div>
          <div style="font-size:0.75rem;color:var(--text-muted)">🎭 ${analysis.tone || 'Neutral'} tone</div>
          <div style="font-size:0.75rem;color:var(--text-muted)">🏷️ ${(analysis.keywords || []).slice(0,3).join(', ')}</div>
          <div style="font-size:0.75rem;color:var(--text-muted)">🧠 ${analysis.sentiment || 'neutral'}</div>
        </div>
        ${suggestions ? `<div style="border-top:1px solid rgba(220,38,38,0.1);padding-top:8px"><ul style="margin:0;padding-left:16px">${suggestions}</ul></div>` : ''}
        <div style="font-size:0.65rem;color:var(--text-muted);margin-top:8px;border-top:1px solid rgba(220,38,38,0.1);padding-top:6px">Powered by IBM Watson NLP</div>
      </div>
    `;
  },

  /**
   * Inline Watson Enhanced Prompt HTML
   */
  renderEnhancedPrompt(result) {
    if (!result?.success) return '';
    const original = result.original || '';
    const enhanced = result.enhanced || '';
    return `
      <div style="background:rgba(220,38,38,0.05);border:1px solid rgba(220,38,38,0.15);border-radius:12px;padding:16px;margin-top:12px">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
          <img src="assets/logo-icon.svg" style="width:20px;height:20px">
          <span style="font-weight:700;font-size:0.85rem">Watson Enhanced Prompt</span>
        </div>
        <div style="margin-bottom:8px">
          <div style="font-size:0.7rem;color:var(--text-muted);margin-bottom:4px">Original:</div>
          <div style="font-size:0.82rem;color:var(--text-secondary);padding:8px;background:var(--bg-card);border-radius:8px">${original}</div>
        </div>
        <div style="margin-bottom:8px">
          <div style="font-size:0.7rem;color:var(--text-muted);margin-bottom:4px">Enhanced:</div>
          <div style="font-size:0.82rem;color:var(--text-primary);padding:8px;background:rgba(220,38,38,0.08);border-radius:8px;font-weight:500">${enhanced}</div>
        </div>
        <button class="btn btn-primary btn-sm w-full" onclick="copyToClipboard('${enhanced.replace(/'/g, "\\'")}')">
          <i class="fas fa-copy"></i> Use Enhanced Prompt
        </button>
        <div style="font-size:0.65rem;color:var(--text-muted);margin-top:6px">Powered by IBM Watson NLP</div>
      </div>
    `;
  },

  /**
   * Render the Watson Chatbot floating widget
   */
  renderChatbot() {
    const container = document.createElement('div');
    container.id = 'watson-chat-widget';
    container.innerHTML = `
      <style>
        #watson-chat-widget { position:fixed;bottom:24px;right:24px;z-index:9999;font-family:'Space Grotesk',sans-serif }
        #watson-chat-btn {
          width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,#dc2626,#ef4444);
          border:none;color:white;font-size:1.4rem;cursor:pointer;box-shadow:0 4px 20px rgba(220,38,38,0.4);
          display:flex;align-items:center;justify-content:center;transition:all 0.3s;
        }
        #watson-chat-btn:hover { transform:scale(1.1);box-shadow:0 6px 30px rgba(220,38,38,0.6); }
        #watson-chat-box {
          position:absolute;bottom:68px;right:0;width:360px;max-height:500px;
          background:var(--bg-card);border:1px solid var(--border-medium);border-radius:16px;
          box-shadow:0 10px 40px rgba(0,0,0,0.5);display:none;flex-direction:column;overflow:hidden;
        }
        #watson-chat-header {
          padding:14px 16px;background:linear-gradient(135deg,#dc2626,#ef4444);color:white;
          display:flex;align-items:center;gap:10px;font-weight:600;font-size:0.9rem;
        }
        #watson-chat-header img { width:20px;height:20px;border-radius:4px;background:white;padding:2px; }
        #watson-chat-header .close-btn { margin-left:auto;background:none;border:none;color:white;cursor:pointer;font-size:1.1rem;opacity:0.7 }
        #watson-chat-msgs { flex:1;overflow-y:auto;padding:12px;max-height:340px;min-height:200px; }
        #watson-chat-input-area { display:flex;gap:8px;padding:10px 12px;border-top:1px solid var(--border-subtle); }
        #watson-chat-input { flex:1;padding:8px 12px;border-radius:8px;border:1px solid var(--border-subtle);background:var(--bg-secondary);color:var(--text-primary);font-size:0.82rem; }
        #watson-chat-input:focus { outline:none;border-color:var(--accent-primary); }
        .watson-msg { margin-bottom:10px;max-width:85%;padding:10px 14px;border-radius:12px;font-size:0.82rem;line-height:1.5; }
        .watson-msg.user { margin-left:auto;background:var(--accent-primary);color:white;border-bottom-right-radius:4px; }
        .watson-msg.bot { margin-right:auto;background:var(--bg-tertiary);color:var(--text-primary);border-bottom-left-radius:4px; }
        .watson-msg.bot .brand { font-size:0.65rem;color:var(--text-muted);margin-top:4px;display:flex;align-items:center;gap:4px }
        .watson-typing { display:flex;gap:4px;padding:8px 0; }
        .watson-typing span { width:6px;height:6px;border-radius:50%;background:var(--text-muted);animation:bounce 1.4s infinite }
        .watson-typing span:nth-child(2) { animation-delay:0.2s }
        .watson-typing span:nth-child(3) { animation-delay:0.4s }
        @keyframes bounce { 0%,80%,100% { transform:translateY(0) } 40% { transform:translateY(-6px) } }
      </style>
      <div id="watson-chat-box">
        <div id="watson-chat-header">
          <img src="assets/logo-icon.svg" alt="Watson">
          <span>IBM Watson Assistant</span>
          <button class="close-btn" onclick="Watson.toggleChat()"><i class="fas fa-times"></i></button>
        </div>
        <div id="watson-chat-msgs">
          <div class="watson-msg bot">
            👋 Hi! I'm your AI assistant powered by <strong>IBM Watson</strong>. Ask me about generating images, credits, editing, or any ARUA AI feature!
            <div class="brand"><img src="assets/logo-icon.svg" style="width:12px;height:12px"> Watson Assistant</div>
          </div>
        </div>
        <div id="watson-chat-input-area">
          <input type="text" id="watson-chat-input" placeholder="Ask me anything..." onkeydown="if(event.key==='Enter')Watson.sendMessage()">
          <button class="btn btn-primary btn-sm" onclick="Watson.sendMessage()" style="padding:8px 14px"><i class="fas fa-paper-plane"></i></button>
        </div>
      </div>
      <button id="watson-chat-btn" onclick="Watson.toggleChat()">
        <i class="fas fa-robot"></i>
      </button>
    `;
    document.body.appendChild(container);
  },

  toggleChat() {
    this.chatOpen = !this.chatOpen;
    const box = document.getElementById('watson-chat-box');
    const btn = document.getElementById('watson-chat-btn');
    if (box) box.style.display = this.chatOpen ? 'flex' : 'none';
    if (btn) {
      btn.innerHTML = this.chatOpen
        ? '<i class="fas fa-times"></i>'
        : '<i class="fas fa-robot"></i>';
    }
    if (this.chatOpen) {
      setTimeout(() => {
        const input = document.getElementById('watson-chat-input');
        if (input) input.focus();
      }, 300);
    }
  },

  addMessage(text, role) {
    const msgs = document.getElementById('watson-chat-msgs');
    if (!msgs) return;
    const div = document.createElement('div');
    div.className = `watson-msg ${role}`;
    if (role === 'bot') {
      div.innerHTML = text + '<div class="brand"><img src="assets/logo-icon.svg" style="width:12px;height:12px"> Watson Assistant</div>';
    } else {
      div.textContent = text;
    }
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
  },

  showTyping() {
    const msgs = document.getElementById('watson-chat-msgs');
    if (!msgs) return;
    const div = document.createElement('div');
    div.className = 'watson-typing';
    div.id = 'watson-typing-indicator';
    div.innerHTML = '<span></span><span></span><span></span>';
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
  },

  hideTyping() {
    const el = document.getElementById('watson-typing-indicator');
    if (el) el.remove();
  },

  async sendMessage() {
    const input = document.getElementById('watson-chat-input');
    if (!input || !input.value.trim()) return;
    const msg = input.value.trim();
    input.value = '';
    this.addMessage(msg, 'user');
    this.showTyping();
    const result = await this.chat(msg);
    this.hideTyping();
    if (result?.response) {
      this.addMessage(result.response, 'bot');
    } else {
      this.addMessage('Sorry, I had trouble connecting to Watson. Please try again!', 'bot');
    }
  },

  /**
   * Initialize the Watson chatbot widget
   */
  init() {
    if (document.getElementById('watson-chat-widget')) return;
    this.renderChatbot();
  }
};

// Helper function for copy
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    Toast?.success?.('Copied to clipboard!');
  }).catch(() => {
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    ta.remove();
    Toast?.success?.('Copied to clipboard!');
  });
}

// Auto-init when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => Watson.init());
} else {
  Watson.init();
}
