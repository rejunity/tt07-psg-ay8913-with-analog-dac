# Makefile

# defaults
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(PWD)/../rtl/amplitude.v
VERILOG_SOURCES += $(PWD)/../rtl/envelope.v
VERILOG_SOURCES += $(PWD)/../rtl/noise.v
VERILOG_SOURCES += $(PWD)/../rtl/pwm.v
VERILOG_SOURCES += $(PWD)/../rtl/signal_edge.v
VERILOG_SOURCES += $(PWD)/../rtl/tone.v
VERILOG_SOURCES += $(PWD)/../rtl/ay8913.v
# use VHDL_SOURCES for VHDL files

# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL = ay8913

# MODULE is the basename of the Python test file
MODULE = test

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
