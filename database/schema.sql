-- ============================================================
-- ARUA AI - Supabase PostgreSQL Schema
-- Run this in your Supabase SQL Editor to set up all tables
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- PROFILES TABLE
-- Extends Supabase auth.users with application data
-- ============================================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id            UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id       UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    username      TEXT NOT NULL UNIQUE,
    email         TEXT,
    bio           TEXT DEFAULT '',
    avatar_url    TEXT,
    role          TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin', 'moderator')),
    ai_credits      INTEGER DEFAULT 100 CHECK (ai_credits >= 0),
    last_credit_refill TIMESTAMPTZ,
    total_generated INTEGER DEFAULT 0,
    storage_used  BIGINT DEFAULT 0,
    last_login    TIMESTAMPTZ,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON public.profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_profiles_username ON public.profiles(username);

-- ============================================================
-- GENERATED IMAGES TABLE
-- Stores metadata for every AI-generated image
-- ============================================================
CREATE TABLE IF NOT EXISTS public.generated_images (
    id               UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id          UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    collection_id    UUID,
    prompt           TEXT NOT NULL,
    enhanced_prompt  TEXT,
    negative_prompt  TEXT DEFAULT '',
    style            TEXT DEFAULT 'realistic',
    category         TEXT DEFAULT 'general',
    model            TEXT DEFAULT 'flux',
    aspect_ratio     TEXT DEFAULT '1:1',
    resolution       TEXT DEFAULT 'hd',
    width            INTEGER DEFAULT 1024,
    height           INTEGER DEFAULT 1024,
    seed             BIGINT,
    image_url        TEXT NOT NULL,
    storage_path     TEXT,
    is_favorite      BOOLEAN DEFAULT FALSE,
    is_public        BOOLEAN DEFAULT FALSE,
    downloads        INTEGER DEFAULT 0,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for gallery queries
CREATE INDEX IF NOT EXISTS idx_images_user_id     ON public.generated_images(user_id);
CREATE INDEX IF NOT EXISTS idx_images_created_at  ON public.generated_images(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_images_is_favorite ON public.generated_images(is_favorite);
CREATE INDEX IF NOT EXISTS idx_images_style       ON public.generated_images(style);
CREATE INDEX IF NOT EXISTS idx_images_collection  ON public.generated_images(collection_id);

-- Full-text search on prompt
CREATE INDEX IF NOT EXISTS idx_images_prompt_fts ON public.generated_images
    USING gin(to_tsvector('english', prompt));

-- ============================================================
-- COLLECTIONS TABLE
-- User-created folders for organizing images
-- ============================================================
CREATE TABLE IF NOT EXISTS public.collections (
    id           UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id      UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name         TEXT NOT NULL,
    description  TEXT DEFAULT '',
    cover_image  TEXT,
    image_count  INTEGER DEFAULT 0,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    updated_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_collections_user_id ON public.collections(user_id);

-- Add collection FK to images after collections table exists
ALTER TABLE public.generated_images
    ADD CONSTRAINT fk_images_collection
    FOREIGN KEY (collection_id) REFERENCES public.collections(id) ON DELETE SET NULL
    NOT VALID;

-- ============================================================
-- PROMPT HISTORY TABLE
-- Tracks all prompt enhancement requests
-- ============================================================
CREATE TABLE IF NOT EXISTS public.prompt_history (
    id               UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id          UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    original_prompt  TEXT NOT NULL,
    enhanced_prompt  TEXT,
    style            TEXT,
    category         TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_prompt_history_user ON public.prompt_history(user_id);
CREATE INDEX IF NOT EXISTS idx_prompt_history_date ON public.prompt_history(created_at DESC);

-- ============================================================
-- IMAGE VERSIONS TABLE
-- Version history for edited images
-- ============================================================
CREATE TABLE IF NOT EXISTS public.image_versions (
    id                UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    original_image_id UUID REFERENCES public.generated_images(id) ON DELETE CASCADE,
    user_id           UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    version_url       TEXT,
    edits_applied     JSONB DEFAULT '{}',
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_versions_image_id ON public.image_versions(original_image_id);
CREATE INDEX IF NOT EXISTS idx_versions_user_id  ON public.image_versions(user_id);

-- ============================================================
-- ACTIVITY LOGS TABLE
-- Tracks user actions for dashboard timeline
-- ============================================================
CREATE TABLE IF NOT EXISTS public.activity_logs (
    id         UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    action     TEXT NOT NULL,
    details    TEXT,
    metadata   JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_activity_user_id  ON public.activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_created  ON public.activity_logs(created_at DESC);

-- Cleanup old activity (keep last 1000 per user)
-- Run this periodically via cron or Supabase scheduled functions:
-- DELETE FROM activity_logs WHERE id IN (
--   SELECT id FROM (
--     SELECT id, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) as rn
--     FROM activity_logs
--   ) sub WHERE rn > 1000
-- );

-- ============================================================
-- VIDEOS TABLE
-- Stores AI video creation records (scene images rendered client-side)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.videos (
    id               UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id          UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    prompt           TEXT NOT NULL,
    enhanced_prompt  TEXT,
    style            TEXT DEFAULT 'cinematic',
    category         TEXT DEFAULT 'general',
    model            TEXT DEFAULT 'flux',
    aspect_ratio     TEXT DEFAULT '16:9',
    resolution       TEXT DEFAULT 'hd',
    num_scenes       INTEGER DEFAULT 3,
    scene_duration   NUMERIC DEFAULT 3,
    scene_images     JSONB DEFAULT '[]',
    downloads        INTEGER DEFAULT 0,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_videos_user_id    ON public.videos(user_id);
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON public.videos(created_at DESC);

-- ============================================================
-- PROJECTS TABLE
-- Stores AI-generated project bundles (logos, brand kits, etc.)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.projects (
    id           UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id      UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title        TEXT NOT NULL,
    project_type TEXT NOT NULL,
    prompt       TEXT,
    assets       JSONB DEFAULT '[]',
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_projects_user_id     ON public.projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_created_at  ON public.projects(created_at DESC);

-- ============================================================
-- DOWNLOADS TABLE
-- Track image download events for analytics
-- ============================================================
CREATE TABLE IF NOT EXISTS public.downloads (
    id         UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    image_id   UUID REFERENCES public.generated_images(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_downloads_user_id ON public.downloads(user_id);
CREATE INDEX IF NOT EXISTS idx_downloads_image_id ON public.downloads(image_id);

-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- Users can only access their own data
-- ============================================================

-- Enable RLS on all tables
ALTER TABLE public.profiles          ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.generated_images  ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.collections       ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.prompt_history    ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.image_versions    ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_logs     ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.downloads         ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.videos            ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects          ENABLE ROW LEVEL SECURITY;

-- PROFILES: Users can read/update their own profile
CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Service role can do anything (for backend)
CREATE POLICY "Service role full access profiles"
    ON public.profiles FOR ALL
    USING (auth.role() = 'service_role');

-- GENERATED IMAGES: Users see only their own images
CREATE POLICY "Users can manage own images"
    ON public.generated_images FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Service role full access images"
    ON public.generated_images FOR ALL
    USING (auth.role() = 'service_role');

-- Public images are viewable by all
CREATE POLICY "Public images are viewable"
    ON public.generated_images FOR SELECT
    USING (is_public = TRUE);

-- COLLECTIONS: Users manage own collections
CREATE POLICY "Users can manage own collections"
    ON public.collections FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Service role full access collections"
    ON public.collections FOR ALL
    USING (auth.role() = 'service_role');

-- PROMPT HISTORY: User's own history only
CREATE POLICY "Users can view own prompt history"
    ON public.prompt_history FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Service role full access prompt history"
    ON public.prompt_history FOR ALL
    USING (auth.role() = 'service_role');

-- IMAGE VERSIONS: User's own versions only
CREATE POLICY "Users can manage own versions"
    ON public.image_versions FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Service role full access versions"
    ON public.image_versions FOR ALL
    USING (auth.role() = 'service_role');

-- ACTIVITY LOGS
CREATE POLICY "Users can view own activity"
    ON public.activity_logs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Service role full access activity"
    ON public.activity_logs FOR ALL
    USING (auth.role() = 'service_role');

-- DOWNLOADS
CREATE POLICY "Users can view own downloads"
    ON public.downloads FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Service role full access downloads"
    ON public.downloads FOR ALL
    USING (auth.role() = 'service_role');

-- VIDEOS
CREATE POLICY "Users can manage own videos"
    ON public.videos FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Service role full access videos"
    ON public.videos FOR ALL
    USING (auth.role() = 'service_role');

-- PROJECTS
CREATE POLICY "Users can manage own projects"
    ON public.projects FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Service role full access projects"
    ON public.projects FOR ALL
    USING (auth.role() = 'service_role');

-- ============================================================
-- FUNCTIONS & TRIGGERS
-- Automatic profile creation and timestamp updates
-- ============================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_profiles_timestamp
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER update_collections_timestamp
    BEFORE UPDATE ON public.collections
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

-- Auto-create profile on new auth user
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
    _username TEXT;
BEGIN
    -- Use metadata username or derive from email
    _username := COALESCE(
        NEW.raw_user_meta_data->>'username',
        SPLIT_PART(NEW.email, '@', 1)
    );

    -- Ensure username uniqueness
    IF EXISTS (SELECT 1 FROM public.profiles WHERE username = _username) THEN
        _username := _username || '_' || SUBSTRING(NEW.id::TEXT, 1, 6);
    END IF;

    INSERT INTO public.profiles (user_id, username, email, ai_credits, role)
    VALUES (
        NEW.id,
        _username,
        NEW.email,
        100,
        'user'
    )
    ON CONFLICT (user_id) DO NOTHING;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger: Create profile when new user signs up
CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================================
-- STORAGE BUCKETS
-- Create storage buckets for images and avatars
-- (Run in Supabase dashboard or via API)
-- ============================================================

-- INSERT INTO storage.buckets (id, name, public)
-- VALUES ('arua-generated', 'arua-generated', TRUE)
-- ON CONFLICT (id) DO NOTHING;

-- INSERT INTO storage.buckets (id, name, public)
-- VALUES ('arua-avatars', 'arua-avatars', TRUE)
-- ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- SEED DATA (Optional - creates test admin user)
-- ============================================================

-- To create an admin user, first sign up normally via the app,
-- then run:
-- UPDATE public.profiles SET role = 'admin'
-- WHERE email = 'your-email@example.com';

-- ============================================================
-- VERIFICATION QUERIES
-- Run these to verify setup is correct
-- ============================================================
-- SELECT tablename FROM pg_tables WHERE schemaname = 'public';
-- SELECT policyname, tablename FROM pg_policies WHERE schemaname = 'public';
