import array

# Note: ROM is 16-bit, file format has opcode byte then data byte.
# On the schematic, data byte is shown as higher bits of the word
# so we leave them in that order here.
#   LD $01 --> 0001 in .asm --> 00 01 in .rom --> 256 in this array.

with open("gigatron-rom/ROMv3.rom", "rb") as fh:
    rom_image = array.array("H", fh.read())

print ("P3 128 512 1 ")

for x in rom_image:
    print(1 if x & 255 else 0, 1 if x & ~255 else 0, 1 if x == 0 else 0)


