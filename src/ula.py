class ULA:
    def __init__(self, bit_size= 32):
        self.bit_size = bit_size
        self.mask = (1 << bit_size) - 1 
    def calculate(self, f0, f1, inva, inc, internal_value_a, internal_value_b, sll8, sra1):
        # Inversor
        if inva == 1:
            internal_value_a = (~internal_value_a) & self.mask
        # Cálculos and, or e NOT B
        result_and = internal_value_a & internal_value_b
        result_or  = internal_value_a | internal_value_b
        result_not_b = (~internal_value_b) & self.mask
        
        # Retorna o valor total da soma 
        total_sum = internal_value_a + internal_value_b + inc
        sum_result = total_sum & self.mask
        
        # Salva o resultado do carry em uma variável definitiva
        calculated_carry = 1 if total_sum > self.mask else 0
        # Inicializa value_s e um carry_out padrão
        value_s = 0 
        carry_out = 0
        
        if f0 == 0 and f1 == 0:
            value_s, carry_out = result_and, 0
        elif f0 == 0 and f1 == 1:
            value_s, carry_out = result_or, 0
        elif f0 == 1 and f1 == 0:
            value_s, carry_out = result_not_b, 0
        elif f0 == 1 and f1 == 1:
            value_s, carry_out = sum_result, calculated_carry
        sd = value_s
        bit_signal = 0
        if sll8 == 1:
            sd = (value_s << 8 & self.mask)
        
        elif sra1 == 1:
            # Captura o bit mais significativo
            is_negative = (value_s >> (self.bit_size - 1)) & 1
            
            if is_negative:
                # Faz o shift e força o bit 31 a ser 1 (com uma máscara OR)
                sd = (value_s >> 1) | (1 << (self.bit_size - 1))
            else:
                # Shift simples para a direita
                sd = value_s >> 1
        z = 1 if sd == 0 else 0
        n = (sd >> (self.bit_size - 1)) & 1
        return value_s, sd, carry_out, n, z
