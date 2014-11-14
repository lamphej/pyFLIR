import serial
import crcmod
from pyflir.constants import STATUS_BYTES

class Camera(object):

    def __init__(self, serial_port, baud_rate=57600):
        self.serial_connection = serial.Serial(
            port=serial_port,
            baudrate=baud_rate,
            parity=serial.PARITY_NONE,
            stopbits=1,
            xonxoff=False
        )

    def close_connection(self):
        if self.serial_connection._isOpen:
            self.serial_connection.close()

class Packet(object):
    """
        Byte #      Upper Byte          Comments
        1           Process Code        Set to 0x6E on all valid incoming and reply messages
        2           Status              See 3.2.1
        3           Reserved
        4           Function            See 3.2.2
        5           Byte Count (MSB)    See 3.2.3
        6           Byte Count (LSB)
        7           CRC1 (MSB)          See 3.2.4
        8           CRC1 (LSB)
        N           Argument            See 3.2.5
        N+1         CRC2 (MSB)          See 3.2.4
        N+2         CRC2 (LSB)
    """

    def __init__(self, **kwargs):
        self.process_code = 0x6E
        self.status = kwargs.get('status', STATUS_BYTES.CAM_OK)
        self.reserved = kwargs.get('reserved', 0x00)
        self.function = kwargs.get('function', 0x00)
        self.bytecount = kwargs.get('bytecount', 0x00)
        self.bytecount_msb = kwargs.get('bytecount_msb', 0x00)
        self.bytecount_lsb = kwargs.get('bytecount_lsb', 0x00)
        self.crc1 = 0x00
        self.args = []

    def MSB(self, n):
        ndx = 0
        while ( 1 < n ):
            n = ( n >> 1 )
            ndx += 1
        return ndx

    def return_serial_packet(self):
        bytecount_binstr = bin(self.bytecount).replace('b', '')
        # try:
        #     self.bytecount_msb = len(bytecount_binstr)-bytecount_binstr.index('1')
        #     for i in range(len(bytecount_binstr)):
        #         if bytecount_binstr[i] == '1':
        #             self.bytecount_lsb = len(bytecount_binstr)-i
        # except:
        #     pass
        self.bytecount_msb = self.MSB(self.bytecount)
        bin_str = bin(self.process_code).replace('0b', '')
        bin_str += bin(self.status).replace('0b', '')
        bin_str += bin(self.reserved).replace('0b', '')
        bin_str += bin(self.function).replace('0b', '')
        bin_str += bin(self.bytecount_msb).replace('0b', '')
        bin_str += bin(self.bytecount_lsb).replace('0b', '')
        bin_str += "0"*16
        rev = bin_str[::-1]
        bin_sum = sum([pow(2, i) for i in range(len(rev)) if rev[i]=='1'])
        crc = self.byte_crc(bin_str)
        print crc
        return crc

    def calculate_crc(self):
        byte_str = bin(self.process_code).replace('b', '').ljust(16, '0')
        print byte_str

    def should_xor(self, word, polynomial):
        msb = polynomial.index('1')
        return word[msb] == '1'

    def raw_byte_crc(self, b):
        return self.byte_crc(bin(b).replace('b', '') + "0"*16)

    def byte_crc(self, b):
        polynomial = '10001000000100001'

        previous_word = b
        init_length = len(previous_word)
        crc = ''
        while len(polynomial) < init_length:
            do_xor  = self.should_xor(previous_word, polynomial)
            if do_xor:
                crc = ''.join([str(int(previous_word[i])^int(polynomial[i])) for i in range(len(polynomial))])
                crc += "0"*(init_length-len(crc))
            else:
                crc = previous_word
            previous_word = crc
            polynomial = "0" + polynomial
        rev_word = crc[::-1]
        bin_sum = sum([pow(2, i) for i in range(len(rev_word)) if rev_word[i]=='1'])
        return hex(bin_sum)