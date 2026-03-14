#
#   elf_loader/cpu_emulator.py
#   CPU 模拟器模块
#   提供 x86/x86_64 CPU 模拟功能，用于执行 ELF 程序。
#
#   模拟 CPU 型号：SpaceCPU 1 Pro (x86/x86_64) || 未量产，处于构思阶段
#
#   By GoutouStdio
#   @ 2022~2026 GoutouStdio. Open all rights.

from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field
from enum import IntEnum
import logging

from .elf_constants import ELFMachine

logger = logging.getLogger(__name__)


class Register32(IntEnum):
    EAX, ECX, EDX, EBX, ESP, EBP, ESI, EDI, EIP, EFLAGS = range(10)


class Register64(IntEnum):
    RAX, RCX, RDX, RBX, RSP, RBP, RSI, RDI = range(8)
    R8, R9, R10, R11, R12, R13, R14, R15 = range(8, 16)
    RIP, RFLAGS = 16, 17


class EFlags(IntEnum):
    CF, PF, AF, ZF, SF, TF, IF, DF, OF = 0, 2, 4, 6, 7, 8, 9, 10, 11


@dataclass
class CPUState:
    regs: Dict[int, int] = field(default_factory=dict)
    cs: int = 0x23
    ds: int = 0x2b
    es: int = 0x2b
    fs: int = 0x2b
    gs: int = 0x2b
    ss: int = 0x2b
    fpu_stack: List[float] = field(default_factory=list)
    xmm_regs: Dict[int, bytes] = field(default_factory=dict)
    cr0: int = 0x80000011
    cr2: int = 0
    cr3: int = 0
    cr4: int = 0
    dr0: int = 0
    dr1: int = 0
    dr2: int = 0
    dr3: int = 0
    dr6: int = 0
    dr7: int = 0
    
    def __post_init__(self):
        if not self.regs:
            for i in range(18):
                self.regs[i] = 0


class CPUException(Exception):
    pass


class InvalidInstruction(CPUException):
    pass


class PageFault(CPUException):
    def __init__(self, address: int, is_write: bool = False):
        self.address = address
        self.is_write = is_write
        super().__init__(f"Page fault at 0x{address:08x} ({'write' if is_write else 'read'})")


class SyscallInterrupt(CPUException):
    def __init__(self, number: int, args: List[int]):
        self.number = number
        self.syscall_args = args
        super().__init__(f"Syscall {number} with args {args}")


class MemoryController:
    def __init__(self, loader):
        self.loader = loader
        self.page_size = 4096
        
    def read_byte(self, addr: int) -> int:
        region = self._find_region(addr)
        if region is None:
            raise PageFault(addr, False)
        return region.data[addr - region.start]
    
    def read_word(self, addr: int) -> int:
        return self.read_byte(addr) | (self.read_byte(addr + 1) << 8)
    
    def read_dword(self, addr: int) -> int:
        return (self.read_byte(addr) | (self.read_byte(addr + 1) << 8) |
                (self.read_byte(addr + 2) << 16) | (self.read_byte(addr + 3) << 24))
    
    def read_qword(self, addr: int) -> int:
        return self.read_dword(addr) | (self.read_dword(addr + 4) << 32)
    
    def read_bytes(self, addr: int, size: int) -> bytes:
        return bytes(self.read_byte(addr + i) for i in range(size))
    
    def write_byte(self, addr: int, value: int) -> None:
        region = self._find_region(addr)
        if region is None or not region.writable:
            raise PageFault(addr, True)
        region.data[addr - region.start] = value & 0xff
    
    def write_word(self, addr: int, value: int) -> None:
        self.write_byte(addr, value & 0xff)
        self.write_byte(addr + 1, (value >> 8) & 0xff)
    
    def write_dword(self, addr: int, value: int) -> None:
        for i in range(4):
            self.write_byte(addr + i, (value >> (i * 8)) & 0xff)
    
    def write_qword(self, addr: int, value: int) -> None:
        for i in range(8):
            self.write_byte(addr + i, (value >> (i * 8)) & 0xff)
    
    def write_bytes(self, addr: int, data: bytes) -> None:
        for i, byte in enumerate(data):
            self.write_byte(addr + i, byte)
    
    def _find_region(self, addr: int):
        for region in self.loader.memory.values():
            if region.start <= addr < region.start + len(region.data):
                return region
        return None


@dataclass
class DecodedOperand:
    operand_type: str
    size: int = 64
    reg: int = -1
    mod: int = 0
    rm: int = 0
    sib: int = 0
    disp: int = 0
    imm: int = 0
    has_sib: bool = False


