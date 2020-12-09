from Crypto.Hash import HMAC, SHA256
from Crypto.Cipher import Salsa20
import socket
import threading


class Client:
    def __init__(self):
        self.create_connection()

    def create_connection(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        global secret

        while 1:
            try:
                host = input('Enter host name --> ')
                port = int(input('Enter port --> '))
                secret = input('Enter password --> ')

                #Secret is the password. it is modified to ensure it is the required 16 bytes to be used as the key.
                while len(secret) < 16:
                    secret += '0'
                secret = bytes(secret.encode())

                #the SHA-256 algorithm used to generate HMACs is also used to store the secret key
                h = HMAC.new(secret, digestmod=SHA256)
                if h.hexdigest() != 'add3939f9ece211a60559d606d3cb6e53a78769bf9cee24c279088fcc866f212':
                    print('Incorrect Password')
                    return
                #if the user enters the wrong password the hash will not match and the program is terminated
                self.s.connect((host, port))
                break
            except:
                print("Couldn't connect to server")

        #This is where the user inputs their user name and then connects to the chatroom
        self.username = input('Enter username --> ')
        self.s.send(self.username.encode())
        message_handler = threading.Thread(target=self.handle_messages, args=())
        message_handler.start()

        input_handler = threading.Thread(target=self.input_handler, args=())
        input_handler.start()

    def handle_messages(self):
        while 1:

            bs = self.s.recv(1204)
            #the program tries to decode the incoming bytes
            #while the messages coming from other users are encrypted with Salsa20, the server messages are not
            #The encrypted messages would raise an error using decode(), so they are handled by the except DecodeError
            try:
                bs.decode()
            except UnicodeDecodeError:

                #the first 8 bytes of the ciphertext are the nonce. The recipient needs this to decrypt
                nonce = bs[:8]
                ciphertext = bs[8:]
                #A salsa20 object is created to carry out decryption
                cipher = Salsa20.new(key=secret, nonce=nonce)
                bs = cipher.decrypt(ciphertext)
                #After decryption, the first 64 bytes are the HMAC to be verified. The rest of the message is plaintext
                ha = bs[:64]
                msg = bs[64:]
                print(msg.decode())
                fmac = HMAC.new(msg, digestmod=SHA256)

                try:
                    fmac.hexverify(ha)
                   # print('This message has been verified via HMAC')
                #With the line above, the user is notified that incoming messages have been verified by HMAC.
                except ValueError:
                    print("The message is wrong")

            else:
                print(bs.decode())

    #The method used to handle encryption and sending out ciphertext
    def input_handler(self):
        while 1:
            inp = self.username + ' - ' + input()
            binp = bytes(inp.encode())
            # HMAC was used to authenticate the message. Hexdigest converts the hash to print/readable hexadecimal
            h = HMAC.new(binp, digestmod=SHA256)
            #the plaintext is combined here with the HMAC. These are then encypted together
            plaintext = (h.hexdigest() + inp).encode()
            # A salsa20 object is created to carry out encryption
            cipher = Salsa20.new(key=secret)
            ciphertext = cipher.nonce + cipher.encrypt(plaintext)
            self.s.send(ciphertext)


client = Client()
