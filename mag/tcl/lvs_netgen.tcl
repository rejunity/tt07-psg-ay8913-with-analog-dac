set layout [readnet spice $project.lvs.spice]
set source [readnet spice /dev/null]
readnet spice $::env(PDK_ROOT)/$::env(PDK)/libs.ref/sky130_fd_sc_hd/spice/sky130_fd_sc_hd.spice $source
# add any spice files of your analog blocks:
readnet spice ../xschem/simulation/dac_16nfet.spice $source
# add an GL verilog of your digital blocks:
readnet verilog ../verilog/gl/ay8913.v $source
# top level GL verilog
# also could be: readnet verilog ../verilog/gl/$project.v $source
# Matt links project.v to /gl/$project.v ^^^
readnet verilog ../src/project.v $source
lvs "$layout $project" "$source $project" $::env(PDK_ROOT)/sky130A/libs.tech/netgen/sky130A_setup.tcl lvs.report -blackbox
