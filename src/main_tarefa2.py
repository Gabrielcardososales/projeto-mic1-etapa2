from pathlib import Path
from ula import ULA  # Certifique-se de que sua classe ULA está neste arquivo

class ProcessorMic1:
    def __init__(self):
        self.ula = ULA()
        
        # Registradores em minúsculas para bater com o formato do log
        self.registers = {
            "mar": 0, "mdr": 0, "pc": 0, "mbr": 0, 
            "sp": 0, "lv": 0, "cpp": 0, "tos": 0, 
            "opc": 0, "h": 0
        }
        
        # Ordem exata de exibição dos registradores exigida no log da professora
        self.reg_order = ["mar", "mdr", "pc", "mbr", "sp", "lv", "cpp", "tos", "opc", "h"]
        
        self.current_dir = Path(__file__).parent
        self.log_path = self.current_dir.parent / 'logs' / 'logFinal_tarefa2.txt'
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.cycle_count = 1

    def load_initial_registers(self, filepath):
        with open(filepath, 'r') as f:
            for line in f:
                if "=" in line:
                    reg, val = line.strip().split('=')
                    self.registers[reg.strip().lower()] = int(val.strip(), 2)

    def decode_instruction(self, instruction):
        ula_ctrl = int(instruction[0:8], 2)
        bus_c_ctrl = int(instruction[8:17], 2)
        bus_b_ctrl = int(instruction[17:21], 2)
        return ula_ctrl, bus_c_ctrl, bus_b_ctrl

    def get_bus_b(self, bus_b_ctrl):
        # Mapeamento do Barramento B
        mapping = {
            8: "tos", 7: "opc", 6: "cpp", 5: "lv", 
            4: "sp", 3: "mbru", 2: "mbr", 1: "pc", 0: "mdr"
        }
        reg_name = mapping.get(bus_b_ctrl, "none")
        
        if reg_name == "none":
            return 0, reg_name
            
        if reg_name == "mbru":  
            val = self.registers["mbr"]
            if (val & 0b10000000) != 0:  
                return val | 0xFFFFFF00, reg_name
            return val, reg_name
        elif reg_name == "mbr":   
            return self.registers["mbr"] & 0x000000FF, reg_name
        else:
            return self.registers[reg_name], reg_name

    def get_c_bus_names(self, bus_c_ctrl):
        # Ordem FINAL E DEFINITIVA: 'sp' no índice 3 e 'lv' no índice 4
        regs_c = ["mar", "mdr", "pc", "sp", "lv", "cpp", "tos", "opc", "h"]
        bus_c_names = []
        for i in reversed(range(9)):
            if (bus_c_ctrl >> i) & 1:
                bus_c_names.append(regs_c[i])
        return bus_c_names

    def set_bus_c(self, bus_c_ctrl, sd_value):
        # Ordem FINAL E DEFINITIVA: 'sp' no índice 3 e 'lv' no índice 4
        regs_c = ["mar", "mdr", "pc", "sp", "lv", "cpp", "tos", "opc", "h"]
        for i, reg in enumerate(regs_c):
            if (bus_c_ctrl >> i) & 1:
                self.registers[reg] = sd_value
                self.registers[reg] &= 0xFFFFFFFF  # Garante consistência de 32 bits no Python

    def format_registers(self):
        out = []
        for reg in self.reg_order:
            val = self.registers[reg]
            if reg == "mbr":
                out.append(f"{reg} = {val:08b}")
            else:
                out.append(f"{reg} = {val:032b}")
        return "\n".join(out)

    def write_log(self, text, mode='a'):
        with open(self.log_path, mode) as f:
            f.write(text + "\n")

    def run(self, regs_file, prog_file):
        instructions = []
        with open(prog_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    instructions.append(line)

        # Escreve as instruções no topo do arquivo
        self.write_log("\n".join(instructions), mode='w')
        self.write_log("\n=====================================================")
        
        # Carrega e exibe os estados iniciais
        self.load_initial_registers(regs_file)
        self.write_log("> Initial register states")
        self.write_log(self.format_registers())
        
        self.write_log("\n=====================================================")
        self.write_log("Start of program")
        self.write_log("=====================================================")
        
        # Laço de execução dos ciclos
        for inst in instructions:
            ula_ctrl, bus_c_ctrl, bus_b_ctrl = self.decode_instruction(inst)
            
            self.write_log(f"Cycle {self.cycle_count}")
            self.write_log(f"ir = {inst[0:8]} {inst[8:17]} {inst[17:21]}\n")
            
            value_b, b_bus_name = self.get_bus_b(bus_b_ctrl)
            c_bus_names = self.get_c_bus_names(bus_c_ctrl)
            c_bus_str = ", ".join(c_bus_names) if c_bus_names else "none"
            
            self.write_log(f"b_bus = {b_bus_name}")
            self.write_log(f"c_bus = {c_bus_str}\n")
            
            self.write_log("> Registers before instruction")
            self.write_log(self.format_registers() + "\n")
            
            # --- Execução da ULA ---
            value_a = self.registers["h"]
            
            sll8 = (ula_ctrl >> 7) & 1
            sra1 = (ula_ctrl >> 6) & 1
            f0   = (ula_ctrl >> 5) & 1
            f1   = (ula_ctrl >> 4) & 1
            ena  = (ula_ctrl >> 3) & 1
            enb  = (ula_ctrl >> 2) & 1
            inva = (ula_ctrl >> 1) & 1
            inc  = (ula_ctrl >> 0) & 1
            
            internal_a = value_a if ena else 0
            internal_b = value_b if enb else 0
            
            value_s, sd, co, n, z = self.ula.calculate(
                f0, f1, inva, inc, internal_a, internal_b, sll8, sra1
            )
            
            # Atualiza os registradores habilitados pelo barramento C
            self.set_bus_c(bus_c_ctrl, sd)
            # -----------------------
            
            self.write_log("> Registers after instruction")
            self.write_log(self.format_registers())
            self.write_log("=====================================================")
            
            self.cycle_count += 1
            
        # CORREÇÃO 2: Finalização do arquivo usando o número do último ciclo válido executado (sem somar um extra)
        self.write_log(f"Cycle {self.cycle_count - 1}")
        self.write_log("No more lines, EOP.")

if __name__ == "__main__":
    processor = ProcessorMic1()
    
    current_dir = Path(__file__).parent
    regs_file = current_dir.parent / 'data' / 'registradores_etapa2_tarefa2.txt'
    prog_file = current_dir.parent / 'data' / 'programa_etapa2_tarefa2.txt'
    
    processor.run(regs_file, prog_file)