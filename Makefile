BUILDROOT_DIR ?= buildroot
BUILDROOT_REPO ?= https://github.com/buildroot/buildroot.git
BUILDROOT_REF ?= master
OUTPUT_DIR ?= output
DEFCONFIG ?= $(CURDIR)/configs/pi4_64_defconfig
BR2_EXTERNAL_DIR ?= $(CURDIR)/br2_external

BR2_MAKE = $(MAKE) -C "$(BUILDROOT_DIR)" O="$(CURDIR)/$(OUTPUT_DIR)" BR2_EXTERNAL="$(BR2_EXTERNAL_DIR)"

.PHONY: help submodules submodules-update buildroot defconfig menuconfig linux-menuconfig busybox-menuconfig build clean distclean mrproper savedefconfig

help:
	@echo "Buildroot Raspberry Pi 4 repo"
	@echo "Targets:"
	@echo "  make submodules         - initialize and clone git submodules"
	@echo "  make submodules-update  - update submodules to recorded commits"
	@echo "  make buildroot           - clone/update Buildroot"
	@echo "  make defconfig           - configure output/.config from configs/pi4_64_defconfig"
	@echo "  make menuconfig          - open Buildroot menuconfig"
	@echo "  make linux-menuconfig    - open Linux kernel menuconfig"
	@echo "  make busybox-menuconfig  - open BusyBox menuconfig"
	@echo "  make build               - build full image"
	@echo "  make clean               - remove built artifacts"
	@echo "  make distclean           - deep clean output"
	@echo "  make mrproper            - remove Buildroot checkout and output"
	@echo "  make savedefconfig       - save minimized config back to configs/pi4_64_defconfig"

submodules:
	@git submodule update --init --recursive

submodules-update:
	@git submodule update --recursive

buildroot:
	@if [ ! -d "$(BUILDROOT_DIR)/.git" ]; then \
		git clone "$(BUILDROOT_REPO)" "$(BUILDROOT_DIR)"; \
	fi
	@cd "$(BUILDROOT_DIR)" && git fetch --tags --quiet && git checkout "$(BUILDROOT_REF)"

defconfig: buildroot
	$(BR2_MAKE) BR2_DEFCONFIG="$(DEFCONFIG)" defconfig

menuconfig: defconfig
	$(BR2_MAKE) menuconfig

linux-menuconfig: defconfig
	$(BR2_MAKE) linux-menuconfig

busybox-menuconfig: defconfig
	$(BR2_MAKE) busybox-menuconfig

build: defconfig
	$(BR2_MAKE)

clean:
	@if [ -d "$(OUTPUT_DIR)" ]; then \
		$(BR2_MAKE) clean; \
	fi

distclean:
	@if [ -d "$(OUTPUT_DIR)" ]; then \
		$(BR2_MAKE) distclean; \
	fi

mrproper:
	rm -rf "$(OUTPUT_DIR)" "$(BUILDROOT_DIR)"

savedefconfig: defconfig
	$(BR2_MAKE) savedefconfig
	cp "$(OUTPUT_DIR)/defconfig" "$(DEFCONFIG)"
