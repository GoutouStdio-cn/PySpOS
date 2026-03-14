#
#   elf_loader/elf_loader.py
#   ELF 加载器, 内存加载和重定位
#
#   By GoutouStdio
#   @ 2022~2026 GoutouStdio. Open all rights.

import struct
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field

from .elf_parser import ELFParser, ProgramHeader, SectionHeader, ELFSymbol
from .elf_constants import (
    ProgramHeaderType, SectionHeaderType,
    DynamicTag, SymbolBinding, SymbolType,
    RelocationTypeX86_64, RelocationTypeI386,
    SpecialSectionIndex
)


@dataclass
class MemoryRegion:
    """内存区域"""
    start: int              # 起始地址
    size: int               # 大小
    data: bytearray         # 数据
    flags: int = 0          # 保护标志 (读/写/执行)
    name: str = ""          # 区域名称
    
    @property
    def end(self) -> int:
        return self.start + self.size
    
    @property
    def readable(self) -> bool:
        """是否可读"""
        return (self.flags & 0x4) != 0  # PF_R = 0x4
    
    @property
    def writable(self) -> bool:
        """是否可写"""
        return (self.flags & 0x2) != 0  # PF_W = 0x2
    
    @property
    def executable(self) -> bool:
        """是否可执行"""
        return (self.flags & 0x1) != 0  # PF_X = 0x1
    
    def contains(self, addr: int) -> bool:
        return self.start <= addr < self.end
    
    def read(self, addr: int, size: int) -> bytes:
        """从内存读取数据"""
        offset = addr - self.start
        if offset < 0 or offset + size > self.size:
            raise MemoryError(f"内存读取越界: addr=0x{addr:x}, size={size}")
        return bytes(self.data[offset:offset + size])
    
    def write(self, addr: int, data: bytes):
        """向内存写入数据"""
        offset = addr - self.start
        if offset < 0 or offset + len(data) > self.size:
            raise MemoryError(f"内存写入越界: addr=0x{addr:x}, size={len(data)}")
        self.data[offset:offset + len(data)] = data
    
    def read_int(self, addr: int, size: int, signed: bool = False) -> int:
        """读取整数"""
        data = self.read(addr, size)
        fmt = {1: 'B', 2: 'H', 4: 'I', 8: 'Q'}.get(size, 'I')
        if signed:
            fmt = fmt.lower()
        return struct.unpack('<' + fmt, data)[0]
    
    def write_int(self, addr: int, value: int, size: int):
        """写入整数"""
        fmt = {1: 'B', 2: 'H', 4: 'I', 8: 'Q'}.get(size, 'I')
        data = struct.pack('<' + fmt, value & ((1 << (size * 8)) - 1))
        self.write(addr, data)


@dataclass
class LoadedSegment:
    """已加载的段"""
    ph: ProgramHeader       # 原始程序头
    vaddr: int              # 虚拟地址
    memsz: int              # 内存大小
    filesz: int             # 文件大小
    data: bytearray         # 数据


