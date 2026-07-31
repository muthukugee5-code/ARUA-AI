# ARUA AI 🎨
### *The World's Most Advanced AI Creative Platform*

> Built for the **IBM AI Innovation Competition** — A production-ready, full-stack AI platform that competes with Midjourney, Leonardo AI, Adobe Firefly, and Canva AI.

---

## ✨ Overview

ARUA AI is a complete AI creative platform where users can generate, edit, organize, and manage AI-created art, UI designs, logos, 3D renders, anime art, and more — all from a single premium dashboard.

**Live Demo:** `http://localhost:5500/frontend/index.html`  
**Backend API:** `http://localhost:5000/api`

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, JavaScript ES6, GSAP, AOS, Chart.js, Font Awesome |
| **Backend** | Python Flask, Flask-CORS, REST API |
| **Database** | Supabase PostgreSQL + Auth + Storage |
| **AI Models** | Pollinations.ai (Flux), Hugging Face (Mixtral) |
| **Image Processing** | Pillow |
| **Fonts** | Space Grotesk, Inter |

---

## 🚀 Quick Start

### 1. Clone & Install Backend

```bash
cd arua-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials:
# - SUPABASE_URL
# - SUPABASE_ANON_KEY
# - SUPABASE_SERVICE_KEY
# - HUGGINGFACE_API_KEY
# - SECRET_KEY (generate a random string)
```

### 3. Set Up Supabase Database

1. Create a free project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run the full contents of `database/schema.sql`
3. Create two Storage Buckets:
   - `arua-generated` (public)
   - `arua-avatars` (public)
4. Copy your Project URL and keys to `.env`

### 4. Start the Backend

```bash
cd backend
python app.py
# Backend runs on http://localhost:5000
```

### 5. Serve the Frontend

```bash
# Option A: VS Code Live Server (recommended for dev)
# Open frontend/index.html → Right-click → "Open with Live Server"

# Option B: Python HTTP server
cd frontend
python -m http.server 5500
# Visit http://localhost:5500

# Option C: Any static file server
npx serve frontend
```

---

## 📁 Project Structure

```
arua-ai/
├── backend/
│   ├── app.py                    # Flask application factory
│   ├── api/
│   │   ├── auth.py               # Signup, Login, Logout
│   │   ├── generate.py           # AI image generation
│   │   ├── gallery.py            # Gallery, Dashboard, Favorites
│   │   ├── collections.py        # Collection management
│   │   ├── profile.py            # Profile, Avatar, History
│   │   ├── editor.py             # Image editing API
│   │   └── admin.py              # Admin panel
│   └── utils/
│       ├── supabase_client.py    # Supabase REST API client
│       ├── auth_middleware.py    # JWT auth decorators
│       └── image_utils.py        # Pillow image processing
│
├── frontend/
│   ├── index.html                # Landing page
│   ├── login.html                # Login
│   ├── signup.html               # Registration
│   ├── dashboard.html            # User dashboard
│   ├── workspace.html            # AI generation workspace
│   ├── gallery.html              # Image gallery
│   ├── collections.html          # Collections manager
│   ├── editor.html               # Image editor
│   ├── profile.html              # User profile
│   ├── admin.html                # Admin panel
│   ├── styles/
│   │   ├── main.css              # Design system
│   │   └── landing.css           # Landing page styles
│   └── scripts/
│       ├── core.js               # API, Auth, Theme, Particles
│       └── generator.js          # AI workspace logic
│
├── database/
│   └── schema.sql                # Complete PostgreSQL schema + RLS
│
├── uploads/                      # Temporary file uploads
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
└── README.md
```

---

## 🎨 Features

### AI Generators (30+)
- **AI Image** · **3D Studio** · **Anime Studio** · **Manga Generator**
- **UI/UX Designer** · **Mobile App UI** · **Dashboard UI** · **Website UI**
- **Logo Generator** · **Poster Designer** · **Banner** · **Flyer**
- **Business Card** · **Social Media** · **Instagram Post** · **YouTube Thumbnail**
- **Book Cover** · **Album Cover** · **Wallpaper** · **Icon** · **Sticker**
- **Product Mockup** · **Fashion** · **Interior Design** · **Architecture**
- **Character Design** · **Vehicle** · **Product Design** · **Brand Kit**

