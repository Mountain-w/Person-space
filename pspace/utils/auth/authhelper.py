from django.contrib.auth.models import User
import os.path
import base64
from rsa.pkcs1 import DecryptionError
import rsa
from utils.exceptions.exceptions import TokenOutDate, TokenInvalid
from datetime import datetime, timedelta
from pspace.settings import BASE_DIR

file_path = os.path.join(BASE_DIR, 'keys')


def load_keys():
    with open(file_path + '/public.pem', 'rb') as f:
        public_key = rsa.PublicKey.load_pkcs1(f.read())

    with open(file_path + '/private.pem', 'rb') as f:
        private_key = rsa.PrivateKey.load_pkcs1(f.read())

    return public_key, private_key


def generate_token(username, expire=5):
    public_key, _ = load_keys()
    time = str(datetime.now().date())
    playload = ':'.join((username, time, str(expire))).encode('utf-8')
    token = rsa.encrypt(playload, public_key)
    return base64.encodebytes(token).decode('utf-8').replace('\n', '')


def generate_token_for_test(username, expire=5):
    public_key, _ = load_keys()
    time = str(datetime.now().date())
    playload = ':'.join((username, time, str(expire))).encode('utf-8')
    token = rsa.encrypt(playload, public_key)
    return base64.encodebytes(token).decode('utf-8')


def checkout_token(token):
    _, private_key = load_keys()
    try:
        token = base64.decodebytes(token.encode('utf-8'))
        content = rsa.decrypt(token, private_key)
    except Exception:
        raise TokenInvalid('Invalid token')
    playload = content.decode('utf-8')
    username, date, outdate = playload.split(':')
    if not checkout_date(date, outdate):
        raise TokenOutDate('Your token has OutDate')


def checkout_date(date, outdate):
    now = datetime.now().date()
    date = datetime.strptime(date, '%Y-%m-%d').date()
    if (now - date).days > int(outdate):
        return False
    return True


def get_user(token):
    token = base64.decodebytes(token.encode('utf-8'))
    _, private_key = load_keys()
    content = rsa.decrypt(token, private_key)
    playload = content.decode('utf-8')
    username = playload.split(':')[0]
    return User.objects.get(username=username)


def get_user_for_test(token):
    token = base64.decodebytes(token.encode('utf-8'))
    _, private_key = load_keys()
    content = rsa.decrypt(token, private_key)
    playload = content.decode('utf-8')
    username = playload.split(':')[0]
    return username
