/**
 * AURA AI - Core JavaScript Utilities
 * Shared functionality across all pages
 */

// ---- Configuration ----
const PROD_API = 'https://arua-ai.onrender.com/api';

function resolveApiBase() {
  // Allow override via ?api= or localStorage (useful for testing)
  try {
    const urlOverride = new URLSearchParams(window.location.search).get('api');
    if (urlOverride) return urlOverride;
    const stored = localStorage.getItem('arua_api_base');
    if (stored) return stored;
  } catch (e) { /* ignore */ }

  // Local dev: frontend on :5500 or :3000 -> backend on localhost:5000
  const host = window.location.hostname || '';
  if (host === 'localhost' || host === '127.0.0.1') {
    return 'http://localhost:5000/api';
  }
  return PROD_API;
}

const CONFIG = {
  API_BASE: resolveApiBase(),
  APP_NAME: 'AURA AI',
  VERSION: '1.0.0',
  THEME_KEY: 'arua_theme',
  TOKEN_KEY: 'arua_access_token',
  REFRESH_KEY: 'arua_refresh_token',
  USER_KEY: 'arua_user'
};

// ---- API Client ----
const API = {
  /**
   * Make an authenticated API request using Axios.
   */
  async request(method, endpoint, data = null, options = {}) {
    const token = Auth.getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };

    const config = {
      method,
      url: `${CONFIG.API_BASE}${endpoint}`,
      headers,
      ...options
    };

    if (data) {
      if (method === 'GET') {
        config.params = data;
      } else {
        config.data = data;
      }
    }

    try {
      const response = await axios(config);
      return response.data;
    } catch (error) {
      if (error.response) {
        const err = error.response.data;
        if (error.response.status === 401) {
          Auth.logout();
          return null;
        }
        throw new Error(err.message || err.error || 'Request failed');
      }
      throw new Error('Network error. Please check your connection.');
    }
  },

  get: (endpoint, params) => API.request('GET', endpoint, params),
  post: (endpoint, data) => API.request('POST', endpoint, data),
  put: (endpoint, data) => API.request('PUT', endpoint, data),
  patch: (endpoint, data) => API.request('PATCH', endpoint, data),
  delete: (endpoint) => API.request('DELETE', endpoint)
};

// ---- Authentication ----
const Auth = {
  getToken() {
    return localStorage.getItem(CONFIG.TOKEN_KEY) ||
      sessionStorage.getItem(CONFIG.TOKEN_KEY);
  },

  getUser() {
    try {
      const raw = localStorage.getItem(CONFIG.USER_KEY) ||
        sessionStorage.getItem(CONFIG.USER_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch { return null; }
  },

  setSession(data, remember = true) {
    const storage = remember ? localStorage : sessionStorage;
    storage.setItem(CONFIG.TOKEN_KEY, data.access_token);
    if (data.refresh_token) {
      storage.setItem(CONFIG.REFRESH_KEY, data.refresh_token);
    }
    if (data.user) {
      storage.setItem(CONFIG.USER_KEY, JSON.stringify(data.user));
    }
  },

  logout() {
    localStorage.removeItem(CONFIG.TOKEN_KEY);
    localStorage.removeItem(CONFIG.REFRESH_KEY);
    localStorage.removeItem(CONFIG.USER_KEY);
    sessionStorage.removeItem(CONFIG.TOKEN_KEY);
    sessionStorage.removeItem(CONFIG.REFRESH_KEY);
    sessionStorage.removeItem(CONFIG.USER_KEY);
    window.location.href = 'login.html';
  },

  requireAuth() {
    if (!this.getToken()) {
      window.location.href = 'login.html';
      return false;
    }
    return true;
  },

  isLoggedIn() {
    return !!this.getToken();
  }
};

// ---- Theme Manager ----
const Theme = {
  init() {
    const saved = localStorage.getItem(CONFIG.THEME_KEY);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = saved || (prefersDark ? 'dark' : 'light');
    this.apply(theme);

    // Listen for system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem(CONFIG.THEME_KEY)) {
        this.apply(e.matches ? 'dark' : 'light');
      }
    });
  },

  apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(CONFIG.THEME_KEY, theme);
    this.updateIcons(theme);
  },

  toggle() {
    const current = document.documentElement.getAttribute('data-theme');
    this.apply(current === 'dark' ? 'light' : 'dark');
  },

  updateIcons(theme) {
    document.querySelectorAll('[data-theme-icon]').forEach(el => {
      el.className = el.className.replace(/fa-(sun|moon)/, '');
      el.className += theme === 'dark' ? ' fa-sun' : ' fa-moon';
    });
  },

  getCurrent() {
    return document.documentElement.getAttribute('data-theme') || 'dark';
  }
};

