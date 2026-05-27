# API Testing Guide - cURL Examples

This file contains examples to test your FYP platform APIs locally.

## Prerequisites
- Flask server running: `python app.py`
- User authenticated (session cookie present)
- Base URL: `http://localhost:5000`

---

## 1️⃣ Authentication

### Signup
```bash
curl -X POST http://localhost:5000/signup \
  -d "email=user@example.com&username=testuser&password=testpass123"
```

### Login
```bash
curl -X POST http://localhost:5000/login \
  -d "email=user@example.com&password=testpass123" \
  -c cookies.txt
```

---

## 2️⃣ Friend Management

### Add Friend
```bash
curl -X POST http://localhost:5000/api/friends/add \
  -H "Content-Type: application/json" \
  -d '{"username":"friend_username"}' \
  -b cookies.txt
```

### Get Friends List
```bash
curl -X GET http://localhost:5000/api/friends/list \
  -b cookies.txt | jq
```

### Get Pending Requests
```bash
curl -X GET http://localhost:5000/api/friends/pending \
  -b cookies.txt | jq
```

### Accept Friend Request
```bash
curl -X POST http://localhost:5000/api/friends/accept \
  -H "Content-Type: application/json" \
  -d '{"friend_id":"friend-uuid-here"}' \
  -b cookies.txt
```

---

## 3️⃣ Posts

### Create Public Post
```bash
curl -X POST http://localhost:5000/post \
  -d "content=Hello world!&recipient=" \
  -b cookies.txt
```

### Create Post With Image
```bash
curl -X POST http://localhost:5000/post \
  -F "content=Check this image" \
  -F "image=@path/to/image.png" \
  -b cookies.txt
```

---

## 4️⃣ Encrypted Messaging

### Send Encrypted Message
```bash
curl -X POST http://localhost:5000/post \
  -d "content=Public message&secret=This is secret&recipient=friend_username" \
  -b cookies.txt
```

### Send Encrypted Message With Steganography
```bash
curl -X POST http://localhost:5000/post \
  -F "content=Look at the image" \
  -F "secret=Hidden message in image" \
  -F "recipient=friend_username" \
  -F "image=@path/to/cover_image.png" \
  -b cookies.txt
```

### Decode Encrypted Message
```bash
curl -X GET http://localhost:5000/decode/1 \
  -b cookies.txt | jq
```

---

## 5️⃣ Direct Messages

### Send Direct Message
```bash
curl -X POST http://localhost:5000/api/messages/send \
  -H "Content-Type: application/json" \
  -d '{"recipient_id":"friend-uuid","content":"Hello friend"}' \
  -b cookies.txt
```

### Get Messages With Friend
```bash
curl -X GET http://localhost:5000/api/messages/friend-uuid \
  -b cookies.txt | jq
```

### Send Encrypted Direct Message
```bash
curl -X POST http://localhost:5000/api/messages/send-encrypted \
  -F "recipient_username=friend_username" \
  -F "content=Secret message" \
  -F "image=@path/to/image.png" \
  -b cookies.txt
```

---

## 6️⃣ Encrypted Files

### Get All Encrypted Files
```bash
curl -X GET http://localhost:5000/encrypted-files \
  -b cookies.txt
```

### Retrieve Encrypted File
```bash
curl -X GET http://localhost:5000/api/encrypted-files/1 \
  -b cookies.txt | jq
```

---

## 7️⃣ Profile Management

### Get User Profile
```bash
curl -X GET http://localhost:5000/profile/testuser \
  -b cookies.txt
```

### Update Profile
```bash
curl -X POST http://localhost:5000/api/profile/update \
  -F "bio=I love secure communication" \
  -F "avatar=@path/to/avatar.png" \
  -b cookies.txt
```

---

## 💡 Testing Tips

### Using Python Requests (More Convenient)
```python
import requests

# Setup session
session = requests.Session()

# Login
login_response = session.post('http://localhost:5000/login', data={
    'email': 'user@example.com',
    'password': 'password123'
})

# Add friend
response = session.post('http://localhost:5000/api/friends/add', json={
    'username': 'john_doe'
})
print(response.json())

# Get friends
friends = session.get('http://localhost:5000/api/friends/list').json()
print(friends)
```

### Using Postman
1. Import this collection (convert to Postman JSON)
2. Set environment variables:
   - `base_url`: http://localhost:5000
   - `user_id`: your UUID
   - `friend_username`: a friend's username
3. Run requests with test data

### Debug Mode
Add to your curl commands to see detailed responses:
```bash
-v  # verbose (shows headers)
| jq  # pretty-print JSON
```

---

## ✅ Expected Responses

### Success (Friend Added)
```json
{"success": true}
```

### Success (Get Friends)
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "avatar_url": null
  }
]
```

### Error (Friend Not Found)
```json
{
  "error": "Friend not found"
}
```

### Error (Not Logged In)
```json
{
  "error": "Not logged in"
}
```

---

## 🔍 Testing Workflow

1. **Setup Users**
   - Create 2+ test accounts
   - Login with each to get session

2. **Test Friend Features**
   - Add user1 as friend of user2
   - Accept request from user2
   - Verify both see friendship

3. **Test Messaging**
   - Send messages between users
   - Verify encryption/decryption
   - Check message history

4. **Test Steganography**
   - Send encrypted message with image
   - Retrieve and decrypt
   - Verify hidden message intact

5. **Performance Testing**
   - Send bulk messages
   - Large image steganography
   - Check database query times

---

## 🐛 Common Issues & Solutions

### 401 Unauthorized
- Not logged in or session expired
- Solution: Re-login and get new session cookie

### 404 Not Found
- Wrong endpoint or missing ID
- Solution: Verify URL and parameters

### 400 Bad Request
- Invalid JSON or missing required fields
- Solution: Check request format

### 500 Internal Server Error
- Database issue or validation error
- Solution: Check Flask debug output

---

## 📊 Load Testing Sample
```bash
# Test with 10 concurrent requests
for i in {1..10}; do
  curl -X POST http://localhost:5000/post \
    -d "content=Message $i" \
    -b cookies.txt &
done
wait
```

---

## 🔐 Security Notes

- Never send credentials in URL parameters
- Always use HTTPS in production
- Keep session cookies secure
- Test with real encryption before deployment
