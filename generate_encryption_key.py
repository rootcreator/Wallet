import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load the .env file if it exists
load_dotenv()

# Check if the encryption key already exists in the .env file
ENCRYPTION_SECRET_KEY = os.getenv("ENCRYPTION_SECRET_KEY")

if not ENCRYPTION_SECRET_KEY:
    # Generate a new Fernet encryption key
    key = Fernet.generate_key().decode()

    # Print the generated key
    print(f"Generated Encryption Key: {key}")

    # Save the key to .env file
    with open(".env", "a") as f:
        f.write(f"\nENCRYPTION_SECRET_KEY={key}\n")

    print(f"Encryption key saved to .env file.")
else:
    print(f"Encryption Key already exists in .env file: {ENCRYPTION_SECRET_KEY}")
