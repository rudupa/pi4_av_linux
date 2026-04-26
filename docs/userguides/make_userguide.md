# Make User Guide for This Repository

## Table of Contents
- [Purpose](#purpose)
- [Quick GNU Make Basics](#quick-gnu-make-basics)
   - [1. Target, prerequisite, recipe](#1-target-prerequisite-recipe)
   - [2. Variables](#2-variables)
   - [3. Phony targets](#3-phony-targets)
   - [4. Suppressing command echo](#4-suppressing-command-echo)
   - [5. Multi-line shell commands](#5-multi-line-shell-commands)
- [Syntax Used in This Repository Makefile](#syntax-used-in-this-repository-makefile)
   - [Conditional variable defaults](#conditional-variable-defaults)
   - [Derived command macro](#derived-command-macro)
   - [.PHONY declaration](#phony-declaration)
   - [Prerequisite chaining](#prerequisite-chaining)
   - [Shell conditionals inside recipes](#shell-conditionals-inside-recipes)
   - [Command chaining with &&](#command-chaining-with)
- [Buildroot Package .mk Syntax Used in This Repo](#buildroot-package-mk-syntax-used-in-this-repo)
   - [Package metadata variables](#package-metadata-variables)
   - [Multi-line macro blocks with define/endef](#multi-line-macro-blocks-with-defineendef)
   - [Hook variables](#hook-variables)
   - [Package infrastructure selector](#package-infrastructure-selector)
   - [$(INSTALL) command and flags](#install-command-and-flags)
   - [external.mk syntax (`include`, `wildcard`, `sort`)](#externalmk-syntax-include-wildcard-sort)
- [What Each Repository Target Does](#what-each-repository-target-does)
   - [help](#help)
   - [submodules](#submodules)
   - [submodules-update](#submodules-update)
   - [buildroot](#buildroot)
   - [defconfig](#defconfig)
   - [menuconfig](#menuconfig)
   - [linux-menuconfig](#linux-menuconfig)
   - [busybox-menuconfig](#busybox-menuconfig)
   - [build](#build)
   - [clean](#clean)
   - [distclean](#distclean)
   - [mrproper](#mrproper)
   - [savedefconfig](#savedefconfig)
- [Typical Usage Flow in This Repo](#typical-usage-flow-in-this-repo)
- [Useful Override Examples](#useful-override-examples)
- [Summary](#summary)

## Purpose
This guide explains:
1. Basic GNU Make syntax.
2. The Make syntax patterns used in this repository.
3. What each target in the project Makefile does.

Primary reference file: [Makefile](Makefile).

## Quick GNU Make Basics

### 1. Target, prerequisite, recipe
General form:

TARGET: PREREQUISITE1 PREREQUISITE2
<TAB>command 1
<TAB>command 2

Meaning:
1. Make ensures prerequisites are handled first.
2. Then it runs the recipe commands under the target.

### 2. Variables
Common forms:
1. Recursive assignment:
   NAME = value
2. Conditional assignment (set only if not already set):
   NAME ?= value

Read variable value with:
$(NAME)

### 3. Phony targets
A phony target is a command-like target, not a real file.
Declaring phony targets avoids conflicts with files of the same name.

### 4. Suppressing command echo
Prefixing a recipe command with @ runs it without printing the command itself.

### 5. Multi-line shell commands
Use backslash line continuation in a recipe when one shell block spans lines.

## Syntax Used in This Repository Makefile

### Conditional variable defaults
This file uses ?= for user-overridable defaults:
1. BUILDROOT_DIR
2. BUILDROOT_REPO
3. BUILDROOT_REF
4. OUTPUT_DIR
5. DEFCONFIG
6. BR2_EXTERNAL_DIR

Effect:
You can override values from the command line without editing the file.

Example:
make BUILDROOT_REF=2024.02.1 buildroot

### Derived command macro
This file defines:
BR2_MAKE = $(MAKE) -C "$(BUILDROOT_DIR)" O="$(CURDIR)/$(OUTPUT_DIR)" BR2_EXTERNAL="$(BR2_EXTERNAL_DIR)"

What this does:
1. Uses $(MAKE) so nested make calls preserve Make behavior.
2. Uses -C to run inside the Buildroot directory.
3. Uses O= to keep build output in the separate output directory.
4. Uses BR2_EXTERNAL= to include this repository external package tree.

### .PHONY declaration
The file declares operational targets as phony using .PHONY.
This is used for command targets like help, build, clean, menuconfig, and others.

### Prerequisite chaining
Targets depend on each other to enforce order:
1. defconfig depends on buildroot.
2. menuconfig depends on defconfig.
3. linux-menuconfig depends on defconfig.
4. busybox-menuconfig depends on defconfig.
5. build depends on defconfig.
6. savedefconfig depends on defconfig.

Effect:
Running make build automatically ensures Buildroot exists and configuration is prepared.

### Shell conditionals inside recipes
The file uses shell-level if checks inside recipe commands for safe operations.

Pattern used:
@if [ condition ]; then \
  command; \
fi

Used in:
1. buildroot target to clone only when buildroot git directory is missing.
2. clean and distclean targets to run only when output directory exists.

### Command chaining with &&
The buildroot target chains commands with && to ensure later commands run only if earlier steps succeed.

## Buildroot Package .mk Syntax Used in This Repo

This repository also uses Buildroot package makefiles, for example:
`br2_external/package/av_services/av_services.mk`

Other .mk file in this repo:
`br2_external/external.mk`

### Package metadata variables
Typical package variables in Buildroot .mk files:
1. `AV_SERVICES_VERSION = local`
2. `AV_SERVICES_SITE = ...`
3. `AV_SERVICES_SITE_METHOD = local`
4. `AV_SERVICES_LICENSE = Apache-2.0`
5. `AV_SERVICES_DEPENDENCIES = libcurl`

What they do:
1. Define package source and version strategy.
2. Declare license information.
3. Tell Buildroot what other packages must be built first.

### Multi-line macro blocks with define/endef
Buildroot package steps are commonly written as:

define AV_SERVICES_INSTALL_RUNTIME_FILES
	$(INSTALL) ...
	$(INSTALL) ...
endef

What this means:
1. `define/endef` creates a reusable make macro containing shell commands.
2. Buildroot runs it when attached to a hook variable.

### Hook variables
Example used in this repo:
`AV_SERVICES_POST_INSTALL_TARGET_HOOKS += AV_SERVICES_INSTALL_RUNTIME_FILES`

Meaning:
1. `+=` appends a hook function name to an existing list.
2. This specific hook runs after target installation, so runtime files are copied into target rootfs.

### Package infrastructure selector
This repo uses:
`$(eval $(cmake-package))`

Meaning:
1. `$(eval ...)` tells make to parse generated make rules.
2. `$(cmake-package)` injects Buildroot's standard CMake build/install logic for the package.

### $(INSTALL) command and flags
In package install hooks, Buildroot provides `$(INSTALL)` (install tool wrapper).

Flags used in this repo:
1. `$(INSTALL) -d <dir>`
   Creates directory path(s) if missing.
2. `$(INSTALL) -m 0644 <src> <dst>`
   Copies file and sets mode `0644` (owner read/write, group read, others read).
3. `$(INSTALL) -D -m 0755 <src> <dst>`
   Creates parent destination directories as needed, copies file, and sets executable mode `0755`.

Concrete examples from `av_services.mk`:
1. `-d` is used for directories like `/etc/av-core` and `/var/log/av-core`.
2. `-m 0644` is used for config files in `/etc/av-core/*.conf`.
3. `-D -m 0755` is used for init script install at `/etc/init.d/S99avcore`.

### external.mk syntax (`include`, `wildcard`, `sort`)
`br2_external/external.mk` contains:

`include $(sort $(wildcard $(BR2_EXTERNAL_PI4_AV_EXTERNAL_PATH)/package/*/*.mk))`

What each part does:
1. `$(wildcard path/pattern)`
   Expands to all file paths matching the glob. Here it finds package .mk files under `package/*/*.mk`.
2. `$(sort list)`
   Sorts file list in lexical order so include order is deterministic.
3. `include <file-list>`
   Loads each matched package makefile into Buildroot processing.

Why this matters:
1. New package directories are auto-discovered without manually editing `external.mk` each time.
2. Package inclusion order is stable across machines.

## What Each Repository Target Does

### help
Prints usage help and available make targets.

### submodules
Initializes and updates git submodules recursively.

### submodules-update
Updates submodules to recorded commits recursively.

### buildroot
1. Clones Buildroot if not present.
2. Fetches tags.
3. Checks out the configured Buildroot reference.

### defconfig
Generates output/.config from configs/pi4_64_defconfig using Buildroot.

### menuconfig
Opens Buildroot menuconfig interface.

### linux-menuconfig
Opens Linux kernel menuconfig interface from Buildroot.

### busybox-menuconfig
Opens BusyBox menuconfig interface from Buildroot.

### build
Builds the full image after defconfig is applied.

### clean
Cleans build artifacts when output directory exists.

### distclean
Performs deeper clean when output directory exists.

### mrproper
Deletes both output and buildroot directories.
Use carefully because this removes local Buildroot checkout and build outputs.

### savedefconfig
1. Writes minimized Buildroot defconfig from current config.
2. Copies it back to configs/pi4_64_defconfig.

## Typical Usage Flow in This Repo
1. make submodules
2. make defconfig
3. make build

Optional configuration flow:
1. make menuconfig
2. make savedefconfig
3. make build

## Useful Override Examples
1. Use a different Buildroot ref:
   make BUILDROOT_REF=2024.02.1 buildroot
2. Use a different output directory:
   make OUTPUT_DIR=output-debug build
3. Use a different defconfig file:
   make DEFCONFIG=$(CURDIR)/configs/pi4_64_defconfig defconfig

## Summary
This repository Makefile is an orchestration layer for Buildroot.
It standardizes submodule setup, Buildroot checkout, configuration, image build, and cleanup while keeping output separated and external packages enabled through BR2_EXTERNAL.
