import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://myrpgiadvgvvujxvaaph.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im15cnBnaWFkdmd2dnVqeHZhYXBoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk1ODM5MzksImV4cCI6MjEwNTE1OTkzOX0.Q0tnzLFcMU4fKtQfjZja9C6gQrSmPeSfhG7g7d_ETFs';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
