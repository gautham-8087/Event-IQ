-- Drop existing policy just in case
DROP POLICY IF EXISTS "Allow public access to events" ON events;
DROP POLICY IF EXISTS "Enable delete for authenticated users only" ON events;

-- Create a permissive policy for testing
CREATE POLICY "Enable all access for all users" ON events FOR ALL USING (true) WITH CHECK (true);
