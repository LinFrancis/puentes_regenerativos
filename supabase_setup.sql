-- ============================================================
-- PUENTES REGENERATIVOS - Supabase Database Schema
-- ============================================================
-- Ejecutar este SQL en el SQL Editor de Supabase
-- https://app.supabase.com → SQL Editor → New Query
-- ============================================================

-- 1. PROFILES (perfiles de actores regenerativos)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    nombre TEXT NOT NULL,
    tipo_actor TEXT NOT NULL CHECK (tipo_actor IN ('persona', 'organizacion', 'colectivo', 'institucion', 'empresa_social', 'red')),
    descripcion TEXT,
    email TEXT,
    telefono TEXT,
    web TEXT,
    redes_sociales JSONB DEFAULT '{}',
    -- Ubicación
    pais TEXT,
    region TEXT,
    ciudad TEXT,
    comuna TEXT,
    direccion_exacta TEXT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    usa_centroid BOOLEAN DEFAULT FALSE,
    -- Regeneración
    dimensiones_regeneracion TEXT[] DEFAULT '{}',
    acciones JSONB DEFAULT '[]',
    interpretacion_regeneracion TEXT,
    -- Redes
    redes_participa TEXT[] DEFAULT '{}',
    ano_ingreso_red INTEGER,
    ano_inicio_regeneracion INTEGER,
    -- Impacto
    personas_impactadas TEXT,
    hectareas_regeneradas TEXT,
    -- Índice
    indice_puentes DOUBLE PRECISION DEFAULT 0,
    -- Nodo fantasma (para conexiones externas)
    es_fantasma BOOLEAN DEFAULT FALSE,
    fantasma_creado_por UUID REFERENCES auth.users(id),
    -- Timestamps
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_profiles_user_id ON profiles(user_id);
CREATE INDEX idx_profiles_pais ON profiles(pais);
CREATE INDEX idx_profiles_tipo_actor ON profiles(tipo_actor);
CREATE INDEX idx_profiles_es_fantasma ON profiles(es_fantasma);
CREATE INDEX idx_profiles_lat_lon ON profiles(lat, lon);

-- 2. CONNECTIONS (puentes entre perfiles)
CREATE TABLE IF NOT EXISTS connections (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    source_profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    target_profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    tipo_relacion TEXT NOT NULL CHECK (tipo_relacion IN ('colaboracion', 'financiamiento', 'aprendizaje', 'inspiracion')),
    intensidad INTEGER DEFAULT 1 CHECK (intensidad BETWEEN 1 AND 5),
    es_externa BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(source_profile_id, target_profile_id, tipo_relacion)
);

CREATE INDEX idx_connections_source ON connections(source_profile_id);
CREATE INDEX idx_connections_target ON connections(target_profile_id);

-- 3. IMPACT_LOCATIONS (territorios de impacto adicionales)
CREATE TABLE IF NOT EXISTS impact_locations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    pais TEXT,
    region TEXT,
    ciudad TEXT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION
);

CREATE INDEX idx_impact_locations_profile ON impact_locations(profile_id);

-- 4. MESSAGES (foro con hilos anidados)
CREATE TABLE IF NOT EXISTS messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    contenido TEXT NOT NULL,
    parent_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    fecha TIMESTAMPTZ DEFAULT NOW(),
    eliminado BOOLEAN DEFAULT FALSE,
    autor_nombre TEXT
);

CREATE INDEX idx_messages_parent ON messages(parent_id);
CREATE INDEX idx_messages_fecha ON messages(fecha DESC);

-- 5. BIBLIOGRAPHY (bibliografía editable)
CREATE TABLE IF NOT EXISTS bibliografia (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    descripcion TEXT,
    link TEXT,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact_locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE bibliografia ENABLE ROW LEVEL SECURITY;

-- PROFILES: todos pueden leer, solo dueño puede modificar
CREATE POLICY "Profiles: public read" ON profiles FOR SELECT USING (true);
CREATE POLICY "Profiles: owner insert" ON profiles FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Profiles: owner update" ON profiles FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Profiles: owner delete" ON profiles FOR DELETE USING (auth.uid() = user_id);
-- Permitir crear perfiles fantasma
CREATE POLICY "Profiles: ghost insert" ON profiles FOR INSERT WITH CHECK (
    auth.uid() = user_id OR (es_fantasma = TRUE AND auth.uid() = fantasma_creado_por)
);

-- CONNECTIONS: todos leen, creador puede modificar
CREATE POLICY "Connections: public read" ON connections FOR SELECT USING (true);
CREATE POLICY "Connections: auth insert" ON connections FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);
CREATE POLICY "Connections: auth delete" ON connections FOR DELETE USING (auth.uid() IS NOT NULL);

