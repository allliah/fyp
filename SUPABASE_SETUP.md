# Supabase Database Schema Setup

This file contains the SQL to set up all required tables in the Supabase database.

## Instructions:
1. Go to the Supabase project dashboard
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


## Supabase Environment Variables

Add these to `.env` file:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SECRET_KEY=your-flask-secret
```

Use the service role key only on the server side. Do not expose it in frontend code.

Get these from: Supabase Dashboard → Settings → API
