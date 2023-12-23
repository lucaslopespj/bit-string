comparison_operations = {
    "CMP": "1010",
    "CMN": "1011",
}

test_operations = {
    "TST": "1000",
    "TEQ": "1001",
}

move_operations = {
    "MOV": "1101",
    "MVN": "1111",
}

aritm_operations = {
    "ADD": "0100",
    "ADC": "0101",
    "SUB": "0010",
    "SBC": "0110",
    "RSB": "0011",
    "RSC": "0111",
}

logic_operations = {
    "AND": "0000",
    "EOR": "0001",
    "ORR": "1100",
    "BIC": "1110",
}

data_process_operations = {**comparison_operations, **test_operations, **move_operations, **aritm_operations, **logic_operations}

memory_operations = {
    "LDR": "0110",
    "STR": "0110",
}

shift_operations = {
    "LSL": "0000",
    "LSR": "0001",
    "ASR": "0010",
    "ROR": "0011",
}

conditions = {
    "EQ": "0000",
    "NE": "0001",
    "CS": "0010",
    "CC": "0011",
    "MI": "0100",
    "PL": "0101",
    "VS": "0110",
    "VC": "0111",
    "HI": "1000",
    "LS": "1001",
    "GE": "1010",
    "LT": "1011",
    "GT": "1100",
    "LE": "1101",
    "AL": "1110",
}

registers = {
    "R0" : "0000",
    "R1" : "0001",
    "R2" : "0010",
    "R3" : "0011",
    "R4" : "0100",
    "R5" : "0101",
    "R6" : "0110",
    "R7" : "0111",
    "R8" : "1000",
    "R9" : "1001",
    "R10": "1010",
    "R11": "1011",
    "R12": "1100",
    "R13": "1101",
    "SP" : "1101",
    "R14": "1110",
    "LR" : "1110",
    "R15": "1111",
    "PC" : "1111",
}