-- IMPACT_LOCATIONS: todos leen, perfil owner modifica
CREATE POLICY "Impact locations: public read" ON impact_locations FOR SELECT USING (true);
CREATE POLICY "Impact locations: auth insert" ON impact_locations FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);
CREATE POLICY "Impact locations: auth delete" ON impact_locations FOR DELETE USING (auth.uid() IS NOT NULL);

-- MESSAGES: todos leen, auth puede crear
CREATE POLICY "Messages: public read" ON messages FOR SELECT USING (true);
CREATE POLICY "Messages: auth insert" ON messages FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Messages: owner update" ON messages FOR UPDATE USING (auth.uid() = user_id);

-- BIBLIOGRAPHY: todos leen, auth puede crear
CREATE POLICY "Bibliography: public read" ON bibliografia FOR SELECT USING (true);
CREATE POLICY "Bibliography: auth insert" ON bibliografia FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

-- ============================================================
-- STORAGE: Bucket para imágenes de perfiles
-- ============================================================
-- Ejecutar esto en el Dashboard de Supabase → Storage → Create Bucket
-- Nombre: profiles_images
-- Public: true
-- Max file size: 5MB
-- Allowed MIME types: image/jpeg, image/png, image/webp

-- O via SQL:
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'profiles_images',
    'profiles_images',
    true,
    5242880,
    ARRAY['image/jpeg', 'image/png', 'image/webp']
) ON CONFLICT (id) DO NOTHING;

-- Storage policies
CREATE POLICY "Profile images: public read" ON storage.objects FOR SELECT USING (bucket_id = 'profiles_images');
CREATE POLICY "Profile images: auth upload" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'profiles_images' AND auth.uid() IS NOT NULL);
CREATE POLICY "Profile images: auth delete" ON storage.objects FOR DELETE USING (bucket_id = 'profiles_images' AND auth.uid() IS NOT NULL);

-- ============================================================
-- FUNCTION: Auto-update fecha_actualizacion
-- ============================================================
CREATE OR REPLACE FUNCTION update_fecha_actualizacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER profiles_updated
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_actualizacion();

-- ============================================================
-- INSERT INITIAL BIBLIOGRAPHY
-- ============================================================
INSERT INTO bibliografia (titulo, autor, descripcion, link) VALUES
('Designing from place: a regenerative framework and methodology', 'Pamela Mang & Bill Reed', 'Artículo fundacional del diseño regenerativo basado en el concepto de lugar como sistema vivo.', 'https://doi.org/10.1080/09613218.2012.621341'),
('Permacultura: Principios y senderos más allá de la sustentabilidad', 'David Holmgren', 'Obra fundamental de la permacultura con 12 principios de diseño basados en sistemas naturales.', 'https://holmgren.com.au'),
('Introducción al enfoque de la regeneración', 'Francis Mason Bustos', 'Marco conceptual para la docencia regenerativa frente a la triple crisis planetaria.', 'https://doi.org/10.17605/OSF.IO/UCDEH'),
('Diseñando Culturas Regenerativas', 'Daniel Christian Wahl', 'Transición de la sostenibilidad a la regeneración mediante preguntas significativas y diseño sistémico.', ''),
('Mandala de la Sustentabilidad y Principios de Ecoaldeas', 'Global Ecovillage Network (GEN)', '30 principios en 5 dimensiones para diseño de comunidades resilientes.', 'https://ecovillage.org/projects/dimensions-of-sustainability/'),
('COP30 Global Climate Action Agenda', 'UN Climate High-Level Champions', 'Agenda de 6 ejes temáticos y 30 objetivos clave para acción climática.', 'https://www.climatechampions.net/action-agenda/')
ON CONFLICT DO NOTHING;
