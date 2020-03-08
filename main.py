import emulator as emu

cpu = emu.CPU()
cpu.bus.ram[0xFFFC] = 0x00
cpu.bus.ram[0xFFFD] = 0x00
cpu.bus.ram[0x0000] = 0xA9
cpu.bus.ram[0x0001] = 0x01
cpu.bus.ram[0x0002] = 0x65
cpu.bus.ram[0x0003] = 0x01
cpu.bus.ram[0x0004] = 0x4C
cpu.bus.ram[0x0005] = 0x02
cpu.bus.ram[0x0006] = 0x00

# LDA 0x01
# ADC 0x01
# JMP 0x02

cpu.reset()
x = 0

while x < 1000:
    cpu.clock()
    x += 1
