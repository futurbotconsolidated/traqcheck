import requests
import secrets
import string
from django.conf import settings


def parse_resume_file(resume_file):
    try:
        files = {'file': (resume_file.name, resume_file.read(), resume_file.content_type)}
        response = requests.post(settings.RESUME_PARSER_URL, files=files, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Resume parser service error: {str(e)}")


def generate_random_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password
