# SVA LLM-based Assistant

An AI-powered SystemVerilog Assertions (SVA) generation tool that creates high-quality formal verification properties from natural language descriptions. This tool leverages Large Language Models (LLMs) to translate engineering intent into SystemVerilog assertions, complete with quality gates and simulation integration.

## Features

- **Natural Language to SVA**: Convert plain English descriptions into SystemVerilog assertions
- **Quality Gates**: Built-in linting and validation for generated assertions
- **Questa Integration**: Automatic generation of simulation scripts and execution
- **Fallback Templates**: Safe, compilable assertions when LLM is unavailable
- **Concurrent SVA**: Generates industry-standard concurrent assertions with proper clocking and reset handling

## Requirements

### Software Dependencies
- **Python 3.7+** with the following packages:
  - `huggingface_hub` - For LLM inference
  - `pathlib` (built-in)
  - `argparse` (built-in)
  - `subprocess` (built-in)

- **Questa/ModelSim** (optional) - For simulation and verification
  - `vsim` must be in your PATH

### Installation

1. Clone the repository:
```bash
git clone https://github.com/rana-abdalla1/SVA-LLM-based-assistant.git
cd SVA-LLM-based-assistant
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

   Or install manually:
```bash
pip install huggingface_hub
```

3. (Optional) Ensure Questa/ModelSim is installed and `vsim` is in your PATH for simulation.

## Usage

### Basic Command

```bash
python agent/main.py <dut_module> --intent "<your_intent>" [options]
```

### Command Line Arguments

- `dut` - **Required**: Top-level DUT module name (e.g., `hello`)
- `--intent` - **Required**: Engineering intent in plain English
- `--clk` - Clock signal name (default: `clk`)
- `--rst` - Reset signal name (default: `rst_n`)
- `--signals` - Comma-separated signal list (e.g., `valid, ready, data[7:0]`)
- `--model` - HuggingFace model ID (default: `Qwen/Qwen2.5-0.5B-Instruct`)
- `--no-run` - Generate assertions only, skip Questa simulation

### Examples

#### Basic Counter Verification
```bash
python agent/main.py hello --intent "Counter should increment on each clock cycle"
```

#### Handshake Protocol
```bash
python agent/main.py stream --clk clk --rst rst_n \
  --signals "valid, ready, data[7:0]" \
  --intent "Data must remain stable while valid is high and ready is low"
```

#### Generate Only (No Simulation)
```bash
python agent/main.py my_module --intent "Reset should clear all outputs" --no-run
```

## Output Files

The tool generates several files in the `formal/` directory:

- `formal/props/{dut}_props.sv` - Generated SystemVerilog assertions module
- `formal/props/{dut}_bind.sv` - Bind statement connecting assertions to DUT
- `formal/questa/run_agent.do` - Questa simulation script

## Project Structure

```
SVA-LLM-based-assistant/
├── agent/                          # Main application code
│   ├── main.py                     # CLI entry point
│   ├── llm.py                      # LLM integration and fallback templates
│   ├── prompts.py                  # System and user prompts for LLM
│   ├── quality.py                  # SVA linting and quality checks
│   └── questa.py                   # Questa integration and script generation
├── formal/                         # Generated formal verification files
│   ├── props/                      # Assertion properties and bind files
│   └── questa/                     # Simulation scripts and logs
├── hello.sv                        # Example DUT module
├── tb_hello.sv                     # Example testbench
└── README.md                       # This file
```

## How It Works

1. **Input Processing**: The tool takes your DUT module name, signal specifications, and natural language intent
2. **LLM Generation**: Sends structured prompts to a HuggingFace model to generate SystemVerilog assertions
3. **Quality Validation**: Runs built-in quality gates to ensure the generated SVA follows best practices
4. **File Generation**: Creates assertion modules, bind files, and simulation scripts
5. **Simulation** (optional): Automatically runs Questa to verify the assertions

## Generated Assertion Format

The tool generates SystemVerilog modules with:
- Proper clocking (`@(posedge clk)`)
- Reset handling (`disable iff(!rst_n)`)
- One safety assertion per intent
- One anti-vacuity cover property
- Industry-standard concurrent SVA syntax

### Example Output

For a handshake protocol, the tool generates:
```systemverilog
module stream_props(input logic clk, input logic rst_n, input logic valid, input logic ready, input logic [7:0] data);
assert property (@(posedge clk) disable iff(!rst_n) valid && !ready |=> $stable(data) until_with ready);
cover  property (@(posedge clk) disable iff(!rst_n) valid && !ready ##[1:$] ready);
endmodule
```

## Quality Gates

The tool includes several quality checks:
- ✅ Correct module naming (`{dut}_props`)
- ✅ Proper clocking syntax
- ✅ Reset handling
- ✅ Concurrent assertion presence
- ✅ Anti-vacuity cover
- ❌ No `assume` statements (design verification best practice)

## Fallback Mode

When the LLM is unavailable or returns invalid results, the tool automatically falls back to:
- Safe, compilable tautology assertions for general cases
- Standard handshake assertions for protocols with `valid`, `ready`, and `data` signals

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: huggingface_hub**
   ```bash
   pip install huggingface_hub
   ```

2. **vsim not on PATH**
   - Install Questa/ModelSim or use `--no-run` flag
   - Add Questa bin directory to your PATH

3. **Quality gate failed**
   - Check the generated SVA for syntax issues
   - Verify your intent description is clear and specific

### Running Without Simulation

If you don't have Questa installed, use the `--no-run` flag:
```bash
python agent/main.py hello --intent "Counter verification" --no-run
```

Then manually inspect the generated files in `formal/props/`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with various DUT modules and intents
5. Submit a pull request

## License

This project is open source. Please refer to the repository for license details.

## Support

For issues, questions, or contributions, please use the GitHub repository's issue tracker.