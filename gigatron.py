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

# opcode and mode constants.

OP_LD, OP_AND, OP_OR, OP_XOR, OP_ADD, OP_SUB, OP_ST, OP_BCC = range(0,8)
MOD_DAC, MOD_XAC, MOD_YDAC, MOD_YXAC, MOD_DX, MOD_DY, MOD_DOUT, MOD_YXOUT = range(0,8)
MOD_JMP, MOD_BGT, MOD_BLT, MOD_BNE, MOD_BEQ, MOD_BGE, MOD_BLE, MOD_BRA = range(0,8)

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

        accumulator = Signal(8)

        op_code = Signal(3)
        op_mode = Signal(3)
        op_bus = Signal(2)
        op_data = Signal(8)
        Cat(op_bus, op_mode, op_code, op_data).eq(rom_port.dat_r)
     
        sig_ar0 = Signal()
        sig_ar0.eq((op_code == OP_SUB) | (op_code == OP_BCC))
        sig_ar1 = Signal()
        sig_ar1.eq((op_code == OP_OR) | (op_code == OP_XOR) | (op_code == OP_SUB))
        sig_ar2 = Signal()
        sig_ar2.eq((op_code == OP_LD) | (op_code == OP_OR) | (op_code == OP_XOR) | (op_code == OP_ADD) | (op_code == OP_BCC))
        sig_ar3 = Signal()
        sig_ar3.eq((op_code == OP_LD) | (op_code == OP_AND) | (op_code == OP_OR) | (op_code == OP_ADD))
        sig_al = Signal()
        sig_al.eq((op_code == OP_BCC) | (~op_code[2]))

        sig_xl = Signal()
        sig_xl.eq(op_mode != MOD_DX)
        sig_yl = Signal()
        sig_yl.eq(op_mode != MOD_DY)
        sig_ix = Signal()
        sig_ix.eq(op_mode == MOD_YXOUT) 
        sig_eh = Signal()
        sig_eh.eq((op_mode != MOD_YDAC) & (op_mode != MOD_YXAC) & (op_mode != MOD_YXOUT))
        sig_el = Signal()
        sig_el.eq((op_mode != MOD_XAC) & (op_mode != MOD_YXAC) & (op_mode != MOD_YXOUT))
        
        sig_ol = Signal()
        sig_ol.eq(((op_mode != MOD_DOUT) & (op_mode != MOD_YXOUT)) | (op_code == OP_ST))
        sig_ld = Signal()
        sig_ld.eq(((op_mode != MOD_DAC) & (op_mode != MOD_XAC) & (op_mode != MOD_YDAC) & (op_mode != MOD_YXAC)) | (op_code == OP_ST))

        # this isn't quite right, in the schematic it's all about AC7 and the
        # carry-out of the ALU adder, hmmm.

        sig_cond = Signal()
        sig_cond.eq(
                (op_mode == MOD_JMP) | (op_mode == MOD_BRA) |
                ((op_mode == MOD_BNE) & (accumulator != 0)) |
                ((op_mode == MOD_BEQ) & (accumulator == 0)) |
                ((op_mode == MOD_BLT) & (accumulator < 0)) |
                ((op_mode == MOD_BGT) & (accumulator > 0)) |
                ((op_mode == MOD_BLE) & (accumulator <= 0)) |
                ((op_mode == MOD_BGE) & (accumulator >= 0))
        )

        sig_ph = Signal()
        sig_ph.eq((op_code == OP_BCC) & (op_mode == MOD_JMP))
        sig_pl = Signal()
        sig_pl.eq((op_code == OP_BCC) & sig_cond)
        
        data_bus = Signal(8)

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

