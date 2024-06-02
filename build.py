import os
import subprocess
from dotenv import load_dotenv


def build():
    load_dotenv()

    token = os.getenv('BOT_TOKEN')
    openai_api = os.getenv('API_KEY')
    admin_ids = os.getenv('ADMIN_IDS')
    host = os.getenv('HOST')
    database = os.getenv('DATABASE')
    port = os.getenv('PORT')
    user = os.getenv('DB_USER')
    password = os.getenv('PASSWORD')

    docker_build_command = [
        'sudo', 'docker', 'build',
        f'--build-arg', f'BOT_TOKEN={token}',
        f'--build-arg', f'API_KEY={openai_api}',
        f'--build-arg', f'ADMIN_IDS={admin_ids}',
        f'--build-arg', f'HOST={host}',
        f'--build-arg', f'PORT={port}',
        f'--build-arg', f'DB_USER={user}',
        f'--build-arg', f'PASSWORD={password}',
        f'--build-arg', f'DATABASE={database}',
        '-t', 'telegram-bot:latest',
        '.'
    ]

    # Run the Docker build command
    try:
        subprocess.run(docker_build_command, check=True)
        print("Docker build completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Docker build failed with return code {e.returncode}.")


if __name__ == '__main__':
    build()
