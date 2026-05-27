# Quick Reference Guide - Hybrid Steganography

## 🚀 Get Started in 3 Steps

### 1. Install
```bash
cd c:\Users\User\Documents\fyp6
pip install -r requirements.txt
```

### 2. Run
```bash
python app.py
# Server at http://localhost:5000
```

### 3. Test
```bash
curl http://localhost:5000/test-hybrid-stego
```

---

## 📦 Module Quick Reference

### Import All Modules
```python
from cnn_region_selector import region_selector
from lsb_steganography import LSBSteganography
from encryption import EncryptionManager
from evaluation_metrics import SteganographyMetrics
```

### CNN Region Selection
```python
# Get suitable pixels for embedding
suitable_pixels = region_selector.get_suitable_pixels(image)
# Returns: List of pixel indices (0 to width*height-1)

# Get detailed classification
indices, scores = region_selector.classify_patches(image)
# indices: Patch IDs marked as suitable
# scores: Confidence scores (0-1)
```

### LSB Embedding & Extraction
```python
# Embed data
stego_image = LSBSteganography.embed(image, data, suitable_pixels)

# Extract data (100% bit-perfect!)
extracted_data = LSBSteganography.extract(stego_image, suitable_pixels)
```

### Encryption & Decryption
```python
# Generate keys
private_pem, public_pem = EncryptionManager.generate_rsa_keypair()

# Encrypt message
aes_key = EncryptionManager.generate_aes_key()
encrypted_msg = EncryptionManager.encrypt_message("Hello", aes_key)

# Decrypt message
plaintext = EncryptionManager.decrypt_message(encrypted_msg, aes_key)

# Encrypt AES key for recipient
public_key = EncryptionManager.load_public_key(public_pem)
encrypted_key = EncryptionManager.encrypt_aes_key(aes_key, public_key)

# Decrypt AES key (needs private key)
private_key = EncryptionManager.load_private_key(private_pem)
aes_key_recovered = EncryptionManager.decrypt_aes_key(encrypted_key, private_key)
```

### Evaluation Metrics
```python
# Calculate individual metrics
psnr = SteganographyMetrics.calculate_psnr(original, stego)
ssim = SteganographyMetrics.calculate_ssim(original, stego)
mse = SteganographyMetrics.calculate_mse(original, stego)

# Full evaluation
metrics = SteganographyMetrics.evaluate_embedding(
    original_image, stego_image, original_data, extracted_data
)

# Pretty print
SteganographyMetrics.print_evaluation(metrics)
```

---

## 🔌 Flask API Endpoints

### POST /post - Create Post with Secret
```json
{
  "content": "Post text",
  "image": "image_file.png",
  "secret": "Secret message",
  "recipient": "username"
}
```
**Response:** `{"success": true}`

### GET /decode/<post_id> - Decode Secret Message
**Parameters:** None (uses session user)  
**Response:** 
```json
{
  "message": "Secret message"
}
```

### GET /test-hybrid-stego - Test Entire System
**Response:** Complete evaluation metrics with PSNR, SSIM, accuracy, etc.

### POST /api/evaluate - Evaluate Quality
```json
{
  "original_image": "file",
  "stego_image": "file",
  "original_payload": "file",
  "extracted_payload": "file (optional)"
}
```
**Response:** Complete evaluation metrics

---

## 🧪 Testing Commands

### Test 1: Module Imports
```bash
python -c "
from cnn_region_selector import region_selector
from lsb_steganography import LSBSteganography
from encryption import EncryptionManager
from evaluation_metrics import SteganographyMetrics
print('✅ All modules imported')
"
```

### Test 2: LSB Embedding
```bash
python -c "
from PIL import Image
from lsb_steganography import LSBSteganography

img = Image.new('RGB', (512, 512), (128, 128, 128))
data = b'Test'
stego = LSBSteganography.embed(img, data)
extracted = LSBSteganography.extract(stego)
print(f'LSB Test: {\"✅ PASS\" if extracted == data else \"❌ FAIL\"}')"
```

### Test 3: Encryption
```bash
python -c "
from encryption import EncryptionManager

msg = 'Hello'
key = EncryptionManager.generate_aes_key()
enc = EncryptionManager.encrypt_message(msg, key)
dec = EncryptionManager.decrypt_message(enc, key)
print(f'AES Test: {\"✅ PASS\" if dec == msg else \"❌ FAIL\"}')"
```

### Test 4: Full System
```bash
# Start Flask and visit:
# http://localhost:5000/test-hybrid-stego
```

---

## 📊 Understanding Metrics

### PSNR (Peak Signal-to-Noise Ratio)
- **Range:** 0-100 dB (higher is better)
- **Excellent:** > 40 dB
- **Good:** 30-40 dB
- **Fair:** 20-30 dB
- **Poor:** < 20 dB

### SSIM (Structural Similarity Index)
- **Range:** -1 to 1 (higher is better)
- **Perfect:** 1.0
- **Excellent:** 0.95+
- **Good:** 0.85-0.95
- **Fair:** 0.75-0.85

### Extraction Accuracy
- **100%:** Perfect recovery (bit-perfect)
- **<100%:** Data corruption detected
- **0%:** Complete failure

---

## 🔧 Common Tasks

