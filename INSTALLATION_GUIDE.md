# Installation & Setup Guide - Hybrid Steganography

## 📋 Prerequisites

- Python 3.8+ (tested with 3.9+)
- pip (Python package manager)
- 2GB+ free disk space (for TensorFlow)
- 8GB+ RAM recommended
- Pre-trained CNN model (.keras or .h5 format)

---

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies

```bash
# Navigate to project directory
cd fyp6

# Create virtual environment (optional but recommended)
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install all dependencies
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
# Test imports
python -c "
import tensorflow as tf
import numpy as np
from PIL import Image
from cryptography.hazmat.primitives import hashes
from skimage.metrics import peak_signal_noise_ratio
print('✅ All dependencies installed successfully!')
"
```

### 3. Configure Environment

Create `.env` file in project root:

```bash
# .env (create in fyp6 directory)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SECRET_KEY=your_flask_secret_key
```

### 4. Place Model Files

Ensure one of these exists in project root:
- `my_model.keras` (Keras format)
- `cnn_stego_model.h5` (HDF5 format)

```bash
# Verify model file
ls -la *.keras *.h5  # Linux/Mac
dir *.keras *.h5     # Windows
```

### 5. Run Flask Application

```bash
# Start Flask development server
python app.py

# Server starts at http://localhost:5000
```

---

## 📦 Dependency Details

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `tensorflow` | 2.16.1 | CNN inference |
| `keras` | ~3.0 | (included with TensorFlow) |
| `cryptography` | 41.0.4 | AES-256 & RSA-OAEP |
| `numpy` | 1.24.3 | Numerical operations |
| `Pillow` | 10.0.0 | Image processing |
| `scikit-image` | 0.22.0 | PSNR, SSIM metrics |
| `opencv-python` | 4.8.1.78 | Edge detection (fallback) |

### Web Framework

| Package | Version | Purpose |
|---------|---------|---------|
| `Flask` | 2.3.3 | Web application |
| `Werkzeug` | 2.3.7 | WSGI utilities |
| `gunicorn` | 21.2.0 | Production server |

### Database

| Package | Version | Purpose |
|---------|---------|---------|
| `supabase` | 2.3.0 | Database client |
| `python-dotenv` | 1.0.0 | Environment variables |
| `requests` | 2.31.0 | HTTP requests |

---

## 🔧 Detailed Installation

### For Windows Users

```powershell
# Open PowerShell in project directory

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import tensorflow; print(f'TensorFlow {tensorflow.__version__} installed')"
```

### For Linux/Mac Users

```bash
# Open terminal in project directory

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import tensorflow; print(f'TensorFlow {tensorflow.__version__} installed')"
```

---

## ✅ Verification Checklist

Run this script to verify everything is set up correctly:

