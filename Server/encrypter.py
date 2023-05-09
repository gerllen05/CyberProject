from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
import os
import base64
import hashlib


class Encrypter:
    def __init__(self, key):
        self.SALT = "y78wqeher8b23"
        self.KEY = key

    def base64Encoding(self, input):
        dataBase64 = base64.b64encode(input)
        dataBase64P = dataBase64.decode("UTF-8")
        return dataBase64P

    def base64Decoding(self, input):
        return base64.decodebytes(input.encode("ascii"))

    def hash_secret_key(self):
        return hashlib.sha256(self.SALT.encode() + self.KEY).hexdigest()

    def encrypt(self, data_to_encrypt: bytes):
        passwordBytes = self.hash_secret_key().encode()
        salt = get_random_bytes(32)
        PBKDF2_ITERATIONS = 15000
        encryptionKey = PBKDF2(passwordBytes, salt, 32, count=PBKDF2_ITERATIONS, hmac_hash_module=SHA256)
        cipher = AES.new(encryptionKey, AES.MODE_CBC)
        ciphertext = cipher.encrypt(pad(data_to_encrypt, AES.block_size))
        ivBase64 = self.base64Encoding(cipher.iv)
        saltBase64 = self.base64Encoding(salt)
        ciphertextBase64 = self.base64Encoding(ciphertext)
        return f"{saltBase64}:{ivBase64}:{ciphertextBase64}".encode()

    def decrypt(self, encrypted_data: bytes):
        passwordBytes = self.hash_secret_key().encode()
        data = encrypted_data.decode().split(":")
        salt = self.base64Decoding(data[0])
        iv = self.base64Decoding(data[1])
        ciphertext = self.base64Decoding(data[2])
        PBKDF2_ITERATIONS = 15000
        decryptionKey = PBKDF2(passwordBytes, salt, 32, count=PBKDF2_ITERATIONS, hmac_hash_module=SHA256)
        cipher = AES.new(decryptionKey, AES.MODE_CBC, iv)
        decryptedtext = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return decryptedtext