class InstructionDecoder:
    OPCODES = {
        0x00: ('ADD', 'Eb', 'Gb'), 0x01: ('ADD', 'Ev', 'Gv'),
        0x02: ('ADD', 'Gb', 'Eb'), 0x03: ('ADD', 'Gv', 'Ev'),
        0x04: ('ADD', 'AL', 'Ib'), 0x05: ('ADD', 'rAX', 'Iz'),
        0x10: ('ADC', 'Eb', 'Gb'), 0x11: ('ADC', 'Ev', 'Gv'),
        0x12: ('ADC', 'Gb', 'Eb'), 0x13: ('ADC', 'Gv', 'Ev'),
        0x14: ('ADC', 'AL', 'Ib'), 0x15: ('ADC', 'rAX', 'Iz'),
        0x29: ('SUB', 'Ev', 'Gv'), 0x2B: ('SUB', 'Gv', 'Ev'),
        0x2C: ('SUB', 'AL', 'Ib'), 0x2D: ('SUB', 'rAX', 'Iz'),
        0x30: ('XOR', 'Eb', 'Gb'), 0x31: ('XOR', 'Ev', 'Gv'),
        0x32: ('XOR', 'Gb', 'Eb'), 0x33: ('XOR', 'Gv', 'Ev'),
        0x34: ('XOR', 'AL', 'Ib'), 0x35: ('XOR', 'rAX', 'Iz'),
        0x38: ('CMP', 'Eb', 'Gb'), 0x39: ('CMP', 'Ev', 'Gv'),
        0x3A: ('CMP', 'Gb', 'Eb'), 0x3B: ('CMP', 'Gv', 'Ev'),
        0x3C: ('CMP', 'AL', 'Ib'), 0x3D: ('CMP', 'rAX', 'Iz'),
        0x40: ('INC', 'rAX'), 0x41: ('INC', 'rCX'),
        0x50: ('PUSH', 'rAX'), 0x51: ('PUSH', 'rCX'), 0x52: ('PUSH', 'rDX'),
        0x53: ('PUSH', 'rBX'), 0x54: ('PUSH', 'rSP'), 0x55: ('PUSH', 'rBP'),
        0x56: ('PUSH', 'rSI'), 0x57: ('PUSH', 'rDI'),
        0x58: ('POP', 'rAX'), 0x59: ('POP', 'rCX'), 0x5A: ('POP', 'rDX'),
        0x5B: ('POP', 'rBX'), 0x5C: ('POP', 'rSP'), 0x5D: ('POP', 'rBP'),
        0x5E: ('POP', 'rSI'), 0x5F: ('POP', 'rDI'),
        0x6A: ('PUSH', 'Ib'), 0x68: ('PUSH', 'Iz'),
        0x63: ('MOVSXD', 'Ed', 'Gv'),
        0x70: ('JO', 'Jb'), 0x71: ('JNO', 'Jb'), 0x72: ('JB', 'Jb'),
        0x73: ('JNB', 'Jb'), 0x74: ('JZ', 'Jb'), 0x75: ('JNZ', 'Jb'),
        0x76: ('JBE', 'Jb'), 0x77: ('JNBE', 'Jb'), 0x78: ('JS', 'Jb'),
        0x79: ('JNS', 'Jb'), 0x7C: ('JL', 'Jb'), 0x7D: ('JNL', 'Jb'),
        0x7E: ('JLE', 'Jb'), 0x7F: ('JNLE', 'Jb'),
        0x80: ('GRP1', 'Eb', 'Ib'), 0x81: ('GRP1', 'Ev', 'Iz'),
        0x83: ('GRP1', 'Ev', 'Ib'),
        0x84: ('TEST', 'Eb', 'Gb'), 0x85: ('TEST', 'Ev', 'Gv'),
        0xA8: ('TEST', 'AL', 'Ib'), 0xA9: ('TEST', 'rAX', 'Iz'),
        0x88: ('MOV', 'Eb', 'Gb'), 0x89: ('MOV', 'Ev', 'Gv'),
        0x8A: ('MOV', 'Gb', 'Eb'), 0x8B: ('MOV', 'Gv', 'Ev'),
        0x8D: ('LEA', 'Gv', 'M'),
        0x90: ('NOP',), 0xC3: ('RET',), 0xC9: ('LEAVE',),
        0xB0: ('MOV', 'AL', 'Ib'), 0xB8: ('MOV', 'rAX', 'Iv'),
        0xB9: ('MOV', 'rCX', 'Iv'), 0xBA: ('MOV', 'rDX', 'Iv'),
        0xBB: ('MOV', 'rBX', 'Iv'), 0xBC: ('MOV', 'rSP', 'Iv'),
        0xBD: ('MOV', 'rBP', 'Iv'), 0xBE: ('MOV', 'rSI', 'Iv'),
        0xBF: ('MOV', 'rDI', 'Iv'),
        0xC6: ('MOV', 'Eb', 'Ib'), 0xC7: ('MOV', 'Ev', 'Iz'),
        0x99: ('CDQ',),
        0xE8: ('CALL', 'Jz'), 0xE9: ('JMP', 'Jz'), 0xEB: ('JMP', 'Jb'),
        0xF4: ('HLT',), 0xF7: ('GRP3', 'Ev'), 0xFF: ('GRP5', 'Ev'),
    }
    
    OPCODES_0F = {
        0x05: ('SYSCALL',), 0x1F: ('NOP', 'M'),
        0xB6: ('MOVZBL', 'Eb', 'Gv'),
        0x40: ('CMOVO', 'Gv', 'Ev'), 0x41: ('CMOVNO', 'Gv', 'Ev'),
        0x42: ('CMOVB', 'Gv', 'Ev'), 0x43: ('CMOVNB', 'Gv', 'Ev'),
        0x44: ('CMOVZ', 'Gv', 'Ev'), 0x45: ('CMOVNZ', 'Gv', 'Ev'),
        0x46: ('CMOVBE', 'Gv', 'Ev'), 0x47: ('CMOVNBE', 'Gv', 'Ev'),
        0x48: ('CMOVS', 'Gv', 'Ev'), 0x49: ('CMOVNS', 'Gv', 'Ev'),
        0x4A: ('CMOVP', 'Gv', 'Ev'), 0x4B: ('CMOVNP', 'Gv', 'Ev'),
        0x4C: ('CMOVL', 'Gv', 'Ev'), 0x4D: ('CMOVNL', 'Gv', 'Ev'),
        0x4E: ('CMOVLE', 'Gv', 'Ev'), 0x4F: ('CMOVNLE', 'Gv', 'Ev'),
        0x80: ('JO', 'Jz'), 0x81: ('JNO', 'Jz'),
        0x82: ('JB', 'Jz'), 0x83: ('JNB', 'Jz'),
        0x84: ('JZ', 'Jz'), 0x85: ('JNZ', 'Jz'),
        0x86: ('JBE', 'Jz'), 0x87: ('JNBE', 'Jz'),
        0x88: ('JS', 'Jz'), 0x89: ('JNS', 'Jz'),
        0x8C: ('JL', 'Jz'), 0x8D: ('JNL', 'Jz'),
        0x8E: ('JLE', 'Jz'), 0x8F: ('JNLE', 'Jz'),
    }
    
    def __init__(self, is_64bit: bool = True):
        self.is_64bit = is_64bit
        self.rex = 0
        self.has_rex = False
        self.operand_size = 64
        self.address_size = 64
        
    def decode(self, memory: MemoryController, ip: int) -> Tuple[str, int, List[Any]]:
        opcode = memory.read_byte(ip)
        length = 1
        self.has_rex = False
        self.operand_size = 32 if not self.is_64bit else 64
        self.address_size = 32 if not self.is_64bit else 64
        
        if self.is_64bit and 0x40 <= opcode <= 0x4F:
            self.rex = opcode
            self.has_rex = True
            if opcode & 0x08:
                self.operand_size = 64
            opcode = memory.read_byte(ip + length)
            length += 1
        
        if opcode == 0x66:
            self.operand_size = 16
            opcode = memory.read_byte(ip + length)
            length += 1
            while opcode == 0x66:
                opcode = memory.read_byte(ip + length)
                length += 1
        if opcode == 0x67:
            self.address_size = 32
            opcode = memory.read_byte(ip + length)
            length += 1
        
        while opcode in (0x26, 0x2e, 0x36, 0x3e, 0x64, 0x65):
            opcode = memory.read_byte(ip + length)
            length += 1
        
        if opcode == 0x0F:
            return self._decode_0f(memory, ip, length)
        
        if opcode not in self.OPCODES:
            raise InvalidInstruction(f"Unknown opcode: 0x{opcode:02x} at 0x{ip:08x}")
        
        info = self.OPCODES[opcode]
        name = info[0]
        
        if name == 'CDQ' and self.operand_size == 64:
            name = 'CQO'
        
        operands = []
        last_modrm = None
        
        for i, operand_type in enumerate(info[1:]):
            if name == 'GRP1':
                if last_modrm is None:
                    last_modrm, length = self._read_modrm(memory, ip, length, operands)
                grp_op = ('grp_op', last_modrm.reg)
                op_size = 8 if info[1] == 'Eb' else self.operand_size
                next_op = info[i + 2] if i + 2 < len(info) else None
                if next_op == 'Ib':
                    imm = memory.read_byte(ip + length)
                    length += 1
                    operands = [grp_op, last_modrm, ('imm8', imm, op_size)]
                elif next_op == 'Iz':
                    imm, length = self._read_imm(memory, ip, length, self.operand_size)
                    operands = [grp_op, last_modrm, ('immz', imm, self.operand_size)]
                else:
                    operands = [grp_op, last_modrm]
                last_modrm.size = op_size
                break
            elif name in ('GRP3', 'GRP5'):
                if last_modrm is None:
                    last_modrm, length = self._read_modrm(memory, ip, length, operands)
                grp_op = ('grp_op', last_modrm.reg)
                operands = [grp_op, last_modrm]
                break
            elif operand_type in ('Eb', 'Ev', 'Ed'):
                if last_modrm is None:
                    last_modrm, length = self._read_modrm(memory, ip, length, operands)
                    if operand_type == 'Eb':
                        last_modrm.size = 8
                else:
                    operands.append(last_modrm)
            elif operand_type == 'Gb':
                if last_modrm is not None:
                    operands.append(('Gb', last_modrm.reg, 8))
                else:
                    last_modrm, length = self._read_modrm(memory, ip, length, operands)
                    operands[0] = ('Gb', last_modrm.reg, 8)
            elif operand_type == 'Gv':
                if last_modrm is not None:
                    operands.append(('Gv', last_modrm.reg, self.operand_size))
                else:
                    last_modrm, length = self._read_modrm(memory, ip, length, operands)
                    operands[0] = ('Gv', last_modrm.reg, self.operand_size)
            elif operand_type == 'M':
                if last_modrm is None:
                    last_modrm, length = self._read_modrm(memory, ip, length, operands)
                else:
                    operands.append(last_modrm)
            elif operand_type == 'Ib':
                imm = memory.read_byte(ip + length)
                length += 1
                operands.append(('imm8', imm))
            elif operand_type == 'Iz':
                imm, length = self._read_imm(memory, ip, length, self.operand_size)
                operands.append(('immz', imm, self.operand_size))
            elif operand_type == 'Iv':
                imm, length = self._read_imm(memory, ip, length, self.operand_size)
                operands.append(('immv', imm, self.operand_size))
            elif operand_type == 'Jb':
                offset = memory.read_byte(ip + length)
                if offset & 0x80:
                    offset -= 0x100
                length += 1
                operands.append(('rel8', offset))
            elif operand_type == 'Jz':
                offset, length = self._read_imm(memory, ip, length, 32)
                operands.append(('relz', offset, 32))
            elif operand_type.startswith('r'):
                reg_num = self._get_register_number(operand_type, opcode)
                operands.append(('reg', reg_num, self.operand_size))
            elif operand_type == 'AL':
                operands.append(('reg', 0, 8))
        
        return (name, length, operands)
    
    def _decode_0f(self, memory: MemoryController, ip: int, length: int) -> Tuple[str, int, List[Any]]:
        opcode2 = memory.read_byte(ip + length)
        length += 1
        
        if opcode2 not in self.OPCODES_0F:
            raise InvalidInstruction(f"Unknown 0x0F opcode: 0x{opcode2:02x}")
        
        info = self.OPCODES_0F[opcode2]
        name = info[0]
        operands = []
        last_modrm = None
        
        if name == 'SYSCALL':
            return (name, length, operands)
        elif name == 'NOP':
            if len(info) > 1:
                _, length = self._read_modrm(memory, ip, length, operands)
            return (name, length, operands)
        elif name.startswith('J'):
            offset = memory.read_dword(ip + length)
            length += 4
            operands.append(('relz', offset, 32))
            return (name, length, operands)
        elif name == 'MOVZBL':
            last_modrm, length = self._read_modrm(memory, ip, length, operands)
            last_modrm.size = 8
            operands.append(('Gv', last_modrm.reg, self.operand_size))
        elif name.startswith('CMOV'):
            last_modrm, length = self._read_modrm(memory, ip, length, operands)
            if len(operands) == 0:
                operands.append(('Gv', last_modrm.reg, self.operand_size))
                operands.append(last_modrm)
            elif len(operands) == 1:
                operands.insert(0, ('Gv', last_modrm.reg, self.operand_size))
        
        return (name, length, operands)
    
    def _read_modrm(self, memory: MemoryController, ip: int, length: int, operands: List) -> Tuple[DecodedOperand, int]:
        modrm = memory.read_byte(ip + length)
        length += 1
        mod = (modrm >> 6) & 0x3
        reg = (modrm >> 3) & 0x7
        rm = modrm & 0x7
        
        if self.has_rex:
            if self.rex & 0x04:
                reg |= 0x8
            if self.rex & 0x01:
                rm |= 0x8
        
        operand = DecodedOperand(operand_type='modrm', mod=mod, reg=reg, rm=rm)
        
        if mod != 3 and (rm & 0x7) == 4:
            sib = memory.read_byte(ip + length)
            length += 1
            operand.sib = sib
            operand.has_sib = True
        
        if mod == 0 and (rm == 5 or (operand.has_sib and (operand.sib & 0x7) == 5)):
            disp = memory.read_dword(ip + length)
            length += 4
            if disp & 0x80000000:
                disp -= 0x100000000
            operand.disp = disp
        elif mod == 1:
            disp = memory.read_byte(ip + length)
            length += 1
            if disp & 0x80:
                disp -= 0x100
            operand.disp = disp
        elif mod == 2:
            disp = memory.read_dword(ip + length)
            length += 4
            if disp & 0x80000000:
                disp -= 0x100000000
            operand.disp = disp
        
        operands.append(operand)
        return operand, length
    
    def _read_imm(self, memory: MemoryController, ip: int, length: int, size: int) -> Tuple[int, int]:
        if size == 16:
            imm = memory.read_word(ip + length)
            length += 2
        elif size == 32:
            imm = memory.read_dword(ip + length)
            length += 4
        else:
            imm = memory.read_dword(ip + length)
            length += 4
        return imm, length
    
    def _get_register_number(self, reg_name: str, opcode: int) -> int:
        reg_map = {'rAX': 0, 'rCX': 1, 'rDX': 2, 'rBX': 3,
                   'rSP': 4, 'rBP': 5, 'rSI': 6, 'rDI': 7}
        base = reg_map.get(reg_name, 0)
        if self.has_rex and (self.rex & 0x01):
            return base | 0x8
        return base