```python
# verify_setup.py
import sys

def verify_installation():
    print("🔍 Verifying Hybrid Steganography Installation\n")
    
    checks = []
    
    # Check 1: Python version
    try:
        assert sys.version_info >= (3, 8)
        print("✅ Python 3.8+")
        checks.append(True)
    except:
        print("❌ Python 3.8+ required")
        checks.append(False)
    
    # Check 2: TensorFlow
    try:
        import tensorflow as tf
        print(f"✅ TensorFlow {tf.__version__}")
        checks.append(True)
    except:
        print("❌ TensorFlow not installed")
        checks.append(False)
    
    # Check 3: Cryptography
    try:
        from cryptography.hazmat.primitives import hashes
        print("✅ cryptography library")
        checks.append(True)
    except:
        print("❌ cryptography not installed")
        checks.append(False)
    
    # Check 4: Pillow
    try:
        from PIL import Image
        print("✅ Pillow (PIL)")
        checks.append(True)
    except:
        print("❌ Pillow not installed")
        checks.append(False)
    
    # Check 5: scikit-image
    try:
        from skimage.metrics import peak_signal_noise_ratio
        print("✅ scikit-image")
        checks.append(True)
    except:
        print("❌ scikit-image not installed")
        checks.append(False)
    
    # Check 6: OpenCV
    try:
        import cv2
        print("✅ OpenCV")
        checks.append(True)
    except:
        print("❌ OpenCV not installed")
        checks.append(False)
    
    # Check 7: Flask
    try:
        import flask
        print("✅ Flask")
        checks.append(True)
    except:
        print("❌ Flask not installed")
        checks.append(False)
    
    # Check 8: Supabase
    try:
        from supabase import create_client
        print("✅ Supabase")
        checks.append(True)
    except:
        print("❌ Supabase not installed")
        checks.append(False)
    
    # Check 9: Model files
    try:
        import os
        assert os.path.exists("my_model.keras") or os.path.exists("cnn_stego_model.h5")
        print("✅ CNN model file found")
        checks.append(True)
    except:
        print("⚠️  CNN model file not found (will use fallback)")
        checks.append(True)  # Warning, not failure
    
    # Check 10: .env file
    try:
        from dotenv import load_dotenv
        assert os.path.exists(".env")
        print("✅ .env file found")
        checks.append(True)
    except:
        print("⚠️  .env file not found (required for Supabase)")
        checks.append(True)  # Warning, not failure
    
    print("\n" + "="*50)
    if all(checks):
        print("✅ ALL CHECKS PASSED - Ready to run!")
        print("="*50)
        print("\nStart with: python app.py")
        return True
    else:
        print("❌ SOME CHECKS FAILED - See above for details")
        print("="*50)
        return False

if __name__ == "__main__":
    success = verify_installation()
    sys.exit(0 if success else 1)
```

Run verification:
```bash
python verify_setup.py
```

---

## 🧪 Testing the Installation

### Test 1: Basic Module Import

```bash
python -c "
from cnn_region_selector import CNNRegionSelector
from lsb_steganography import LSBSteganography
from encryption import EncryptionManager
from evaluation_metrics import SteganographyMetrics
print('✅ All modules imported successfully')
"
```

### Test 2: LSB Embedding

```bash
python -c "
from PIL import Image
from lsb_steganography import LSBSteganography

img = Image.new('RGB', (512, 512), (128, 128, 128))
data = b'Test message'
stego = LSBSteganography.embed(img, data)
extracted = LSBSteganography.extract(stego)

if extracted == data:
    print('✅ LSB embedding test PASSED')
else:
    print('❌ LSB embedding test FAILED')
"
```

### Test 3: Encryption

```bash
python -c "
from encryption import EncryptionManager

msg = 'Hello World'
key = EncryptionManager.generate_aes_key()
encrypted = EncryptionManager.encrypt_message(msg, key)
decrypted = EncryptionManager.decrypt_message(encrypted, key)

if decrypted == msg:
    print('✅ Encryption test PASSED')
else:
    print('❌ Encryption test FAILED')
"
```

### Test 4: CNN Region Selector

```bash
python -c "
from PIL import Image
from cnn_region_selector import CNNRegionSelector

selector = CNNRegionSelector()
img = Image.new('RGB', (512, 512), (128, 128, 128))
suitable = selector.get_suitable_pixels(img)

print(f'✅ CNN Region Selector test PASSED')
print(f'   Found {len(suitable)} suitable pixels')
"
```

### Test 5: Flask Server Start

```bash
# Start server (will run on localhost:5000)
python app.py

# In another terminal, test endpoint
curl http://localhost:5000/
# Should return HTML of index page
```

---

## 🔧 Configuration Options

### Environment Variables (.env)

```ini
# Database (Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Flask
SECRET_KEY=your-very-long-random-secret-key-change-this!
FLASK_ENV=development  # or 'production'
FLASK_DEBUG=False  # Set to True for development

# Model paths (optional, auto-detect by default)
CNN_MODEL_PATH=my_model.keras
# or: CNN_MODEL_PATH=cnn_stego_model.h5
```

### CNN Model Selection

The system automatically detects models in this order:
1. `my_model.keras` (Keras 3.x format)
2. `cnn_stego_model.h5` (HDF5 format)
3. Falls back to edge detection if neither found

To explicitly specify:
```python
from cnn_region_selector import CNNRegionSelector
selector = CNNRegionSelector(model_path="path/to/your/model.keras")
```

