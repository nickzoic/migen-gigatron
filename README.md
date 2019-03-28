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

## Building

Other than a bunch of Ubuntu packages, and some of the Python libraries, 
everything is pulled in as submodules and built within the tree, or at least that's the idea.

```
    git submodule update --init --recursive

    cat ubuntu-packages.txt | xargs sudo apt install -y

    make -j$(nproc)

    pip install -e migen/
    pip install tinyprog

    PATH=$PWD/build/bin:$PATH 

    python3 test.py
```

## Programming

### SystemD ModemManager

First stop ModemManager messing with you.  If `tinyprog` crashes out part way through
and/or you're getting `dmesg` error logs like: `cdc_acm 1-1:1.0: failed to set dtr/rts`
then that's probably the problem.

See https://askubuntu.com/questions/399263/udev-rules-seem-ignored-can-not-prevent-modem-manager-from-grabbing-device and then fume quietly to yourself for a while.

Assuming you don't actually have any modems the easiest thing is just to tell ModemManager to leave `/dev/ttyACM*` alone:

* Edit `/lib/systemd/system/ModemManager.service` and add to the `[Service]` section:
```
Environment="MM_FILTER_RULE_TTY_ACM_INTERFACE=0"
```

Otherwise you can add specific udev rules for this device and then remind systemd ModemManager to actually respect those rules:

* Create `/etc/udev/rules.d/99-tinyfpga.rules` and add rule 
```
ATTR{idProduct}=="6130", ATTR{idVendor}=="1d50", ENV{ID_MM_DEVICE_IGNORE}="1", MODE="666"
```
* sudo udevadm control --reload
* Edit `/lib/systemd/system/ModemManager.service` and change `ExecStart=/usr/sbin/ModemManager --filter-policy=strict` to `ExecStart=/usr/sbin/ModemManager --filter-policy=default`

Either way, reload the ModemManager configuration:

```
sudo systemctl daemon-reload
sudo systemctl restart ModemManager
```

### Tinyprog

```
    tinyprog -p build/test.bin
```

