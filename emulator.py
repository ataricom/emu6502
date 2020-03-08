import enum
from status_reg import Flag


class Bus:
    def __init__(self):
        self.ram = [0] * 0xFFFF    # temporary RAM

    def read(self, address):
        if 0x0000 <= address <= 65536:
            return self.ram[address]

    def write(self, address, data):
        if 0x0000 <= address <= 0xffff:
            self.ram[address] = data


class CPU:
    a = 0
    x = 0
    y = 0
    sp = 0
    pc = 0
    status = Flag()

    fetched = 0
    temp = 0
    address_absolute = 0
    address_relative = 0
    opcode = 0
    current_byte = 0
    cycles = 0
    clock_count = 0
    halt = False

    def __init__(self):
        self.bus = Bus()
        self.read = self.bus.read
        self.write = self.bus.write

        self.lookup = [
            Instruction('BRK', self.BRK, self.IMM, 7),  # 0x00
            Instruction('ORA', self.ORA, self.IZX, 6),  # 0x01
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x02
            Instruction('XXX', self.XXX, self.IMP, 8),  # 0x03
            Instruction('XXX', self.XXX, self.IMP, 3),  # 0x04
            Instruction('ORA', self.ORA, self.ZP0, 3),  # 0x05
            Instruction('ASL', self.ASL, self.ZP0, 5),  # 0x06
            Instruction('XXX', self.XXX, self.IMP, 5),  # 0x07
            Instruction('PHP', self.PHP, self.IMP, 3),  # 0x08
            Instruction('ORA', self.ORA, self.IMM, 2),  # 0x09
            Instruction('ASL', self.ASL, self.IMP, 2),  # 0x0A
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x0B
            Instruction('XXX', self.XXX, self.IMP, 4),  # 0x0C
            Instruction('ORA', self.ORA, self.ABS, 4),  # 0x0D
            Instruction('ASL', self.ASL, self.ABS, 6),  # 0x0E
            Instruction('XXX', self.XXX, self.IMP, 6),  # 0x0F
            Instruction('BPL', self.BPL, self.REL, 2),  # 0x10
            Instruction('ORA', self.ORA, self.IZY, 5),  # 0x11
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x12
            Instruction('XXX', self.XXX, self.IMP, 8),  # 0x13
            Instruction('XXX', self.XXX, self.IMP, 4),  # 0x14
            Instruction('ORA', self.ORA, self.ZPX, 4),  # 0x15
            Instruction('ASL', self.ASL, self.ZPX, 6),  # 0x16
            Instruction('XXX', self.XXX, self.IMP, 6),  # 0x17
            Instruction('CLC', self.CLC, self.IMP, 2),  # 0x18
            Instruction('ORA', self.ORA, self.ABY, 4),  # 0x19
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x1A
            Instruction('XXX', self.XXX, self.IMP, 7),  # 0x1B
            Instruction('XXX', self.XXX, self.IMP, 4),  # 0x1C
            Instruction('ORA', self.ORA, self.ABX, 4),  # 0x1D
            Instruction('ASL', self.ASL, self.ABX, 7),  # 0x1E
            Instruction('XXX', self.XXX, self.IMP, 7),  # 0x1F
            Instruction('JSR', self.JSR, self.ABS, 6),  # 0x20
            Instruction('AND', self.AND, self.IZX, 6),  # 0x21
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x22
            Instruction('XXX', self.XXX, self.IMP, 8),  # 0x23
            Instruction('BIT', self.BIT, self.ZP0, 3),  # 0x24
            Instruction('AND', self.AND, self.ZP0, 3),  # 0x25
            Instruction('ROL', self.ROL, self.ZP0, 5),  # 0x26
            Instruction('XXX', self.XXX, self.IMP, 5),  # 0x27
            Instruction('PLP', self.PLP, self.IMP, 4),  # 0x28
            Instruction('AND', self.AND, self.IMM, 2),  # 0x29
            Instruction('ROL', self.ROL, self.IMP, 2),  # 0x2A
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x2B
            Instruction('BIT', self.BIT, self.ABS, 4),  # 0x2C
            Instruction('AND', self.AND, self.ABS, 4),  # 0x2D
            Instruction('ROL', self.ROL, self.ABS, 6),  # 0x2E
            Instruction('XXX', self.XXX, self.IMP, 6),  # 0x2F
            Instruction('BMI', self.BMI, self.REL, 2),  # 0x30
            Instruction('AND', self.AND, self.IZY, 5),  # 0x31
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x32
            Instruction('XXX', self.XXX, self.IMP, 8),  # 0x33
            Instruction('XXX', self.XXX, self.IMP, 4),  # 0x34
            Instruction('AND', self.AND, self.ZPX, 4),  # 0x35
            Instruction('ROL', self.ROL, self.ZPX, 6),  # 0x36
            Instruction('XXX', self.XXX, self.IMP, 6),  # 0x37
            Instruction('SEC', self.SEC, self.IMP, 2),  # 0x38
            Instruction('AND', self.AND, self.ABY, 4),  # 0x39
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x3A
            Instruction('XXX', self.XXX, self.IMP, 7),  # 0x3B
            Instruction('XXX', self.XXX, self.IMP, 4),  # 0x3C
            Instruction('AND', self.AND, self.ABX, 4),  # 0x3D
            Instruction('ROL', self.ROL, self.ABX, 7),  # 0x3E
            Instruction('XXX', self.XXX, self.IMP, 7),  # 0x3F
            Instruction('RTI', self.RTI, self.IMP, 6),  # 0x40
            Instruction('EOR', self.EOR, self.IZX, 6),  # 0x41
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x42
            Instruction('XXX', self.XXX, self.IMP, 8),  # 0x43
            Instruction('XXX', self.XXX, self.IMP, 3),  # 0x44
            Instruction('EOR', self.EOR, self.ZP0, 3),  # 0x45
            Instruction('LSR', self.LSR, self.ZP0, 5),  # 0x46
            Instruction('XXX', self.XXX, self.IMP, 5),  # 0x47
            Instruction('PHA', self.PHA, self.IMP, 3),  # 0x48
            Instruction('EOR', self.EOR, self.IMM, 2),  # 0x49
            Instruction('LSR', self.LSR, self.IMP, 2),  # 0x4A
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x4B
            Instruction('JMP', self.JMP, self.ABS, 3),  # 0x4C
            Instruction('EOR', self.EOR, self.ABS, 4),  # 0x4D
            Instruction('LSR', self.LSR, self.ABS, 6),  # 0x4E
            Instruction('XXX', self.XXX, self.IMP, 6),  # 0x4F
            Instruction('BVC', self.BVC, self.REL, 2),  # 0x50
            Instruction('EOR', self.EOR, self.IZY, 5),  # 0x51
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x52
            Instruction('XXX', self.XXX, self.IMP, 8),  # 0x53
            Instruction('XXX', self.XXX, self.IMP, 4),  # 0x54
            Instruction('EOR', self.EOR, self.ZPX, 4),  # 0x55
            Instruction('LSR', self.LSR, self.ZPX, 6),  # 0x56
            Instruction('XXX', self.XXX, self.IMP, 6),  # 0x57
            Instruction('CLI', self.CLI, self.IMP, 2),  # 0x58
            Instruction('EOR', self.EOR, self.ABY, 4),  # 0x59
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x5A
            Instruction('XXX', self.XXX, self.IMP, 7),  # 0x5B
            Instruction('XXX', self.XXX, self.IMP, 4),  # 0x5C
            Instruction('EOR', self.EOR, self.ABX, 4),  # 0x5D
            Instruction('LSR', self.LSR, self.ABX, 7),  # 0x5E
            Instruction('XXX', self.XXX, self.IMP, 7),  # 0x5F
            Instruction('RTS', self.RTS, self.IMP, 6),  # 0x60
            Instruction('ADC', self.ADC, self.IZX, 6),  # 0x61
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x62
            Instruction('XXX', self.XXX, self.IMP, 8),  # 0x63
            Instruction('XXX', self.XXX, self.IMP, 3),  # 0x64
            Instruction('ADC', self.ADC, self.ZP0, 3),  # 0x65
            Instruction('ROR', self.ROR, self.ZP0, 5),  # 0x66
            Instruction('XXX', self.XXX, self.IMP, 5),  # 0x67
            Instruction('PLA', self.PLA, self.IMP, 4),  # 0x68
            Instruction('ADC', self.ADC, self.IMM, 2),  # 0x69
            Instruction('ROR', self.ROR, self.IMP, 2),  # 0x6A
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x6B
            Instruction('JMP', self.JMP, self.IND, 5),  # 0x6C
            Instruction('ADC', self.ADC, self.ABS, 4),  # 0x6D
            Instruction('ROR', self.ROR, self.ABS, 6),  # 0x6E
            Instruction('XXX', self.XXX, self.IMP, 6),  # 0x6F
            Instruction('BVS', self.BVS, self.REL, 2),  # 0x70
            Instruction('ADC', self.ADC, self.IZY, 5),  # 0x71
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x72
            Instruction('XXX', self.XXX, self.IMP, 8),  # 0x73
            Instruction('XXX', self.XXX, self.IMP, 4),  # 0x74
            Instruction('ADC', self.ADC, self.ZPX, 4),  # 0x75
            Instruction('ROR', self.ROR, self.ZPX, 6),  # 0x76
            Instruction('XXX', self.XXX, self.IMP, 6),  # 0x77
            Instruction('SEI', self.SEI, self.IMP, 2),  # 0x78
            Instruction('ADC', self.ADC, self.ABY, 4),  # 0x79
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x7A
            Instruction('XXX', self.XXX, self.IMP, 7),  # 0x7B
            Instruction('XXX', self.XXX, self.IMP, 4),  # 0x7C
            Instruction('ADC', self.ADC, self.ABX, 4),  # 0x7D
            Instruction('ROR', self.ROR, self.ABX, 7),  # 0x7E
            Instruction('XXX', self.XXX, self.IMP, 7),  # 0x7F
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x80
            Instruction('STA', self.STA, self.IZX, 6),  # 0x81
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x82
            Instruction('XXX', self.XXX, self.IMP, 6),  # 0x83
            Instruction('STY', self.STY, self.ZP0, 3),  # 0x84
            Instruction('STA', self.STA, self.ZP0, 3),  # 0x85
            Instruction('STX', self.STX, self.ZP0, 3),  # 0x86
            Instruction('XXX', self.XXX, self.IMP, 3),  # 0x87
            Instruction('DEY', self.DEY, self.IMP, 2),  # 0x88
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x89
            Instruction('TXA', self.TXA, self.IMP, 2),  # 0x8A
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x8B
            Instruction('STY', self.STY, self.ABS, 4),  # 0x8C
            Instruction('STA', self.STA, self.ABS, 4),  # 0x8D
            Instruction('STX', self.STX, self.ABS, 4),  # 0x8E
            Instruction('XXX', self.XXX, self.IMP, 4),  # 0x8F
            Instruction('BCC', self.BCC, self.REL, 2),  # 0x90
            Instruction('STA', self.STA, self.IZY, 6),  # 0x91
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0x92
            Instruction('XXX', self.XXX, self.IMP, 6),  # 0x93
            Instruction('STY', self.STY, self.ZPX, 4),  # 0x94
            Instruction('STA', self.STA, self.ZPX, 4),  # 0x95
            Instruction('STX', self.STX, self.ZPY, 4),  # 0x96
            Instruction('XXX', self.XXX, self.IMP, 4),  # 0x97
            Instruction('TYA', self.TYA, self.IMP, 2),  # 0x98
            Instruction('STA', self.STA, self.ABY, 5),  # 0x99
            Instruction('TXS', self.TXS, self.IMP, 2),  # 0x9A
            Instruction('XXX', self.XXX, self.IMP, 5),  # 0x9B
            Instruction('XXX', self.XXX, self.IMP, 5),  # 0x9C
            Instruction('STA', self.STA, self.ABX, 5),  # 0x9D
            Instruction('XXX', self.XXX, self.IMP, 5),  # 0x9E
            Instruction('XXX', self.XXX, self.IMP, 5),  # 0x9F
            Instruction('LDY', self.LDY, self.IMM, 2),  # 0xA0
            Instruction('LDA', self.LDA, self.IZX, 6),  # 0xA1
            Instruction('LDX', self.LDX, self.IMM, 2),  # 0xA2
            Instruction('XXX', self.XXX, self.IMP, 6),  # 0xA3
            Instruction('LDY', self.LDY, self.ZP0, 3),  # 0xA4
            Instruction('LDA', self.LDA, self.ZP0, 3),  # 0xA5
            Instruction('LDX', self.LDX, self.ZP0, 3),  # 0xA6
            Instruction('XXX', self.XXX, self.IMP, 3),  # 0xA7
            Instruction('TAY', self.TAY, self.IMP, 2),  # 0xA8
            Instruction('LDA', self.LDA, self.IMM, 2),  # 0xA9
            Instruction('TAX', self.TAX, self.IMP, 2),  # 0xAA
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0xAB
            Instruction('LDY', self.LDY, self.ABS, 4),  # 0xAC
            Instruction('LDA', self.LDA, self.ABS, 4),  # 0xAD
            Instruction('LDX', self.LDX, self.ABS, 4),  # 0xAE
            Instruction('XXX', self.XXX, self.IMP, 4),  # 0xAF
            Instruction('BCS', self.BCS, self.REL, 2),  # 0xB0
            Instruction('LDA', self.LDA, self.IZY, 5),  # 0xB1
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0xB2
            Instruction('XXX', self.XXX, self.IMP, 5),  # 0xB3
            Instruction('LDY', self.LDY, self.ZPX, 4),  # 0xB4
            Instruction('LDA', self.LDA, self.ZPX, 4),  # 0xB5
            Instruction('LDX', self.LDX, self.ZPY, 4),  # 0xB6
            Instruction('XXX', self.XXX, self.IMP, 4),  # 0xB7
            Instruction('CLV', self.CLV, self.IMP, 2),  # 0xB8
            Instruction('LDA', self.LDA, self.ABY, 4),  # 0xB9
            Instruction('TSX', self.TSX, self.IMP, 2),  # 0xBA
            Instruction('XXX', self.XXX, self.IMP, 4),  # 0xBB
            Instruction('LDY', self.LDY, self.ABX, 4),  # 0xBC
            Instruction('LDA', self.LDA, self.ABX, 4),  # 0xBD
            Instruction('LDX', self.LDX, self.ABY, 4),  # 0xBE
            Instruction('XXX', self.XXX, self.IMP, 4),  # 0xBF
            Instruction('CPY', self.CPY, self.IMM, 2),  # 0xC0
            Instruction('CMP', self.CMP, self.IZX, 6),  # 0xC1
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0xC2
            Instruction('XXX', self.XXX, self.IMP, 8),  # 0xC3
            Instruction('CPY', self.CPY, self.ZP0, 3),  # 0xC4
            Instruction('CMP', self.CMP, self.ZP0, 3),  # 0xC5
            Instruction('DEC', self.DEC, self.ZP0, 5),  # 0xC6
            Instruction('XXX', self.XXX, self.IMP, 5),  # 0xC7
            Instruction('INY', self.INY, self.IMP, 2),  # 0xC8
            Instruction('CMP', self.CMP, self.IMM, 2),  # 0xC9
            Instruction('DEX', self.DEX, self.IMP, 2),  # 0xCA
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0xCB
            Instruction('CPY', self.CPY, self.ABS, 4),  # 0xCC
            Instruction('CMP', self.CMP, self.ABS, 4),  # 0xCD
            Instruction('DEC', self.DEC, self.ABS, 6),  # 0xCE
            Instruction('XXX', self.XXX, self.IMP, 6),  # 0xCF
            Instruction('BNE', self.BNE, self.REL, 2),  # 0xD0
            Instruction('CMP', self.CMP, self.IZY, 5),  # 0xD1
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0xD2
            Instruction('XXX', self.XXX, self.IMP, 8),  # 0xD3
            Instruction('XXX', self.XXX, self.IMP, 4),  # 0xD4
            Instruction('CMP', self.CMP, self.ZPX, 4),  # 0xD5
            Instruction('DEC', self.DEC, self.ZPX, 6),  # 0xD6
            Instruction('XXX', self.XXX, self.IMP, 6),  # 0xD7
            Instruction('CLD', self.CLD, self.IMP, 2),  # 0xD8
            Instruction('CMP', self.CMP, self.ABY, 4),  # 0xD9
            Instruction('NOP', self.NOP, self.IMP, 2),  # 0xDA
            Instruction('XXX', self.XXX, self.IMP, 7),  # 0xDB
            Instruction('XXX', self.XXX, self.IMP, 4),  # 0xDC
            Instruction('CMP', self.CMP, self.ABX, 4),  # 0xDD
            Instruction('DEC', self.DEC, self.ABX, 7),  # 0xDE
            Instruction('XXX', self.XXX, self.IMP, 7),  # 0xDF
            Instruction('CPX', self.CPX, self.IMM, 2),  # 0xE0
            Instruction('SBC', self.SBC, self.IZX, 6),  # 0xE1
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0xE2
            Instruction('XXX', self.XXX, self.IMP, 8),  # 0xE3
            Instruction('CPX', self.CPX, self.ZP0, 3),  # 0xE4
            Instruction('SBC', self.SBC, self.ZP0, 3),  # 0xE5
            Instruction('INC', self.INC, self.ZP0, 5),  # 0xE6
            Instruction('XXX', self.XXX, self.IMP, 5),  # 0xE7
            Instruction('INX', self.INX, self.IMP, 2),  # 0xE8
            Instruction('SBC', self.SBC, self.IMM, 2),  # 0xE9
            Instruction('NOP', self.NOP, self.IMP, 2),  # 0xEA
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0xEB
            Instruction('CPX', self.CPX, self.ABS, 4),  # 0xEC
            Instruction('SBC', self.SBC, self.ABS, 4),  # 0xED
            Instruction('INC', self.INC, self.ABS, 6),  # 0xEE
            Instruction('XXX', self.XXX, self.IMP, 6),  # 0xEF
            Instruction('BEQ', self.BEQ, self.REL, 2),  # 0xF0
            Instruction('SBC', self.SBC, self.IZY, 5),  # 0xF1
            Instruction('XXX', self.XXX, self.IMP, 2),  # 0xF2
            Instruction('XXX', self.XXX, self.IMP, 8),  # 0xF3
            Instruction('XXX', self.XXX, self.IMP, 4),  # 0xF4
            Instruction('SBC', self.SBC, self.ZPX, 4),  # 0xF5
            Instruction('INC', self.INC, self.ZPX, 6),  # 0xF6
            Instruction('XXX', self.XXX, self.IMP, 6),  # 0xF7
            Instruction('SED', self.SED, self.IMP, 2),  # 0xF8
            Instruction('SBC', self.SBC, self.ABY, 4),  # 0xF9
            Instruction('NOP', self.NOP, self.IMP, 2),  # 0xFA
            Instruction('XXX', self.XXX, self.IMP, 7),  # 0xFB
            Instruction('XXX', self.XXX, self.IMP, 4),  # 0xFC
            Instruction('SBC', self.SBC, self.ABX, 4),  # 0xFD
            Instruction('INC', self.INC, self.ABX, 7),  # 0xFE
            Instruction('XXX', self.XXX, self.IMP, 7),  # 0xFF
        ]

    def reset(self):
        # Look up starting address at 0xFFFC
        self.address_absolute = 0xFFFC
        lo_byte = self.bus.read(self.address_absolute + 0)
        hi_byte = self.bus.read(self.address_absolute + 1)
        self.pc = (hi_byte << 8) | lo_byte

        # Reset registers
        self.a = 0
        self.x = 0
        self.y = 0
        self.sp = 0xFD
        self.status.U = True

        self.address_absolute = 0
        self.address_relative = 0
        self.fetched = 0
        self.cycles = 8


    def irq(self):
        pass

    def nmi(self):
        pass

    def clock(self):
        if self.cycles == 0:
            self.opcode = self.read(self.pc)
            self.current_byte = self.lookup[self.opcode]
            self.pc += 1
            self.cycles = self.current_byte.cycles

            # get needed bytes per addressing mode
            # execute operator
            self.current_byte.addr_mode()
            self.current_byte.operator()
        self.cycles -= 1
        self.clock_count += 1
        print('clock: {}  cycle: {}  pc: {}  fetched: {}  opcode: {}'.format(
            self.clock_count, self.cycles, self.pc, self.fetched,
            self.lookup[self.opcode].name))

    def complete(self):
        pass

    def fetch(self):
        if not self.lookup[self.opcode].addr_mode == self.IMP():
            self.fetched = self.bus.read(self.address_absolute)
            # return self.fetched

    def IMP(self):      # addressing modes
        self.fetched = self.a
        self.cycles += 0

    def IMM(self):
        self.address_absolute = self.pc + 1
        print(f'addr_abs set to {self.address_absolute}')
        self.cycles += 0

    def ZP0(self):
        self.address_absolute = self.read(self.pc)
        self.pc += 1
        self.address_absolute &= 0x00FF
        self.cycles += 0

    def ZPX(self):
        self.address_absolute = self.read(self.pc) + self.x
        self.pc += 1
        self.address_absolute &= 0x00FF
        self.cycles += 0

    def ZPY(self):
        self.address_absolute = self.read(self.pc) + self.y
        self.pc += 1
        self.address_absolute &= 0x00FF
        self.cycles += 0

    def REL(self):
        self.address_relative = self.read(self.pc)
        self.pc += 1
        if self.address_relative & 0x80:
            self.address_relative |= 0xFF00
        self.cycles += 0

    def ABS(self):
        lo_byte = self.read(self.pc)
        self.pc += 1
        hi_byte = self.read(self.pc)
        self.pc += 1

        self.address_relative = (hi_byte << 8) | lo_byte
        self.cycles += 0

    def ABX(self):
        lo_byte = self.read(self.pc)
        self.pc += 1
        hi_byte = self.read(self.pc)
        self.pc += 1

        self.address_relative = (hi_byte << 8) | lo_byte
        self.address_relative += self.x

        if (self.address_relative & 0xFF00) != (hi_byte << 8):
            self.cycles += 1
        else:
            self.cycles += 0

    def ABY(self):
        lo_byte = self.read(self.pc)
        self.pc += 1
        hi_byte = self.read(self.pc)
        self.pc += 1

        self.address_relative = (hi_byte << 8) | lo_byte
        self.address_relative += self.y

        if (self.address_relative & 0xFF00) != (hi_byte << 8):
            self.cycles += 1
        else:
            self.cycles += 0

    def IND(self):
        lo_ptr = self.read(self.pc)
        self.pc += 1
        hi_ptr = self.read(self.pc)
        self.pc += 1

        pointer = (hi_ptr << 8) | lo_ptr
        if lo_ptr == 0x00FF:
            self.address_relative = (self.read(pointer & 0xFF00) << 8) | self.read(pointer + 0)
        else:
            self.address_relative = (self.read(pointer + 1) << 8) | self.read(pointer + 0)
        self.cycles += 0

    def IZX(self):
        temp = self.read(self.pc)
        self.pc += 1

        lo_byte = self.read((temp + self.x) & 0x00FF)
        hi_byte = self.read((temp + self.x + 1) & 0x00FF)
        self.address_absolute = (hi_byte << 8) | lo_byte
        self.cycles += 0

    def IZY(self):
        temp = self.read(self.pc)
        self.pc += 1

        lo_byte = self.read(temp & 0x00FF)
        hi_byte = self.read((temp + 1) & 0x00FF)

        self.address_absolute = (hi_byte << 8) | lo_byte
        self.address_absolute += self.y

        if (self.address_absolute & 0xFF00) != (hi_byte << 8):
            self.cycles += 1
        else:
            self.cycles += 0

    def ADC(self):      # instructions
        self.fetch()
        temp = self.a + self.fetched + int(self.status.C)
        self.status.C = bool(temp > 255)
        self.status.Z = bool((temp & 0x00FF) == 0)
        self.status.V = bool(-(self.a ^ self.fetched) & (self.a ^ temp) & 0x0080)
        self.cycles += 0

    def AND(self):
        self.fetch()
        self.a = self.a & self.fetched
        self.status.Z = bool(self.a == 0x00)
        self.status.N = bool(self.a & 0x80)

        # self.cycles += 0    # no additional clock cycles needed
        self.cycles += 0

    def ASL(self):
        self.fetch()
        temp = self.fetched << 1
        self.status.C = bool((temp & 0xFF00) > 0)
        self.status.Z = bool((temp & 0x00FF) == 0)
        if self.current_byte.addr_mode == self.IMP:
            self.a = temp & 0x00FF
        else:
            self.write(self.address_absolute, temp & 0x00FF)
        self.cycles += 0

    def BCC(self):
        if self.status.C == 0:
            self.cycles += 1
            self.address_absolute = self.pc + self.address_relative

            if (self.address_absolute & 0xFF00) != (self.pc & 0xFF00):
                self.cycles += 1

            self.pc = self.address_absolute
        self.cycles += 0

    def BCS(self):
        if self.status.C == 1:
            self.cycles += 1
            self.address_absolute = self.pc + self.address_relative

            if (self.address_absolute & 0xFF00) != (self.pc & 0xFF00):
                self.cycles += 1

            self.pc = self.address_absolute
        self.cycles += 0

    def BEQ(self):
        if self.status.Z == 1:
            self.cycles += 1
            self.address_absolute = self.pc + self.address_relative

            if (self.address_absolute & 0xFF00) != (self.pc & 0xFF00):
                self.cycles += 1

            self.pc = self.address_absolute
        self.cycles += 0

    def BIT(self):
        self.fetch()
        temp = self.a & self.fetched
        self.status.Z = bool((temp & 0x00FF) == 0)
        self.status.N = bool(self.fetched & (1 << 7))
        self.status.V = bool(self.fetched & (1 << 6))
        self.cycles += 0

    def BMI(self):
        if self.status.N == 1:
            self.cycles += 1
            self.address_absolute = self.pc + self.address_relative

            if (self.address_absolute & 0xFF00) != (self.pc & 0xFF00):
                self.cycles += 1

            self.pc = self.address_absolute
        self.cycles += 0

    def BNE(self):
        if self.status.Z == 0:
            self.cycles += 1
            self.address_absolute = self.pc + self.address_relative

            if (self.address_absolute & 0xFF00) != (self.pc & 0xFF00):
                self.cycles += 1

            self.pc = self.address_absolute
        self.cycles += 0

    def BPL(self):
        if self.status.N == 0:
            self.cycles += 1
            self.address_absolute = self.pc + self.address_relative

            if (self.address_absolute & 0xFF00) != (self.pc & 0xFF00):
                self.cycles += 1

            self.pc = self.address_absolute
        self.cycles += 0

    def BRK(self):
        self.pc += 1
        self.status.I = True
        self.write(0x0100 + self.sp, (self.pc >> 8) & 0x00FF)
        self.sp -= 1
        self.write(0x0100 + self.sp, self.sp & 0x00FF)
        self.sp -= 1

        self.status.B = True
        self.write(0x0100 + self.sp, self.status.get_byte())
        self.sp -= 1
        self.status.B = False
        self.pc = self.read(0xFFFE) | (self.read(0xFFFF) << 8)

        self.halt = True

        self.cycles += 0

    def BVC(self):
        if self.status.V == 0:
            self.cycles += 1
            self.address_absolute = self.pc + self.address_relative

            if (self.address_absolute & 0xFF00) != (self.pc & 0xFF00):
                self.cycles += 1

            self.pc = self.address_absolute
        self.cycles += 0

    def BVS(self):
        if self.status.V == 1:
            self.cycles += 1
            self.address_absolute = self.pc + self.address_relative

            if (self.address_absolute & 0xFF00) != (self.pc & 0xFF00):
                self.cycles += 1

            self.pc = self.address_absolute
        self.cycles += 0

    def CLC(self):
        self.status.C = False
        self.cycles += 0

    def CLD(self):
        self.status.D = False
        self.cycles += 0

    def CLI(self):
        self.status.I = False
        self.cycles += 0

    def CLV(self):
        self.status.V = False
        self.cycles += 0

    def CMP(self):
        self.fetch()
        temp = self.a - self.fetched
        self.status.C = bool(self.a >= self.fetched)
        self.status.Z = bool((temp & 0x00FF) == 0x0000)
        self.status.N = bool(temp & 0x0080)
        self.cycles += 1

    def CPX(self):
        self.fetch()
        temp = self.x - self.fetched
        self.status.C = bool(self.x >= self.fetched)
        self.status.Z = bool((temp & 0x00FF) == 0x0000)
        self.status.N = bool(temp & 0x0080)
        self.cycles += 0

    def CPY(self):
        self.fetch()
        temp = self.y - self.fetched
        self.status.C = bool(self.y >= self.fetched)
        self.status.Z = bool((temp & 0x00FF) == 0x0000)
        self.status.N = bool(temp & 0x0080)
        self.cycles += 0

    def DEC(self):
        self.fetch()
        temp = self.fetched - 1
        self.write(self.address_absolute, temp & 0x00FF)
        self.status.Z = bool((temp & 0x00FF) == 0x0000)
        self.status.N = bool(temp & 0x0080)
        self.cycles += 0

    def DEX(self):
        self.x -= 1
        self.status.Z = bool(self.x == 0x00)
        self.status.N = bool(self.x & 0x0080)
        self.cycles += 0

    def DEY(self):
        self.y -= 1
        self.status.Z = bool(self.y == 0x00)
        self.status.N = bool(self.y & 0x0080)
        self.cycles += 0

    def EOR(self):
        self.fetch()
        self.a = self.a ^ self.fetched
        self.status.Z = bool(self.a == 0x00)
        self.status.N = bool(self.a & 0x0080)
        self.cycles += 0

    def INC(self):
        self.fetch()
        temp = self.fetched + 1
        self.write(self.address_absolute, temp & 0x00FF)
        self.status.Z = bool((temp & 0x00FF) == 0x0000)
        self.status.N = bool(temp & 0x0080)
        self.cycles += 0

    def INX(self):
        self.x += 1
        self.status.Z = bool(self.x == 0x00)
        self.status.N = bool(self.x & 0x0080)
        self.cycles += 0

    def INY(self):
        self.y += 1
        self.status.Z = bool(self.y == 0x00)
        self.status.N = bool(self.y & 0x0080)
        self.cycles += 0

    def JMP(self):
        self.pc = self.address_absolute
        self.cycles += 0

    def JSR(self):
        self.pc -= 1

        self.write(0x0100 + self.sp, (self.pc << 8) & 0x00FF)
        self.sp -= 1
        self.write(0x0100 + self.sp, self.pc & 0x00FF)
        self.sp -= 1

        self.pc = self.address_absolute
        self.cycles += 0

    def LDA(self):
        self.fetch()
        self.a = self.fetched
        self.status.Z = bool(self.a == 0x00)
        self.status.N = bool(self.a & 0x0080)
        self.cycles += 1

    def LDX(self):
        self.fetch()
        self.x = self.fetched
        self.status.Z = bool(self.x == 0x00)
        self.status.N = bool(self.x & 0x0080)
        self.cycles += 0

    def LDY(self):
        self.fetch()
        self.y = self.fetched
        self.status.Z = bool(self.y == 0x00)
        self.status.N = bool(self.y & 0x0080)
        self.cycles += 0

    def LSR(self):
        self.cycles += 0

    def NOP(self):
        self.cycles += 0

    def ORA(self):
        self.cycles += 0

    def PHA(self):
        self.cycles += 0

    def PHP(self):
        self.cycles += 0

    def PLA(self):
        self.cycles += 0

    def PLP(self):
        self.cycles += 0

    def ROL(self):
        self.cycles += 0

    def ROR(self):
        self.cycles += 0

    def RTI(self):
        self.cycles += 0

    def RTS(self):
        self.cycles += 0

    def SBC(self):
        self.cycles += 0

    def SEC(self):
        self.cycles += 0

    def SED(self):
        self.cycles += 0

    def SEI(self):
        self.cycles += 0

    def STA(self):
        self.cycles += 0

    def STX(self):
        self.cycles += 0

    def STY(self):
        self.cycles += 0

    def TAX(self):
        self.cycles += 0

    def TAY(self):
        self.cycles += 0

    def TSX(self):
        self.cycles += 0

    def TXA(self):
        self.cycles += 0

    def TXS(self):
        self.cycles += 0

    def TYA(self):
        self.cycles += 0

    def XXX(self):
        self.cycles += 0


class Instruction:
    def __init__(self, name, operator, addr_mode, cycles):
        self.name = name
        self.operator = operator
        self.addr_mode = addr_mode
        self.cycles = cycles

