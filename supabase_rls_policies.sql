-- RLS Policies for Knowledge GPT Backend
-- This script creates the necessary Row Level Security policies to allow your backend to function

-- =======================
-- SEARCHES TABLE POLICIES
-- =======================

-- Allow service role to do everything with searches
CREATE POLICY "Service role can manage searches" ON public.searches
FOR ALL 
TO service_role
USING (true)
WITH CHECK (true);

-- Optional: Allow authenticated users to read their own searches
-- (uncomment if you add user authentication later)
-- CREATE POLICY "Users can read own searches" ON public.searches
-- FOR SELECT 
-- TO authenticated
-- USING (auth.uid() = user_id);

-- =======================
-- PEOPLE TABLE POLICIES  
-- =======================

-- Allow service role to manage people records
CREATE POLICY "Service role can manage people" ON public.people
FOR ALL
TO service_role  
USING (true)
WITH CHECK (true);

-- Optional: Allow authenticated users to read people from their searches
-- (uncomment if you add user authentication later)
-- CREATE POLICY "Users can read people from their searches" ON public.people
-- FOR SELECT
-- TO authenticated
-- USING (
--   EXISTS (
--     SELECT 1 FROM public.searches 
--     WHERE searches.id = people.search_id 
--     AND searches.user_id = auth.uid()
--   )
-- );

-- =======================
-- EXCLUSIONS TABLE POLICIES
-- =======================

-- Allow service role to manage exclusions
CREATE POLICY "Service role can manage exclusions" ON public.exclusions
FOR ALL
TO service_role
USING (true) 
WITH CHECK (true);

-- =======================
-- USERS TABLE POLICIES (if you use it later)
-- =======================

-- Allow users to read their own profile
CREATE POLICY "Users can read own profile" ON public.users
FOR SELECT
TO authenticated
USING (auth.uid() = id);

-- Allow users to update their own profile  
CREATE POLICY "Users can update own profile" ON public.users
FOR UPDATE
TO authenticated
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- Allow service role to manage users
CREATE POLICY "Service role can manage users" ON public.users
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- =======================
-- VERIFICATION
-- =======================

-- Check that RLS is enabled on all tables
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('searches', 'people', 'users', 'exclusions')
ORDER BY tablename;

-- Check all policies
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE schemaname = 'public'
ORDER BY tablename, policyname;