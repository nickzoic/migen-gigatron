from migen import *
from migen.build.platforms import tinyfpga_bx
plat = tinyfpga_bx.Platform()

led = plat.request("user_led")
m = Module()
counter = Signal(26)
m.comb += led.eq(counter[25])
m.sync += counter.eq(counter + 1)

plat.build(m, build_name='test')
