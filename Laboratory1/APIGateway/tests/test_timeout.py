import unittest
from http.server import SimpleHTTPRequestHandler, HTTPServer
from multiprocessing import Process
from time import sleep

import requests
import requests_mock

import gatewayConfigDefault

# Your gateway's configuration
GATEWAY_URL = 'http://localhost:5000'
DELAY_SERVER_PORT = 8080  # A separate port for our delay server
DELAY_TIME = 10  # The delay server will wait this long before responding


# Delay server
class DelayedHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        sleep(DELAY_TIME)  # Intentional delay
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')


def run_delay_server():
    server_address = ('', DELAY_SERVER_PORT)
    httpd = HTTPServer(server_address, DelayedHTTPRequestHandler)
    httpd.serve_forever()


class TestTimeout(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Start the delay server in a separate process
        cls.delay_server_process = Process(target=run_delay_server)
        cls.delay_server_process.start()

    @classmethod
    def tearDownClass(cls):
        # Terminate the delay server
        cls.delay_server_process.terminate()

    def test_timeout(self):
        # Mock the service discovery to return the delay server's address
        mocked_service_address = f'http://localhost:{DELAY_SERVER_PORT}'

        with requests_mock.Mocker() as m:
            m.get(f'{gatewayConfigDefault.SERVICE_DISCOVERY}discover/testservice', json={'service_address': mocked_service_address})

            m.get(f'{GATEWAY_URL}/testservice/somepath', json={"message": "This is a mock response"}, status_code=504)

            response = requests.get(f'{GATEWAY_URL}/testservice/somepath')
            self.assertEqual(response.status_code, 504)  # Expecting a timeout response


if __name__ == '__main__':
    unittest.main()
