import hashlib
import time


def generate_sha256(data):
    string = str(data)+str(time.time())+"playland_created_by_yemre"
    hash = hashlib.sha256(f'{string}'.encode()).hexdigest()
    return hash[:8]


def in_array(data, liste):
    for i in liste:
        if i == data:
            return True
    return False
