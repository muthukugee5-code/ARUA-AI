/**
 * AURA AI - Video Studio
 * Creates AI videos from generated scene images.
 * Renders a Ken Burns slideshow on canvas and records it with MediaRecorder.
 * Works entirely in the browser - no ffmpeg or server-side video needed.
 */

const VideoStudio = {
  isCreating: false,
  renderer: null,
  videos: [],
  currentVideo: null,

  /**
   * Request scene images from the backend
   */
  async create(params) {
    return await API.post('/video/create', params);
  },

  /**
   * Load saved videos from localStorage
   */
  loadVideos() {
    try {
      const saved = localStorage.getItem('arua_videos');
      this.videos = saved ? JSON.parse(saved) : [];
    } catch { this.videos = []; }
    return this.videos;
  },

  saveVideo(record) {
    this.loadVideos();
    this.videos.unshift(record);
    if (this.videos.length > 20) this.videos.pop();
    localStorage.setItem('arua_videos', JSON.stringify(this.videos));
  },

  /**
   * Full pipeline: create scenes -> render -> record -> preview
   */
  async generate() {
    if (this.isCreating) return;

    const promptInput = document.getElementById('prompt-input');
    const prompt = promptInput?.value?.trim();

    if (!prompt) {
      Toast.error('Please enter a prompt first');
      promptInput?.focus();
      return;
    }

    const numScenes = parseInt(document.getElementById('video-scenes')?.value || 3);
    const sceneDuration = parseFloat(document.getElementById('video-duration')?.value || 3);

    const params = {
      prompt,
      style: Generator.currentStyle,
      category: Generator.currentCategory,
      aspect_ratio: Generator.currentAspectRatio,
      resolution: document.getElementById('resolution-select')?.value || 'hd',
      num_scenes: numScenes,
      scene_duration: sceneDuration,
      enhance_prompt: document.getElementById('enhance-toggle')?.checked ?? true,
      model: Generator.currentModel
    };

    this.isCreating = true;
    Workspace.startGenerating(numScenes);

    try {
      const result = await this.create(params);

      if (!result?.video) {
        Toast.error('Video creation failed');
        return;
      }

      const video = result.video;
      const scenes = video.scenes || [];
      if (!scenes.length) {
        Toast.error('No scenes were generated');
        return;
      }

      // Show scene previews immediately
      this.showSceneGrid(video);

      // Render the actual video file
      this.renderer = new VideoRenderer({
        scenes,
        width: video.width || 1280,
        height: video.height || 720,
        onProgress: (pct, msg) => this.renderProgress(pct, msg)
      });

      const blob = await this.renderer.render();
      const url = URL.createObjectURL(blob);

      const record = {
        id: video.id,
        prompt: prompt,
        style: params.style,
        num_scenes: numScenes,
        scene_duration: sceneDuration,
        created_at: new Date().toISOString(),
        url,
        scenes
      };
      this.currentVideo = record;
      this.saveVideo(record);

      this.displayResult(record);
      Generator.savePrompt(prompt, Generator.currentStyle);

      const creditsEl = document.getElementById('sidebar-credits');
      if (creditsEl) creditsEl.textContent = Format.number(result.credits_remaining || 0);

      Toast.success(`🎬 ${numScenes}-scene video created!`);

    } catch (err) {
      Toast.error(err.message || 'Video creation failed');
    } finally {
      this.isCreating = false;
      Workspace.stopGenerating();
    }
  },

  renderProgress(pct, msg) {
    const progressBar = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    if (progressBar) progressBar.style.width = `${pct}%`;
    if (progressText) progressText.textContent = msg || `Rendering video... ${Math.round(pct)}%`;
  },

  showSceneGrid(video) {
    const container = document.getElementById('results-container');
    const emptyState = document.getElementById('empty-state');
    const resultsSection = document.getElementById('results-section');
    if (!container) return;

    DOM.show(resultsSection);
    DOM.hide(emptyState);
    container.style.display = 'grid';

    container.innerHTML = video.scenes.map((s, i) => `
      <div class="image-card" style="animation-delay: ${i * 0.1}s">
        <img src="${s.url}" alt="Scene ${i + 1}" loading="lazy"
          onerror="this.src='data:image/svg+xml,<svg xmlns=\\"http://www.w3.org/2000/svg\\" width=\\"200\\" height=\\"200\\"><rect fill=\\"%23111\\"/><text x=\\"100\\" y=\\"100\\" text-anchor=\\"middle\\" fill=\\"%23666\\" font-size=\\"12\\">Loading...</text></svg>'">
        <div class="image-card-overlay">
          <div class="flex gap-sm">
            <span class="badge badge-primary">Scene ${i + 1}</span>
          </div>
        </div>
      </div>
    `).join('');
  },

  displayResult(record) {
    const container = document.getElementById('results-container');
    if (!container) return;
    container.style.display = 'block';

    const totalSeconds = (record.num_scenes * record.scene_duration).toFixed(1);

    container.innerHTML = `
      <div style="background:var(--bg-card);border:1px solid var(--border-subtle);border-radius:var(--radius-xl);overflow:hidden;margin-bottom:16px">
        <video controls autoplay loop muted playsinline style="width:100%;max-height:480px;background:#000;display:block"
          src="${record.url}"></video>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px">
        <span class="badge badge-primary"><i class="fas fa-film"></i> ${record.num_scenes} scenes</span>
        <span class="badge badge-primary"><i class="fas fa-clock"></i> ${totalSeconds}s</span>
        <span class="badge badge-primary"><i class="fas fa-palette"></i> ${record.style}</span>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn btn-aurora" onclick="VideoStudio.downloadCurrent()">
          <i class="fas fa-download"></i> Download Video
        </button>
        <button class="btn btn-glass" onclick="VideoStudio.regenerate()">
          <i class="fas fa-redo"></i> Regenerate Scenes
        </button>
      </div>
      <p style="color:var(--text-muted);font-size:0.8rem;margin-top:12px">
        <i class="fas fa-info-circle"></i> Video is rendered in your browser as WebM (VP9). Works in all modern browsers.
      </p>
    `;
  },

  downloadCurrent() {
    if (!this.currentVideo?.url) {
      Toast.error('No video to download');
      return;
    }
    const a = document.createElement('a');
    a.href = this.currentVideo.url;
    a.download = `arua-ai-${this.currentVideo.id}.webm`;
    a.click();
    Toast.success('Video downloaded!');
  },

  regenerate() {
    document.getElementById('results-container').style.display = 'none';
    DOM.show('empty-state');
  },

  renderHistory() {
    const container = document.getElementById('video-history');
    if (!container) return;
    this.loadVideos();

    if (!this.videos.length) {
      container.innerHTML = '<p class="text-muted text-small">No videos yet. Create one above!</p>';
      return;
    }

    container.innerHTML = this.videos.slice(0, 5).map(v => `
      <div class="history-item glass" style="padding:10px 14px;border-radius:10px;margin-bottom:6px;cursor:pointer"
        onclick="VideoStudio.playSaved('${v.id}')">
        <div style="font-size:0.85rem;color:var(--text-secondary)" class="text-truncate">🎬 ${v.prompt}</div>
        <div style="font-size:0.75rem;color:var(--text-muted);margin-top:3px">${v.num_scenes} scenes · ${Format.relativeTime(v.created_at)}</div>
      </div>
    `).join('');
  },

  playSaved(id) {
    const v = this.videos.find(x => x.id === id);
    if (!v) return;
    this.currentVideo = v;
    const container = document.getElementById('results-container');
    const emptyState = document.getElementById('empty-state');
    const resultsSection = document.getElementById('results-section');
    if (container && resultsSection && emptyState) {
      DOM.show(resultsSection);
      DOM.hide(emptyState);
    }
    this.displayResult(v);
  }
};

