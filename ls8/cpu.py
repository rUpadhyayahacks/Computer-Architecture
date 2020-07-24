import sys


CALL = 0b01010000
HLT = 0b00000001
JEQ = 0b01010101
JMP = 0b01010100
JNE = 0b01010110
LDI = 0b10000010
POP = 0b01000110
PRA = 0b01001000
PRN = 0b01000111
PUSH = 0b01000101
RET = 0b00010001
ST = 0b10000100

ADD = 0b10100000
CMP = 0b10100111
SUB = 0b10100001
DIV = 0b10100011
MOD = 0b10100100
MUL = 0b10100010
# TODO if time permitting 
NOT = 0b01101001
OR = 0b10101010
SHL = 0b10101100
SHR = 0b10101101
AND = 0b10101000
XOR = 0b10101011
ADDI = 0b10100101
SP = 7


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.register = [0] * 8
        self.pc = 0
        self.fl = 0b00000000
        self.register[SP] = 0xF4
        self.process_table = {
            CALL: self.call,
            HLT: self.hlt,
            JEQ: self.jeq,
            JMP: self.jmp,
            JNE: self.jne,
            LDI: self.ldi,
            POP: self.pop,
            PRA: self.pra,
            PRN: self.prn,
            PUSH: self.push,
            RET: self.ret,
            ST: self.st,
            ADD: self.alu,
            CMP: self.alu,
            DIV: self.alu,
            MUL: self.alu,
            SUB: self.alu,
        }

    def call(self, op_a, op_b=None):
        '''
        Calls a subroutine(function) at address stored in register[op_a]
        '''
        self.register[SP] -= 1
        self.ram_write(self.register[SP], self.pc + 2)
        self.pc = self.register[op_a]

    def hlt(self, op_a=None, op_b=None):
        '''
        Halt cpu and exit emulator
        '''
        sys.exit()

    def jeq(self, op_a, op_b=None):
        '''
        Check 'Equal' flag. If true, jump to register[op_a]
        '''
        if self.fl & 0b1 == 1:
            self.pc = self.register[op_a]
        else:
            self.pc += 2

    def jmp(self, op_a, op_b=None):
        '''
        Jump to the address stored in register[op_a]
        '''
        self.pc = self.register[op_a]

    def jne(self, op_a, op_b=None):
        '''
        Check 'Equal' flag. If clear, jump to register[op_a]
        '''
        if self.fl & 0b1 == 0:
            self.pc = self.register[op_a]
        else:
            self.pc += 2

    def ldi(self, op_a, op_b):
        '''
        Set the value of register[op_a] to op_b
        '''
        self.register[op_a] = op_b

    def pop(self, op_a, op_b=None):
        '''
        Pop the value at the top of the stack into register[op_a]
        '''
        value = self.ram_read(self.register[SP])
        self.register[op_a] = value
        self.register[SP] += 1
        return value

    def pra(self, op_a, op_b=None):
        '''
        Print alpha character value stored in the given register
        '''
        print(chr(self.register[op_a]))

    def prn(self, op_a, op_b=None):
        '''
        Print numeric value stored in register[op_a]
        '''
        print(self.register[op_a])

    def push(self, op_a, op_b=None):
        '''
        Push the value in the register[op_a] onto the stack
        '''
        self.register[SP] -= 1
        self.ram_write(self.register[SP], self.register[op_a])

    def ret(self, op_a=None, op_b=None):
        '''
        Return from subroutine
        '''
        self.pc = self.ram_read(self.register[SP])
        self.register[SP] += 1

    def st(self, op_a, op_b):
        '''
        Store value in register[op_b] in the address stored in register[op_a]
        '''
        self.ram_write(self.register[op_a], self.register[op_b])

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        with open(filename) as f:
            for line in f:
                line = line.split('#')
                line = line[0].strip()
                if line == '':
                    continue
                self.ram[address] = int(line, 2)
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == ADD:
            self.register[reg_a] += self.register[reg_b]
        elif op == ADDI:
            self.register[reg_a] += reg_b
        elif op == AND:
            self.register[reg_a] &= self.register[reg_b]
        elif op == CMP:
            op_a = self.register[reg_a]
            op_b = self.register[reg_b]
            if op_a == op_b:
                self.fl = 0b00000001
            elif op_a < op_b:
                self.fl = 0b00000100
            elif op_a > op_b:
                self.fl = 0b00000010
        elif op == DIV:
            if self.register[reg_b] != 0:
                self.register[reg_a] /= self.register[reg_b]
            else:
                raise Exception("Cannot divide by 0")
        elif op == MOD:
            if self.register[reg_b] != 0:
                self.register[reg_a] %= self.register[reg_b]
            else:
                raise Exception('Cannot divide by 0')
        elif op == MUL:
            self.register[reg_a] *= self.register[reg_b]
        elif op == SUB:
            self.register[reg_a] -= self.register[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, mar):
        '''
        Takes address (mar) in ram and returns the value (mdr) stored there
        '''
        mdr = self.ram[mar]
        return mdr

    def ram_write(self, mar, mdr):
        '''
        Stores 'value' (MDR) at given 'address' (MAR) in ram
        '''
        self.ram[mar] = mdr

    def run(self):
        '''
        Run the CPU
        '''



        while True:
            ir = self.ram[self.pc]
            op_a = self.ram_read(self.pc + 1)
            op_b = self.ram_read(self.pc + 2)
            run_counter = (ir >> 6) + 1
            alu_op = ((ir >> 5) & 0b1)
            set_pc = ((ir >> 4) & 0b1)
            if ir in self.process_table:
                if alu_op:
                    self.process_table[ir](ir, op_a, op_b)
                else:
                    self.process_table[ir](op_a, op_b)
            else:
                print('Unsupported operation')
            if not set_pc:
                self.pc += run_counter

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X %02X |" % (
            self.pc,
            self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')

        print()