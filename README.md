# Migen Gigatron

An attempt to implement the
[Gigatron TTL Microcomputer](https://gigatron.io/)
on an
[FPGA](https://en.wikipedia.org/wiki/Field-programmable_gate_array), specifically the
[TinyFPGA BX](https://tinyfpga.com/bx/guide.html) using 
[Migen](https://m-labs.hk/migen/).

## Why?

To learn Migen and a bit more about FPGA programming. I've previously
[messed around with FuPy](https://nick.zoic.org/art/fupy-micropython-for-fpga/)
but it's a pretty complicated place to dive in.

Also I'm just blown away by what the Gigatron creators have achieved from
[so few parts](doc/Schematics.pdf)
and how much this would have changed the history of personal computing
if Woz had homebrewed something like this instead of the 
[MOS 6502](https://en.wikipedia.org/wiki/MOS_Technology_6502) in the 
[Apple 1](https://en.wikipedia.org/wiki/Apple_I).

### It's already been done ...

[Yeah, but in Verilog.](https://github.com/menloparkinnovation/menlo_gigatron)

## Building Tools

Other than a bunch of Ubuntu packages, and some of the Python libraries, 
everything is pulled in as submodules and built within the tree, or at least that's the idea.

```
    git submodule update --init --recursive

    cat ubuntu-packages.txt | xargs sudo apt install -y

    make -j$(nproc)

    pip install -e migen/
    pip install tinyprog
```

## Building Gateware

```
    PATH=$PWD/build/bin:$PATH 
    python3 test.py
```

## Programming

First [make sure systemd modemmanager isn't messing with you](https://nick.zoic.org/art/failed-to-set-dtr-rts-systemd-modemmanager/) 

Then you can run tinyprog to copy the gateway onto the FPGA.  Press the reset button and then:

```
    tinyprog -p build/test.bin
```

