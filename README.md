🎨 ARUA AI

One Platform. Unlimited Creative Possibilities.

IBM AI Builders Challenge 2026 — July Challenge
Challenge Theme: Reimagine Creative Industries with AI

""Live Demo" (https://arua-ai.vercel.app)
""Backend API" (https://arua-ai.onrender.com)
""GitHub Repository"  (https://github.com/muthukugee5-code/ARUA-AI)

---

📌 Project Overview

ARUA AI is an AI-powered creative production platform that allows users to generate, edit, organize, and manage AI-created visual content from one intelligent workspace.

The platform combines more than 30 creative generators, multiple visual styles, prompt-enhancement tools, image-editing features, image upscaling, background removal, collections, favorites, prompt history, and asset management.

Instead of requiring creators to use multiple disconnected applications for image generation, logo creation, UI design, image editing, background removal, upscaling, and creative asset organization, ARUA AI brings these capabilities together in one complete platform.

ARUA AI is designed for:

- Graphic designers
- Digital artists
- Students
- Content creators
- Social media managers
- Marketing teams
- UI/UX designers
- Developers
- Freelancers
- Independent creators
- Startup teams
- Small businesses

ARUA AI was developed for the IBM AI Builders Challenge 2026 — July Challenge: Reimagine Creative Industries with AI, with IBM Bob used as the primary AI-assisted development tool throughout planning, development, debugging, testing, deployment, and documentation.

---

🎯 Selected Challenge Theme

Reimagine Creative Industries with AI

The July Challenge explores how artificial intelligence can transform the way people create content, design experiences, communicate ideas, and bring creative concepts to life.

ARUA AI directly addresses this challenge by providing an intelligent creative environment where users can generate and refine professional digital assets using AI-assisted tools.

The platform focuses on:

- AI-powered image generation
- AI-assisted prompt enhancement
- Digital art creation
- Graphic design automation
- UI and UX concept generation
- Logo and brand identity creation
- Image editing and enhancement
- Creative asset organization
- Marketing content creation
- Accessible creative production

ARUA AI demonstrates how artificial intelligence can act as a complete creative production partner rather than functioning only as a basic image generator.

---

❗ Problem Statement

Creating professional visual content often requires several different applications, technical skills, paid subscriptions, and design tools.

A creator may need separate platforms to:

- Generate AI images
- Improve creative prompts
- Create logos
- Design user interfaces
- Produce posters and banners
- Remove image backgrounds
- Upscale image quality
- Apply image filters
- Organize generated content
- Save prompt history
- Manage creative collections
- Produce brand assets
- Create social media graphics

Switching between disconnected tools makes the creative process time-consuming, expensive, and difficult to manage.

Many professional creative platforms also require:

- Paid subscriptions
- High-performance computers
- Advanced design knowledge
- Complex software installation
- Multiple user accounts
- Separate cloud-storage services

Students, independent creators, freelancers, and small teams may not have access to all these resources.

The challenge is therefore not simply:

«How can AI generate an image?»

The larger challenge is:

«How can AI support the complete creative workflow—from idea development and prompt enhancement to image generation, editing, organization, and final asset management?»

---

💡 Solution Description

ARUA AI introduces a unified AI-powered creative production workflow.

The user begins by selecting a creative generator, entering an idea, choosing a visual style, and configuring the desired output.

ARUA AI processes the request through its AI services, generates the visual asset, and provides tools for editing, enhancing, saving, organizing, and managing the generated content.

                         USER IDEA
                             │
                             ▼
                    SELECT CREATIVE TOOL
                             │
                             ▼
                       ENTER PROMPT
                             │
                             ▼
                    SMART PROMPT AI
                             │
                             ▼
                    SELECT ART STYLE
                             │
                             ▼
                   AI IMAGE GENERATION
                             │
                             ▼
                    IMAGE ENHANCEMENT
                             │
               ┌─────────────┼─────────────┐
               ▼             ▼             ▼
          IMAGE EDITOR    AI UPSCALER   BACKGROUND
                                         REMOVER
               │             │             │
               └─────────────┼─────────────┘
                             ▼
                    SAVE AND ORGANIZE
                             │
                             ▼
                   FINAL CREATIVE ASSET

The platform allows users to manage the complete creative process from one premium dashboard.

---

🧠 AI Approach and Architecture

ARUA AI uses a service-based AI architecture.

