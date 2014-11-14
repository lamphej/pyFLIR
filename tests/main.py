from pyflir.core import Camera, Packet

if __name__ == "__main__":
    # c = Camera("COM4", baud_rate=9600)
    # print c
    # c.close_connection()
    p = Packet()
    p.function = 0x0B
    p.bytecount = 0x0000
    serial_bytes = p.return_serial_packet()