class Arm:

    def __init__(self, filename):
        file = open(filename, "r")
        self.instructions = file.read().splitlines()
        file.close()

    def convert_to_binary(self, number, digits):      
        # hexa
        if number[0:2] == "0x":
            return bin(int(number[2:], 16))[2:].zfill(digits)
        # decimal
        elif number[0] == "#": 
            return bin(int(number[1:]))[2:].zfill(digits)
        else:
            return bin(int(number))[2:].zfill(digits)

    def condition_code(self, condition):
        if condition in conditions.keys():
            return conditions[condition]
        else:
            return "0000"
        
    def set_condition_code(self, operation):
        if any(operation in op for op in [comparison_operations.keys(), test_operations.keys()]):
            return "1"
        else:
            if len(operation) == 4 and operation[3] == "S":
                return "1"
            elif len(operation) == 5 and operation[4] == "S":
                return "1"
            else:
                return "0"

    def operand_2_code(self, operand_2):
        # immediate
        if len(operand_2) == 1:
            immediate_operand = "1"
            immediate = self.convert_to_binary(operand_2[0], 12)
            return (immediate_operand, immediate)

        elif len(operand_2) == 3:
            immediate_operand = "0"
            shift_type = operand_2[1]
            shift_type_code = shift_operations[shift_type][2:4]
            rm = operand_2[0]
            rm_code = registers[rm]

            # shift register
            if operand_2[2][0] == "R":
                rs = operand_2[2]
                rs_code = registers[rs]
                return (immediate_operand, rs_code + "0" + shift_type_code + "1" + rm_code)
            # shift amount
            else:
                shift_amount = operand_2[2]
                shift_amount_code = self.convert_to_binary(shift_amount, 5)
                return (immediate_operand, shift_amount_code + shift_type_code + "0" + rm_code)
    
    def instruction_code(self):

        for instruction in self.instructions:

            instruction = instruction.upper().replace(", ", " ").replace(",", " ").split(" ")
            print("\n")
            print(instruction)

            # rotation nao implementado
            if instruction[0][0:3] in data_process_operations.keys():
                
                operation = instruction[0][0:3]
                operation_code = data_process_operations[operation]
                         
                condition = instruction[0][3:5]
                condition_code = self.condition_code(condition)

                set_condition_code = self.set_condition_code(operation)

                if any(operation in op for op in [comparison_operations.keys(), test_operations.keys()]):
                    rd = "0000"
                    rn = registers[instruction[1]] 
                elif any(operation in op for op in [aritm_operations.keys(), logic_operations.keys()]):
                    rd = registers[instruction[1]]
                    rn = registers[instruction[2]]
                elif any(operation in op for op in [move_operations.keys()]):
                    rd = registers[instruction[1]]
                    rn = "0000"

                if any(operation in op for op in [aritm_operations.keys(), logic_operations.keys()]):
                    immediate_operand, operand_2_code = self.operand_2_code(instruction[3:])          
                else:
                    immediate_operand, operand_2_code = self.operand_2_code(instruction[2:])   
                
                code = f"{condition_code} 00 {immediate_operand} {operation_code} {set_condition_code} {rn} {rd} {operand_2_code}"
                print(code)

            elif "B" in instruction[0][0]:

                if len(instruction[0]) > 1 and instruction[0][1] == "X":
                    condition = instruction[0][2:4]
                    condition_code = self.condition_code(condition)
                    rn = self.register_code(instruction[1])
                    
                    code = f"{condition_code} 0001 0010 1111 1111 1111 0001 {rn}"

                else: 
                    if len(instruction[0]) > 1 and instruction[0][1] == "L":
                        condition = instruction[0][2:4]
                        link_bit = "1"
                    else:
                        condition = instruction[0][1:3]
                        link_bit = "0"
                
                    condition_code = self.condition_code(condition)
                    offset = self.offset_code(instruction[1])

                    code = f"{condition_code} 101 {link_bit} {offset}"
                    
                print(code)

            elif instruction[0][0:3] in memory_operations.keys():

                condition = instruction[0][3:5]
                condition_code = self.condition_code(condition)

                if len(instruction[0]) == 4 and instruction[0][3] == "B":
                    byte_bit = "1"
                if len(instruction[0]) > 5 and instruction[0][5] == "B":
                    byte_bit = "1"
                else:
                    byte_bit = "0"

                if instruction[0][0:3] == "LDR":
                    load_bit = "1"
                else:
                    load_bit = "0"

                # sorce/destination register
                rd = registers[instruction[1]] 

                if len(instruction) > 3 and "]" in instruction[2]:
                    pre_indexing_bit = "0"
                else:
                    pre_indexing_bit = "1"

                # base register
                rn = registers[instruction[2].replace("[", "").replace("]", "")]

                if len(instruction) > 3 and "-" in instruction[3]:
                    up_bit = "0"
                else:
                    up_bit = "1"

                if len(instruction) > 3 and "!" in instruction[3]:
                    write_back_bit = "1"
                else:
                    write_back_bit = "0"

                if len(instruction) > 3 and "R" in instruction[3]:
                    
                    # offset register
                    rm = registers[instruction[3].replace("-", "").replace("]", "").replace("!", "")]

                    if len(instruction) > 5:
                        shift_type = instruction[4]
                        shift_type_code = shift_operations[shift_type][2:4]
                        shift_amount = self.convert_to_binary(instruction[5].replace("]","").replace("!", ""), 5)
                    else:
                        shift_type_code = "00"
                        shift_amount = self.convert_to_binary("0", 5)
                    
                    offset_code = f"{shift_amount} {shift_type_code} 0 {rm}"

                else:
                    if len(instruction) > 3:
                        offset = instruction[3].replace("-", "").replace("]", "").replace("!", "")
                        offset_code = self.convert_to_binary(offset, 12)
                    else:
                        offset_code = self.convert_to_binary("0", 12)

                code = f"{condition_code} 001 {pre_indexing_bit} {up_bit} {byte_bit} {write_back_bit} {load_bit} {rn} {rd} {offset_code}"
                print(code)

arm = Arm("code.txt")
arm.instruction_code()
