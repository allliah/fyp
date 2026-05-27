# Supabase Database Schema Setup

This file contains the SQL to set up all required tables in your Supabase database.

## Instructions:
1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy and paste each SQL block below
4. Execute them in order

---

## Table 1: Users (Enhanced)
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username VARCHAR(255) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  public_key TEXT NOT NULL,
  private_key TEXT NOT NULL,
  bio TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
```

---

## Table 2: Posts
```sql
CREATE TABLE posts (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  image BYTEA,
  encrypted_message TEXT,
  encrypted_aes_key TEXT,
  recipient_id UUID REFERENCES users(id) ON DELETE SET NULL,
  visibility VARCHAR(50) DEFAULT 'public',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_recipient_id ON posts(recipient_id);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
```

---

## Table 3: Friends
```sql
CREATE TABLE friends (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  friend_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status VARCHAR(50) DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  accepted_at TIMESTAMP,
  UNIQUE(user_id, friend_id),
  CHECK (user_id != friend_id)
);

CREATE INDEX idx_friends_user_id ON friends(user_id);
CREATE INDEX idx_friends_friend_id ON friends(friend_id);
CREATE INDEX idx_friends_status ON friends(status);
```

---

## Table 4: Encrypted Files (Steganography Storage)
```sql
CREATE TABLE encrypted_files (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  filename VARCHAR(255) NOT NULL,
  stego_image BYTEA NOT NULL,
  encrypted_message TEXT NOT NULL,
  encrypted_aes_key TEXT NOT NULL,
  recipient_id UUID REFERENCES users(id) ON DELETE SET NULL,
  file_hash VARCHAR(64),
  file_size BIGINT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  shared_with TEXT[] DEFAULT '{}',
  description TEXT
);

CREATE INDEX idx_encrypted_files_user_id ON encrypted_files(user_id);
CREATE INDEX idx_encrypted_files_recipient_id ON encrypted_files(recipient_id);
CREATE INDEX idx_encrypted_files_created_at ON encrypted_files(created_at DESC);
```

---

## Table 5: Messages (Private Direct Messages)
```sql
CREATE TABLE messages (
  id BIGSERIAL PRIMARY KEY,
  sender_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  recipient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  encrypted_content TEXT,
  is_read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_sender_id ON messages(sender_id);
CREATE INDEX idx_messages_recipient_id ON messages(recipient_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
```

---

## Row Level Security (RLS) Policies

Enable RLS on all tables:

```sql
-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE friends ENABLE ROW LEVEL SECURITY;
ALTER TABLE encrypted_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Users can read all profiles but only update their own
CREATE POLICY "users_can_read_all" ON users FOR SELECT USING (true);
CREATE POLICY "users_can_insert_own" ON users FOR INSERT WITH CHECK (auth.uid() = id);
CREATE POLICY "users_can_update_own" ON users FOR UPDATE USING (auth.uid() = id);

-- Posts are readable by public or recipient; writable only by creator
CREATE POLICY "posts_publicly_readable" ON posts FOR SELECT USING (visibility = 'public' OR user_id = auth.uid() OR recipient_id = auth.uid());
CREATE POLICY "posts_creator_can_write" ON posts FOR INSERT WITH CHECK (user_id = auth.uid());
CREATE POLICY "posts_creator_can_update" ON posts FOR UPDATE USING (user_id = auth.uid());
CREATE POLICY "posts_creator_can_delete" ON posts FOR DELETE USING (user_id = auth.uid());

-- Friends: can view own friendships
CREATE POLICY "friends_can_view_own" ON friends FOR SELECT USING (user_id = auth.uid() OR friend_id = auth.uid());
CREATE POLICY "friends_can_create" ON friends FOR INSERT WITH CHECK (user_id = auth.uid());
CREATE POLICY "friends_can_update" ON friends FOR UPDATE USING (friend_id = auth.uid() AND status = 'pending');

-- Encrypted files: owner can access their own
CREATE POLICY "encrypted_files_owner_access" ON encrypted_files FOR SELECT USING (user_id = auth.uid() OR recipient_id = auth.uid());
CREATE POLICY "encrypted_files_owner_write" ON encrypted_files FOR INSERT WITH CHECK (user_id = auth.uid());

-- Messages: only participants can view
CREATE POLICY "messages_own_access" ON messages FOR SELECT USING (sender_id = auth.uid() OR recipient_id = auth.uid());
CREATE POLICY "messages_can_send" ON messages FOR INSERT WITH CHECK (sender_id = auth.uid());
```

---

## Supabase Environment Variables

Add these to your `.env` file:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SECRET_KEY=your-flask-secret
```

Use the service role key only on the server side. Do not expose it in frontend code.

Get these from: Supabase Dashboard → Settings → API
