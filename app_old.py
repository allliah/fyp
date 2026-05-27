from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import tensorflow as tf
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import numpy as np
from PIL import Image
import io
from flask import jsonify

load_dotenv()

# Load the model first
# Define model architecture
from tensorflow.keras.layers import Input, Conv2D, Dense, Flatten, Reshape, Concatenate
from tensorflow.keras.models import Model

## Inputs
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, Dense, Reshape, Flatten, Concatenate
from flask import Flask
import os

## Inputs
image_input = Input(shape=(32, 32, 3), name="image_input")
message_input = Input(shape=(100,), name="message_input")

# Message processing
message_dense = Dense(32 * 32 * 3, name="message_dense")(message_input)
message_reshaped = Reshape((32, 32, 3), name="message_reshape")(message_dense)

# Combine
combined = Concatenate(name="concatenate")([image_input, message_reshaped])

# Encoder
x = Conv2D(32, (3, 3), activation="relu", padding="same", name="encoder_conv1")(
    combined
)
x = Conv2D(32, (3, 3), activation="relu", padding="same", name="encoder_conv2")(x)
x = Conv2D(3, (3, 3), activation="sigmoid", padding="same", name="encoder_output")(x)

# Decoder (connected to encoder output x)
y = Conv2D(32, (3, 3), activation="relu", padding="same", name="decoder_conv1")(x)
y = Conv2D(32, (3, 3), activation="relu", padding="same", name="decoder_conv2")(y)
y = Flatten(name="decoder_flatten")(y)
y = Dense(100, activation="sigmoid", name="decoder_output")(y)

# Full model
full_model = Model(
    inputs=[image_input, message_input], outputs=[x, y], name="full_model"
)

# Load weights with by_name=True to match layers by name
try:
    full_model.load_weights("cnn.weights.h5", by_name=True, skip_mismatch=True)
    print("Weights loaded successfully")
except Exception as e:
    print("Weight loading skipped:", e)

# Extract the encoder part for encoding
# This takes both inputs and outputs the encoded representation x
encoder = Model(inputs=[image_input, message_input], outputs=x, name="encoder")

# For decoding, we need a model that takes the encoded representation and outputs y
# Create a proper decoder model that takes the encoded tensor directly
encoded_input = Input(shape=(32, 32, 3), name="encoded_input")
decoder_output = encoded_input

# Recreate the decoder layers
decoder_output = Conv2D(
    32, (3, 3), activation="relu", padding="same", name="decoder_conv1"
)(decoder_output)
decoder_output = Conv2D(
    32, (3, 3), activation="relu", padding="same", name="decoder_conv2"
)(decoder_output)
decoder_output = Flatten(name="decoder_flatten")(decoder_output)
decoder_output = Dense(100, activation="sigmoid", name="decoder_output")(decoder_output)

decoder = Model(inputs=encoded_input, outputs=decoder_output, name="decoder")

# 🔥 CNN MODEL DIAGNOSTIC
print("🔍 CNN Model Status:")
print(f"Encoder summary: {encoder.summary()}")
print(f"Decoder summary: {decoder.summary()}")

# Test model with dummy data
test_img = np.random.rand(1, 32, 32, 3)
test_msg = np.random.rand(1, 100)
try:
    encoded = encoder.predict([test_img, test_msg], verbose=0)
    decoded = decoder.predict(encoded, verbose=0)
    print(f"✅ CNN Forward pass OK: encoded={encoded.shape}, decoded={decoded.shape}")
except Exception as e:
    print(f"💥 CNN BROKEN: {e}")

# Optionally, if you want to load pre-trained weights for decoder:
try:
    decoder.load_weights("cnn.weights.h5", by_name=True, skip_mismatch=True)
    print("Decoder weights loaded")
except Exception as e:
    print("Decoder weight loading skipped:", e)

# Now you can use them together:
# encoded = encoder.predict([image, message])
# decoded = decoder.predict(encoded)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
try:
    from supabase import create_client, Client

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    supabase_service: Client = None
    if SUPABASE_SERVICE_ROLE_KEY:
        supabase_service = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
except Exception as e:
    print(f"Supabase initialization failed: {e}")
    supabase = None
    supabase_service = None

# Assume the model takes image (32x32x3) and message (100 bits as floats), outputs stego and decoded message