// ---- Toast Notifications ----
const Toast = {
  container: null,

  init() {
    if (!document.getElementById('toast-container')) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      document.body.appendChild(this.container);
    } else {
      this.container = document.getElementById('toast-container');
    }
  },

  show(message, type = 'info', duration = 4000) {
    if (!this.container) this.init();

    const icons = {
      success: 'fa-check-circle',
      error: 'fa-times-circle',
      warning: 'fa-exclamation-triangle',
      info: 'fa-info-circle'
    };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <i class="fas ${icons[type] || icons.info} toast-icon"></i>
      <span class="toast-message">${message}</span>
      <i class="fas fa-times toast-close" onclick="this.parentElement.remove()"></i>
    `;

    this.container.appendChild(toast);

    if (duration > 0) {
      setTimeout(() => {
        toast.classList.add('removing');
        setTimeout(() => toast.remove(), 300);
      }, duration);
    }

    return toast;
  },

  success: (msg, duration) => Toast.show(msg, 'success', duration),
  error: (msg, duration) => Toast.show(msg, 'error', duration),
  warning: (msg, duration) => Toast.show(msg, 'warning', duration),
  info: (msg, duration) => Toast.show(msg, 'info', duration)
};

// ---- Mouse Glow Effect ----
const MouseGlow = {
  init() {
    const glow = document.querySelector('.mouse-glow');
    if (!glow) return;

    document.addEventListener('mousemove', (e) => {
      glow.style.left = `${e.clientX}px`;
      glow.style.top = `${e.clientY}px`;
    });
  }
};

// ---- Particle System ----
const Particles = {
  canvas: null,
  ctx: null,
  particles: [],
  animFrame: null,

  init(canvasId = 'particle-canvas') {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;

    this.ctx = this.canvas.getContext('2d');
    this.resize();
    this.createParticles(60);
    this.animate();

    window.addEventListener('resize', () => this.resize());
  },

  resize() {
    if (!this.canvas) return;
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  },

  createParticles(count) {
    this.particles = [];
    for (let i = 0; i < count; i++) {
      this.particles.push({
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        radius: Math.random() * 1.5 + 0.3,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        opacity: Math.random() * 0.5 + 0.1,
        color: Math.random() > 0.5 ? '124, 92, 216' : '91, 141, 239'
      });
    }
  },

  animate() {
    if (!this.ctx) return;
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    this.particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;

      // Wrap around edges
      if (p.x < 0) p.x = this.canvas.width;
      if (p.x > this.canvas.width) p.x = 0;
      if (p.y < 0) p.y = this.canvas.height;
      if (p.y > this.canvas.height) p.y = 0;

      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      this.ctx.fillStyle = `rgba(${p.color}, ${p.opacity})`;
      this.ctx.fill();
    });

    // Draw connections
    for (let i = 0; i < this.particles.length; i++) {
      for (let j = i + 1; j < this.particles.length; j++) {
        const dx = this.particles[i].x - this.particles[j].x;
        const dy = this.particles[i].y - this.particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 120) {
          this.ctx.beginPath();
          this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
          this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
          this.ctx.strokeStyle = `rgba(124, 92, 216, ${0.08 * (1 - dist / 120)})`;
          this.ctx.lineWidth = 0.5;
          this.ctx.stroke();
        }
      }
    }

    this.animFrame = requestAnimationFrame(() => this.animate());
  },

  destroy() {
    if (this.animFrame) cancelAnimationFrame(this.animFrame);
  }
};

// ---- Button Ripple Effect ----
const Ripple = {
  init() {
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn');
      if (!btn) return;

      const rect = btn.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height) * 2;
      const x = e.clientX - rect.left - size / 2;
      const y = e.clientY - rect.top - size / 2;

      const ripple = document.createElement('span');
      ripple.className = 'ripple';
      ripple.style.cssText = `width: ${size}px; height: ${size}px; left: ${x}px; top: ${y}px;`;
      btn.appendChild(ripple);

      setTimeout(() => ripple.remove(), 600);
    });
  }
};

// ---- Form Utilities ----
const Form = {
  validate(formEl) {
    const inputs = formEl.querySelectorAll('[required]');
    let valid = true;

    inputs.forEach(input => {
      if (!input.value.trim()) {
        this.setError(input, 'This field is required');
        valid = false;
      } else {
        this.clearError(input);
      }
    });

    return valid;
  },

  setError(input, message) {
    input.classList.add('error');
    const existing = input.parentElement.querySelector('.form-error');
    if (!existing) {
      const error = document.createElement('div');
      error.className = 'form-error';
      error.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
      input.parentElement.appendChild(error);
    } else {
      existing.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    }
  },

  clearError(input) {
    input.classList.remove('error');
    const error = input.parentElement.querySelector('.form-error');
    if (error) error.remove();
  },

  clearAllErrors(formEl) {
    formEl.querySelectorAll('.form-error').forEach(e => e.remove());
    formEl.querySelectorAll('.error').forEach(e => e.classList.remove('error'));
  },

  setLoading(btn, loading, text = 'Loading...') {
    if (loading) {
      btn.disabled = true;
      btn._originalContent = btn.innerHTML;
      btn.innerHTML = `<div class="spinner"></div> ${text}`;
    } else {
      btn.disabled = false;
      btn.innerHTML = btn._originalContent || text;
    }
  }
};

// ---- Number Formatting ----
const Format = {
  number(n) {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
    return n.toString();
  },

  fileSize(bytes) {
    if (bytes >= 1073741824) return (bytes / 1073741824).toFixed(2) + ' GB';
    if (bytes >= 1048576) return (bytes / 1048576).toFixed(2) + ' MB';
    if (bytes >= 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return bytes + ' B';
  },

  date(dateStr) {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  },

  relativeTime(dateStr) {
    const diff = Date.now() - new Date(dateStr);
    const mins = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return this.date(dateStr);
  }
};

// ---- DOM Helpers ----
const DOM = {
  $: (sel, parent = document) => parent.querySelector(sel),
  $$: (sel, parent = document) => [...parent.querySelectorAll(sel)],

  show(el) {
    if (typeof el === 'string') el = document.querySelector(el);
    if (el) el.classList.remove('hidden');
  },

  hide(el) {
    if (typeof el === 'string') el = document.querySelector(el);
    if (el) el.classList.add('hidden');
  },

  toggle(el) {
    if (typeof el === 'string') el = document.querySelector(el);
    if (el) el.classList.toggle('hidden');
  },

  setText(sel, text) {
    const el = typeof sel === 'string' ? document.querySelector(sel) : sel;
    if (el) el.textContent = text;
  },

  setHTML(sel, html) {
    const el = typeof sel === 'string' ? document.querySelector(sel) : sel;
    if (el) el.innerHTML = html;
  },

  on(sel, event, handler, parent = document) {
    const els = typeof sel === 'string' ? parent.querySelectorAll(sel) : [sel];
    els.forEach(el => el.addEventListener(event, handler));
  }
};

// ---- Sidebar User Display ----
function initSidebarUser() {
  const user = Auth.getUser();
  if (!user) return;

  const nameEl = document.getElementById('sidebar-user-name');
  const avatarEl = document.getElementById('sidebar-user-avatar');
  const creditsEl = document.getElementById('sidebar-credits');

  if (nameEl) nameEl.textContent = user.username || user.email?.split('@')[0] || 'User';
  if (avatarEl) {
    if (user.avatar_url) {
      avatarEl.innerHTML = `<img src="${user.avatar_url}" alt="Avatar">`;
    } else {
      const initial = (user.username || user.email || 'U')[0].toUpperCase();
      avatarEl.textContent = initial;
    }
  }
  if (creditsEl) creditsEl.textContent = Format.number(user.ai_credits || 0);
}

// ---- Navigation Active State ----
function setActiveNav() {
  const current = window.location.pathname.split('/').pop().replace('.html', '');
  document.querySelectorAll('.nav-item').forEach(item => {
    const href = item.getAttribute('href') || '';
    const page = href.split('/').pop().replace('.html', '');
    if (page === current || (current === '' && page === 'dashboard')) {
      item.classList.add('active');
    }
  });
}

// ---- Sidebar Toggle ----
function initMobileSidebar() {
  const toggleBtn = document.getElementById('sidebar-toggle');
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.createElement('div');
  overlay.className = 'sidebar-overlay';
  overlay.style.cssText = `position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:99;display:none`;
  document.body.appendChild(overlay);

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      const isMobile = window.innerWidth <= 768;
      if (isMobile) {
        sidebar.classList.toggle('mobile-open');
        overlay.style.display = sidebar.classList.contains('mobile-open') ? 'block' : 'none';
      } else {
        document.body.classList.toggle('sidebar-collapsed');
        overlay.style.display = 'none';
      }
    });

    overlay.addEventListener('click', () => {
      sidebar.classList.remove('mobile-open');
      overlay.style.display = 'none';
    });

    window.addEventListener('resize', () => {
      if (window.innerWidth > 768) {
        overlay.style.display = 'none';
      }
    });
  }
}

// ---- Initialize Core ----
function initCore() {
  Theme.init();
  Toast.init();
  MouseGlow.init();
  Ripple.init();

  // Theme toggle buttons
  document.querySelectorAll('[data-action="toggle-theme"]').forEach(btn => {
    btn.addEventListener('click', () => Theme.toggle());
  });
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initCore);
