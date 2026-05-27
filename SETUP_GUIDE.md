# Complete Supabase & Flask Setup Guide

## 📋 Overview

Your FYP social steganography platform now includes:
- ✅ User authentication (signup/login)
- ✅ User profiles with bio and avatar
- ✅ Friends management system
- ✅ Public feed with encrypted posts
- ✅ Direct messaging (encrypted)
- ✅ Encrypted file storage with steganography
- ✅ RSA + AES hybrid encryption

---

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

Make sure your `requirements.txt` includes:
```
flask
supabase
python-dotenv
tensorflow
pillow
cryptography
numpy
```

### 3.2 Start Flask Server
```bash
python app.py
```

Server will run at: `http://localhost:5000`

---

## 📱 Step 4: Using the Features

### 4.1 Create Account & Login
1. Go to `http://localhost:5000`
2. Click **Sign Up**
3. Enter email, username, password
4. Your RSA key pair is automatically generated and stored

### 4.2 Manage Friends

#### Add a Friend
```javascript
// Via API
fetch('/api/friends/add', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: 'friend_username'})
})
```

#### View Friend Requests
```javascript
fetch('/api/friends/pending')
    .then(r => r.json())
    .then(requests => console.log(requests))
```

#### Accept Friend Request
```javascript
fetch('/api/friends/accept', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({friend_id: 'friend_user_id'})
})
```

#### List Your Friends
```javascript
fetch('/api/friends/list')
    .then(r => r.json())
    .then(friends => console.log(friends))
```

### 4.3 Public Posts
1. Go to **Feed** page
2. Create a post with optional image
3. Click **Post**
4. Posts appear in feed for all users

### 4.4 Encrypted Posts (Steganography)

**For sending a secret message to a friend:**

1. Go to **Feed**
2. Enter your message in "Secret Message"
3. Select recipient from dropdown
4. Upload an image (optional - for steganography)
5. Click **Send Secret**

**Process:**
- Message is encrypted with AES-256
- AES key is encrypted with recipient's RSA public key
- If image provided, encrypted message is hidden in image using steganography
- Recipient can only decrypt if they have the private key

### 4.5 Direct Messages
1. Go to **Messages**
2. Click a friend name
3. Type message and send
4. Messages are encrypted and stored in database
5. Both users can view conversation

### 4.6 Encrypted Files
1. Go to **Encrypted Files**
2. View all your encrypted communications
3. Click "View & Decrypt" to read encrypted messages
4. System automatically handles decryption with your private key

### 4.7 User Profile
1. Click your username or profile link
2. View/edit bio
3. See your friends and posts
4. Visit other users' public profiles

---

## 🔐 Security Architecture

### Encryption Flow

```
User Message
    ↓
[AES-256 Encryption] ← Random AES Key (32 bytes)
    ↓
Encrypted Message
    ↓
[Optional Steganography] ← Hide in Cover Image
    ↓
[RSA-2048 Encrypt AES Key] ← Recipient's Public Key
    ↓
Store in Database
    ↓
Send to Recipient
    ↓
Recipient Decrypts:
    - Use Private Key to decrypt AES key
    - Use AES key to decrypt message
    - [Optional] Extract from image using Steganography
```

### Key Management
- **RSA Keys**: Generated per user, stored in database (⚠️ private key in DB is for demo only)
- **AES Keys**: Generated per message, encrypted with recipient's RSA public key
- **Session**: Flask session stores `user_id` and `username`

---

## 📊 Database Schema

### Users Table
- `id` (UUID): User ID from auth
- `username` (VARCHAR): Unique username
- `email` (VARCHAR): Email
- `public_key` (TEXT): RSA public key (shared)
- `private_key` (TEXT): RSA private key (sensitive!)
- `bio` (TEXT): User biography
- `avatar_url` (TEXT): Profile avatar

### Posts Table
- `id` (BIGSERIAL): Post ID
- `user_id` (UUID): Author
- `content` (TEXT): Post content
- `image` (BYTEA): Image data
- `encrypted_message` (TEXT): Encrypted secret
- `encrypted_aes_key` (TEXT): RSA-encrypted AES key
- `recipient_id` (UUID): If secret message
- `visibility` (VARCHAR): 'public' or 'private'

### Friends Table
- `id` (BIGSERIAL): Friendship ID
- `user_id` (UUID): Requester
- `friend_id` (UUID): Recipient
- `status` (VARCHAR): 'pending' or 'accepted'

### Messages Table
- `id` (BIGSERIAL): Message ID
- `sender_id` (UUID): Sender
- `recipient_id` (UUID): Recipient
- `content` (TEXT): Message
- `encrypted_content` (TEXT): Encrypted version
- `is_read` (BOOLEAN): Read status

### Encrypted Files Table
- `id` (BIGSERIAL): File ID
- `user_id` (UUID): Owner
- `filename` (VARCHAR): File name
- `stego_image` (BYTEA): Image with hidden message
- `encrypted_message` (TEXT): Hidden encrypted content
- `encrypted_aes_key` (TEXT): RSA-encrypted AES key
- `recipient_id` (UUID): Intended recipient

---

## 🛠️ API Reference

### Friend Management
```
POST /api/friends/add
POST /api/friends/accept
GET  /api/friends/list
GET  /api/friends/pending
```

### Messaging
```
GET  /api/messages/<friend_id>
POST /api/messages/send
POST /api/messages/send-encrypted
```

### Encrypted Files
```
GET /api/encrypted-files/<file_id>
```

### Profile
```
POST /api/profile/update
GET  /profile/<username>
```

---

## 🐛 Troubleshooting

### "Supabase initialization failed"
- Check `.env` file has correct `SUPABASE_URL` and `SUPABASE_KEY`
- Reload environment: `pip install python-dotenv`

### "Table does not exist"
- Verify all SQL blocks from SUPABASE_SETUP.md were executed
- Check SQL Editor for errors
- Refresh Supabase dashboard

### "Private key decode error"
- Private key format issue in database
- Ensure RSA keys are properly serialized in PEM format

### "Access denied" on encrypted files
- Only sender and recipient can view
- Check Row Level Security policies are enabled

### Weights loading errors
- Place `cnn.weights.h5` in project root if training completed
- Or weights will be skipped, model still works with random initialization

---

## 📝 Next Steps

1. **Deploy to Heroku/AWS/Railway**
   - Set environment variables in platform
   - Push to Git repository

2. **Improve UI**
   - Update HTML templates with better styling
   - Add real-time notifications using WebSockets

3. **Production Security**
   - Move private keys to secure key management system (AWS KMS, HashiCorp Vault)
   - Enable HTTPS
   - Add rate limiting
   - Implement proper session management

4. **Features to Add**
   - Group messages
   - File sharing
   - Message deletion
   - User blocking
   - Notifications

---

## 📞 Support

For issues:
1. Check Supabase logs: Dashboard → Logs
2. Check Flask debug output
3. Verify network connectivity
4. Review error messages in browser console
