-- Create Deletion Requests Table
-- CREATE TABLE IF NOT EXISTS deletion_requests (
--     id TEXT PRIMARY KEY,
--     event_id TEXT REFERENCES events(id) ON DELETE CASCADE,
--     requested_by TEXT REFERENCES users(id) ON DELETE CASCADE,
--     status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
-- );

-- Enable RLS
-- ALTER TABLE deletion_requests ENABLE ROW LEVEL SECURITY;

-- CREATE POLICY "Allow public access to deletion_requests" ON deletion_requests FOR ALL USING (true) WITH CHECK (true);

-- Create Archived Events Table
CREATE TABLE IF NOT EXISTS archived_events (
    id TEXT PRIMARY KEY,
    original_id TEXT,
    title TEXT,
    type TEXT,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    description TEXT,
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS for archived_events
ALTER TABLE archived_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public access to archived_events" ON archived_events FOR ALL USING (true) WITH CHECK (true);
