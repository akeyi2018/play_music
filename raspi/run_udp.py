from udp_8_band import Udp_server_led

def run_led():
    udp_server = Udp_server_led()
    udp_server.run()

run_led()