Instead of placing all AI functionality inside one large component, the platform separates:

- Frontend user experience
- Backend API services
- AI provider integration
- Prompt enhancement
- Image generation
- Image processing
- Authentication
- Database operations
- Cloud storage
- Creative asset management

The core AI workflow includes:

1. User prompt processing
2. AI-assisted prompt enhancement
3. Creative category selection
4. Style configuration
5. Image generation
6. Image processing
7. Asset storage
8. Gallery management
9. Version history
10. Collection management

Core Principle

AI Generation
      +
Prompt Intelligence
      +
Image Processing
      +
Creative Asset Management
      =
Complete AI Creative Platform

The provider-based architecture allows AI services to be configured or replaced without redesigning the complete application.

---

🔄 AI Creative Workflow

Step 1 — User Authentication

The user creates an account or signs in securely through the ARUA AI authentication system.

Step 2 — Creative Tool Selection

The user selects one of the available creative generators, such as:

- AI Image Generator
- Logo Generator
- UI/UX Designer
- Anime Studio
- Poster Designer
- 3D Studio
- Social Media Designer
- Product Mockup Generator
- Brand Kit Generator

Step 3 — Prompt Input

The user enters a creative idea or description.

Example:

«Create a futuristic cyberpunk city with neon streets, flying vehicles, cinematic lighting, and realistic reflections.»

Step 4 — Smart Prompt Enhancement

The Smart Prompt AI improves the original prompt by adding useful creative details, including:

- Lighting
- Composition
- Camera angle
- Visual quality
- Color direction
- Artistic style
- Environmental details
- Rendering details

Step 5 — Style Selection

The user selects a preferred visual style, such as:

- Realistic
- Anime
- Manga
- Cinematic
- Fantasy
- Cyberpunk
- Watercolor
- Oil painting
- Pixel art
- Minimal
- Luxury
- Concept art

Step 6 — AI Image Generation

The backend sends the enhanced prompt and selected configuration to the configured AI image-generation service.

Step 7 — Image Processing

The generated image can be processed using built-in tools, including:

- Brightness adjustment
- Contrast adjustment
- Saturation adjustment
- Blur
- Sharpening
- Filters
- Upscaling
- Background removal

Step 8 — Save and Organize

The user can:

- Save generated images
- Add images to favorites
- Create collections
- Reuse previous prompts
- View prompt history
- Manage edited versions
- Download completed assets

Step 9 — Final Creative Output

The completed creative asset is displayed in the ARUA AI workspace and stored in the user’s personal gallery.

---

🏗️ System Architecture

┌─────────────────────────────────────────────┐
│                    USER                     │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│                WEB FRONTEND                 │
│                                             │
│  Landing Page                               │
│  Authentication                            │
│  Dashboard                                 │
│  AI Generation Workspace                   │
│  Image Editor                              │
│  Gallery                                   │
│  Collections                               │
│  User Profile                              │
│  Admin Panel                               │
└─────────────────────┬───────────────────────┘
                      │
                      │ REST API
                      ▼
┌─────────────────────────────────────────────┐
│               FLASK BACKEND                 │
│                                             │
│  Authentication API                        │
│  Image Generation API                      │
│  Prompt Enhancement                        │
│  Gallery Management                        │
│  Collection Management                     │
│  Profile Management                        │
│  Image Editor API                          │
│  Admin Services                            │
└──────────────┬──────────────┬───────────────┘
               │              │
               ▼              ▼
┌──────────────────────┐  ┌──────────────────┐
│     AI PROVIDERS     │  │ IMAGE PROCESSING │
│                      │  │                  │
│  Pollinations AI     │  │ Pillow           │
│  Hugging Face        │  │ Filters          │
│  Flux Model          │  │ Upscaling        │
│  Mixtral Model       │  │ Background Tools │
└───────────┬──────────┘  └─────────┬────────┘
            │                       │
            └───────────┬───────────┘
                        ▼
┌─────────────────────────────────────────────┐
│                  SUPABASE                   │
│                                             │
│  PostgreSQL Database                       │
│  Authentication                            │
│  Image Storage                             │
│  User Profiles                             │
│  Generated Assets                          │
│  Collections                               │
│  Prompt History                            │
└─────────────────────────────────────────────┘

---

🛠️ Technology Stack

Frontend

