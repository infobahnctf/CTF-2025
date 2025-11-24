# Makefile for the cocotb testbench
SIM ?= verilator
TOPLEVEL_LANG ?= verilog
TOPLEVEL := axi_encrypt_slave
VERILOG_SOURCES := $(PWD)/src/encrypt.sv $(PWD)/src/top.sv

MODULE := tests.test_axi_encrypt
EXTRA_ARGS += --sv --timing --trace --trace-structs -Wall -Wno-UNOPTFLAT -Wno-DECLFILENAME
WAVES ?= 1

all: sim

clean::
	$(RM) -rf results.xnl tests/__pycache__

include $(shell cocotb-config --makefiles)/Makefile.sim
