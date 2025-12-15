-- Create Events Table
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    title TEXT,
    type TEXT,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Resources Table
CREATE TABLE IF NOT EXISTS resources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    capacity INTEGER DEFAULT 0,
    specialization TEXT,
    count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Allocations Table
CREATE TABLE IF NOT EXISTS allocations (
    id TEXT PRIMARY KEY, -- Changed from BIGINT GENERATED to TEXT to match "A1", "A2" format
    event_id TEXT REFERENCES events(id) ON DELETE CASCADE,
    resource_id TEXT REFERENCES resources(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policies
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE allocations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public access to events" ON events FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public access to resources" ON resources FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public access to allocations" ON allocations FOR ALL USING (true) WITH CHECK (true);