class CPUEmulator:
    def __init__(self, loader, syscall_handler: Optional[Callable] = None):
        self.loader = loader
        self.parser = loader.parser
        self.is_64bit = not self.parser.is_32bit
        self.memory = MemoryController(loader)
        self.decoder = InstructionDecoder(self.is_64bit)
        self.state = CPUState()
        self.syscall_handler = syscall_handler
        self.instruction_count = 0
        self.max_instructions = 10_000_000
        self.next_ip = 0
        self._init_registers()
    
    def _init_registers(self) -> None:
        stack_top = self.loader.stack_top
        if stack_top >= 0x7fff0000:
            stack_top = 0x7ffefff0
        if self.is_64bit:
            self.state.regs[Register64.RSP] = stack_top
            self.state.regs[Register64.RIP] = self.loader.entry_point
            self.state.regs[Register64.RFLAGS] = 0x202
        else:
            self.state.regs[Register32.ESP] = stack_top
            self.state.regs[Register32.EIP] = self.loader.entry_point
            self.state.regs[Register32.EFLAGS] = 0x202
    
    def set_argv_envp(self, argv: List[str], envp: Dict[str, str]) -> None:
        if self.is_64bit:
            self._setup_argv_envp_64(argv, envp)
        else:
            self._setup_argv_envp_32(argv, envp)
    
    def _setup_argv_envp_64(self, argv: List[str], envp: Dict[str, str]) -> None:
        stack_top = self.loader.stack_top
        if stack_top >= 0x7fff0000:
            stack_top = 0x7ffefff0
        rsp = stack_top & ~0xF
        
        def push_qword(value: int) -> int:
            nonlocal rsp
            rsp -= 8
            self.memory.write_qword(rsp, value)
            return rsp
        
        def push_data(data: bytes) -> int:
            nonlocal rsp
            rsp -= len(data)
            self.memory.write_bytes(rsp, data)
            return rsp
        
        envp_addrs = [push_data(f"{k}={v}\x00".encode()) for k, v in reversed(list(envp.items()))]
        argv_addrs = [push_data((arg + '\x00').encode()) for arg in reversed(argv)]
        rsp &= ~0x7
        
        push_qword(0)
        push_qword(0)
        for addr in reversed(envp_addrs):
            push_qword(addr)
        push_qword(0)
        for addr in reversed(argv_addrs):
            push_qword(addr)
        push_qword(len(argv))
        
        self.state.regs[Register64.RSP] = rsp
    
    def _setup_argv_envp_32(self, argv: List[str], envp: Dict[str, str]) -> None:
        stack_top = self.loader.stack_top
        if stack_top >= 0x7fff0000:
            stack_top = 0x7ffefff0
        esp = stack_top & ~0x3
        
        def push_dword(value: int) -> int:
            nonlocal esp
            esp -= 4
            self.memory.write_dword(esp, value)
            return esp
        
        def push_data(data: bytes) -> int:
            nonlocal esp
            esp -= len(data)
            self.memory.write_bytes(esp, data)
            return esp
        
        envp_addrs = [push_data(f"{k}={v}\x00".encode()) for k, v in reversed(list(envp.items()))]
        argv_addrs = [push_data((arg + '\x00').encode()) for arg in reversed(argv)]
        esp &= ~0x3
        
        push_dword(0)
        push_dword(0)
        for addr in reversed(envp_addrs):
            push_dword(addr)
        push_dword(0)
        for addr in reversed(argv_addrs):
            push_dword(addr)
        push_dword(len(argv))
        
        self.state.regs[Register32.ESP] = esp
    
    def run(self, max_instructions: Optional[int] = None) -> int:
        if max_instructions:
            self.max_instructions = max_instructions
        
        try:
            while self.instruction_count < self.max_instructions:
                ip = self._get_ip()
                name, length, operands = self.decoder.decode(self.memory, ip)
                result = self._execute(name, length, operands)
                
                if result == 'exit':
                    break
                
                self.instruction_count += 1
        
        except SyscallInterrupt as e:
            if self.syscall_handler:
                try:
                    result = self.syscall_handler(e.number, *e.syscall_args)
                    self._set_reg(0, result)
                    return self.run(self.max_instructions)
                except SystemExit as se:
                    return se.code if hasattr(se, 'code') and se.code is not None else 0
            return -1
        except SystemExit as se:
            return se.code if hasattr(se, 'code') and se.code is not None else 0
        except Exception as e:
            logger.error(f"Execution error at 0x{self._get_ip():08x}: {e}")
            raise
        
        return self._get_reg(0)
    
    def _get_ip(self) -> int:
        return self.state.regs[Register64.RIP if self.is_64bit else Register32.EIP]
    
    def _set_ip(self, value: int) -> None:
        self.state.regs[Register64.RIP if self.is_64bit else Register32.EIP] = value
    
    def _get_reg(self, reg: int) -> int:
        return self.state.regs.get(reg, 0)
    
    def _set_reg(self, reg: int, value: int, size: int = 64) -> None:
        if size == 8:
            old = self.state.regs.get(reg, 0)
            self.state.regs[reg] = (old & ~0xFF) | (value & 0xFF)
        elif size == 16:
            old = self.state.regs.get(reg, 0)
            self.state.regs[reg] = (old & ~0xFFFF) | (value & 0xFFFF)
        elif size == 32:
            self.state.regs[reg] = (value & 0xFFFFFFFF)
        else:
            self.state.regs[reg] = value & 0xFFFFFFFFFFFFFFFF
    
    def _get_sp(self) -> int:
        return self.state.regs[Register64.RSP if self.is_64bit else Register32.ESP]
    
    def _set_sp(self, value: int) -> None:
        self.state.regs[Register64.RSP if self.is_64bit else Register32.ESP] = value
    
    def _get_bp(self) -> int:
        return self.state.regs[Register64.RBP if self.is_64bit else Register32.EBP]
    
    def _set_bp(self, value: int) -> None:
        self.state.regs[Register64.RBP if self.is_64bit else Register32.EBP] = value
    
    def _execute(self, name: str, length: int, operands: List[Any]) -> Optional[str]:
        ip = self._get_ip()
        self.next_ip = ip + length
        
        if name == 'NOP': # Nop 命令
            pass
        elif name == 'SYSCALL':
            self._set_ip(self.next_ip)
            raise SyscallInterrupt(
                self._get_reg(Register64.RAX),
                [self._get_reg(r) for r in [Register64.RDI, Register64.RSI, Register64.RDX,
                                            Register64.R10, Register64.R8, Register64.R9]]
            )
        elif name == 'HLT':
            return 'exit'
        elif name == 'PUSH':
            self._exec_push(operands)
        elif name == 'POP':
            self._exec_pop(operands)
        elif name == 'MOV':
            self._exec_mov(operands)
        elif name == 'ADD':
            self._exec_add(operands)
        elif name == 'ADC':
            self._exec_adc(operands)
        elif name == 'SUB':
            self._exec_sub(operands)
        elif name == 'XOR':
            self._exec_xor(operands)
        elif name == 'CALL':
            self.next_ip = self._exec_call(operands, self.next_ip)
        elif name == 'RET':
            self.next_ip = self._exec_ret()
        elif name == 'JMP':
            self.next_ip = self._exec_jmp(operands, ip)
        elif name.startswith('J'):
            self.next_ip = self._exec_cond_jmp(name, operands, ip, self.next_ip)
        elif name == 'LEA':
            self._exec_lea(operands)
        elif name == 'LEAVE':
            self._exec_leave()
        elif name == 'CDQ':
            rax = self._get_reg(0)
            if rax & 0x80000000:
                self._set_reg(2, 0xFFFFFFFF)
            else:
                self._set_reg(2, 0)
        elif name == 'CQO':
            rax = self._get_reg(0)
            if rax & 0x8000000000000000:
                self._set_reg(2, 0xFFFFFFFFFFFFFFFF)
            else:
                self._set_reg(2, 0)
        elif name == 'TEST':
            self._exec_test(operands)
        elif name == 'CMP':
            self._exec_cmp(operands)
        elif name == 'GRP1':
            self._exec_grp1(operands)
        elif name == 'GRP3':
            self._exec_grp3(operands)
        elif name == 'GRP5':
            self._exec_grp5(operands)
        elif name == 'MOVSXD':
            self._exec_movsxd(operands)
        elif name == 'MOVZBL':
            self._exec_movzbl(operands)
        elif name.startswith('CMOV'):
            self._exec_cmov(name, operands)
        else:
            logger.warning(f"Unimplemented instruction: {name}")
        
        self._set_ip(self.next_ip)
        return None
    
    def _calc_effective_address(self, operand: DecodedOperand) -> int:
        if not isinstance(operand, DecodedOperand):
            return 0
        
        mod, rm, disp = operand.mod, operand.rm, operand.disp
        
        if mod == 3:
            return self._get_reg(rm)
        
        addr = 0
        
        if operand.has_sib:
            sib = operand.sib
            scale = 1 << ((sib >> 6) & 0x3)
            index = (sib >> 3) & 0x7
            base = sib & 0x7
            
            if self.decoder.has_rex:
                if self.decoder.rex & 0x02:
                    index |= 0x8
                if self.decoder.rex & 0x01:
                    base |= 0x8
            
            if index != 4:
                addr += self._get_reg(index) * scale
            
            if base == 5 and mod == 0:
                addr += disp
            else:
                addr += self._get_reg(base) + disp
        else:
            if mod == 0 and rm == 5:
                addr = self.next_ip + disp
            else:
                addr = self._get_reg(rm) + disp
        
        return addr & 0xFFFFFFFFFFFFFFFF
    
    def _exec_push(self, operands: List[Any]) -> None:
        op = operands[0]
        value = self._get_reg(op[1]) if op[0] == 'reg' else op[1] if op[0] in ('imm8', 'immz') else 0
        
        sp = self._get_sp()
        if self.is_64bit:
            sp -= 8
            self.memory.write_qword(sp, value)
        else:
            sp -= 4
            self.memory.write_dword(sp, value)
        self._set_sp(sp)
    
    def _exec_pop(self, operands: List[Any]) -> None:
        op = operands[0]
        if op[0] != 'reg':
            return
        
        sp = self._get_sp()
        value = self.memory.read_qword(sp) if self.is_64bit else self.memory.read_dword(sp)
        sp += 8 if self.is_64bit else 4
        
        self._set_reg(op[1], value)
        self._set_sp(sp)
    
    def _exec_mov(self, operands: List[Any]) -> None:
        dst, src = operands
        value = self._get_operand_value(src)
        self._set_operand_value(dst, value)
    
    def _exec_add(self, operands: List[Any]) -> None:
        dst, src = operands
        dst_val = self._get_operand_value(dst)
        src_val = self._get_operand_value(src)
        result = dst_val + src_val
        self._set_operand_value(dst, result)
        self._update_flags(result, self._get_operand_size(dst))
    
    def _exec_adc(self, operands: List[Any]) -> None:
        dst, src = operands
        dst_val = self._get_operand_value(dst)
        src_val = self._get_operand_value(src)
        cf = 1 if self._get_flags() & (1 << EFlags.CF) else 0
        result = dst_val + src_val + cf
        self._set_operand_value(dst, result)
        self._update_flags(result, self._get_operand_size(dst))
    
    def _exec_sub(self, operands: List[Any]) -> None:
        dst, src = operands
        dst_val = self._get_operand_value(dst)
        src_val = self._get_operand_value(src)
        result = dst_val - src_val
        self._set_operand_value(dst, result)
        self._update_flags(result, self._get_operand_size(dst))
    
    def _exec_xor(self, operands: List[Any]) -> None:
        dst, src = operands
        dst_val = self._get_operand_value(dst)
        src_val = self._get_operand_value(src)
        result = dst_val ^ src_val
        self._set_operand_value(dst, result)
        self._update_flags(result, self._get_operand_size(dst))
    
    def _exec_call(self, operands: List[Any], next_ip: int) -> int:
        op = operands[0]
        
        sp = self._get_sp()
        if self.is_64bit:
            sp -= 8
            self.memory.write_qword(sp, next_ip)
        else:
            sp -= 4
            self.memory.write_dword(sp, next_ip)
        self._set_sp(sp)
        
        if op[0] == 'relz':
            offset = op[1]
            if offset & 0x80000000:
                offset -= 0x100000000
            return next_ip + offset
        return next_ip
    
    def _exec_ret(self) -> int:
        sp = self._get_sp()
        target = self.memory.read_qword(sp) if self.is_64bit else self.memory.read_dword(sp)
        self._set_sp(sp + (8 if self.is_64bit else 4))
        return target
    
    def _exec_jmp(self, operands: List[Any], ip: int) -> int:
        op = operands[0]
        if op[0] == 'rel8':
            return ip + op[1] + 2
        elif op[0] == 'relz':
            offset = op[1]
            if offset & 0x80000000:
                offset -= 0x100000000
            return ip + offset + 5
        return ip + 2
    
    def _exec_cond_jmp(self, name: str, operands: List[Any], ip: int, next_ip: int) -> int:
        flags = self._get_flags()
        
        cond_map = {
            'JZ': lambda f: f & (1 << EFlags.ZF),
            'JNZ': lambda f: not (f & (1 << EFlags.ZF)),
            'JB': lambda f: f & (1 << EFlags.CF),
            'JNB': lambda f: not (f & (1 << EFlags.CF)),
            'JS': lambda f: f & (1 << EFlags.SF),
            'JNS': lambda f: not (f & (1 << EFlags.SF)),
            'JO': lambda f: f & (1 << EFlags.OF),
            'JNO': lambda f: not (f & (1 << EFlags.OF)),
            'JL': lambda f: ((f >> EFlags.SF) & 1) != ((f >> EFlags.OF) & 1),
            'JNL': lambda f: ((f >> EFlags.SF) & 1) == ((f >> EFlags.OF) & 1),
            'JLE': lambda f: (f & (1 << EFlags.ZF)) or (((f >> EFlags.SF) & 1) != ((f >> EFlags.OF) & 1)),
            'JNLE': lambda f: not (f & (1 << EFlags.ZF)) and (((f >> EFlags.SF) & 1) == ((f >> EFlags.OF) & 1)),
        }
        
        check = cond_map.get(name)
        if check and check(flags):
            op = operands[0]
            if op[0] == 'rel8':
                return next_ip + op[1]
            elif op[0] == 'relz':
                offset = op[1]
                if offset & 0x80000000:
                    offset -= 0x100000000
                return next_ip + offset
        
        return next_ip
    
    def _exec_lea(self, operands: List[Any]) -> None:
        dst, src = operands
        if isinstance(src, DecodedOperand):
            addr = self._calc_effective_address(src)
            self._set_reg(dst[1], addr)
    
    def _exec_leave(self) -> None:
        self._set_sp(self._get_bp())
        sp = self._get_sp()
        value = self.memory.read_qword(sp) if self.is_64bit else self.memory.read_dword(sp)
        self._set_bp(value)
        self._set_sp(sp + (8 if self.is_64bit else 4))
    
    def _exec_test(self, operands: List[Any]) -> None:
        op1, op2 = operands
        val1 = self._get_operand_value(op1)
        val2 = self._get_operand_value(op2)
        result = val1 & val2
        self._update_flags(result, self._get_operand_size(op1))
    
    def _exec_cmp(self, operands: List[Any]) -> None:
        op1, op2 = operands
        val1 = self._get_operand_value(op1)
        val2 = self._get_operand_value(op2)
        size = self._get_operand_size(op1)
        mask = (1 << size) - 1
        result = (val1 - val2) & mask
        
        flags = self._get_flags()
        flags &= ~((1 << EFlags.ZF) | (1 << EFlags.SF) | (1 << EFlags.CF) | (1 << EFlags.OF))
        
        if result == 0:
            flags |= (1 << EFlags.ZF)
        if result & (1 << (size - 1)):
            flags |= (1 << EFlags.SF)
        if val1 < val2:
            flags |= (1 << EFlags.CF)
        
        self._set_flags(flags)
    
    def _exec_grp1(self, operands: List[Any]) -> None:
        if len(operands) < 3:
            return
        
        grp_op = operands[0][1] if operands[0][0] == 'grp_op' else 0
        dst = operands[1]
        src = operands[2]
        
        dst_val = self._get_operand_value(dst)
        src_val = src[1] if src[0] == 'imm8' else src[1]
        dst_size = self._get_operand_size(dst)
        
        if src[0] == 'imm8' and (src_val & 0x80):
            if dst_size == 64:
                src_val |= 0xFFFFFFFFFFFFFF00
            elif dst_size == 32:
                src_val |= 0xFFFFFF00
            elif dst_size == 16:
                src_val |= 0xFF00
        
        mask = (1 << dst_size) - 1
        
        if grp_op == 0:
            result = (dst_val + src_val) & mask
        elif grp_op == 1:
            result = (dst_val | src_val) & mask
        elif grp_op == 2:
            cf = 1 if self._get_flags() & (1 << EFlags.CF) else 0
            result = (dst_val + src_val + cf) & mask
        elif grp_op == 3:
            cf = 1 if self._get_flags() & (1 << EFlags.CF) else 0
            result = (dst_val - src_val - cf) & mask
        elif grp_op == 4:
            result = (dst_val & src_val) & mask
        elif grp_op == 5:
            result = (dst_val - src_val) & mask
        elif grp_op == 6:
            result = (dst_val ^ src_val) & mask
        elif grp_op == 7:
            result = (dst_val - src_val) & mask
            self._update_flags(result, dst_size)
            return
        
        self._set_operand_value(dst, result)
        self._update_flags(result, dst_size)
    
    def _exec_grp3(self, operands: List[Any]) -> None:
        if len(operands) < 2:
            return
        op = operands[0]
        grp_op = op[1] if isinstance(op, tuple) and op[0] == 'grp_op' else 0
        dst = operands[1]
        dst_val = self._get_operand_value(dst)
        dst_size = self._get_operand_size(dst)
        mask = (1 << dst_size) - 1
        
        if grp_op == 2:  # NOT
            result = (~dst_val) & mask
            self._set_operand_value(dst, result)
        elif grp_op == 3:  # NEG
            result = (-dst_val) & mask
            self._set_operand_value(dst, result)
            self._update_flags(result, dst_size)
        elif grp_op == 4:  # MUL
            rax = self._get_reg(0)
            result = (rax * dst_val) & mask
            self._set_reg(0, result)
        elif grp_op == 5:  # IMUL
            rax = self._get_reg(0)
            if dst_val & (1 << (dst_size - 1)):
                dst_val = dst_val - (1 << dst_size)
            if rax & (1 << (dst_size - 1)):
                rax = rax - (1 << dst_size)
            result = (rax * dst_val) & mask
            self._set_reg(0, result)
        elif grp_op == 6:  # DIV
            rax = self._get_reg(0)
            rdx = self._get_reg(2)
            if dst_val != 0:
                dividend = (rdx << dst_size) | rax
                quotient = dividend // dst_val
                remainder = dividend % dst_val
                self._set_reg(0, quotient & mask)
                self._set_reg(2, remainder & mask)
        elif grp_op == 7:  # IDIV
            rax = self._get_reg(0)
            rdx = self._get_reg(2)
            sign_bit = 1 << (dst_size - 1)
            sign_ext = 1 << dst_size
            
            if dst_val & sign_bit:
                dst_val = dst_val - sign_ext
            if dst_val != 0:
                dividend = (rdx << dst_size) | rax
                sign_bit2 = 1 << (dst_size * 2 - 1)
                if dividend & sign_bit2:
                    dividend = dividend - (1 << (dst_size * 2))
                
                quotient = int(dividend / dst_val)
                remainder = dividend - quotient * dst_val
                
                self._set_reg(0, quotient & mask)
                self._set_reg(2, remainder & mask)
    
    def _exec_grp5(self, operands: List[Any]) -> None:
        if len(operands) < 2:
            return
        op = operands[0]
        grp_op = op[1] if isinstance(op, tuple) and op[0] == 'grp_op' else 0
        dst = operands[1]
        dst_val = self._get_operand_value(dst)
        
        if grp_op == 0:  # INC
            result = (dst_val + 1) & ((1 << self._get_operand_size(dst)) - 1)
            self._set_operand_value(dst, result)
        elif grp_op == 1:  # DEC
            result = (dst_val - 1) & ((1 << self._get_operand_size(dst)) - 1)
            self._set_operand_value(dst, result)
        elif grp_op == 2:  # CALL Ev
            sp = self._get_sp() - 8
            self.memory.write_qword(sp, self.next_ip)
            self._set_sp(sp)
            self.next_ip = dst_val
        elif grp_op == 4:  # JMP Ev
            self.next_ip = dst_val
        elif grp_op == 6:  # PUSH
            sp = self._get_sp() - 8
            self.memory.write_qword(sp, dst_val)
            self._set_sp(sp)
    
    def _exec_movsxd(self, operands: List[Any]) -> None:
        src, dst = operands
        src_val = self._get_operand_value(src) & 0xFFFFFFFF
        if src_val & 0x80000000:
            result = src_val | 0xFFFFFFFF00000000
        else:
            result = src_val
        self._set_reg(dst[1], result)
    
    def _exec_movzbl(self, operands: List[Any]) -> None:
        src, dst = operands
        src_val = self._get_operand_value(src) & 0xFF
        self._set_reg(dst[1], src_val)
    
    def _exec_cmov(self, name: str, operands: List[Any]) -> None:
        cond = name[4:]
        flags = self._get_flags()
        cf = (flags >> EFlags.CF) & 1
        zf = (flags >> EFlags.ZF) & 1
        sf = (flags >> EFlags.SF) & 1
        of = (flags >> EFlags.OF) & 1
        pf = (flags >> EFlags.PF) & 1
        
        take = False
        if cond == 'O': take = of == 1
        elif cond == 'NO': take = of == 0
        elif cond == 'B': take = cf == 1
        elif cond == 'NB': take = cf == 0
        elif cond == 'Z': take = zf == 1
        elif cond == 'NZ': take = zf == 0
        elif cond == 'BE': take = cf == 1 or zf == 1
        elif cond == 'NBE': take = cf == 0 and zf == 0
        elif cond == 'S': take = sf == 1
        elif cond == 'NS': take = sf == 0
        elif cond == 'P': take = pf == 1
        elif cond == 'NP': take = pf == 0
        elif cond == 'L': take = sf != of
        elif cond == 'NL': take = sf == of
        elif cond == 'LE': take = zf == 1 or sf != of
        elif cond == 'NLE': take = zf == 0 and sf == of
        
        if take and len(operands) >= 2:
            dst, src = operands[0], operands[1]
            src_val = self._get_operand_value(src)
            if isinstance(dst, tuple) and dst[0] == 'Gv':
                self._set_reg(dst[1], src_val)
            elif isinstance(dst, DecodedOperand):
                self._set_operand_value(dst, src_val)
    
    def _get_operand_value(self, operand: Any) -> int:
        if isinstance(operand, tuple):
            if operand[0] == 'reg':
                return self._get_reg(operand[1])
            elif operand[0] in ('imm8', 'immz', 'immv'):
                return operand[1]
            elif operand[0] in ('Gv', 'Gb'):
                return self._get_reg(operand[1])
        elif isinstance(operand, DecodedOperand):
            if operand.mod == 3:
                return self._get_reg(operand.rm)
            else:
                addr = self._calc_effective_address(operand)
                size = self._get_operand_size(operand)
                if size == 8:
                    return self.memory.read_byte(addr)
                elif size == 16:
                    return self.memory.read_word(addr)
                elif size == 32:
                    return self.memory.read_dword(addr)
                else:
                    return self.memory.read_qword(addr)
        return 0
    
    def _set_operand_value(self, operand: Any, value: int) -> None:
        if isinstance(operand, tuple):
            if operand[0] == 'reg':
                self._set_reg(operand[1], value)
            elif operand[0] == 'Gv':
                self._set_reg(operand[1], value)
        elif isinstance(operand, DecodedOperand):
            if operand.mod == 3:
                self._set_reg(operand.rm, value, self._get_operand_size(operand))
            else:
                addr = self._calc_effective_address(operand)
                size = self._get_operand_size(operand)
                if size == 8:
                    self.memory.write_byte(addr, value & 0xFF)
                elif size == 16:
                    self.memory.write_word(addr, value & 0xFFFF)
                elif size == 32:
                    self.memory.write_dword(addr, value & 0xFFFFFFFF)
                else:
                    self.memory.write_qword(addr, value)
    
    def _get_operand_size(self, operand: Any) -> int:
        if isinstance(operand, tuple):
            if len(operand) > 2:
                return operand[2]
            return self.decoder.operand_size
        elif isinstance(operand, DecodedOperand):
            if hasattr(operand, 'size'):
                return operand.size
            if operand.operand_type == 'modrm':
                return self.decoder.operand_size
        return 64
    
    def _get_flags(self) -> int:
        return self.state.regs[Register64.RFLAGS if self.is_64bit else Register32.EFLAGS]
    
    def _set_flags(self, value: int) -> None:
        self.state.regs[Register64.RFLAGS if self.is_64bit else Register32.EFLAGS] = value
    
    def _update_flags(self, result: int, size: int) -> None:
        flags = self._get_flags()
        flags &= ~((1 << EFlags.ZF) | (1 << EFlags.SF) | (1 << EFlags.CF) | (1 << EFlags.OF))
        
        mask = (1 << size) - 1
        if (result & mask) == 0:
            flags |= (1 << EFlags.ZF)
        if result & (1 << (size - 1)):
            flags |= (1 << EFlags.SF)
        
        self._set_flags(flags)
    
    def get_state(self) -> Dict[str, Any]:
        return {
            'instruction_count': self.instruction_count,
            'registers': dict(self.state.regs),
            'is_64bit': self.is_64bit,
        }
