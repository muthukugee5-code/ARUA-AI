/**
 * AURA AI - AI Generation Engine
 * Handles all AI image generation, prompt enhancement, and workspace logic
 */

const Generator = {
  currentStyle: 'realistic',
  currentCategory: 'general',
  currentAspectRatio: '1:1',
  currentModel: 'flux',
  promptHistory: [],

  /**
   * Generate AI images
   */
  async generate(params) {
    return await API.post('/generate', params);
  },

  /**
   * Enhance a prompt using AI
   */
  async enhancePrompt(prompt, style, category) {
    return await API.post('/enhance-prompt', { prompt, style, category });
  },

  /**
   * Get suggestions for prompt improvement
   */
  getLocalSuggestions(prompt) {
    const suggestions = [];
    const lower = prompt.toLowerCase();

    if (!lower.includes('light') && !lower.includes('shadow') && !lower.includes('illuminat')) {
      suggestions.push({ text: '+ dramatic lighting', addition: ', dramatic lighting, rim light' });
    }
    if (!lower.includes('detail') && !lower.includes('4k') && !lower.includes('8k')) {
      suggestions.push({ text: '+ ultra detail', addition: ', ultra detailed, 8K resolution' });
    }
    if (!lower.includes('style') && !lower.includes('art')) {
      suggestions.push({ text: '+ artistic style', addition: ', award winning digital art' });
    }
    if (!lower.includes('color') && !lower.includes('vibrant')) {
      suggestions.push({ text: '+ vivid colors', addition: ', vibrant color palette, rich colors' });
    }

    return suggestions;
  },

  /**
   * Save prompt to local history
   */
  savePrompt(prompt, style) {
    this.promptHistory.unshift({ prompt, style, date: new Date().toISOString() });
    if (this.promptHistory.length > 50) this.promptHistory.pop();
    localStorage.setItem('arua_prompt_history', JSON.stringify(this.promptHistory));
  },

  /**
   * Load saved prompts
   */
  loadHistory() {
    try {
      const saved = localStorage.getItem('arua_prompt_history');
      this.promptHistory = saved ? JSON.parse(saved) : [];
    } catch { this.promptHistory = []; }
    return this.promptHistory;
  }
};

