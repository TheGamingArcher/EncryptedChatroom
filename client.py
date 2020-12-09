from Crypto.Hash import HMAC, SHA256
from Crypto.Cipher import Salsa20
import socket
import threading


class Client:
    def __init__(self):
        self.create_connection()

    def create_connection(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while 1:
            try:
                host = input('Enter host name --> ')
                port = int(input('Enter port --> '))
                self.s.connect((host, port))

                break
            except:
                print("Couldn't connect to server")

        self.username = input('Enter username --> ')
        self.s.send(self.username.encode())

        message_handler = threading.Thread(target=self.handle_messages, args=())
        message_handler.start()

        input_handler = threading.Thread(target=self.input_handler, args=())
        input_handler.start()

    def handle_messages(self):
        while 1:

            bs = self.s.recv(1204)
            try:
                bs.decode().find('New person joined the room. Username:')

            except UnicodeDecodeError:

                msg_nonce = bs[:8]
                ciphertext = bs[8:]
                secret = b'1234567890123456'
                cipher = Salsa20.new(key=secret, nonce=msg_nonce)
                bs = cipher.decrypt(ciphertext)
                ha = bs[:64]
                msg = bs[64:]
                print(msg.decode())
                fmac = HMAC.new(msg, digestmod=SHA256)

                try:
                    fmac.hexverify(ha)
                    print('This message has been verified via HMAC')

                except ValueError:
                    print("The message is wrong")

            else:
                print(bs.decode())

    def input_handler(self):
        while 1:
            inp = self.username + ' - ' + input()
            binp = bytes(inp.encode())
            h = HMAC.new(binp, digestmod=SHA256)
            plaintext = (h.hexdigest() + inp).encode()
            secret = b'1234567890123456'
            cipher = Salsa20.new(key=secret)
            ciphertext = cipher.nonce + cipher.encrypt(plaintext)
            self.s.send(ciphertext)


client = Client()