/**
 * Canvas-based Ken Burns video renderer
 * Cross-fades scenes with slow zoom/pan and records via MediaRecorder
 */
class VideoRenderer {
  constructor({ scenes, width = 1280, height = 720, fps = 30, onProgress = null }) {
    this.scenes = scenes;
    this.width = width;
    this.height = height;
    this.fps = fps;
    this.onProgress = onProgress;
    this.canvas = document.createElement('canvas');
    this.canvas.width = width;
    this.canvas.height = height;
    this.ctx = this.canvas.getContext('2d');
  }

  async render() {
    // Preload all scene images
    const images = [];
    for (let i = 0; i < this.scenes.length; i++) {
      this.onProgress?.(Math.round((i / this.scenes.length) * 20), `Loading scene ${i + 1}/${this.scenes.length}...`);
      images.push(await this.loadImage(this.scenes[i].url));
    }

    const duration = this.scenes[0]?.duration || 3;
    const totalSeconds = this.scenes.length * duration;

    // Set up MediaRecorder
    const stream = this.canvas.captureStream(this.fps);
    const mime = this.pickMimeType();
    const recorder = new MediaRecorder(stream, { mimeType: mime, videoBitsPerSecond: 8_000_000 });
    const chunks = [];

    recorder.ondataavailable = (e) => { if (e.data?.size) chunks.push(e.data); };

    const finished = new Promise((resolve) => {
      recorder.onstop = () => resolve(new Blob(chunks, { type: mime }));
    });

    recorder.start(100);

    // Render each scene with Ken Burns effect
    let sceneIndex = 0;
    for (const img of images) {
      this.onProgress?.(20 + Math.round((sceneIndex / images.length) * 70), `Rendering scene ${sceneIndex + 1}/${images.length}...`);
      await this.renderScene(img, duration, sceneIndex);
      sceneIndex++;
    }

    this.onProgress?.(95, 'Finalizing video...');
    recorder.stop();
    await sleep(300); // let MediaRecorder flush

    this.onProgress?.(100, 'Done');
    await sleep(200);
    return finished;
  }

  renderScene(img, duration, sceneIndex) {
    return new Promise((resolve) => {
      const start = performance.now();
      const zoomIn = sceneIndex % 2 === 0;

      const draw = () => {
        const elapsed = (performance.now() - start) / 1000;
        const t = Math.min(elapsed / duration, 1);
        const ease = 1 - Math.pow(1 - t, 3); // ease-out cubic

        const zoomStart = 1.0;
        const zoomEnd = 1.12;
        const scale = zoomIn
          ? zoomStart + (zoomEnd - zoomStart) * ease
          : zoomEnd - (zoomEnd - zoomStart) * ease;

        // Slow horizontal pan
        const panX = (ease - 0.5) * this.width * 0.04;
        const panY = (ease - 0.5) * this.height * 0.03;

        const ctx = this.ctx;
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, this.width, this.height);

        const w = this.width * scale;
        const h = this.height * scale;
        const cx = this.width / 2 - w / 2 + panX;
        const cy = this.height / 2 - h / 2 + panY;

        ctx.drawImage(img, cx, cy, w, h);

        if (elapsed < duration) {
          requestAnimationFrame(draw);
        } else {
          // Fade to next scene
          resolve();
        }
      };

      draw();
    });
  }

  loadImage(url) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error(`Failed to load scene image: ${url}`));
      img.src = url;
    });
  }

  pickMimeType() {
    const candidates = [
      'video/webm;codecs=vp9',
      'video/webm;codecs=vp8',
      'video/webm'
    ];
    for (const m of candidates) {
      if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported(m)) return m;
    }
    return 'video/webm';
  }
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}