- HTML5
- CSS3
- JavaScript ES6
- GSAP
- AOS
- Chart.js
- Font Awesome
- REST API integration
- Responsive web interface

Backend

- Python
- Flask
- Flask-CORS
- Gunicorn
- REST API
- JWT authentication
- Environment-based configuration

Artificial Intelligence

- Pollinations AI
- Flux image-generation model
- Hugging Face Inference API
- Mixtral prompt-enhancement model
- Provider-based AI integration

Image Processing

- Pillow
- Image filters
- Image enhancement
- Image resizing
- Lanczos upscaling
- Background-processing tools

Database and Storage

- Supabase
- PostgreSQL
- Supabase Authentication
- Supabase Storage
- Row Level Security
- User-specific data management

Development and Deployment Tools

- IBM Bob
- Visual Studio Code
- Git
- GitHub
- Vercel
- Render
- Supabase
- Postman

---

🔷 How IBM Bob Was Used

IBM Bob was used as the primary AI-assisted development tool during the development of ARUA AI.

IBM Bob supported multiple stages of the software development lifecycle.

Codebase Understanding

IBM Bob was used to inspect and understand the complete project structure, including:

- Frontend pages
- Backend services
- API routes
- Authentication
- Database integration
- AI provider integration
- Image-processing utilities
- Application configuration

Planning

IBM Bob assisted in creating implementation plans before making changes to complex sections of the project.

This helped preserve the original project concept and architecture while improving functionality and integration.

Frontend Development

IBM Bob supported the development and refinement of:

- Landing page
- Login page
- Registration page
- Dashboard
- AI generation workspace
- Image gallery
- Collections
- Image editor
- User profile
- Admin dashboard
- Responsive layouts

Backend Development

IBM Bob assisted with:

- Flask application structure
- REST API implementation
- Authentication endpoints
- AI generation services
- Prompt enhancement
- Gallery services
- Collection management
- Profile APIs
- Administrator functionality

AI Integration

IBM Bob supported the integration and refinement of:

- Pollinations AI
- Flux image generation
- Hugging Face APIs
- Prompt enhancement
- AI service error handling
- Generated-image processing

Database Integration

IBM Bob assisted with:

- Supabase configuration
- PostgreSQL database schema
- Authentication integration
- Storage bucket configuration
- User profile management
- Row Level Security policies

Debugging

IBM Bob was used to investigate and resolve issues involving:

- Frontend-to-backend communication
- API endpoint errors
- CORS configuration
- Authentication failures
- Deployment settings
- Environment variables
- Image loading
- Responsive UI alignment
- Database operations

UI/UX Refinement

IBM Bob helped improve the visual consistency and usability of ARUA AI while preserving the project’s original creative concept and technical architecture.

Testing and Validation

IBM Bob supported:

- API testing
- Authentication testing
- AI generation testing
- Frontend integration testing
- Deployment validation
- Error investigation
- Responsive design inspection

This demonstrates the use of IBM Bob not only for isolated code generation, but as an AI-assisted development partner across understanding, planning, development, debugging, testing, deployment, and documentation.

---

🎓 IBM SkillsBuild Learning

As part of the IBM AI Builders Challenge learning requirement, the required IBM SkillsBuild learning activity was completed.

Completed Learning Activity

How IBM Bob and AI Tools Are Changing the Way Solutions Are Built

This IBM SkillsBuild learning activity introduced how IBM Bob and other AI-assisted development tools are transforming modern software development workflows.

The activity covered how AI tools can support:

- Solution planning
- Code understanding
- Software development
- Debugging
- Testing
- Documentation
- Productivity improvement

The completion certificate has been retained as proof and will be submitted through the official IBM AI Builders Challenge platform as required.

---

✨ Key Features

- More than 30 AI creative generators
- More than 25 creative styles
- AI-powered image generation
- Smart prompt enhancement
- AI image editor
- Image upscaling
- Background removal
- User authentication
- Personal user dashboard
- Generated-image gallery
- Favorite-image management
- Creative collections
- Prompt library
- Prompt history
- Version history
- Brand kit generation
- User profile management
- Admin dashboard
- Responsive user interface
- Cloud database integration
- Cloud image storage
- REST API architecture
- Secure user-specific data access

---

🎨 AI Creative Generators

Digital Art

