CMAKE?=`which cmake`
BUILD_DIR=$(PWD)/build
ICEPACK_BIN=$(BUILD_DIR)/bin/icepack
NEXTPNR_BIN=$(BUILD_DIR)/bin/nextpnr
YOSYS_BIN=$(BUILD_DIR)/bin/yosys

all: tools

tools: $(ICEPACK_BIN) $(NEXTPNR_BIN) $(YOSYS_BIN)

$(ICEPACK_BIN):
	$(MAKE) -C icestorm -j `nproc`
	$(MAKE) -C icestorm PREFIX=$(BUILD_DIR) install

$(NEXTPNR_BIN):
	$(CMAKE) nextpnr -B nextpnr/build -DARCH=ice40 -DCMAKE_INSTALL_PREFIX=$(BUILD_DIR) -DICEBOX_ROOT=$(BUILD_DIR)/share/icebox
	$(CMAKE) --build nextpnr/build --parallel `nproc`
	$(MAKE) -C nextpnr/build install

$(YOSYS_BIN):
	$(CMAKE) yosys -B yosys/build -DCMAKE_INSTALL_PREFIX=$(BUILD_DIR)
	$(CMAKE) --build yosys/build --parallel `nproc`
	$(MAKE) -C yosys/build PREFIX=$(BUILD_DIR) install

clean:
	rm -r build nextpnr/build yosys/build