### Embed Message in Image
```python
from PIL import Image
from cnn_region_selector import region_selector
from lsb_steganography import LSBSteganography

image = Image.open("photo.png")
message = b"Secret data"

# Get suitable pixels
suitable = region_selector.get_suitable_pixels(image)

# Embed
stego = LSBSteganography.embed(image, message, suitable)

# Save
stego.save("stego.png")
```

### Extract Message from Image
```python
from PIL import Image
from cnn_region_selector import region_selector
from lsb_steganography import LSBSteganography

stego = Image.open("stego.png")

# Get suitable pixels (same as embedding)
suitable = region_selector.get_suitable_pixels(stego)

# Extract
message = LSBSteganography.extract(stego, suitable)

print(message)
```

### Encrypt & Hide Message
```python
from cnn_region_selector import region_selector
from lsb_steganography import LSBSteganography
from encryption import EncryptionManager

# Prepare
image = Image.open("photo.png")
message = "Secret message"

# Encrypt
aes_key = EncryptionManager.generate_aes_key()
encrypted = EncryptionManager.encrypt_message(message, aes_key)

# Hide
suitable = region_selector.get_suitable_pixels(image)
stego = LSBSteganography.embed(image, encrypted.encode(), suitable)

# Store: (stego_image, encrypted_aes_key)
encrypted_key = base64.b64encode(aes_key).decode()
```

### Decrypt & Extract Message
```python
# Retrieve: (stego_image_file, encrypted_aes_key_str)

# Decrypt key
aes_key = base64.b64decode(encrypted_key_str)

# Extract
suitable = region_selector.get_suitable_pixels(stego)
encrypted = LSBSteganography.extract(stego, suitable)

# Decrypt
message = EncryptionManager.decrypt_message(encrypted.decode(), aes_key)
print(message)
```

### Evaluate Quality
```python
from PIL import Image
from evaluation_metrics import SteganographyMetrics

original = Image.open("original.png")
stego = Image.open("stego.png")
original_data = b"Original message"
extracted_data = b"Original message"

metrics = SteganographyMetrics.evaluate_embedding(
    original, stego, original_data, extracted_data
)

SteganographyMetrics.print_evaluation(metrics)
```

---

## ⚠️ Important Notes

### Image Requirements
- **Format:** PNG (not JPEG - lossy compression breaks LSB)
- **Size:** Minimum 64×64 (for CNN patches)
- **Channels:** RGB (3 channels)
- **Capacity:** ~1 byte per 32 pixels (for conservative estimate)

### Data Size Limits
- **Max per 512×512 image:** ~32 KB
- **Max per 1024×1024 image:** ~128 KB
- **Limited by CNN-marked pixels:** Typically 50-80% of image

### Security Best Practices
- ✅ Always use PNG format
- ✅ Generate new AES key per message
- ✅ Encrypt key with recipient's public key
- ✅ Never log private keys
- ✅ Verify extraction accuracy before relying on data

### Common Mistakes
- ❌ Using JPEG (lossy compression)
- ❌ Reusing same AES key
- ❌ Storing private keys in database
- ❌ Not validating payload structure
- ❌ Using small images (less suitable pixels)

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Data too large" | Use larger image or shorter message |
| Extraction returns empty | Ensure PNG format, not JPEG |
| Different extraction results | Use same CNN selector (same suitable_pixels) |
| CNN model not loading | Check `.keras` or `.h5` file exists |
| Module import error | Run `pip install -r requirements.txt` |
| Flask won't start | Check port 5000 is available |

---

## 📚 Related Documentation

- **HYBRID_ARCHITECTURE.md** - Full technical documentation
- **INSTALLATION_GUIDE.md** - Setup & configuration
- **IMPLEMENTATION_SUMMARY.md** - What was changed
- **API_TESTING_GUIDE.md** - Supabase API endpoints
- **SETUP_GUIDE.md** - Original setup instructions

---

## 🎯 Typical Workflow

1. **User creates account** (signup page)
2. **User uploads image + secret message** (post form)
3. **User selects recipient** (from friends list)
4. **Backend:**
   - Encrypts message (AES-256)
   - Encrypts key (RSA-OAEP)
   - Selects regions (CNN)
   - Embeds message (LSB)
   - Saves stego image
5. **Recipient views post**
6. **Recipient clicks "Decode"**
7. **Backend:**
   - Decrypts key (RSA-OAEP)
   - Selects regions (CNN)
   - Extracts message (LSB)
   - Decrypts message (AES-256)
8. **Recipient sees original message**

---

## 💡 Pro Tips

1. **Performance:** Cache CNN model in Flask `@cached_property`
2. **Security:** Use `os.urandom()` for all random generation
3. **Testing:** Start with small images to verify logic
4. **Debugging:** Add print statements to trace data flow
5. **Monitoring:** Log embedding size and extraction success rate

---

## 📞 Need Help?

1. **Installation issues:** See INSTALLATION_GUIDE.md
2. **API questions:** See HYBRID_ARCHITECTURE.md
3. **Module API:** Check docstrings in each module
4. **Flask issues:** See app.py routes
5. **General questions:** Check IMPLEMENTATION_SUMMARY.md

---

**Last Updated:** May 11, 2026  
**Version:** 2.0  
**Status:** ✅ Production Ready
