from time import sleep
import socket
import sys

class LED_client:
    def __init__(self):
        server_address = ('localhost', 10000)
        try:
            # Create a TCP/IP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect the socket to the port where the server is listening
            print >>sys.stderr, 'connecting to %s port %s' % server_address
            self.sock.connect(server_address)
            self.set_mode("rainbow")
        except:
            print 'connecting to %s port %s failed!' % server_address

    def set_mode(self, mode):
        try:
            # Send data
            print >>sys.stderr, 'sending "%s"' % mode
            self.sock.sendall(mode)

            # Look for the response
            amount_received = 0
            amount_expected = len(mode)

            while amount_received < amount_expected:
                data = self.sock.recv(16)
                amount_received += len(data)
                print >>sys.stderr, 'received "%s"' % data
        except:
            print("sending failed")

    def close(self):
        print >>sys.stderr, 'closing socket'
        self.sock.close()

# Main program logic follows:
if __name__ == '__main__':
    led = LED_client()
    led.set_mode("countdown")
    sleep(10)
    led.set_mode("finished")
    led.close()