- AI Image Generator
- Anime Studio
- Manga Generator
- Character Designer
- Fantasy Art Generator
- Concept Art Generator
- Wallpaper Generator
- Pixel Art Generator

UI and Product Design

- UI/UX Designer
- Mobile App UI Generator
- Website UI Generator
- Dashboard UI Generator
- Product Design Generator
- Product Mockup Generator

Branding and Marketing

- Logo Generator
- Brand Kit Generator
- Business Card Generator
- Poster Designer
- Banner Generator
- Flyer Generator
- Social Media Designer
- Instagram Post Generator
- YouTube Thumbnail Generator

Media and Entertainment

- 3D Studio
- Book Cover Generator
- Album Cover Generator
- Sticker Generator
- Icon Generator
- Vehicle Concept Generator
- Fashion Design Generator
- Interior Design Generator
- Architecture Generator

---

🖌️ Available AI Styles

ARUA AI supports multiple creative styles, including:

- Realistic
- Hyper-realistic
- Anime
- Manga
- Pixar-inspired
- Disney-inspired
- Cartoon
- Watercolor
- Oil painting
- Pencil sketch
- Digital painting
- Pixel art
- Fantasy
- Cyberpunk
- Science fiction
- Gothic
- HDR
- Cinematic
- Clay
- Low poly
- Isometric
- Luxury
- Minimal
- Concept art
- Illustration

---

💎 Creative Features

Feature| Description
Smart Prompt AI| Enhances user prompts with lighting, composition, artistic style, camera direction, and quality details
AI Image Generator| Produces creative visual content from natural-language descriptions
Image Editor| Adjusts brightness, contrast, saturation, blur, sharpening, and filters
AI Upscaler| Improves image dimensions and visual quality using high-quality resampling
Background Remover| Removes image backgrounds for design and marketing use
Version History| Stores edited versions without replacing the original asset
Collections| Organizes generated images into custom folders
Prompt Library| Saves, searches, and reuses successful creative prompts
Favorites| Allows users to mark and quickly access preferred images
Brand Kit| Supports the creation of coordinated brand identity concepts
Prompt History| Tracks previous creative prompts and generation requests
Admin Dashboard| Provides platform statistics and user-management controls

---

📁 Project Structure

ARUA-AI/
│
├── backend/
│   ├── app.py
│   │
│   ├── api/
│   │   ├── auth.py
│   │   ├── generate.py
│   │   ├── gallery.py
│   │   ├── collections.py
│   │   ├── profile.py
│   │   ├── editor.py
│   │   └── admin.py
│   │
│   └── utils/
│       ├── supabase_client.py
│       ├── auth_middleware.py
│       └── image_utils.py
│
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── workspace.html
│   ├── gallery.html
│   ├── collections.html
│   ├── editor.html
│   ├── profile.html
│   ├── admin.html
│   │
│   ├── styles/
│   │   ├── main.css
│   │   └── landing.css
│   │
│   └── scripts/
│       ├── core.js
│       └── generator.js
│
├── database/
│   └── schema.sql
│
├── screenshots/
├── uploads/
├── .env.example
├── .gitignore
├── requirements.txt
├── render.yaml
├── vercel.json
├── LICENSE
└── README.md

---

🚀 Getting Started

Prerequisites

Install the following:

- Git
- Python 3.11 or later
- pip
- A modern web browser
- Visual Studio Code
- A Supabase account

---

📥 Clone the Repository

git clone https://github.com/muthukugee5-code/ARUA-AI.git
cd ARUA-AI

---

⚙️ Backend Setup

Create a Python virtual environment:

python -m venv venv

Windows PowerShell

.\venv\Scripts\Activate.ps1

Windows Command Prompt

venv\Scripts\activate

Linux or macOS

source venv/bin/activate

Install the required dependencies:

pip install -r requirements.txt

Create the environment file:

.env.example → .env

Add the required configuration values to the ".env" file.

Navigate to the backend:

cd backend

Start the Flask application:

python app.py

The local backend will run at:

http://localhost:5000

The local API base URL is:

http://localhost:5000/api

---

🗄️ Supabase Setup

Step 1 — Create a Supabase Project

Create a new project using the Supabase dashboard.

Step 2 — Configure the Database

Open the Supabase SQL Editor and run the complete contents of:

database/schema.sql

Step 3 — Create Storage Buckets

Create the following storage buckets:

arua-generated
arua-avatars

Con
