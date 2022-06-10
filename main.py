
import sdl2
import sdl2.ext
import math
import random

class Chip8:
    def __init__(self):
        self.shiftMethod = True # a configurable option for instructions that shift 8XY6 & 8XYE
        self.cycleSpeed = 1700 # 700 MHz is a good speed for most Chip8 games
        self.memory = [0x0]*4096 # 4 kilobytes of RAM
        self.display = [[0] * 32 for _ in range(64)] # 64 x 32 pixels monochrome
        self.PC = 0x200 # A program counter pointing at current instruction in memory
        self.I = 0 # 16-bit index register
        self.stack = [] # 16-bit addresses, used to cal subroutines and return
        self.stackPointer = 0
        self.delayTimer = 0 # 8-bit delay timer decrements 60 times per second
        self.soundTimer = 0 # works as the delay timer but beeps while not 0
        self.variableRegister = {
            0x0: 0x00,
            0x1: 0x00,
            0x2: 0x00,
            0x3: 0x00,
            0x4: 0x00,
            0x5: 0x00,
            0x6: 0x00,
            0x7: 0x00,
            0x8: 0x00,
            0x9: 0x00,
            0xA: 0x00,
            0xB: 0x00,
            0xC: 0x00,
            0xD: 0x00,
            0xE: 0x00,
            0xF: 0x00
        }
        self.keypad = {
            0x0: [sdl2.SDL_SCANCODE_0, sdl2.SDLK_0],
            0x1: [sdl2.SDL_SCANCODE_1, sdl2.SDLK_1],
            0x2: [sdl2.SDL_SCANCODE_2, sdl2.SDLK_2],
            0x3: [sdl2.SDL_SCANCODE_3, sdl2.SDLK_3],
            0x4: [sdl2.SDL_SCANCODE_4, sdl2.SDLK_4],
            0x5: [sdl2.SDL_SCANCODE_5, sdl2.SDLK_5],
            0x6: [sdl2.SDL_SCANCODE_6, sdl2.SDLK_6],
            0x7: [sdl2.SDL_SCANCODE_7, sdl2.SDLK_7],
            0x8: [sdl2.SDL_SCANCODE_8, sdl2.SDLK_8],
            0x9: [sdl2.SDL_SCANCODE_9, sdl2.SDLK_9],
            0xA: [sdl2.SDL_SCANCODE_A, sdl2.SDLK_a],
            0xB: [sdl2.SDL_SCANCODE_B, sdl2.SDLK_b],
            0xC: [sdl2.SDL_SCANCODE_C, sdl2.SDLK_c],
            0xD: [sdl2.SDL_SCANCODE_D, sdl2.SDLK_d],
            0xE: [sdl2.SDL_SCANCODE_E, sdl2.SDLK_e],
            0xF: [sdl2.SDL_SCANCODE_F, sdl2.SDLK_f]
        }
        self.keyUp = None
        self.fonts = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]
        for idx, byte in enumerate(self.fonts):
            self.memory[idx] = byte
        self.run()

    def load(self):
        #file = "C:/Users/danny/Desktop/GameDev/Chip8/roms/test_opcode.ch8"
        #file = "C:/Users/danny/Desktop/GameDev/Chip8/roms/IBM Logo.ch8"
        file = "C:/Users/danny/Desktop/GameDev/Chip8/roms/Breakout [Carmelo Cortez, 1979].ch8"
        #file = "C:/Users/danny/Desktop/GameDev/Chip8/roms/Connect 4 [David Winter].ch8"
        
        with open(file, "rb") as rom:
            loc = 0x200
            for byte in rom.read():
                self.memory[loc] = byte
                loc += 1

    def fetch(self):
        # print('fetching')
        firstByte = self.memory[self.PC]        # read instruction PC is pointing at
        secondByte = self.memory[self.PC + 1]
        opcode = (firstByte << 8 | secondByte)
        #print(f'firstByte = {firstByte} secondByte = {secondByte} opcode = {hex(opcode)}')
        self.PC += 2                            # increment PC by 2 for next opcode
        return opcode

    def execute(self, opcode):
        # print('executing', opcode)
        # Use bitwise operations to extract opcode
        nib1 = (opcode & 0xf000) >> 12    # first nibble of opcode
        X = (opcode & 0x0f00) >> 8        # second nibble of opcode
        Y = (opcode & 0x00f0) >> 4        # third nibble of opcode
        N = opcode & 0x000f             # fourth nibble of opcode
        NN = opcode & 0x00ff            # second byte of opcode
        NNN = opcode & 0x0fff           # second, third, fourth nibbles

        # print(f'opcode is {hex(opcode)}')
        # print(f'nib1 should be {opcode & 0xf000 >> 12}')
        # print(f'Nib1 is {nib1}')
        # print(f'NNN is {NNN}')

        if nib1 == 0x0:
            if NNN == 0x0E0:    
                # 00E0 CLS - Clear Display
                self.display = [[0] * 32 for _ in range(64)] # 64 x 32 pixels monochrome
            elif NNN == 0x0EE:   
                # 00EE RET - Return from subroutine
                self.PC = self.stack.pop()
            else:
                # 0NNN - Not Implemented
                pass
        elif nib1 == 0x1:
            # 1NNN JUMP - Set program counter to address
            #print(f'setting program counter to {NNN}')
            self.PC = NNN
        elif nib1 == 0x2:
            # 2NNN CALL - store program counter then set program counter
            self.stack.append(self.PC)
            self.PC = NNN
        elif nib1 == 0x3:
            # 3XNN skip one instruction if value in VX equal to NN
            if self.variableRegister[X] == NN:
                self.PC += 2
        elif nib1 == 0x4:
            # 4XNN skip one instruction if value in VX NOT equal to NN
            if self.variableRegister[X] != NN:
                self.PC += 2
        elif nib1 == 0x5:
            # 5XY0 skip one instruction if value in VX equal to VY
            if self.variableRegister[X] == self.variableRegister[Y]:
                self.PC += 2
        elif nib1 == 0x6:
            # 6XNN SET - set VX to NN
            self.variableRegister[X] = NN
        elif nib1 == 0x7:
            # 7XNN ADD - add NN to VX
            self.variableRegister[X] += NN
            self.variableRegister[X] &= 0xFF
        elif nib1 == 0x8:
            # Logical and arithmetic instructions
            if N == 0x0:
                # 8XY0 set VX to VY
                self.variableRegister[X] = self.variableRegister[Y]
            elif N == 0x1:
                # 8XY1 set VX to Binary OR of VX and VY
                self.variableRegister[X] |= self.variableRegister[Y]
            elif N == 0x2:
                # 8XY2 set VX to Binary AND of VX and VY
                self.variableRegister[X] &= self.variableRegister[Y]
            elif N == 0x3:
                # 8XY3 set VX to Binary XOR of VX and VY
                self.variableRegister[X] ^= self.variableRegister[Y]
            elif N == 0x4:
                # 8XY4 add VY to VX
                self.variableRegister[X] += self.variableRegister[Y]
                if self.variableRegister[X] > 0xFF:
                    self.variableRegister[X] &= 0xFF
                    self.variableRegister[0xF] = 1
                else:
                    self.variableRegister[X] = 0
            elif N == 0x5:
                # 8XY5 subtract VY from VX
                # VF Flag is set to 1 if the result is positive and 0 if negative
                if self.variableRegister[X] > self.variableRegister[Y]:
                    self.variableRegister[0xF] = 1
                else:
                    self.variableRegister[0xF] = 0
                self.variableRegister[X] = self.variableRegister[X] - self.variableRegister[Y]
                # only keep the smallest 8 bits
                self.variableRegister[X] &= 0xFF
            elif N == 0x6:
                # 8XY6 shift the value in VX one bit to the right 
                # shift method determines whether VY is copied into VX before the operation
                # The VY copy was the original method of this instruction, but it was changed with Chip-48
                if self.shiftMethod:
                    self.variableRegister[X] = self.variableRegister[Y]
                # set VF flag to value of the bit to be shifted out
                self.variableRegister[0xF] = (self.variableRegister[X] & 1)
                # shift VX
                self.variableRegister[X] >>= 1
            elif N == 0x7:
                # 8XY7 subtract VX from VY and set to VX
                # VF Flag is set to 1 if the result is positive and 0 if negative
                if self.variableRegister[Y] > self.variableRegister[X]:
                    self.variableRegister[0xF] = 1
                elif self.variableRegister[X] > self.variableRegister[Y]:
                    self.variableRegister[0xF] = 0
                self.variableRegister[X] = self.variableRegister[Y] - self.variableRegister[X]
                # only keep the smallest 8 bits
                self.variableRegister[X] &= 0xFF
            elif N == 0xE:
                # 8XYE shift the value in VX one bit to the left 
                # shift method determines whether VY is copied into VX before the operation
                # The VY copy was the original method of this instruction, but it was changed with Chip-48
                if self.shiftMethod:
                    self.variableRegister[X] = self.variableRegister[Y]
                # set VF flag to value of the bit to be shifted out
                self.variableRegister[0xF] = (self.variableRegister[X] & 0b10000000)
                # shift VX to the left and only keep the smallest 8 bits
                self.variableRegister[X] <<= 1
                self.variableRegister[X] &= 0xFF
        elif nib1 == 0x9:
            # 9XY0 skip one instruction if value in VX NOT equal to VY
            if self.variableRegister[X] != self.variableRegister[Y]:
                self.PC += 2
        elif nib1 == 0xA:
            # ANNN SET - set index register to NNN
            self.I = NNN
        elif nib1 == 0xB:
            # BNNN Jump to the address NNN plus value in V0
            self.PC = NNN + self.variableRegister[0x0]
        elif nib1 == 0xC:
            # CXNN Set VX to random number and binary AND with NN
            self.variableRegister[X] = random.randint(0, 255) & NN
        elif nib1 == 0xD:
            # DXYN - draw a sprite from memory location in I to X and Y coords
            pixelX = self.variableRegister[X] & 63
            pixelY = self.variableRegister[Y] & 31
            self.variableRegister[0xF] = 0
            #print(f'drawing sprite: to {pixelX} and {pixelY} ')
            for row in range(N):
                byte = self.memory[self.I + row]
                #print(f'byte is {byte}')

                for col in range(8):
                    # print(f'current pixel X: {pixelX + col} and current pixel Y: {pixelY + row}')
                    if pixelX + col >= 64 or pixelY + row >= 32:
                        # do not draw pixels outside of display bounds
                        continue
                    # create a bit mask to identify the current bit in the byte (pixel in the row)
                    bitMask = 1 << 7 - col
                    # get the value of the sprites pixel
                    pixelVal = (byte & bitMask) >> 7 - col
                    # check if both display and sprite pixels are on and will be turned off by XOR then set VF flag
                    #print(f'mask: {bitMask} val: {pixelVal}')
                    if self.display[pixelX + col][pixelY + row] and pixelVal:
                        self.variableRegister[0xF] = 1
                    # bitwise XOR the sprites pixel with the display pixel
                    self.display[pixelX + col][pixelY + row] ^= pixelVal
        elif nib1 == 0xE:
            keyStates = sdl2.SDL_GetKeyboardState(None)
            if NN == 0x9E:
                # EX9E Skip instruction if key in VX is down
                print(f'EX9E {self.keypad[X][0]}')
                if keyStates[self.keypad[X][0]]:
                    self.PC += 2
            elif NN == 0xA1:
                # EXA1 Skip instruction if key in VX is NOT down
                print(f'EXA1 {self.keypad[X][0]}')
                if not keyStates[self.keypad[X][0]]:
                    print(f'skipping instruction because key {self.keypad[X][0]} not down')
                    self.PC += 2
        elif nib1 == 0xF:
            if NN == 0x07:
                # FX07 set VX to value of delay timer
                self.variableRegister[X] = self.delayTimer
            elif NN == 0x15:
                # FX15 set delay timer to value of VX
                self.delayTimer = self.variableRegister[X]
            elif NN == 0x18:
                # FX18 set sound timer to value of VX
                self.soundTimer = self.variableRegister[X]
            elif NN == 0x1E:
                # Add VX to Index and set the VF Flag to 1 if it goes above 0x
                self.I += self.variableRegister[X]
                if self.I > 0xFFF:
                    self.variableRegister[0xF] = 1
                    self.I &= 0xFFF
            elif NN == 0x0A:
                # FX0A block execution until a key is pressed then assign to VX
                if self.keyUp == None:
                    self.PC -= 2
                else:
                    print('key press instruction register')
                    for hexVal, keypad in self.keypad.items():
                        if self.keyUp == keypad[1]:
                            print(f'found key {keypad[1]}')
                            self.variableRegister[X] = hexVal
                            break
            elif NN == 0x29:
                # FX29 set Index to address of hex character in VX
                self.I = (self.variableRegister[X] & 0xF)
            elif NN == 0x33:
                # FX33 Store decimal digits of VX in consecutive memory starting at Index
                digits = str(self.variableRegister[X])
                for idx, digit in enumerate(digits):
                    self.memory[self.I + idx] = int(digit)
            elif NN == 0x55:
                # FX55 Store all register values up to VX into memory starting at Index
                for key, val in self.variableRegister.items():
                    if key > X:
                        continue
                    self.memory[self.I + key] = val
            elif NN == 0x65:
                # FX65 Store values in memory starting at index into the register up to VX
                for key in self.variableRegister.keys():
                    if key > X:
                        continue                    
                    self.variableRegister[key] = self.memory[self.I + key]
        else:
            # instruction not recognised
            #raise Exception(f"Instruction {opcode} is not recognsied")
            pass
                    

    def run(self):
        sdl2.ext.init()
        window = sdl2.ext.Window('Chip 8', size=(640, 320))
        window.show()
        renderer = SoftwareRenderer(window)
        renderer.display = self.display
        world = sdl2.ext.World()
        world.add_system(renderer)
        ms = math.floor(1 / self.cycleSpeed * 10000) # calculate milliseconds to refresh cycle
        self.load()
        running = True
        while running:
            self.keyUp = None
            timer = sdl2.timer.SDL_GetTicks() * 1000
            if timer % 60 == 0:
                # print('timerrefresh')
                if self.delayTimer > 0:
                    self.delayTimer -= 1
                if self.soundTimer > 0:
                    self.soundTimer -= 1
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    running = False
                    break
                if event.type == sdl2.SDL_KEYUP:
                    print(f'key up: {event.key.keysym.sym}')
                    self.keyUp = event.key.keysym.sym
            self.cycle()
            renderer.display = self.display
            world.process()
            sdl2.SDL_Delay(ms)

    def cycle(self):
        # print(f'delay: {self.delayTimer} sound: {self.soundTimer}')
        instruction = self.fetch()
        self.execute(instruction)


class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        self.window = window
        self.background = sdl2.ext.Color(0, 0, 0)
        self.foreground = sdl2.ext.Color(255, 255, 255)
        self.display = None
        super(SoftwareRenderer, self).__init__(window)

    # Modifies the default renderer to show a black screen
    def render(self, components):
        pixels = sdl2.ext.pixels3d(self.surface)
        for x in range(64):
            for y in range(32):
                x10 = x*10
                y10 = y*10
                if self.display[x][y]:
                    pixels[x10:x10+10,y10:y10+10] = self.foreground
                    #pixels[x,y] = self.foreground
                else:
                    pixels[x10:x10+10,y10:y10+10] = self.background
                    #pixels[x,y] = self.background
        
        for x in range(0, 640, 10):
            sdl2.ext.fill(self.surface, sdl2.ext.Color(30,30,30), (x, 0, 1, 320))
        for y in range(0, 320, 10):
            sdl2.ext.fill(self.surface, sdl2.ext.Color(30,30,30), (0, y, 640, 1))
                
        super(SoftwareRenderer, self).render(components)

interpreter = Chip8()