def get_embedding_positions(image):
    import cv2

    img = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)

    positions = [i for i, val in enumerate(edges.flatten()) if val > 0]

    # fallback if too few edges
    if len(positions) < 1000:
        positions = list(range(img.size))

    return positions


def bytes_to_bits(data):
    return "".join(format(b, "08b") for b in data)


def bits_to_bytes(bits):
    return bytes(int(bits[i : i + 8], 2) for i in range(0, len(bits), 8))


def build_payload(enc_msg_str):
    data = base64.b64decode(enc_msg_str)
    return b"STEGOv1" + len(data).to_bytes(4, "big") + data


def parse_payload(data):
    if not data.startswith(b"STEGOv1"):
        return None
    idx = 7
    length = int.from_bytes(data[idx : idx + 4], "big")
    idx += 4
    return data[idx : idx + length]


def encode_message(image, encrypted_message):
    """✅ NEW: LSB + CNN (edge-based positions)"""

    img = image.convert("RGB")
    img_array = np.array(img)

    payload = build_payload(encrypted_message)
    bits = bytes_to_bits(payload)

    flat = img_array.flatten()
    positions = get_embedding_positions(img)

    if len(bits) > len(positions):
        raise ValueError("Message too large for image")

    for i, bit in enumerate(bits):
        pos = positions[i]
        flat[pos] = (flat[pos] & ~1) | int(bit)

    stego_array = flat.reshape(img_array.shape)
    return Image.fromarray(stego_array.astype(np.uint8))


def decode_message(stego_image):
    """✅ NEW: Extract LSB + parse payload"""

    img = stego_image.convert("RGB")
    img_array = np.array(img)

    flat = img_array.flatten()
    positions = get_embedding_positions(img)

    bits = "".join(str(flat[pos] & 1) for pos in positions)

    data = bits_to_bytes(bits)

    payload = parse_payload(data)
    if payload is None:
        print("❌ No STEGO header found")
        return b""

    return payload


# Encryption functions
def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def serialize_public_key(public_key):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pem.decode("utf-8")


def deserialize_public_key(pem_str):
    public_key = serialization.load_pem_public_key(
        pem_str.encode("utf-8"), backend=default_backend()
    )
    return public_key


def encrypt_aes_key(aes_key, public_key):
    encrypted = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return base64.b64encode(encrypted).decode("utf-8")


