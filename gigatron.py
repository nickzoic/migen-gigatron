from migen import Module, Signal, Memory
from migen.build.platforms import tinyfpga_bx
from migen.build.generic_platform import Pins, Subsignal, IOStandard
from migen.fhdl import verilog
from migen.fhdl.structure import Mux, Cat, If, Case

import array

plat = tinyfpga_bx.Platform()
plat.add_extension([
    ("output", 0, Pins("B1 C2 C1 D2 D1 E2 E1 G2"), IOStandard("LVCMOS33")),
    ("input", 0, Pins("H1 J1 H2 H9 D9 D8 C9 A9"), IOStandard("LVCMOS33")),
])
output = plat.request("output")
dinput = plat.request("input")

with open("gigatron-rom/ROMv3.rom", "rb") as fh:
    rom_image = array.array("H", fh.read())

class Gigatron(Module):

    def __init__(self):

        self.specials.rom = Memory(16, 4096, rom_image)
        rom_port = self.rom.get_port(write_capable=False)
        self.specials += rom_port

        self.specials.ram = Memory(8, 8192, rom_image)
        ram_port = self.ram.get_port(write_capable=True)
        self.specials += ram_port

        program_counter = Signal(16)
        self.sync += program_counter.eq(program_counter + 1)
        self.comb += rom_port.adr.eq(program_counter)

        op_code = Signal(3)
        op_mode = Signal(3)
        op_bus = Signal(2)
        op_data = Signal(8)
        Cat(op_bus, op_mode, op_code, op_data).eq(rom_port.dat_r)
      
        inst_decode = Signal(7)
        Case(op_code, {
            0: inst_decode.eq(0),
            1: inst_decode.eq(0),
            2: inst_decode.eq(0),
            3: inst_decode.eq(0),
            4: inst_decode.eq(0),
            5: inst_decode.eq(0),
            6: inst_decode.eq(0),
            7: inst_decode.eq(0),
        })
        sig_ar0 = Signal(1)
        sig_ar1 = Signal(1)
        sig_ar2 = Signal(1)
        sig_ar3 = Signal(1)
        sig_al = Signal(1)
        sig_ld2 = Signal(1)
        sig_ph1 = Signal(1)
        Cat(sig_ar0, sig_ar1, sig_ar2, sig_ar3, sig_al, sig_ld2, sig_ph1).eq(inst_decode)

        mode_decode = Signal(7)
        Case(op_mode, {
            0: mode_decode.eq(0),
            1: mode_decode.eq(0),
            2: mode_decode.eq(0),
            3: mode_decode.eq(0),
            4: mode_decode.eq(0),
            5: mode_decode.eq(0),
            6: mode_decode.eq(0),
            7: mode_decode.eq(0),
        })
        sig_xl = Signal(1)
        sig_yl = Signal(1)
        sig_ix = Signal(1)
        sig_eh = Signal(1)
        sig_el = Signal(1)
        sig_ol1 = Signal(1)
        sig_ld1 = Signal(1)
        sig_ph2 = Signal(1)
        Cat(sig_xl, sig_yl, sig_ix, sig_eh, sig_el, sig_ol1, sig_ld1, sig_ph2).eq(mode_decode)

        sig_ld = Signal(1)
        sig_ld.eq(sig_ld1 | sig_ld2)

        sig_ph = Signal(1)
        sig_ph.eq(sig_ph1 | sig_ph2)

        data_bus = Signal(8)
        accumulator = Signal(8)

        Case(op_bus, {
            0: data_bus.eq(op_data),
            1: data_bus.eq(ram_port.dat_r),
            2: data_bus.eq(accumulator),
            3: data_bus.eq(dinput),
        })

        register_x = Signal(8)
        register_y = Signal(8)
        ram_addr_l = Signal(8)
        ram_addr_h = Signal(8)
        ram_addr_l.eq(Mux(sig_el, register_x, data_bus))
        ram_addr_h.eq(Mux(sig_eh, register_y, 0))
        self.comb += ram_port.adr.eq(Cat(ram_addr_l, ram_addr_h))

        self.comb += ram_port.we.eq(rom_port.dat_r[0])
        self.comb += ram_port.dat_w.eq(rom_port.dat_r[0:8])
        self.comb += output.eq(ram_port.dat_r[0:8])


gigatron = Gigatron()
#print(verilog.convert(gigatron))
plat.build(gigatron, build_name='gigatron')

