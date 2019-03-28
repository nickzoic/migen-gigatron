BUILD_DIR=$(PWD)/build
ICEPACK_BIN=$(BUILD_DIR)/bin/icepack
NEXTPNR_BIN=$(BUILD_DIR)/bin/nextpnr
YOSYS_BIN=$(BUILD_DIR)/bin/yosys

all: tools

tools: $(ICEPACK_BIN) $(NEXTPNR_BIN) $(YOSYS_BIN)

$(ICEPACK_BIN):
	$(MAKE) -C icestorm
	$(MAKE) -C icestorm PREFIX=$(BUILD_DIR) install

$(NEXTPNR_BIN):
	(cd nextpnr && c$(MAKE) -DARCH=ice40 -DCMAKE_INSTALL_PREFIX=$(BUILD_DIR) -DICEBOX_ROOT=$(BUILD_DIR)/share/icebox)
	$(MAKE) -C nextpnr
	$(MAKE) -C nextpnr install

$(YOSYS_BIN):
	$(MAKE) -C yosys
	$(MAKE) -C yosys PREFIX=$(BUILD_DIR) install
