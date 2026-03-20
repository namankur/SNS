-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Define custom enum types
CREATE TYPE user_role AS ENUM ('dear_one', 'caller');

-- Table: family_groups
CREATE TABLE family_groups (
    group_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_name TEXT,
    dear_one_id UUID, -- Will add foreign key later after users table is created
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: users
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    phone_number TEXT UNIQUE NOT NULL,
    role user_role NOT NULL,
    family_group_id UUID REFERENCES family_groups(group_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Add the delayed foreign key to family_groups
ALTER TABLE family_groups ADD CONSTRAINT fk_dear_one FOREIGN KEY (dear_one_id) REFERENCES users(user_id);

-- Table: signals
CREATE TABLE signals (
    signal_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    screen_active_last_mins INTEGER,
    movement_type TEXT, -- STILL/WALKING/IN_VEHICLE
    last_interaction_time TEXT, -- HH:MM format
    battery_level INTEGER, -- 0-100
    is_charging BOOLEAN,
    network_type TEXT, -- WIFI/MOBILE/NONE
    dnd_active BOOLEAN,
    ringer_mode TEXT DEFAULT 'NORMAL', -- NORMAL/VIBRATE/SILENT
    ringer_volume INTEGER DEFAULT 50, -- 0-100
    is_headphone_plugged BOOLEAN DEFAULT FALSE,
    ambient_light TEXT,
    phone_orientation TEXT,
    proximity TEXT,
    synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ADD COLUMN ringer_mode TEXT DEFAULT 'NORMAL',
-- ADD COLUMN ringer_volume INTEGER DEFAULT 50,
-- ADD COLUMN is_headphone_plugged BOOLEAN DEFAULT FALSE,
-- ADD COLUMN ambient_light TEXT,
-- ADD COLUMN phone_orientation TEXT,
-- ADD COLUMN proximity TEXT;
-- ALTER TABLE signals DROP COLUMN IF EXISTS wifi_ssid, DROP COLUMN IF EXISTS last_app_used, DROP COLUMN IF EXISTS app_category;

-- Table: routine_profiles
CREATE TABLE routine_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(user_id),
    wake_time_avg TEXT, -- HH:MM
    wake_time_variance_mins INTEGER,
    nap_window_start TEXT, -- HH:MM
    nap_window_end TEXT, -- HH:MM
    sleep_time_avg TEXT, -- HH:MM
    walk_days TEXT[], -- ["MON","WED","FRI"]
    walk_time_avg TEXT, -- HH:MM
    hourly_activity_baseline JSONB, -- {0: 0.1, 1: 0.0, ...23: 0.8}
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    days_of_data INTEGER DEFAULT 0
);

-- Table: check_requests
CREATE TABLE check_requests (
    request_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    caller_id UUID REFERENCES users(user_id) NOT NULL,
    dear_one_id UUID REFERENCES users(user_id) NOT NULL,
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    response_generated TEXT,
    deviation_score FLOAT,
    tier TEXT -- free/premium
);

-- Table: caller_dear_one_links
CREATE TABLE caller_dear_one_links (
    link_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    caller_id UUID REFERENCES users(user_id) NOT NULL,
    dear_one_id UUID REFERENCES users(user_id) NOT NULL,
    nickname TEXT, -- "Maa", "Papa", "Dadi"
    linked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);
