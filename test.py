import migen
from migen.build.platforms import tinyfpga_bx
plat = tinyfpga_bx.Platform()

import array

# Note: ROM is 16-bit, file format has opcode byte then data byte.
# On the schematic, data byte is shown as higher bits of the word
# so we leave them in that order here.
#   LD $01 --> 0001 in .asm --> 00 01 in .rom --> 256 in this array.

with open("gigatron-rom/ROMv3.rom", "rb") as fh:
    rom_image = array.array("H", fh.read())

class Gigatron(migen.Module):

    def __init__(self, output):
        ram = migen.Memory(16, 32768)
        self.specials += ram
        ram_port = ram.get_port(write_capable=True, we_granularity=8)
        self.specials += ram_port

        rom = migen.Memory(16, 32768, rom_image)
        self.specials += rom
        rom_port = rom.get_port(write_capable=False)
        self.specials += rom_port

        self.counter = migen.Signal(17)
        self.comb += ram_port.adr.eq(self.counter)
        self.comb += rom_port.adr.eq(self.counter)
        self.comb += output.eq(ram_port.dat_r[0] & rom_port.dat_r[0] & ram_port.dat_r[1])
        self.sync += self.counter.eq(self.counter + 1)

led = plat.request("user_led")

gigatron = Gigatron(led)
plat.build(gigatron, build_name='test')
