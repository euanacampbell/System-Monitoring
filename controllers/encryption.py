import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet


class Encryption():

    def __init__(self,):
        encodedInput = "initialinsert" # This is input in the form of a string
        derive = encodedInput.encode() # Convert to type bytes

        salt = b'lotsandlotsofpsssalt' # CHANGE THIS - recommend using a key from os.urandom(16), must be of type bytes
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        self.key = base64.urlsafe_b64encode(kdf.derive(derive)) # Can only use kdf once
    
    def Encrypt(self,message):

        message = message.encode()
        f = Fernet(self.key)
        encrypted = f.encrypt(message)

        return(encrypted.decode("utf-8"))

    def Decrypt(self,message):
        
        message = str.encode(message)
        f = Fernet(self.key)
        decrypted = f.decrypt(message)

        return(decrypted.decode("utf-8"))
    
    def DecryptPasswords(self, encrypted):

        decryptedList = {}
        for i in encrypted:
            decrypted = self.Decrypt(i[2])
            decryptedList[i[1]] = decrypted
        
        return(decryptedList)