---

## 📊 System Requirements

### Minimum
- CPU: 2-core processor
- RAM: 4GB
- Storage: 2GB
- Python: 3.8+

### Recommended
- CPU: 4+ core processor
- RAM: 8GB+
- Storage: 5GB (for TensorFlow cache)
- Python: 3.10+
- GPU: NVIDIA (with CUDA support) for faster CNN inference

### GPU Support (Optional)

For GPU acceleration:
```bash
# Uninstall CPU version
pip uninstall tensorflow -y

# Install GPU version
pip install tensorflow[and-cuda]

# Verify
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

---

## 🐛 Troubleshooting Installation

### Issue: `ModuleNotFoundError: No module named 'tensorflow'`

```bash
# Solution 1: Install missing package
pip install tensorflow==2.16.1

# Solution 2: Check virtual environment is activated
which python  # Linux/Mac - should show .venv path
where python  # Windows - should show .venv path

# Solution 3: Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: `ImportError: libblas.so.3` (Linux)

```bash
# Install system dependencies
sudo apt-get install libblas3 liblapack3 libopenblas-base  # Ubuntu/Debian
brew install openblas  # macOS
```

### Issue: Memory error during installation

```bash
# Install with limited concurrency
pip install -r requirements.txt --no-cache-dir

# Or install packages one by one
pip install numpy
pip install tensorflow
# ... etc
```

### Issue: `TypeError: 'NoneType' object is not subscriptable` (CNN)

Model not loaded properly. Check:
```python
from cnn_region_selector import region_selector
print(f"Model loaded: {region_selector.model is not None}")

# If None, check model file:
import os
print(f"my_model.keras exists: {os.path.exists('my_model.keras')}")
print(f"cnn_stego_model.h5 exists: {os.path.exists('cnn_stego_model.h5')}")
```

---

## 🚀 Running the Application

### Development Mode

```bash
# With debug mode enabled
FLASK_ENV=development FLASK_DEBUG=True python app.py

# Server at http://localhost:5000
# Auto-reloads on file changes
```

### Production Mode

```bash
# Using Gunicorn (recommended)
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# With environment variables
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker (Optional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

Build and run:
```bash
docker build -t hybrid-stego .
docker run -p 8000:8000 --env-file .env hybrid-stego
```

---

## 📝 First-Time Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] CNN model file placed in project root
- [ ] .env file created with Supabase credentials
- [ ] Verification script ran successfully
- [ ] Flask server starts without errors
- [ ] Can access http://localhost:5000

---

## 🎯 Next Steps

After successful installation:

1. **Run the test endpoint:**
   ```bash
   curl http://localhost:5000/test-hybrid-stego
   ```

2. **Sign up an account:**
   - Go to http://localhost:5000
   - Create account with email/password

3. **Create a test post with steganography:**
   - Upload image + secret message
   - Specify recipient

4. **Decode the message:**
   - View post from recipient's account
   - Decode button extracts embedded message

5. **Check evaluation metrics:**
   - POST to /api/evaluate with image files

---

## 📚 Additional Resources

- **Hybrid Architecture Documentation:** `HYBRID_ARCHITECTURE.md`
- **Setup Guide:** `SETUP_GUIDE.md`
- **Supabase Documentation:** `SUPABASE_SETUP.md`
- **API Documentation:** `API_TESTING_GUIDE.md`
- **CNN Training Notebook:** `cnn_training.ipynb`

---

## 💬 Support

If you encounter issues:

1. **Check logs:**
   ```bash
   tail -f app.log  # Linux/Mac
   Get-Content app.log -Tail 100  # Windows
   ```

2. **Run verification:**
   ```bash
   python verify_setup.py
   ```

3. **Test individual modules:**
   ```bash
   python -c "from cnn_region_selector import region_selector; print(region_selector.model)"
   ```

4. **Check Python version:**
   ```bash
   python --version  # Should be 3.8+
   ```

---

**Last Updated:** May 11, 2026  
**Version:** 2.0 (Hybrid Architecture)  
**Status:** ✅ Ready for Setup
