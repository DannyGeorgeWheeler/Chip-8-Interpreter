
import sdl2

memory = [] # 4 kilobytes of RAM

display = [] # 64 x 32 pixels monochrome

PC = 0 # A program counter pointing at current instruction in memory

I = 0 # 16-bit index register

stack = [] # 16-bit addresses, used to cal subroutines and return

stackPointer = 0

delayTimer = 0 # 8-bit delay timer decrements 60 times per second

soundTimer = 0 # works as the delay timer but beeps while not 0

variableRegister = {
    'V0': 0b0000,
    'V1': 0b0000,
    'V2': 0b0000,
    'V3': 0b0000,
    'V4': 0b0000,
    'V5': 0b0000,
    'V6': 0b0000,
    'V7': 0b0000,
    'V8': 0b0000,
    'V9': 0b0000,
    'VA': 0b0000,
    'VB': 0b0000,
    'VC': 0b0000,
    'VD': 0b0000,
    'VE': 0b0000,
    'VF': 0b0000,
}

def Fetch():
    print(memory[PC])   # read instruction PC is pointing at
    PC += 2             # increment PC by 2 for next opcode

def Decode(opcode):
    A = hex(opcode[2])       # first nibble of opcode
    X = hex(opcode[3])       # second nibble of opcode 
    Y = hex(opcode[4])       # third nibble of opcode
    N = hex(opcode[5])       # fourth nibble of opcode
    NN = hex(opcode[4:6])    # second byte of opcode
    NNN = hex(opcode[3:6])   # second, third, fourth nibbles


    if A == '0':
        if NNN == '0E0':    
            # 00E0 CLS - Clear Display
            display = []
        elif NNN = '0EE':   
            # 00EE RET - Return from subroutine
            PC = stack.pop()
        else:
            # 0NNN - Not Implemented
            pass
    elif A == '1':
        # 1NNN JUMP - Set program counter to address
        PC = NNN
    elif A == '2':
        # 2NNN CALL - store program counter then set program counter
        stack.append(PC)
        PC = NNN
    elif A == '6':
        # 6XNN SET - set VX to NN
        variableRegister['V'+X] = NN
    elif A == '7':
        # 7XNN ADD - add NN to VX
        int()
        variableRegister['V'+X] += NN

    

    

            