class ELFLoader:
    """ELF 加载器"""
    
    # 默认内存布局
    DEFAULT_BASE_ADDR = 0x400000
    STACK_SIZE = 8 * 1024 * 1024  # 8MB 栈
    STACK_TOP = 0x7fff0000
    HEAP_START = 0x80000000
    
    def __init__(self, parser: ELFParser, base_addr: Optional[int] = None):
        """
        初始化 ELF 加载器
        
        Args:
            parser: 已解析的 ELF 文件
            base_addr: 加载基址（为 None 时使用文件指定的地址）
        """
        self.parser = parser
        self.base_addr = base_addr or self.DEFAULT_BASE_ADDR
        
        # 内存区域
        self.memory: Dict[int, MemoryRegion] = {}  # 起始地址 -> 区域
        self.segments: List[LoadedSegment] = []
        
        # 加载信息
        self.entry_point: int = 0
        self.brk: int = 0           # 程序中断（堆结束）
        self.heap_start: int = 0
        self.stack_top: int = self.STACK_TOP - 16  # 栈顶地址
        
        # 符号解析
        self.symbols: Dict[str, int] = {}  # 符号名 -> 地址
        self.plt_entries: Dict[str, int] = {}  # PLT 条目
        self.got_entries: Dict[int, int] = {}  # GOT 条目地址 -> 目标地址
        
        # 重定位信息
        self.relocations_done = False
        
        # 动态链接信息
        self.dynamic_info: Dict[int, int] = {}  # 标签 -> 值
        self.needed_libs: List[str] = []
    
    def load(self) -> 'ELFLoader':
        """
        加载 ELF 文件到内存
        
        Returns:
            self 用于链式调用
        """
        # 计算加载偏移
        if self.parser.header.e_type == 2:  # ET_EXEC
            # 可执行文件使用固定地址
            load_offset = 0
        else:
            # 共享库使用基址
            load_offset = self.base_addr
        
        # 加载所有可加载段
        for ph in self.parser.program_headers:
            if ph.p_type == ProgramHeaderType.PT_LOAD:
                self._load_segment(ph, load_offset)
        
        # 设置入口点
        self.entry_point = self.parser.header.e_entry + load_offset
        
        # 解析动态链接信息
        self._parse_dynamic(load_offset)
        
        # 执行重定位
        self._perform_relocations(load_offset)
        
        # 设置堆起始
        self._setup_heap()
        
        # 创建栈
        self._create_stack()
        
        return self
    
    def _load_segment(self, ph: ProgramHeader, load_offset: int):
        """加载单个段"""
        vaddr = ph.p_vaddr + load_offset
        memsz = ph.p_memsz
        filesz = ph.p_filesz
        
        # 创建数据缓冲区
        data = bytearray(memsz)
        
        # 从文件复制数据
        if filesz > 0:
            file_data = self.parser.data[ph.p_offset:ph.p_offset + filesz]
            data[:filesz] = file_data
        
        # 清零 BSS 部分
        if memsz > filesz:
            data[filesz:] = b'\x00' * (memsz - filesz)
        
        # 创建内存区域
        region = MemoryRegion(
            start=vaddr,
            size=memsz,
            data=data,
            flags=ph.p_flags,
            name=f"segment_0x{vaddr:x}"
        )
        
        self.memory[vaddr] = region
        self.segments.append(LoadedSegment(
            ph=ph,
            vaddr=vaddr,
            memsz=memsz,
            filesz=filesz,
            data=data
        ))
    
    def _parse_dynamic(self, load_offset: int):
        """解析动态链接信息"""
        for dyn in self.parser.dynamics:
            tag = dyn.d_tag
            val = dyn.d_val
            
            # 调整地址值
            if dyn.is_pointer and val != 0:
                val += load_offset
            
            self.dynamic_info[tag] = val
        
        # 获取所需库
        self.needed_libs = self.parser.get_needed_libraries()
        
        # 解析符号表
        self._parse_symbols(load_offset)
    
    def _parse_symbols(self, load_offset: int):
        """解析符号表"""
        symtab_addr = self.dynamic_info.get(DynamicTag.DT_SYMTAB, 0)
        strtab_addr = self.dynamic_info.get(DynamicTag.DT_STRTAB, 0)
        
        if symtab_addr == 0 or strtab_addr == 0:
            # 使用节区表中的符号
            for sym in self.parser.symbols:
                if sym.name and sym.st_value != 0:
                    self.symbols[sym.name] = sym.st_value + load_offset
            for sym in self.parser.dynamic_symbols:
                if sym.name and sym.st_value != 0:
                    self.symbols[sym.name] = sym.st_value + load_offset
            return
        
        # 从动态段解析符号
        sym_ent_size = self.dynamic_info.get(DynamicTag.DT_SYMENT, 
                                              16 if self.parser.is_32bit else 24)
        
        # 计算符号数量（通过哈希表或字符串表大小估算）
        strtab_size = self.dynamic_info.get(DynamicTag.DT_STRSZ, 0)
        
        # 读取字符串表
        strtab_data = self._read_memory(strtab_addr, strtab_size)
        
        # 解析符号
        sym_idx = 0
        while True:
            sym_addr = symtab_addr + sym_idx * sym_ent_size
            
            # 读取符号条目
            try:
                if self.parser.is_32bit:
                    name_offset = self._read_memory_int(sym_addr, 4)
                    value = self._read_memory_int(sym_addr + 4, 4)
                    size = self._read_memory_int(sym_addr + 8, 4)
                    info = self._read_memory_int(sym_addr + 12, 1)
                    other = self._read_memory_int(sym_addr + 13, 1)
                    shndx = self._read_memory_int(sym_addr + 14, 2)
                else:
                    name_offset = self._read_memory_int(sym_addr, 4)
                    info = self._read_memory_int(sym_addr + 4, 1)
                    other = self._read_memory_int(sym_addr + 5, 1)
                    shndx = self._read_memory_int(sym_addr + 6, 2)
                    value = self._read_memory_int(sym_addr + 8, 8)
                    size = self._read_memory_int(sym_addr + 16, 8)
            except MemoryError:
                break
            
            if name_offset == 0 and value == 0:
                sym_idx += 1
                if sym_idx > 10000:  # 防止无限循环
                    break
                continue
            
            # 获取符号名
            name = self._get_string_from_data(strtab_data, name_offset)
            
            if name and value != 0:
                # 调整地址
                if shndx != SpecialSectionIndex.SHN_ABS:
                    value += load_offset
                self.symbols[name] = value
            
            sym_idx += 1
            
            if sym_idx > 10000:  # 防止无限循环
                break
    
    def _perform_relocations(self, load_offset: int):
        """执行重定位"""
        if self.relocations_done:
            return
        
        # 获取重定位信息
        rela_addr = self.dynamic_info.get(DynamicTag.DT_RELA, 0)
        rela_size = self.dynamic_info.get(DynamicTag.DT_RELASZ, 0)
        rela_ent = self.dynamic_info.get(DynamicTag.DT_RELAENT, 
                                         12 if self.parser.is_32bit else 24)
        
        rel_addr = self.dynamic_info.get(DynamicTag.DT_REL, 0)
        rel_size = self.dynamic_info.get(DynamicTag.DT_RELSZ, 0)
        rel_ent = self.dynamic_info.get(DynamicTag.DT_RELENT,
                                        8 if self.parser.is_32bit else 16)
        
        plt_rel_addr = self.dynamic_info.get(DynamicTag.DT_JMPREL, 0)
        plt_rel_size = self.dynamic_info.get(DynamicTag.DT_PLTRELSZ, 0)
        plt_rel_type = self.dynamic_info.get(DynamicTag.DT_PLTREL, 0)
        
        # 执行 RELA 重定位
        if rela_addr and rela_size:
            self._do_rela_relocations(rela_addr, rela_size, rela_ent, load_offset)
        
        # 执行 REL 重定位
        if rel_addr and rel_size:
            self._do_rel_relocations(rel_addr, rel_size, rel_ent, load_offset)
        
        # 执行 PLT 重定位
        if plt_rel_addr and plt_rel_size:
            if plt_rel_type == DynamicTag.DT_RELA:
                self._do_rela_relocations(plt_rel_addr, plt_rel_size, rela_ent, load_offset)
            else:
                self._do_rel_relocations(plt_rel_addr, plt_rel_size, rel_ent, load_offset)
        
        # 处理从节区解析的重定位
        for rel in self.parser.relocations:
            self._apply_relocation(rel, load_offset)
        
        self.relocations_done = True
    
    def _do_rela_relocations(self, addr: int, size: int, ent_size: int, load_offset: int):
        """执行 RELA 重定位"""
        num_entries = size // ent_size
        
        for i in range(num_entries):
            entry_addr = addr + i * ent_size

            if self.parser.is_32bit:
                r_offset = self._read_memory_int(entry_addr, 4)
                r_info = self._read_memory_int(entry_addr + 4, 4)
                r_addend = self._read_memory_int(entry_addr + 8, 4, signed=True)
            else:
                r_offset = self._read_memory_int(entry_addr, 8)
                r_info = self._read_memory_int(entry_addr + 8, 8)
                r_addend = self._read_memory_int(entry_addr + 16, 8, signed=True)
            
            from .elf_parser import ELFRelocationA
            rel = ELFRelocationA(
                r_offset=r_offset + load_offset,
                r_info=r_info,
                r_addend=r_addend
            )
            self._apply_relocation(rel, load_offset)
    
    def _do_rel_relocations(self, addr: int, size: int, ent_size: int, load_offset: int):
        """执行 REL 重定位"""
        num_entries = size // ent_size
        
        for i in range(num_entries):
            entry_addr = addr + i * ent_size
            
            if self.parser.is_32bit:
                r_offset = self._read_memory_int(entry_addr, 4)
                r_info = self._read_memory_int(entry_addr + 4, 4)
            else:
                r_offset = self._read_memory_int(entry_addr, 8)
                r_info = self._read_memory_int(entry_addr + 8, 8)
            
            from .elf_parser import ELFRelocation
            rel = ELFRelocation(
                r_offset=r_offset + load_offset,
                r_info=r_info
            )
            self._apply_relocation(rel, load_offset)
    
    def _apply_relocation(self, rel, load_offset: int):
        """应用单个重定位"""
        addr = rel.r_offset
        sym_idx = rel.sym
        rel_type = rel.type
        
        # 获取加数
        addend = getattr(rel, 'r_addend', 0)
        
        # 获取符号值
        sym_value = 0
        if sym_idx > 0:
            # 从动态符号表获取
            if sym_idx < len(self.parser.dynamic_symbols):
                sym = self.parser.dynamic_symbols[sym_idx]
                if not sym.is_undefined:
                    sym_value = sym.st_value + load_offset
                # 未定义符号将在运行时解析
        
        # 根据重定位类型计算新值
        if self.parser.is_32bit:
            new_value = self._calc_relocation_32(rel_type, addr, sym_value, addend, load_offset)
            size = 4
        else:
            new_value = self._calc_relocation_64(rel_type, addr, sym_value, addend, load_offset)
            size = 8 if rel_type not in (RelocationTypeX86_64.R_X86_64_32,
                                          RelocationTypeX86_64.R_X86_64_32S) else 4
        
        # 写入新值
        if new_value is not None:
            try:
                self._write_memory_int(addr, new_value, size)
            except MemoryError:
                pass  # 忽略越界写入
    
    def _calc_relocation_64(self, rel_type: int, addr: int, sym_value: int, 
                            addend: int, load_offset: int) -> Optional[int]:
        """计算 64 位重定位值"""
        if rel_type == RelocationTypeX86_64.R_X86_64_NONE:
            return None
        
        elif rel_type == RelocationTypeX86_64.R_X86_64_64:
            return sym_value + addend
        
        elif rel_type == RelocationTypeX86_64.R_X86_64_PC32:
            return (sym_value + addend - addr) & 0xffffffff
        
        elif rel_type == RelocationTypeX86_64.R_X86_64_32:
            return (sym_value + addend) & 0xffffffff
        
        elif rel_type == RelocationTypeX86_64.R_X86_64_32S:
            value = sym_value + addend
            # 符号扩展检查
            if value & 0x80000000:
                value |= ~0xffffffff
            return value & 0xffffffff
        
        elif rel_type == RelocationTypeX86_64.R_X86_64_GLOB_DAT:
            return sym_value + addend
        
        elif rel_type == RelocationTypeX86_64.R_X86_64_JUMP_SLOT:
            return sym_value
        
        elif rel_type == RelocationTypeX86_64.R_X86_64_RELATIVE:
            return load_offset + addend
        
        elif rel_type == RelocationTypeX86_64.R_X86_64_COPY:
            # 复制重定位 - 需要复制符号数据
            # 这里简化处理，返回符号地址
            return sym_value
        
        elif rel_type == RelocationTypeX86_64.R_X86_64_16:
            return (sym_value + addend) & 0xffff
        
        elif rel_type == RelocationTypeX86_64.R_X86_64_PC16:
            return (sym_value + addend - addr) & 0xffff
        
        elif rel_type == RelocationTypeX86_64.R_X86_64_8:
            return (sym_value + addend) & 0xff
        
        elif rel_type == RelocationTypeX86_64.R_X86_64_PC8:
            return (sym_value + addend - addr) & 0xff
        
        # 其他类型暂不处理
        return None
    
    def _calc_relocation_32(self, rel_type: int, addr: int, sym_value: int,
                            addend: int, load_offset: int) -> Optional[int]:
        """计算 32 位重定位值"""
        if rel_type == RelocationTypeI386.R_386_NONE:
            return None
        
        elif rel_type == RelocationTypeI386.R_386_32:
            return (sym_value + addend) & 0xffffffff
        
        elif rel_type == RelocationTypeI386.R_386_PC32:
            return (sym_value + addend - addr) & 0xffffffff
        
        elif rel_type == RelocationTypeI386.R_386_GLOB_DAT:
            return sym_value
        
        elif rel_type == RelocationTypeI386.R_386_JUMP_SLOT:
            return sym_value
        
        elif rel_type == RelocationTypeI386.R_386_RELATIVE:
            return load_offset + addend
        
        elif rel_type == RelocationTypeI386.R_386_COPY:
            return sym_value
        
        elif rel_type == RelocationTypeI386.R_386_16:
            return (sym_value + addend) & 0xffff
        
        elif rel_type == RelocationTypeI386.R_386_PC16:
            return (sym_value + addend - addr) & 0xffff
        
        elif rel_type == RelocationTypeI386.R_386_8:
            return (sym_value + addend) & 0xff
        
        elif rel_type == RelocationTypeI386.R_386_PC8:
            return (sym_value + addend - addr) & 0xff
        
        return None
    
    def _setup_heap(self):
        """设置堆"""
        # 找到最高的已加载段
        max_addr = 0
        for seg in self.segments:
            end = seg.vaddr + seg.memsz
            if end > max_addr:
                max_addr = end
        
        page_size = 0x1000
        self.heap_start = (max_addr + page_size - 1) // page_size * page_size
        self.brk = self.heap_start
        
        heap_region = MemoryRegion(
            start=self.heap_start,
            size=page_size,
            data=bytearray(page_size),
            flags=0x6,
            name="heap"
        )
        self.memory[self.heap_start] = heap_region
    
    def _create_stack(self):
        """创建栈"""
        stack_bottom = self.STACK_TOP - self.STACK_SIZE
        
        region = MemoryRegion(
            start=stack_bottom,
            size=self.STACK_SIZE + 0x10000,
            data=bytearray(self.STACK_SIZE + 0x10000),
            flags=0x6,
            name="stack"
        )
        
        self.memory[stack_bottom] = region
        self.stack_top = self.STACK_TOP + 0x8000
    
    def _read_memory(self, addr: int, size: int) -> bytes:
        """从内存读取"""
        for region in self.memory.values():
            if region.contains(addr):
                return region.read(addr, size)
        raise MemoryError(f"无法读取内存: addr=0x{addr:x}")
    
    def _read_memory_int(self, addr: int, size: int, signed: bool = False) -> int:
        """从内存读取整数"""
        for region in self.memory.values():
            if region.contains(addr):
                return region.read_int(addr, size, signed)
        raise MemoryError(f"无法读取内存: addr=0x{addr:x}")
    
    def _write_memory_int(self, addr: int, value: int, size: int):
        """向内存写入整数"""
        for region in self.memory.values():
            if region.contains(addr):
                region.write_int(addr, value, size)
                return
        raise MemoryError(f"无法写入内存: addr=0x{addr:x}")
    
    def _get_string_from_data(self, data: bytes, offset: int) -> str:
        """从数据中获取字符串"""
        if offset >= len(data):
            return ""
        end = data.find(b'\x00', offset)
        if end == -1:
            end = len(data)
        return data[offset:end].decode('utf-8', errors='replace')
    
    def read_memory(self, addr: int, size: int) -> bytes:
        """从内存读取（公共接口）"""
        return self._read_memory(addr, size)
    
    def write_memory(self, addr: int, data: bytes):
        """向内存写入（公共接口）"""
        for region in self.memory.values():
            if region.contains(addr):
                region.write(addr, data)
                return
        raise MemoryError(f"无法写入内存: addr=0x{addr:x}")
    
    def read_int(self, addr: int, size: int, signed: bool = False) -> int:
        """读取整数（公共接口）"""
        return self._read_memory_int(addr, size, signed)
    
    def write_int(self, addr: int, value: int, size: int):
        """写入整数（公共接口）"""
        self._write_memory_int(addr, value, size)
    
    def get_stack_top(self) -> int:
        """获取栈顶地址"""
        return self.stack_top
    
    def get_entry_point(self) -> int:
        """获取入口点地址"""
        return self.entry_point
    
    def brk_extend(self, new_brk: int) -> int:
        """扩展堆"""
        new_brk = new_brk & 0xFFFFFFFFFFFFFFFF
        if new_brk < self.heap_start:
            return self.brk
        
        if new_brk <= self.brk:
            return self.brk
        
        page_size = 0x1000
        new_end = (new_brk + page_size - 1) // page_size * page_size
        
        heap_region_key = None
        heap_region = None
        for key, region in self.memory.items():
            if region.name == "heap":
                heap_region_key = key
                heap_region = region
                break
        
        if heap_region is None:
            region = MemoryRegion(
                start=self.heap_start,
                size=new_end - self.heap_start,
                data=bytearray(new_end - self.heap_start),
                flags=0x6,
                name="heap"
            )
            self.memory[self.heap_start] = region
        else:
            if new_end > heap_region.end:
                old_data = heap_region.data
                new_size = new_end - heap_region.start
                new_data = bytearray(new_size)
                new_data[:len(old_data)] = old_data
                heap_region.data = new_data
                heap_region.size = new_size
        
        self.brk = new_brk
        return self.brk
    
    def resolve_symbol(self, name: str) -> Optional[int]:
        """解析符号地址"""
        return self.symbols.get(name)
    
    def get_memory_map(self) -> List[Tuple[int, int, str]]:
        """获取内存映射"""
        result = []
        for start, region in sorted(self.memory.items()):
            result.append((start, region.end, region.name))
        return result
