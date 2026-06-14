"AI-Driven Image Steganography for Secure Web Communication"

This repository contain source code for a functional web-based prototype that was developed as a 
proof of concept for AI-Driven Image Steganography for Secure Web Communication. 
The system will feature a social media–like interface where users can log in, add friends, 
and exchange hidden messages embedded inside images. The implemented pipeline 
combines AES encryption, RSA key protection, a CNN-based region selector, and LSB 
image embedding to securely hide and transmit messages while preserving image quality. 
The system is expected to demonstrate reliable message embedding and recovery while 
maintaining strong visual integrity and evaluated using metrics such as PSNR and SSIM. 

---

## Features

- User authentication
- Dashboard
- Database connection with Supabase
- CRUD operations
- Responsive UI

---

## Tech Stack

- Python
- Flask
- Supabase
- HTML/CSS
- JavaScript
- PostgreSQL

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/project-name.git
cd project-name
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

Windows:

```bash
.venv\Scripts\activate
```

Mac/Linux:

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create `.env`

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SECRET_KEY=your_secret_key
```

---

## Run Application

```bash
python app.py
```

Open browser:

```text
http://127.0.0.1:5000
```

---
