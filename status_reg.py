# flag byte used for status register
# bit flags are stored as bools
# can set_byte() to set the individual bits
# get_byte() returns single byte word


class Flag:
    def __init__(self):
        self.C = False  # 0b00000001
        self.Z = False  # 0b00000010
        self.I = False  # 0b00000100
        self.D = False  # 0b00001000
        self.B = False  # 0b00010000
        self.U = False  # 0b00100000
        self.V = False  # 0b01000000
        self.N = False  # 0b10000000

    def set_byte(self, byte):
        self.C = bool(byte & 0b00000001)
        self.Z = bool(byte & 0b00000010)
        self.I = bool(byte & 0b00000100)
        self.D = bool(byte & 0b00001000)
        self.B = bool(byte & 0b00010000)
        self.U = bool(byte & 0b00100000)
        self.V = bool(byte & 0b01000000)
        self.N = bool(byte & 0b10000000)

    def get_byte(self):
        byte = int(self.C << 0)
        byte += int(self.Z << 1)
        byte += int(self.I << 2)
        byte += int(self.D << 3)
        byte += int(self.B << 4)
        byte += int(self.U << 5)
        byte += int(self.V << 6)
        byte += int(self.N << 7)
        return byte

