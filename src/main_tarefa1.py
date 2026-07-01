from pathlib import Path
from ula import ULA

class Processor:
    def __init__ (self):
        self.ir = 0
        self.pc = 0
        self.value_a = 0b00000000000000000000000000000001
        self.value_b = 0b10000000000000000000000000000000
        self.value_s = 0b00000000000000000000000000000000
        self.value_sd = 0b00000000000000000000000000000000
        self.n = 0b00000000000000000000000000000000
        self.z = 0b00000000000000000000000000000000
        self.co = 0b0
        self.ula = ULA ()

        # Define as variáveis de onde está o arquivo de log e verifica se ele existe.
        self.current_dir = Path(__file__).parent
        self.log_path = self.current_dir.parent / 'logs' / 'logFinal_tarefa1.txt'
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def decodifier (self):
        # Decodifica a instrução em um array com 8 dígitos no arquivo de entrada
        instructions = []
        for i in reversed (range(8)):
            instructions.append(self.ir >> i & 0b1)
        return instructions
    
    def effective_value_a_b (self, ena, enb):
        # Determina o valor de A e B a partir das entradas ENA e ENB
        internal_value_a = self.value_a if ena == 1 else 0
        internal_value_b = self.value_b if enb == 1 else 0

        return internal_value_a, internal_value_b

    def execute_instruction (self):
        # Retorna os valores do array de instrução em 8 valores diferentes após a decodificação
        sll8, sra1, f0, f1, ena, enb, inva, inc  = self.decodifier()

        # Incrementa o PC a cada linha lida, inclusive na inválida
        self.pc = self.pc + 1

        # Verifica se SLL8 e SRA1 são igual a 1, pois caso sejam, o programa deve ser finalizado.
        if sll8 == 1 and sra1 == 1:
            self.write_error_log()
            return

        # Determina os valores internos de A e B a partir de ENA e ENB
        internal_value_a, internal_value_b = self.effective_value_a_b(ena, enb)
        # Recebe os valores da ULA na ordem: S, Sd, Vai-um, N, Z
        self.value_s, self.sd, self.co, self.n, self.z = self.ula.calculate(f0, f1, inva, inc, internal_value_a, internal_value_b, sll8, sra1)

        self.write_log(internal_value_a, internal_value_b)

    def start_log(self):
        # Abre no modo 'w' para sobrescrever logs antigos e inicia o cabeçalho
        with open(self.log_path, 'w') as f:
            f.write(f"b = {self.value_b:032b}\n")
            f.write(f"a = {self.value_a:032b}\n\n")
            f.write("Start of Program\n")

    def write_log(self, internal_value_a, internal_value_b):
        # Abre no modo 'a' (append) para adicionar ao final do arquivo

        with open(self.log_path, 'a') as f:
            f.write("============================================================\n")
            f.write(f"Cycle {self.pc}\n\n")
            f.write(f"PC = {self.pc}\n")
            # :08b garante que seja binário e sempre tenha 8 dígitos (zeros à esquerda)
            f.write(f"IR = {self.ir:08b}\n") 
            f.write(f"b = {internal_value_b:032b}\n")
            f.write(f"a = {internal_value_a:032b}\n")
            f.write(f"s = {self.value_s:032b}\n")
            f.write(f"sd = {self.sd:032b}\n")
            f.write(f"n = {self.n}\n")
            f.write(f"z = {self.z}\n")
            f.write(f"co = {self.co}\n")

    def end_log(self):
        # Escreve o final do programa 
        with open(self.log_path, 'a') as f:
            f.write("============================================================\n")
            f.write(f"Cycle {self.pc + 1}\n\n")
            f.write(f"PC = {self.pc + 1}\n")
            f.write("> Line is empty, EOP.\n")
    
    def write_error_log(self):
        # Escreve o erro caso tenha algum sinal inválido no programa
        with open(self.log_path, 'a') as f:
            f.write("============================================================\n")
            f.write(f"Cycle {self.pc}\n\n")
            f.write(f"PC = {self.pc}\n")
            f.write(f"IR = {self.ir:08b}\n")
            f.write("> Error, invalid control signals.\n")

def read_archive(processor):
    # Descobre onde está o arquivo de entrada independente de onde está sendo feita a execução do programa
    current_dir = Path(__file__).parent
    archive_dir = current_dir.parent / 'data' / 'programa_etapa2_tarefa1.txt'

    processor.start_log()

    with open (archive_dir, 'r') as archive:
        for line in archive:
            line = line.strip()
            processor.ir = int(line, 2)
            processor.execute_instruction()

    processor.end_log()

processor = Processor ()
data = read_archive(processor)