### AI Styles (25+)
Realistic · Hyper Realistic · Anime · Manga · Pixar · Disney · Cartoon · Watercolor · Oil Painting · Pencil Sketch · Digital Painting · Pixel Art · Fantasy · Cyberpunk · Sci-Fi · Gothic · HDR · Cinematic · Clay · Low Poly · Isometric · Luxury · Minimal · Concept Art

### Premium Features
| Feature | Description |
|---------|-------------|
| **Smart Prompt AI** | Auto-enhances prompts with lighting, composition, quality keywords |
| **Image Editor** | Brightness, Contrast, Saturation, Blur, Sharpen, 7 filters |
| **AI Upscaler** | 2x-4x upscaling using Lanczos + AI |
| **Background Remover** | One-click background removal |
| **Version History** | Every edit saved as a new version |
| **Collections** | Organize images into named folders |
| **Prompt Library** | Save, search, and reuse prompts |
| **Brand Kit** | Complete brand identity generation |

---

## 🔌 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/signup` | Register new user | ❌ |
| POST | `/api/login` | Authenticate user | ❌ |
| POST | `/api/logout` | Logout | ✅ |
| GET | `/api/me` | Get current user | ✅ |
| POST | `/api/generate` | Generate AI images | ✅ |
| POST | `/api/enhance-prompt` | Enhance prompt | ✅ |
| GET | `/api/dashboard` | Dashboard stats | ✅ |
| GET | `/api/gallery` | Get image gallery | ✅ |
| GET | `/api/favorites` | Get favorites | ✅ |
| POST | `/api/favorite` | Toggle favorite | ✅ |
| DELETE | `/api/image/:id` | Delete image | ✅ |
| GET | `/api/collections` | Get collections | ✅ |
| POST | `/api/collections` | Create collection | ✅ |
| POST | `/api/editor/edit` | Apply image edits | ✅ |
| POST | `/api/editor/upscale` | Upscale image | ✅ |
| POST | `/api/editor/remove-background` | Remove BG | ✅ |
| GET | `/api/profile` | Get profile | ✅ |
| PUT | `/api/profile` | Update profile | ✅ |
| GET | `/api/history` | Prompt history | ✅ |
| GET | `/api/admin/stats` | Platform stats | 👑 |
| GET | `/api/admin/users` | All users | 👑 |
| DELETE | `/api/admin/users/:id` | Delete user | 👑 |

---

## 🔒 Security

- ✅ **JWT Authentication** via Supabase Auth
- ✅ **Row Level Security** (PostgreSQL RLS) — users see only their data
- ✅ **CORS Protection** — configurable allowed origins
- ✅ **Rate Limiting** — prevents abuse (30 generates/min, etc.)
- ✅ **Input Validation** — all inputs sanitized
- ✅ **Environment Variables** — no secrets in code
- ✅ **Password Hashing** — handled by Supabase (bcrypt)

---

## 🌐 AI Services (All Free Tier)

| Service | Use | Cost |
|---------|-----|------|
| **Pollinations.ai** | Image generation (Flux model) | 🆓 Unlimited free |
| **Hugging Face** | Prompt enhancement (Mixtral-8x7B) | 🆓 ~30K tokens/month |
| **Supabase** | Database, Auth, Storage | 🆓 500MB + 50k users free |

---

## 🎯 IBM AI Innovation Competition

This project demonstrates:
- **Production-quality engineering** with clean architecture
- **Real AI integration** with state-of-the-art models
- **Scalable full-stack design** (REST API + SPA frontend)
- **Enterprise security** (JWT, RLS, rate limiting, CORS)
- **Premium UX/UI** rivaling commercial AI platforms
- **Free-tier AI** democratizing creative tools

---

## 🛠️ Make Your First Admin

After creating an account via the app:

```sql
-- Run in Supabase SQL Editor
UPDATE public.profiles 
SET role = 'admin' 
WHERE email = 'your-email@example.com';
```

---

## 📄 License

MIT License — Built for education and competition purposes.

---

<p align="center">Made with ❤️ for IBM AI Innovation Competition · ARUA AI © 2024</p>
