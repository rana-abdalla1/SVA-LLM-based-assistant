vlib work
vmap work work
vlog -sv hello.sv formal/props/stream_props.sv formal/props/stream_bind.sv tb_hello.sv
vsim -c work.tb_hello -do "run -all; report -assertions -verbose; quit -f"