// ---- Workspace UI Controller ----
const Workspace = {
  isGenerating: false,
  currentImages: [],
  progressInterval: null,

  init() {
    this.bindEvents();
    this.initStyleSelector();
    this.initGeneratorCards();
    this.loadHistory();
  },

  bindEvents() {
    // Generate button
    const generateBtn = document.getElementById('generate-btn');
    if (generateBtn) {
      generateBtn.addEventListener('click', () => this.generate());
    }

    // Enhance prompt button
    const enhanceBtn = document.getElementById('enhance-btn');
    if (enhanceBtn) {
      enhanceBtn.addEventListener('click', () => this.enhanceCurrentPrompt());
    }

    // Prompt input - live suggestions
    const promptInput = document.getElementById('prompt-input');
    if (promptInput) {
      let debounce;
      promptInput.addEventListener('input', () => {
        clearTimeout(debounce);
        debounce = setTimeout(() => this.updateSuggestions(promptInput.value), 300);
      });

      // Keyboard shortcut Ctrl+Enter to generate
      promptInput.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') this.generate();
      });
    }

    // Aspect ratio buttons
    document.querySelectorAll('[data-ratio]').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('[data-ratio]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        Generator.currentAspectRatio = btn.dataset.ratio;
      });
    });

    // Number of images
    const numRange = document.getElementById('num-images');
    const numDisplay = document.getElementById('num-images-display');
    if (numRange && numDisplay) {
      numRange.addEventListener('input', () => {
        numDisplay.textContent = numRange.value;
      });
    }

    // Save prompt button
    const savePromptBtn = document.getElementById('save-prompt-btn');
    if (savePromptBtn) {
      savePromptBtn.addEventListener('click', () => this.saveCurrentPrompt());
    }
  },

  initStyleSelector() {
    document.querySelectorAll('.style-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        document.querySelectorAll('.style-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        Generator.currentStyle = chip.dataset.style;
      });
    });
  },

  initGeneratorCards() {
    document.querySelectorAll('.generator-card').forEach(card => {
      card.addEventListener('click', () => {
        document.querySelectorAll('.generator-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        Generator.currentCategory = card.dataset.category;

        // Update category prompt hints
        const categoryTitle = document.getElementById('category-title');
        if (categoryTitle) categoryTitle.textContent = card.querySelector('.generator-name')?.textContent || '';
      });
    });
  },

  async generate() {
    if (this.isGenerating) return;

    const promptInput = document.getElementById('prompt-input');
    const prompt = promptInput?.value?.trim();

    if (!prompt) {
      Toast.error('Please enter a prompt first');
      promptInput?.focus();
      return;
    }

    const params = {
      prompt,
      negative_prompt: document.getElementById('negative-prompt')?.value?.trim() || '',
      style: Generator.currentStyle,
      category: Generator.currentCategory,
      aspect_ratio: Generator.currentAspectRatio,
      resolution: document.getElementById('resolution-select')?.value || 'hd',
      quality: document.getElementById('quality-select')?.value || 'high',
      num_images: parseInt(document.getElementById('num-images')?.value || 1),
      seed: parseInt(document.getElementById('seed-input')?.value || -1),
      enhance_prompt: document.getElementById('enhance-toggle')?.checked ?? true,
      model: Generator.currentModel
    };

    this.startGenerating(params.num_images);

    try {
      const result = await Generator.generate(params);

      if (!result) {
        this.stopGenerating();
        return;
      }

      this.currentImages = result.images || [];
      this.displayResults(result);
      Generator.savePrompt(prompt, Generator.currentStyle);

      Toast.success(`✨ ${result.images.length} image${result.images.length > 1 ? 's' : ''} generated!`);

      // Update credits display
      const creditsEl = document.getElementById('sidebar-credits');
      if (creditsEl) creditsEl.textContent = Format.number(result.credits_remaining || 0);

    } catch (err) {
      Toast.error(err.message || 'Generation failed');
    } finally {
      this.stopGenerating();
    }
  },

  startGenerating(count) {
    this.isGenerating = true;
    const btn = document.getElementById('generate-btn');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');

    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<div class="spinner"></div> Generating...';
    }

    DOM.show(progressContainer);

    // Animate progress bar
    let progress = 0;
    this.progressInterval = setInterval(() => {
      progress = Math.min(progress + Math.random() * 8, 90);
      if (progressBar) progressBar.style.width = `${progress}%`;
      if (progressText) {
        const messages = ['Initializing AI model...', 'Processing prompt...', 'Generating pixels...', 'Applying style...', 'Enhancing details...', 'Almost done...'];
        const idx = Math.floor((progress / 90) * messages.length);
        progressText.textContent = messages[Math.min(idx, messages.length - 1)];
      }
    }, 300);
  },

  stopGenerating() {
    this.isGenerating = false;
    clearInterval(this.progressInterval);

    const btn = document.getElementById('generate-btn');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-fill');

    if (progressBar) progressBar.style.width = '100%';
    setTimeout(() => {
      DOM.hide(progressContainer);
      if (progressBar) progressBar.style.width = '0';
    }, 500);

    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-magic"></i> Generate';
    }
  },

  displayResults(result) {
    const container = document.getElementById('results-container');
    const emptyState = document.getElementById('empty-state');
    const resultsSection = document.getElementById('results-section');

    if (!container) return;

    DOM.show(resultsSection);
    DOM.hide(emptyState);

    // Show enhanced prompt
    const enhancedPromptEl = document.getElementById('enhanced-prompt-display');
    if (enhancedPromptEl && result.enhanced_prompt !== result.original_prompt) {
      enhancedPromptEl.textContent = result.enhanced_prompt;
      DOM.show(document.getElementById('enhanced-prompt-section'));
    }

    // Render image cards
    const html = result.images.map((img, i) => `
      <div class="image-card" data-id="${img.id}" data-url="${img.url}" style="animation-delay: ${i * 0.1}s">
        <img src="${img.url}" alt="Generated image ${i + 1}" loading="lazy"
          onerror="this.src='data:image/svg+xml,<svg xmlns=\\"http://www.w3.org/2000/svg\\" width=\\"200\\" height=\\"200\\"><rect fill=\\"%23111\\"/><text x=\\"100\\" y=\\"100\\" text-anchor=\\"middle\\" fill=\\"%23666\\" font-size=\\"12\\">Loading...</text></svg>'"
        >
        <div class="image-card-overlay">
          <div class="flex gap-sm">
            <span class="badge badge-primary">${img.width}×${img.height}</span>
          </div>
        </div>
        <div class="image-card-actions">
          <button class="image-action-btn" onclick="Workspace.favoriteImage('${img.id}', this)" data-tooltip="Favorite">
            <i class="fas fa-heart"></i>
          </button>
          <button class="image-action-btn" onclick="Workspace.downloadImage('${img.url}', '${img.id}')" data-tooltip="Download">
            <i class="fas fa-download"></i>
          </button>
          <button class="image-action-btn" onclick="Workspace.openEditor('${img.url}', '${img.id}')" data-tooltip="Edit">
            <i class="fas fa-edit"></i>
          </button>
          <button class="image-action-btn" onclick="Workspace.openLightbox('${img.url}')" data-tooltip="View Full">
            <i class="fas fa-expand"></i>
          </button>
        </div>
      </div>
    `).join('');

    container.innerHTML = html;

    // Animate with GSAP if available
    if (typeof gsap !== 'undefined') {
      gsap.from('.image-card', {
        duration: 0.5,
        opacity: 0,
        y: 20,
        stagger: 0.1,
        ease: 'power2.out'
      });
    }
  },

  async enhanceCurrentPrompt() {
    const promptInput = document.getElementById('prompt-input');
    const prompt = promptInput?.value?.trim();

    if (!prompt) {
      Toast.warning('Enter a prompt first');
      return;
    }

    const btn = document.getElementById('enhance-btn');
    Form.setLoading(btn, true, 'Enhancing...');

    try {
      const result = await Generator.enhancePrompt(prompt, Generator.currentStyle, Generator.currentCategory);

      if (result?.enhanced) {
        promptInput.value = result.enhanced;
        promptInput.style.borderColor = 'var(--accent-green)';
        setTimeout(() => promptInput.style.borderColor = '', 2000);

        Toast.success('Prompt enhanced! ✨');

        // Show suggestions
        if (result.suggestions?.length) {
          this.renderSuggestions(result.suggestions);
        }
      }
    } catch (err) {
      // Apply local enhancement as fallback
      const enhanced = Generator.enhancePrompt(prompt, Generator.currentStyle);
      promptInput.value = enhanced;
      Toast.info('Prompt locally enhanced');
    } finally {
      Form.setLoading(btn, false);
      btn.innerHTML = '<i class="fas fa-wand-magic-sparkles"></i> Enhance';
    }
  },

  updateSuggestions(prompt) {
    if (!prompt || prompt.length < 5) return;
    const suggestions = Generator.getLocalSuggestions(prompt);
    this.renderQuickSuggestions(suggestions);
  },

  renderQuickSuggestions(suggestions) {
    const container = document.getElementById('quick-suggestions');
    if (!container) return;

    container.innerHTML = suggestions.map(s => `
      <button class="style-chip" onclick="Workspace.applyQuickSuggestion(this, '${s.addition}')">
        ${s.text}
      </button>
    `).join('');
  },

  applyQuickSuggestion(btn, addition) {
    const promptInput = document.getElementById('prompt-input');
    if (promptInput && addition) {
      promptInput.value += addition;
      btn.classList.add('active');
      setTimeout(() => btn.classList.remove('active'), 500);
    }
  },

  async favoriteImage(imageId, btn) {
    try {
      const result = await API.post('/favorite', { image_id: imageId });
      if (result?.is_favorite) {
        btn.classList.add('active');
        Toast.success('Added to favorites ❤️');
      } else {
        btn.classList.remove('active');
        Toast.info('Removed from favorites');
      }
    } catch (err) {
      Toast.error('Failed to update favorite');
    }
  },

  downloadImage(url, id) {
    const a = document.createElement('a');
    a.href = url;
    a.download = `arua-ai-${id}.jpg`;
    a.target = '_blank';
    a.click();
    Toast.success('Download started!');
  },

  openEditor(url, id) {
    window.location.href = `editor.html?image=${encodeURIComponent(url)}&id=${id}`;
  },

  openLightbox(url) {
    let lightbox = document.getElementById('lightbox-modal');
    if (!lightbox) {
      lightbox = document.createElement('div');
      lightbox.id = 'lightbox-modal';
      lightbox.className = 'modal-overlay';
      lightbox.innerHTML = `
        <div style="max-width:90vw;max-height:90vh;position:relative">
          <img id="lightbox-img" style="max-width:100%;max-height:85vh;border-radius:16px;display:block">
          <button class="btn btn-glass" style="position:absolute;top:-50px;right:0" onclick="document.getElementById('lightbox-modal').classList.remove('active')">
            <i class="fas fa-times"></i> Close
          </button>
        </div>
      `;
      lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) lightbox.classList.remove('active');
      });
      document.body.appendChild(lightbox);
    }

    document.getElementById('lightbox-img').src = url;
    lightbox.classList.add('active');
  },

  saveCurrentPrompt() {
    const prompt = document.getElementById('prompt-input')?.value?.trim();
    if (!prompt) return;
    Generator.savePrompt(prompt, Generator.currentStyle);
    Toast.success('Prompt saved!');
  },

  loadHistory() {
    Generator.loadHistory();
    this.renderHistory();
  },

  renderHistory() {
    const container = document.getElementById('prompt-history');
    if (!container) return;

    if (!Generator.promptHistory.length) {
      container.innerHTML = '<p class="text-muted text-small">No saved prompts yet</p>';
      return;
    }

    container.innerHTML = Generator.promptHistory.slice(0, 8).map(item => `
      <div class="history-item glass" style="padding:10px 14px;border-radius:10px;margin-bottom:6px;cursor:pointer"
        onclick="document.getElementById('prompt-input').value = '${item.prompt.replace(/'/g, "\\'")}'"
      >
        <div style="font-size:0.85rem;color:var(--text-secondary)" class="text-truncate">${item.prompt}</div>
        <div style="font-size:0.75rem;color:var(--text-muted);margin-top:3px">${Format.relativeTime(item.date)}</div>
      </div>
    `).join('');
  }
};
