#
#   elf_loader/__init__.py
#   PySpOS ELF 加载器与模拟器 init 模块
#
#   By GoutouStdio
#   @ 2022~2026 GoutouStdio. Open all rights.

# ELF on Windows Space 兼容层版本信息
__version__ = "1.0.0"
__develop_stage__ = "beta"
__cpu_emulator_name__ = "SpaceCPU 1 Pro"
__supported_archs__ = ["x86", "x86_64"]
__syscall_abi__ = "SpaceOS ABI 兼容"

from .elf_constants import (
    ELFClass, ELFData, ELFOSABI, ELFType,
    ELFMachine, SectionHeaderType, SectionHeaderFlags, ProgramHeaderType,
    ProgramHeaderFlags, SymbolBinding, SymbolType, DynamicTag,
    RelocationTypeX86_64, RelocationTypeI386
)
from .elf_parser import ELFParser, ELFHeader, ProgramHeader, SectionHeader
from .elf_parser import ELFSymbol, ELFDynamic, ELFRelocation, ELFRelocationA
from .elf_loader import ELFLoader, MemoryRegion, LoadedSegment
from .syscall_emulator import SyscallEmulator
from .cpu_emulator import CPUEmulator, CPUState, Register32, Register64
from .elf_runner import ELFRunner, ELFDebugger, ExecutionResult, run_elf

__all__ = [
    # 版本信息
    '__version__',
    '__develop_stage__',
    '__cpu_emulator_name__',
    '__supported_archs__',
    '__syscall_abi__',
    # 常量
    'ELFClass', 'ELFData', 'ELFOSABI',
    'ELFType', 'ELFMachine', 'SectionHeaderType', 'SectionHeaderFlags',
    'ProgramHeaderType', 'ProgramHeaderFlags', 'SymbolBinding',
    'SymbolType', 'DynamicTag', 'RelocationTypeX86_64', 'RelocationTypeI386',
    # ELF 解析
    'ELFParser',
    'ELFHeader',
    'ProgramHeader',
    'SectionHeader',
    'ELFSymbol',
    'ELFDynamic',
    'ELFRelocation',
    'ELFRelocationA',
    # ELF 加载
    'ELFLoader',
    'MemoryRegion',
    'LoadedSegment',
    # 系统调用模拟
    'SyscallEmulator',
    # CPU 模拟
    'CPUEmulator', # CPU模拟器（SpaceCPU 1 Pro）
    'CPUState',    # CPU状态寄存器
    'Register32',  # 32位寄存器
    'Register64',  # 64位寄存器
    # 程序执行
    'ELFRunner',
    'ELFDebugger',
    'ExecutionResult',
    'run_elf',
]
