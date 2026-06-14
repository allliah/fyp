# Complete Supabase & Flask Setup Guide

## 🔧 Step 1: Set Up Supabase

### 1.1 Create Project
1. Go to [supabase.com](https://supabase.com) and sign up
2. Create a new project
3. Choose PostgreSQL database
4. Note your **Project URL** and **Anon Key**

### 1.2 Create Database Tables
1. Go to **SQL Editor** in your Supabase dashboard
2. Copy the entire contents of `SUPABASE_SETUP.md` (all SQL blocks)
3. Execute each SQL block in order
4. Wait for all tables to be created successfully

### 1.3 Enable Row Level Security (RLS)
The SQL blocks in SUPABASE_SETUP.md already include RLS policies. Verify they're enabled:
1. Go to **Authentication** → **Policies**
2. Ensure all tables have RLS enabled
3. Verify policies are applied

---

## 📁 Step 2: Update Environment Variables

Create a `.env` file in your project root:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here

# Flask
SECRET_KEY=your-unique-secret-key-here
FLASK_ENV=development
```

**Where to get these values:**
- `SUPABASE_URL`: Supabase Dashboard → Settings → API → Project URL
- `SUPABASE_KEY`: Supabase Dashboard → Settings → API → Anon Public Key
- `SECRET_KEY`: Generate any random string (use `python -c "import secrets; print(secrets.token_hex(32))"`)

---

## 🚀 Step 3: Run Your Application

### 3.1 Install Dependencies
```bash
pip install -r requirements.txt
```

### 3.2 Start Flask Server
```bash
python app.py
```

Server will run at: `http://localhost:5000`

---