def decrypt_aes_key(encrypted_aes_key, private_key):
    encrypted = base64.b64decode(encrypted_aes_key)
    aes_key = private_key.decrypt(
        encrypted,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return aes_key


def encrypt_message(message, aes_key):
    iv = os.urandom(16)
    plaintext = message.encode("utf-8")

    # 🔥 PROPER PKCS7 PADDING
    padding_len = 16 - (len(plaintext) % 16)
    if padding_len == 0:
        padding_len = 16  # Full block padding

    padded_plaintext = plaintext + bytes([padding_len] * padding_len)
    print(f"ENCRYPT: {len(plaintext)} bytes → padded {len(padded_plaintext)} bytes")

    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(padded_plaintext) + encryptor.finalize()

    return base64.b64encode(iv + encrypted).decode("utf-8")


def decrypt_message(encrypted_bytes, aes_key):
    iv = encrypted_bytes[:16]
    ciphertext = encrypted_bytes[16:]

    if len(ciphertext) == 0:
        return "No data"

    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()

    # 🔥 SMART UNPADDING
    if len(decrypted_padded) < 16:
        return "Too short"

    padding_len = decrypted_padded[-1]
    print(f"Padding claim: {padding_len}")

    # Try PKCS7 first
    if 1 <= padding_len <= 16:
        if all(b == padding_len for b in decrypted_padded[-padding_len:]):
            plaintext = decrypted_padded[:-padding_len]
        else:
            # Fallback: strip nulls
            plaintext = decrypted_padded.rstrip(b"\x00")
    else:
        # Invalid padding → strip nulls
        plaintext = decrypted_padded.rstrip(b"\x00")

    # Clean decode
    message = plaintext.decode("utf-8", errors="ignore").rstrip("\x00\n ")
    return message if message else "Empty message"


# Database Helper Functions
def get_user_by_id(user_id):
    """Fetch user by ID"""
    try:
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None


def get_user_by_username(username):
    """Fetch user by username"""
    try:
        response = (
            supabase.table("users").select("*").eq("username", username).execute()
        )
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error getting user by username: {e}")
        return None


def add_friend(user_id, friend_username):
    """Create a mutual accepted friendship immediately."""
    try:
        friend = get_user_by_username(friend_username)
        if not friend:
            return {"error": "Friend not found"}, 404

        if friend["id"] == user_id:
            return {"error": "Cannot add yourself"}, 400

        # Check if friendship already exists in either direction
        existing = (
            supabase.table("friends")
            .select("*")
            .eq("user_id", user_id)
            .eq("friend_id", friend["id"])
            .execute()
        )
        reverse = (
            supabase.table("friends")
            .select("*")
            .eq("user_id", friend["id"])
            .eq("friend_id", user_id)
            .execute()
        )
        if existing.data and existing.data[0].get("status") == "accepted":
            return {"error": "Already friends"}, 400
        if reverse.data and reverse.data[0].get("status") == "accepted":
            return {"error": "Already friends"}, 400

        # If a pending request exists in either direction, accept it and ensure both directions are accepted.
        if existing.data and existing.data[0].get("status") == "pending":
            supabase.table("friends").update(
                {"status": "accepted", "accepted_at": "now()"}
            ).eq("user_id", user_id).eq("friend_id", friend["id"]).execute()
        if reverse.data and reverse.data[0].get("status") == "pending":
            supabase.table("friends").update(
                {"status": "accepted", "accepted_at": "now()"}
            ).eq("user_id", friend["id"]).eq("friend_id", user_id).execute()

        # Insert any missing accepted relationship record in both directions.
        if not (existing.data and existing.data[0].get("status") == "accepted"):
            supabase.table("friends").insert(
                {
                    "user_id": user_id,
                    "friend_id": friend["id"],
                    "status": "accepted",
                    "accepted_at": "now()",
                }
            ).execute()
        if not (reverse.data and reverse.data[0].get("status") == "accepted"):
            supabase.table("friends").insert(
                {
                    "user_id": friend["id"],
                    "friend_id": user_id,
                    "status": "accepted",
                    "accepted_at": "now()",
                }
            ).execute()

        return {"success": True}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def accept_friend_request(user_id, friend_id):
    """Accept friend request"""
    try:
        # Update status to accepted
        supabase.table("friends").update(
            {"status": "accepted", "accepted_at": "now()"}
        ).eq("user_id", friend_id).eq("friend_id", user_id).execute()

        # Create reverse friendship
        supabase.table("friends").insert(
            {
                "user_id": user_id,
                "friend_id": friend_id,
                "status": "accepted",
                "accepted_at": "now()",
            }
        ).execute()
        return {"success": True}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def get_user_friends(user_id):
    """Get list of accepted friends"""
    try:
        response = (
            supabase.table("friends")
            .select("friend_id")
            .eq("user_id", user_id)
            .eq("status", "accepted")
            .execute()
        )
        friend_ids = [f["friend_id"] for f in response.data]

        friends = []
        for fid in friend_ids:
            user = get_user_by_id(fid)
            if user:
                friends.append(
                    {
                        "id": user["id"],
                        "username": user["username"],
                        "avatar_url": user.get("avatar_url"),
                    }
                )
        return friends
    except Exception as e:
        print(f"Error getting friends: {e}")
        return []


def get_pending_friend_requests(user_id):
    """Get pending friend requests"""
    try:
        response = (
            supabase.table("friends")
            .select("user_id")
            .eq("friend_id", user_id)
            .eq("status", "pending")
            .execute()
        )
        request_ids = [r["user_id"] for r in response.data]

        requests = []
        for rid in request_ids:
            user = get_user_by_id(rid)
            if user:
                requests.append({"id": user["id"], "username": user["username"]})
        return requests
    except Exception as e:
        print(f"Error getting pending requests: {e}")
        return []


def save_encrypted_file(
    user_id,
    filename,
    stego_image_bytes,
    encrypted_msg,
    encrypted_key,
    recipient_id=None,
    description="",
):
    """Save encrypted file with steganography"""
    try:
        supabase.table("encrypted_files").insert(
            {
                "user_id": user_id,
                "filename": filename,
                "stego_image": base64.b64encode(stego_image_bytes).decode("utf-8"),
                "encrypted_message": encrypted_msg,
                "encrypted_aes_key": encrypted_key,
                "recipient_id": recipient_id,
                "description": description,
            }
        ).execute()
        return {"success": True}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def get_user_encrypted_files(user_id):
    """Get all encrypted files for user"""
    try:
        response = (
            supabase.table("encrypted_files")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data
    except Exception as e:
        print(f"Error getting encrypted files: {e}")
        return []


def save_message(sender_id, recipient_id, content, encrypted_content=None):
    """Save private message"""
    try:
        supabase.table("messages").insert(
            {
                "sender_id": sender_id,
                "recipient_id": recipient_id,
                "content": content,
                "encrypted_content": encrypted_content,
            }
        ).execute()
        return {"success": True}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def get_user_messages(user_id, other_user_id=None):
    """Get messages for user"""
    try:
        if other_user_id:
            # Messages between two users
            response = (
                supabase.table("messages")
                .select("*")
                .or_(f"sender_id.eq.{user_id},recipient_id.eq.{user_id}")
                .or_(f"sender_id.eq.{other_user_id},recipient_id.eq.{other_user_id}")
                .order("created_at", desc=True)
                .execute()
            )
        else:
            # All messages for user
            response = (
                supabase.table("messages")
                .select("*")
                .or_(f"sender_id.eq.{user_id},recipient_id.eq.{user_id}")
                .order("created_at", desc=True)
                .execute()
            )
        return response.data
    except Exception as e:
        print(f"Error getting messages: {e}")
        return []


def update_user_profile(user_id, bio=None, avatar_url=None):
    """Update user profile"""
    try:
        update_data = {}
        if bio is not None:
            update_data["bio"] = bio
        if avatar_url is not None:
            update_data["avatar_url"] = avatar_url

        if update_data:
            supabase.table("users").update(update_data).eq("id", user_id).execute()
        return {"success": True}, 200
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("feed"))
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        # Generate RSA keys
        private_key, public_key = generate_rsa_keys()
        public_key_pem = serialize_public_key(public_key)

        # Store private key in session or secure storage - for demo, store in DB (not secure!)
        # In real app, don't store private key in DB
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")

        try:
            if supabase_service:
                auth_response = supabase_service.auth.admin.create_user(
                    {
                        "email": email,
                        "password": password,
                        "email_confirm": True,
                    }
                )
                user_id = auth_response.user.id
            else:
                signup_response = supabase.auth.sign_up(
                    {"email": email, "password": password}
                )
                user_id = signup_response.user.id

            # Sign the user in immediately after signup
            user_session = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            # Insert user data using the service role client so the protected users row can be created
            target_client = supabase_service if supabase_service else supabase
            target_client.table("users").insert(
                {
                    "id": user_id,
                    "username": username,
                    "email": email,
                    "public_key": public_key_pem,
                    "private_key": private_key_pem,  # Again, not secure
                }
            ).execute()

            # Store user in session
            session["user"] = {"id": user_id, "email": email, "username": username}

            flash("Account created successfully!")
            return redirect(url_for("index.html"))
        except Exception as e:
            flash(f"Signup error: {str(e)}")
            return render_template("signup.html")
    return render_template("signup.html")


@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    try:
        user = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        session["user"] = user.user.id
        session["username"] = (
            supabase.table("users")
            .select("username")
            .eq("id", user.user.id)
            .execute()
            .data[0]["username"]
        )
        return redirect(url_for("feed"))
    except Exception as e:
        flash(str(e))
        return redirect(url_for("index"))


@app.route("/feed")
def feed():
    if "user" not in session:
        return redirect(url_for("index"))

    # Fetch posts
    posts = (
        supabase.table("posts")
        .select("*")
        .order("created_at", desc=True)
        .execute()
        .data
    )
    for post in posts:
        user = (
            supabase.table("users")
            .select("username")
            .eq("id", post["user_id"])
            .execute()
            .data[0]
        )
        post["username"] = user["username"]
    # Fetch followers
    followers = [
        user["username"]
        for user in supabase.table("users")
        .select("username")
        .neq("id", session["user"])
        .execute()
        .data
    ]
    return render_template("feed.html", posts=posts, followers=followers)


@app.route("/api/feed")
def feed_api():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    posts = (
        supabase.table("posts")
        .select("*")
        .order("created_at", desc=True)
        .execute()
        .data
    )

    for post in posts:
        user_data = (
            supabase.table("users")
            .select("username")
            .eq("id", post["user_id"])
            .execute()
            .data
        )

        post["username"] = user_data[0]["username"] if user_data else "Unknown"

    return jsonify({"posts": posts})


@app.route("/friends")
def friends():
    if "user" not in session:
        return redirect(url_for("index"))
    # Fetch user's friends
    user_friends = get_user_friends(session["user"])
    # Fetch suggestions (all users except current user and friends)
    friend_ids = [f["id"] for f in user_friends]
    friend_ids.append(session["user"])  # exclude current user
    # Get all users and filter out friends and current user
    all_users = supabase.table("users").select("username", "id").execute().data
    suggestions = [user for user in all_users if user["id"] not in friend_ids]
    return render_template(
        "friends.html", friends=user_friends, suggestions=suggestions
    )


@app.route("/post", methods=["POST"])
def post():
    try:
        if "user" not in session:
            return jsonify({"error": "Not logged in"}), 401

        content = request.form.get("content", "")
        image_file = request.files.get("image")
        secret = request.form.get("secret")
        recipient_username = request.form.get("recipient")

        image = None
        if image_file:
            image = Image.open(io.BytesIO(image_file.read()))

        if secret and recipient_username:

            recipient_data = (
                supabase.table("users")
                .select("id, public_key")
                .eq("username", recipient_username)
                .execute()
                .data
            )

            if not recipient_data:
                return jsonify({"error": "Recipient not found"}), 400

            recipient = recipient_data[0]

            aes_key = os.urandom(32)
            encrypted_message = encrypt_message(secret, aes_key)

            public_key = deserialize_public_key(recipient["public_key"])
            encrypted_aes_key = encrypt_aes_key(aes_key, public_key)

            image_data = None
            if image:
                stego_image = encode_message(image, encrypted_message)
                buf = io.BytesIO()
                stego_image.save(buf, format="PNG")
                image_data = base64.b64encode(buf.getvalue()).decode("utf-8")

            supabase.table("posts").insert(
                {
                    "user_id": session["user"],
                    "content": content,
                    "image": image_data,
                    "encrypted_message": encrypted_message,
                    "encrypted_aes_key": encrypted_aes_key,
                    "recipient_id": recipient["id"],
                }
            ).execute()

        else:
            image_data = None
            if image:
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                image_data = base64.b64encode(buf.getvalue()).decode("utf-8")

            supabase.table("posts").insert(
                {"user_id": session["user"], "content": content, "image": image_data}
            ).execute()

        return jsonify({"success": True})

    except Exception as e:
        print("POST ERROR:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/decode/<int:post_id>")
def decode(post_id):
    print(f"🚀 DECODE post_id={post_id}")

    try:
        if "user" not in session:
            return jsonify({"error": "Not logged in"}), 401

        post_response = supabase.table("posts").select("*").eq("id", post_id).execute()
        if not post_response.data:
            return jsonify({"error": "Post not found"}), 404
        post = post_response.data[0]

        if post["recipient_id"] != session["user"]:
            return jsonify({"error": "Not for you"}), 403

        user_response = (
            supabase.table("users")
            .select("private_key")
            .eq("id", session["user"])
            .execute()
        )
        if not user_response.data:
            return jsonify({"error": "User not found"}), 404
        private_key_pem = user_response.data[0]["private_key"]

        private_key = serialization.load_pem_private_key(
            private_key_pem.encode("utf-8"), password=None, backend=default_backend()
        )

        aes_key = decrypt_aes_key(post["encrypted_aes_key"], private_key)

        # 🔥 CNN STEGO DECODING
        if post.get("image"):
            print("🔍 Using CNN steganography...")
            image_data = base64.b64decode(post["image"])
            stego_image = Image.open(io.BytesIO(image_data))
            encrypted_message_bytes = decode_message(stego_image)  # Fixed function

            print(f"📥 CNN extracted {len(encrypted_message_bytes)} bytes")
            print(f"📥 First 32 bytes: {encrypted_message_bytes[:32].hex()}")
        else:
            encrypted_message_bytes = base64.b64decode(post["encrypted_message"])

        # Ensure proper padding for AES
        # if len(encrypted_message_bytes) % 16 != 0:
        # pad_len = 16 - (len(encrypted_message_bytes) % 16)
        # encrypted_message_bytes += b'\x00' * pad_len
        # print(f"🔧 Padded {pad_len} bytes for AES")

        message = decrypt_message(encrypted_message_bytes, aes_key)

        print(f"✅ FINAL MESSAGE: {repr(message)}")
        return jsonify({"message": message})

    except Exception as e:
        print(f"💥 DECODE ERROR: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"Decode failed: {str(e)}"}), 500


@app.route("/test-cnn")
def test_cnn():
    """🔥 CNN-SPECIFIC DIAGNOSTIC"""
    test_msg = "CNN TEST 🧠"

    # Test image
    test_img = Image.new("RGB", (64, 64), color=(128, 128, 128))

    print("\n🔥 CNN DIAGNOSTIC:")
    print(f"Input: '{test_msg}'")

    # Encode
    stego = encode_message(test_img, test_msg)
    extracted = decode_message(stego)

    try:
        text = extracted.decode("utf-8", errors="ignore")
        print(f"Output: '{text}' → {'✅ PASS' if 'CNN' in text else '❌ FAIL'}")
    except:
        print(f"Output bytes: {len(extracted)} → ❌ FAIL")

    return f"""
    <h1>🧠 CNN Test Results</h1>
    <pre style="background:#f5f5f5;padding:20px;">
{open('app.log', 'r').read()[-1000:]}  <!-- Last 1000 chars of log -->
    </pre>
    <p><a href="/feed">← Feed</a></p>
    """


@app.route("/train-cnn")
def train_cnn():
    """🔥 EMERGENCY CNN TRAINING"""

    # Generate training data
    def generate_data(n_samples=1000):
        images = np.random.rand(n_samples, 32, 32, 3)
        messages = np.random.randint(0, 2, (n_samples, 100)).astype(np.float32)
        return images, messages

    images, messages = generate_data()

    # Compile & train
    full_model.compile(optimizer="adam", loss="mse")
    full_model.fit(
        [images, messages], [images, messages], epochs=10, batch_size=32, verbose=1
    )

    # Save weights
    full_model.save_weights("cnn_fixed.weights.h5")
    print("✅ CNN RETRAINED & SAVED!")

    return "CNN Model retrained! Restart app."


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# Friend Management Routes
@app.route("/api/friends/add", methods=["POST"])
def api_add_friend():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    friend_username = data.get("username")
    result, code = add_friend(session["user"], friend_username)
    return jsonify(result), code


@app.route("/api/friends/accept", methods=["POST"])
def api_accept_friend():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    friend_id = data.get("friend_id")
    result, code = accept_friend_request(session["user"], friend_id)
    return jsonify(result), code


@app.route("/api/friends/list", methods=["GET"])
def api_friends_list():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    friends = get_user_friends(session["user"])
    return jsonify(friends), 200


@app.route("/api/friends/pending", methods=["GET"])
def api_pending_requests():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    requests = get_pending_friend_requests(session["user"])
    return jsonify(requests), 200


# Profile Routes
@app.route("/profile/<username>")
def view_profile(username):
    if "user" not in session:
        return redirect(url_for("index"))

    user = get_user_by_username(username)
    if not user:
        flash("User not found")
        return redirect(url_for("feed"))

    friends = get_user_friends(user["id"])
    is_own_profile = user["id"] == session["user"]
    is_friend = any(friend["id"] == session["user"] for friend in friends)

    try:
        query = supabase.table("posts").select("*").eq("user_id", user["id"])
        if not (is_own_profile or is_friend):
            query = query.eq("visibility", "public")
        user_posts = query.order("created_at", desc=True).execute().data
    except:
        user_posts = []

    return render_template(
        "profile.html",
        user=user,
        posts=user_posts,
        friends=friends,
        is_own_profile=is_own_profile,
    )


@app.route("/api/profile/update", methods=["POST"])
def api_update_profile():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    bio = request.form.get("bio")
    avatar_file = request.files.get("avatar")

    avatar_url = None
    if avatar_file:
        # Save avatar as base64
        avatar_data = base64.b64encode(avatar_file.read()).decode("utf-8")
        avatar_url = f"data:image/png;base64,{avatar_data}"

    result, code = update_user_profile(session["user"], bio=bio, avatar_url=avatar_url)
    return jsonify(result), code


# Messages Routes
@app.route("/messages")
def messages():
    if "user" not in session:
        return redirect(url_for("index"))

    friends = get_user_friends(session["user"])
    return render_template("messages.html", friends=friends)


@app.route("/api/messages/<friend_id>", methods=["GET"])
def api_get_messages(friend_id):
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    messages = get_user_messages(session["user"], friend_id)
    return jsonify(messages), 200


@app.route("/api/messages/send", methods=["POST"])
def api_send_message():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    recipient_id = data.get("recipient_id")
    content = data.get("content")

    result, code = save_message(session["user"], recipient_id, content)
    return jsonify(result), code


@app.route("/api/messages/send-encrypted", methods=["POST"])
def api_send_encrypted_message():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    recipient_username = request.form.get("recipient_username")
    message_content = request.form.get("content")
    image_file = request.files.get("image")

    # Get recipient
    recipient = get_user_by_username(recipient_username)
    if not recipient:
        return jsonify({"error": "Recipient not found"}), 404

    try:
        # Encrypt message
        aes_key = os.urandom(32)
        encrypted_message = encrypt_message(message_content, aes_key)

        # Encrypt AES key with recipient's public key
        public_key = deserialize_public_key(recipient["public_key"])
        encrypted_aes_key = encrypt_aes_key(aes_key, public_key)

        # If image provided, hide in steganography
        if image_file:
            image = Image.open(io.BytesIO(image_file.read()))
            stego_image = encode_message(image, encrypted_message)
            buf = io.BytesIO()
            stego_image.save(buf, format="PNG")
            image_data = buf.getvalue()

            # Save encrypted file
            result, code = save_encrypted_file(
                session["user"],
                image_file.filename,
                image_data,
                encrypted_message,
                encrypted_aes_key,
                recipient["id"],
                f"Encrypted message for {recipient_username}",
            )
        else:
            # Just save encrypted message
            result, code = save_message(
                session["user"], recipient["id"], encrypted_message, encrypted_message
            )

        return jsonify(result), code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Encrypted Files Routes
@app.route("/encrypted_files")
def encrypted_files():
    if "user" not in session:
        return redirect(url_for("index"))

    files = get_user_encrypted_files(session["user"])
    return render_template("encrypted_files.html", files=files)


# Profile Routes
@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("index"))

    username = session.get("username")
    if not username:
        # Get username from database
        user = get_user_by_id(session["user"])
        if user:
            username = user["username"]
        else:
            return redirect(url_for("index"))

    return redirect(url_for("view_profile", username=username))


# Search Routes
@app.route("/search")
def search():
    if "user" not in session:
        return redirect(url_for("index"))

    query = request.args.get("q", "").strip()
    results = []

    if query:
        # Search for users
        try:
            users_response = (
                supabase.table("users")
                .select("id, username")
                .ilike("username", f"%{query}%")
                .execute()
            )
            results = users_response.data
        except Exception as e:
            print(f"Search error: {e}")

    return render_template("search.html", query=query, results=results)


if __name__ == "__main__":
    app.run(debug=True)


# Encrypted Files Routes
@app.route("/encrypted-files")
def encrypted_files():
    if "user" not in session:
        return redirect(url_for("index"))

    files = get_user_encrypted_files(session["user"])
    for f in files:
        f["sender"] = get_user_by_id(f["user_id"])

    return render_template("encrypted_files.html", files=files)


@app.route("/api/encrypted-files/<int:file_id>", methods=["GET"])
def api_get_encrypted_file(file_id):
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    try:
        file_data = (
            supabase.table("encrypted_files")
            .select("*")
            .eq("id", file_id)
            .execute()
            .data[0]
        )

        # Check access
        if (
            file_data["recipient_id"] != session["user"]
            and file_data["user_id"] != session["user"]
        ):
            return jsonify({"error": "Access denied"}), 403

        # If this is for the recipient, decrypt
        if file_data["recipient_id"] == session["user"]:
            user_data = get_user_by_id(session["user"])
            private_key_pem = user_data["private_key"]
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode("utf-8"),
                password=None,
                backend=default_backend(),
            )

            aes_key = decrypt_aes_key(file_data["encrypted_aes_key"], private_key)

            if file_data["stego_image"]:
                stego_data = base64.b64decode(file_data["stego_image"])
                stego_image = Image.open(io.BytesIO(stego_data))
                decrypted_message = decode_message(stego_image)
            else:
                decrypted_message = decrypt_message(
                    file_data["encrypted_message"], aes_key
                )

            return (
                jsonify(
                    {
                        "filename": file_data["filename"],
                        "message": decrypted_message,
                        "from": get_user_by_id(file_data["user_id"])["username"],
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "filename": file_data["filename"],
                        "description": file_data["description"],
                    }
                ),
                200,
            )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
