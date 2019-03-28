BUILD_DIR=$(PWD)/build

all: icestorm-build nextpnr-build yosys-build

icestorm-build:
	$(MAKE) -C icestorm
	$(MAKE) -C icestorm PREFIX=$(BUILD_DIR) install

nextpnr-build:
	(cd nextpnr && c$(MAKE) -DARCH=ice40 -DCMAKE_INSTALL_PREFIX=$(BUILD_DIR) -DICEBOX_ROOT=$(BUILD_DIR)/share/icebox)
	$(MAKE) -C nextpnr
	$(MAKE) -C nextpnr install

yosys-build:
	$(MAKE) -C yosys
	$(MAKE) -C yosys PREFIX=$(BUILD_DIR) install
