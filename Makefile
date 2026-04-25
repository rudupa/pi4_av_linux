BUILDROOT_DIR ?= buildroot
BUILDROOT_REPO ?= https://github.com/buildroot/buildroot.git
BUILDROOT_REF ?= master
OUTPUT_DIR ?= output
DEFCONFIG ?= $(CURDIR)/configs/pi4_64_defconfig

.PHONY: help buildroot defconfig menuconfig linux-menuconfig busybox-menuconfig build clean distclean mrproper savedefconfig

help:
	@echo "Buildroot Raspberry Pi 4 repo"
	@echo "Targets:"
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

buildroot:
	@if [ ! -d "$(BUILDROOT_DIR)/.git" ]; then \
		git clone "$(BUILDROOT_REPO)" "$(BUILDROOT_DIR)"; \
	fi
	@cd "$(BUILDROOT_DIR)" && git fetch --tags --quiet && git checkout "$(BUILDROOT_REF)"

defconfig: buildroot
	$(MAKE) -C "$(BUILDROOT_DIR)" O="$(CURDIR)/$(OUTPUT_DIR)" BR2_DEFCONFIG="$(DEFCONFIG)" defconfig

menuconfig: defconfig
	$(MAKE) -C "$(BUILDROOT_DIR)" O="$(CURDIR)/$(OUTPUT_DIR)" menuconfig

linux-menuconfig: defconfig
	$(MAKE) -C "$(BUILDROOT_DIR)" O="$(CURDIR)/$(OUTPUT_DIR)" linux-menuconfig

busybox-menuconfig: defconfig
	$(MAKE) -C "$(BUILDROOT_DIR)" O="$(CURDIR)/$(OUTPUT_DIR)" busybox-menuconfig

build: defconfig
	$(MAKE) -C "$(BUILDROOT_DIR)" O="$(CURDIR)/$(OUTPUT_DIR)"

clean:
	@if [ -d "$(OUTPUT_DIR)" ]; then \
		$(MAKE) -C "$(BUILDROOT_DIR)" O="$(CURDIR)/$(OUTPUT_DIR)" clean; \
	fi

distclean:
	@if [ -d "$(OUTPUT_DIR)" ]; then \
		$(MAKE) -C "$(BUILDROOT_DIR)" O="$(CURDIR)/$(OUTPUT_DIR)" distclean; \
	fi

mrproper:
	rm -rf "$(OUTPUT_DIR)" "$(BUILDROOT_DIR)"

savedefconfig: defconfig
	$(MAKE) -C "$(BUILDROOT_DIR)" O="$(CURDIR)/$(OUTPUT_DIR)" savedefconfig
	cp "$(OUTPUT_DIR)/defconfig" "$(DEFCONFIG)"
