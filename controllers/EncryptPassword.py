



from encryption   import Encryption



if __name__ == "__main__":

    encryption = Encryption()

    message = input( "What would you like to Encrpt?\n" )

    encrypted = encryption.Encrypt(message)

    print( "Encrypted message is: " + encrypted )