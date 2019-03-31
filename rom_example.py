from migen import Module, Signal, Memory
from migen.build.platforms import tinyfpga_bx
from migen.build.generic_platform import Pins, Subsignal, IOStandard
from migen.fhdl import verilog

plat = tinyfpga_bx.Platform()
led = plat.request("user_led")

plat.add_extension([
    ("output", 0, Pins("A2 A1 B1 C2 C1 D2 D1 E2"), IOStandard("LVCMOS33"))
])
out = plat.request("output")

rom_image = range(0,256)

class RomExample(Module):

    def __init__(self, output):

        self.specials.rom = Memory(8, 16384, rom_image)
        rom_port = self.rom.get_port(write_capable=False)
        self.specials += rom_port

        counter = Signal(16)
        self.sync += counter.eq(counter + 1)
        self.comb += rom_port.adr.eq(counter)
        self.comb += output.eq(rom_port.dat_r)

example = RomExample(out)
#print(verilog.convert(example))
plat.build(example, build_name='test')

