import secrets
import os


def generate_key():
    # Generate a random key
    key = secrets.token_urlsafe(32)
    env_file = ".env"

    if not os.path.exists(env_file):
        print(f"Creating {env_file} from .env.example...")
        if os.path.exists(".env.example"):
            with open(".env.example", "r") as f:
                content = f.read()
            with open(env_file, "w") as f:
                f.write(content)
        else:
            with open(env_file, "w") as f:
                f.write(f"API_SECRET_KEY={key}\n")

    # Update the key in .env
    with open(env_file, "r") as f:
        lines = f.readlines()

    with open(env_file, "w") as f:
        found = False
        for line in lines:
            if line.startswith("API_SECRET_KEY="):
                f.write(f"API_SECRET_KEY={key}\n")
                found = True
            else:
                f.write(line)
        if not found:
            f.write(f"\nAPI_SECRET_KEY={key}\n")

    print(f"Successfully updated API_SECRET_KEY in {env_file}")
    print(f"New Key: {key}")


if __name__ == "__main__":
    generate_key()
