vlib work
vmap work work
vlog -sv formal\props\hello_props.sv formal\props\hello_bind.sv
vsim -c work.hello -do "run -all; report -assertions -verbose; quit -f"
