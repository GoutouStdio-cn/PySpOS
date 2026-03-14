#
#   elf_loader/elf_parser.py
#   ELF 文件解析器
#
#   By GoutouStdio
#   @ 2022~2026 GoutouStdio. Open all rights.


import struct
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple, BinaryIO, Union
from io import BytesIO

from .elf_constants import (
    ELFMAG, SELFMAG,
    ELFClass, ELFData, ELFOSABI, ELFType, ELFMachine,
    ProgramHeaderType, ProgramHeaderFlags,
    SectionHeaderType, SectionHeaderFlags,
    DynamicTag, SymbolBinding, SymbolType,
    RelocationTypeX86_64, RelocationTypeI386,
    SpecialSectionIndex,
    PT_GNU_STACK, PT_GNU_RELRO, PT_GNU_PROPERTY,
    SHT_GNU_HASH, SHT_GNU_ATTRIBUTES, SHT_GNU_LIBLIST,
    SHT_CHECKSUM, SHT_GNU_VERDEF, SHT_GNU_VERNEED, SHT_GNU_VERSYM,
    DT_GNU_HASH, DT_VERSYM, DT_VERDEF, DT_VERNEED
)


@dataclass
class ELFIdent:
    """ELF 标识结构"""
    ei_mag: bytes           # 魔数
    ei_class: int           # 文件类别 (32/64 位)
    ei_data: int            # 数据编码
    ei_version: int         # ELF 版本
    ei_osabi: int           # 操作系统/ABI
    ei_abiversion: int      # ABI 版本
    ei_pad: bytes           # 填充
    
    @property
    def is_32bit(self) -> bool:
        return self.ei_class == ELFClass.ELFCLASS32
    
    @property
    def is_64bit(self) -> bool:
        return self.ei_class == ELFClass.ELFCLASS64
    
    @property
    def is_little_endian(self) -> bool:
        return self.ei_data == ELFData.ELFDATA2LSB
    
    @property
    def is_big_endian(self) -> bool:
        return self.ei_data == ELFData.ELFDATA2MSB


@dataclass
class ELFHeader:
    """ELF 文件头"""
    e_ident: ELFIdent       # ELF 标识
    e_type: int             # 文件类型
    e_machine: int          # 目标架构
    e_version: int          # 文件版本
    e_entry: int            # 入口点地址
    e_phoff: int            # 程序头表偏移
    e_shoff: int            # 节区头表偏移
    e_flags: int            # 处理器特定标志
    e_ehsize: int           # ELF 头大小
    e_phentsize: int        # 程序头表条目大小
    e_phnum: int            # 程序头表条目数量
    e_shentsize: int        # 节区头表条目大小
    e_shnum: int            # 节区头表条目数量
    e_shstrndx: int         # 节区名称字符串表索引


@dataclass
class ProgramHeader:
    """程序头（段描述）"""
    p_type: int             # 段类型
    p_flags: int            # 段标志 (64 位)
    p_offset: int           # 文件偏移
    p_vaddr: int            # 虚拟地址
    p_paddr: int            # 物理地址
    p_filesz: int           # 文件大小
    p_memsz: int            # 内存大小
    p_align: int            # 对齐
    
    # 32 位特有的字段位置不同
    p_flags_32: int = 0     # 32 位段标志
    
    @property
    def is_loadable(self) -> bool:
        return self.p_type == ProgramHeaderType.PT_LOAD
    
    @property
    def is_interpreter(self) -> bool:
        return self.p_type == ProgramHeaderType.PT_INTERP
    
    @property
    def is_dynamic(self) -> bool:
        return self.p_type == ProgramHeaderType.PT_DYNAMIC
    
    @property
    def is_stack(self) -> bool:
        return self.p_type == PT_GNU_STACK
    
    @property
    def is_readable(self) -> bool:
        flags = self.p_flags if self.p_flags else self.p_flags_32
        return bool(flags & ProgramHeaderFlags.PF_R)
    
    @property
    def is_writable(self) -> bool:
        flags = self.p_flags if self.p_flags else self.p_flags_32
        return bool(flags & ProgramHeaderFlags.PF_W)
    
    @property
    def is_executable(self) -> bool:
        flags = self.p_flags if self.p_flags else self.p_flags_32
        return bool(flags & ProgramHeaderFlags.PF_X)


@dataclass
class SectionHeader:
    """节区头"""
    sh_name: int            # 节区名称字符串表偏移
    sh_type: int            # 节区类型
    sh_flags: int           # 节区标志
    sh_addr: int            # 虚拟地址
    sh_offset: int          # 文件偏移
    sh_size: int            # 节区大小
    sh_link: int            # 链接的节区索引
    sh_info: int            # 附加信息
    sh_addralign: int       # 地址对齐
    sh_entsize: int         # 条目大小
    
    # 运行时填充
    name: str = ""          # 节区名称
    
    @property
    def is_allocatable(self) -> bool:
        return bool(self.sh_flags & SectionHeaderFlags.SHF_ALLOC)
    
    @property
    def is_writable(self) -> bool:
        return bool(self.sh_flags & SectionHeaderFlags.SHF_WRITE)
    
    @property
    def is_executable(self) -> bool:
        return bool(self.sh_flags & SectionHeaderFlags.SHF_EXECINSTR)
    
    @property
    def is_nobits(self) -> bool:
        return self.sh_type == SectionHeaderType.SHT_NOBITS


@dataclass
class ELFSymbol:
    """ELF 符号表条目"""
    st_name: int            # 符号名称字符串表偏移
    st_info: int            # 符号类型和绑定信息
    st_other: int           # 可见性
    st_shndx: int           # 相关节区索引
    st_value: int           # 符号值/地址
    st_size: int            # 符号大小
    
    # 运行时填充
    name: str = ""          # 符号名称
    
    @property
    def bind(self) -> int:
        return self.st_info >> 4
    
    @property
    def type(self) -> int:
        return self.st_info & 0xf
    
    @property
    def visibility(self) -> int:
        return self.st_other & 0x3
    
    @property
    def is_local(self) -> bool:
        return self.bind == SymbolBinding.STB_LOCAL
    
    @property
    def is_global(self) -> bool:
        return self.bind == SymbolBinding.STB_GLOBAL
    
    @property
    def is_weak(self) -> bool:
        return self.bind == SymbolBinding.STB_WEAK
    
    @property
    def is_function(self) -> bool:
        return self.type == SymbolType.STT_FUNC
    
    @property
    def is_object(self) -> bool:
        return self.type == SymbolType.STT_OBJECT
    
    @property
    def is_undefined(self) -> bool:
        return self.st_shndx == SpecialSectionIndex.SHN_UNDEF


@dataclass
class ELFRelocation:
    """ELF 重定位条目 (Rel)"""
    r_offset: int           # 重定位偏移/地址
    r_info: int             # 符号索引和重定位类型
    
    @property
    def sym(self) -> int:
        return self.r_info >> 32
    
    @property
    def type(self) -> int:
        return self.r_info & 0xffffffff


@dataclass
class ELFRelocationA:
    """ELF 重定位条目 (Rela - 带加数)"""
    r_offset: int           # 重定位偏移/地址
    r_info: int             # 符号索引和重定位类型
    r_addend: int           # 加数
    
    @property
    def sym(self) -> int:
        return self.r_info >> 32
    
    @property
    def type(self) -> int:
        return self.r_info & 0xffffffff


@dataclass
class ELFDynamic:
    """ELF 动态链接条目"""
    d_tag: int              # 标签类型
    d_val: int              # 整数值/地址
    
    @property
    def is_pointer(self) -> bool:
        """判断是否为指针类型的标签"""
        pointer_tags = {
            DynamicTag.DT_PLTGOT, DynamicTag.DT_HASH, DynamicTag.DT_STRTAB,
            DynamicTag.DT_SYMTAB, DynamicTag.DT_RELA, DynamicTag.DT_INIT,
            DynamicTag.DT_FINI, DynamicTag.DT_REL, DynamicTag.DT_DEBUG,
            DynamicTag.DT_JMPREL, DynamicTag.DT_INIT_ARRAY, DynamicTag.DT_FINI_ARRAY,
            DynamicTag.DT_PREINIT_ARRAY, DynamicTag.DT_GNU_HASH,
            DynamicTag.DT_TLSDESC_PLT, DynamicTag.DT_TLSDESC_GOT,
            DynamicTag.DT_GNU_CONFLICT, DynamicTag.DT_GNU_LIBLIST,
            DynamicTag.DT_CONFIG, DynamicTag.DT_DEPAUDIT, DynamicTag.DT_AUDIT,
            DynamicTag.DT_PLTPAD, DynamicTag.DT_MOVETAB, DynamicTag.DT_SYMINFO,
            DynamicTag.DT_VERDEF, DynamicTag.DT_VERNEED,
        }
        return self.d_tag in pointer_tags


class ELFParser:
    """ELF 文件解析器"""
    
    def __init__(self, data: bytes):
        """
        初始化 ELF 解析器
        
        Args:
            data: ELF 文件内容
        """
        self.data = data
        self.stream = BytesIO(data)
        
        # 解析结果
        self.header: Optional[ELFHeader] = None
        self.program_headers: List[ProgramHeader] = []
        self.section_headers: List[SectionHeader] = []
        self.symbols: List[ELFSymbol] = []
        self.dynamic_symbols: List[ELFSymbol] = []
        self.dynamics: List[ELFDynamic] = []
        self.relocations: List[Union[ELFRelocation, ELFRelocationA]] = []
        
        # 字符串表
        self.shstrtab: bytes = b""
        self.strtab: bytes = b""
        self.dynstr: bytes = b""
        
        # 节区名称映射
        self.section_by_name: Dict[str, SectionHeader] = {}
        
        # 架构信息
        self.is_32bit = False
        self.is_little_endian = True
        
        # 格式字符串
        self._fmt_half = "<H"  # 16 位
        self._fmt_word = "<I"  # 32 位
        self._fmt_addr = "<I"  # 地址
        self._fmt_off = "<I"   # 偏移
        self._fmt_xword = "<Q" # 64 位
        self._fmt_sword = "<i" # 有符号 32 位
    
    def _set_endian(self, little_endian: bool):
        """设置字节序"""
        prefix = "<" if little_endian else ">"
        self._fmt_half = prefix + "H"
        self._fmt_word = prefix + "I"
        self._fmt_addr = prefix + "I"
        self._fmt_off = prefix + "I"
        self._fmt_xword = prefix + "Q"
        self._fmt_sword = prefix + "i"
    
    def _read(self, size: int) -> bytes:
        """从流中读取数据"""
        return self.stream.read(size)
    
    def _seek(self, offset: int):
        """设置流位置"""
        self.stream.seek(offset)
    
    def _read_half(self) -> int:
        """读取 16 位无符号整数"""
        return struct.unpack(self._fmt_half, self._read(2))[0]
    
    def _read_word(self) -> int:
        """读取 32 位无符号整数"""
        return struct.unpack(self._fmt_word, self._read(4))[0]
    
    def _read_sword(self) -> int:
        """读取 32 位有符号整数"""
        return struct.unpack(self._fmt_sword, self._read(4))[0]
    
    def _read_addr(self) -> int:
        """读取地址（32 位）"""
        return struct.unpack(self._fmt_addr, self._read(4))[0]
    
    def _read_addr64(self) -> int:
        """读取地址（64 位）"""
        return struct.unpack(self._fmt_xword, self._read(8))[0]
    
    def _read_off(self) -> int:
        """读取偏移（32 位）"""
        return struct.unpack(self._fmt_off, self._read(4))[0]
    
    def _read_off64(self) -> int:
        """读取偏移（64 位）"""
        return struct.unpack(self._fmt_xword, self._read(8))[0]
    
    def _read_xword(self) -> int:
        """读取 64 位无符号整数"""
        return struct.unpack(self._fmt_xword, self._read(8))[0]
    
    def _read_sxword(self) -> int:
        """读取 64 位有符号整数"""
        fmt = "<q" if self._fmt_xword.startswith("<") else ">q"
        return struct.unpack(fmt, self._read(8))[0]
    
    def parse(self) -> 'ELFParser':
        """
        解析 ELF 文件
        
        Returns:
            self 用于链式调用
        """
        self._parse_ident()
        self._parse_header()
        self._parse_program_headers()
        self._parse_section_headers()
        self._parse_string_tables()
        self._resolve_section_names()
        self._parse_symbols()
        self._parse_dynamic()
        self._parse_relocations()
        return self
    
    def _parse_ident(self):
        """解析 ELF 标识"""
        self._seek(0)
        
        # 魔数
        ei_mag = self._read(SELFMAG)
        if ei_mag != ELFMAG:
            raise ValueError(f"无效的 ELF 魔数: {ei_mag!r}")
        
        # 文件类别
        ei_class = self._read(1)[0]
        if ei_class not in (ELFClass.ELFCLASS32, ELFClass.ELFCLASS64):
            raise ValueError(f"不支持的 ELF 类别: {ei_class}")
        
        self.is_32bit = (ei_class == ELFClass.ELFCLASS32)
        
        # 数据编码
        ei_data = self._read(1)[0]
        if ei_data not in (ELFData.ELFDATA2LSB, ELFData.ELFDATA2MSB):
            raise ValueError(f"不支持的 ELF 数据编码: {ei_data}")
        
        self.is_little_endian = (ei_data == ELFData.ELFDATA2LSB)
        self._set_endian(self.is_little_endian)
        
        # 版本
        ei_version = self._read(1)[0]
        
        # OS/ABI
        ei_osabi = self._read(1)[0]
        
        # ABI 版本
        ei_abiversion = self._read(1)[0]
        
        # 填充
        ei_pad = self._read(7)
        
        self.ident = ELFIdent(
            ei_mag=ei_mag,
            ei_class=ei_class,
            ei_data=ei_data,
            ei_version=ei_version,
            ei_osabi=ei_osabi,
            ei_abiversion=ei_abiversion,
            ei_pad=ei_pad
        )
    
    def _parse_header(self):
        """解析 ELF 文件头"""
        e_type = self._read_half()
        e_machine = self._read_half()
        e_version = self._read_word()
        
        if self.is_32bit:
            e_entry = self._read_addr()
            e_phoff = self._read_off()
            e_shoff = self._read_off()
        else:
            e_entry = self._read_addr64()
            e_phoff = self._read_off64()
            e_shoff = self._read_off64()
        
        e_flags = self._read_word()
        e_ehsize = self._read_half()
        e_phentsize = self._read_half()
        e_phnum = self._read_half()
        e_shentsize = self._read_half()
        e_shnum = self._read_half()
        e_shstrndx = self._read_half()
        
        self.header = ELFHeader(
            e_ident=self.ident,
            e_type=e_type,
            e_machine=e_machine,
            e_version=e_version,
            e_entry=e_entry,
            e_phoff=e_phoff,
            e_shoff=e_shoff,
            e_flags=e_flags,
            e_ehsize=e_ehsize,
            e_phentsize=e_phentsize,
            e_phnum=e_phnum,
            e_shentsize=e_shentsize,
            e_shnum=e_shnum,
            e_shstrndx=e_shstrndx
        )
    
    def _parse_program_headers(self):
        """解析程序头表"""
        if self.header.e_phoff == 0 or self.header.e_phnum == 0:
            return
        
        self._seek(self.header.e_phoff)
        
        for _ in range(self.header.e_phnum):
            if self.is_32bit:
                ph = self._parse_program_header_32()
            else:
                ph = self._parse_program_header_64()
            self.program_headers.append(ph)
    
    def _parse_program_header_32(self) -> ProgramHeader:
        """解析 32 位程序头"""
        p_type = self._read_word()
        p_offset = self._read_off()
        p_vaddr = self._read_addr()
        p_paddr = self._read_addr()
        p_filesz = self._read_word()
        p_memsz = self._read_word()
        p_flags_32 = self._read_word()
        p_align = self._read_word()
        
        return ProgramHeader(
            p_type=p_type,
            p_flags=0,
            p_offset=p_offset,
            p_vaddr=p_vaddr,
            p_paddr=p_paddr,
            p_filesz=p_filesz,
            p_memsz=p_memsz,
            p_align=p_align,
            p_flags_32=p_flags_32
        )
    
    def _parse_program_header_64(self) -> ProgramHeader:
        """解析 64 位程序头"""
        p_type = self._read_word()
        p_flags = self._read_word()
        p_offset = self._read_off64()
        p_vaddr = self._read_addr64()
        p_paddr = self._read_addr64()
        p_filesz = self._read_xword()
        p_memsz = self._read_xword()
        p_align = self._read_xword()
        
        return ProgramHeader(
            p_type=p_type,
            p_flags=p_flags,
            p_offset=p_offset,
            p_vaddr=p_vaddr,
            p_paddr=p_paddr,
            p_filesz=p_filesz,
            p_memsz=p_memsz,
            p_align=p_align,
            p_flags_32=0
        )
    
    def _parse_section_headers(self):
        """解析节区头表"""
        if self.header.e_shoff == 0 or self.header.e_shnum == 0:
            return
        
        self._seek(self.header.e_shoff)
        
        for _ in range(self.header.e_shnum):
            if self.is_32bit:
                sh = self._parse_section_header_32()
            else:
                sh = self._parse_section_header_64()
            self.section_headers.append(sh)
    
    def _parse_section_header_32(self) -> SectionHeader:
        """解析 32 位节区头"""
        sh_name = self._read_word()
        sh_type = self._read_word()
        sh_flags = self._read_word()
        sh_addr = self._read_addr()
        sh_offset = self._read_off()
        sh_size = self._read_word()
        sh_link = self._read_word()
        sh_info = self._read_word()
        sh_addralign = self._read_word()
        sh_entsize = self._read_word()
        
        return SectionHeader(
            sh_name=sh_name,
            sh_type=sh_type,
            sh_flags=sh_flags,
            sh_addr=sh_addr,
            sh_offset=sh_offset,
            sh_size=sh_size,
            sh_link=sh_link,
            sh_info=sh_info,
            sh_addralign=sh_addralign,
            sh_entsize=sh_entsize
        )
    
    def _parse_section_header_64(self) -> SectionHeader:
        """解析 64 位节区头"""
        sh_name = self._read_word()
        sh_type = self._read_word()
        sh_flags = self._read_xword()
        sh_addr = self._read_addr64()
        sh_offset = self._read_off64()
        sh_size = self._read_xword()
        sh_link = self._read_word()
        sh_info = self._read_word()
        sh_addralign = self._read_xword()
        sh_entsize = self._read_xword()
        
        return SectionHeader(
            sh_name=sh_name,
            sh_type=sh_type,
            sh_flags=sh_flags,
            sh_addr=sh_addr,
            sh_offset=sh_offset,
            sh_size=sh_size,
            sh_link=sh_link,
            sh_info=sh_info,
            sh_addralign=sh_addralign,
            sh_entsize=sh_entsize
        )
    
    def _parse_string_tables(self):
        """解析字符串表"""
        # 节区名称字符串表
        if self.header.e_shstrndx != SpecialSectionIndex.SHN_UNDEF:
            shstrtab_hdr = self.section_headers[self.header.e_shstrndx]
            self.shstrtab = self.data[shstrtab_hdr.sh_offset:
                                      shstrtab_hdr.sh_offset + shstrtab_hdr.sh_size]
    
    def _resolve_section_names(self):
        """解析节区名称"""
        for sh in self.section_headers:
            sh.name = self._get_string(self.shstrtab, sh.sh_name)
            self.section_by_name[sh.name] = sh
    
    def _get_string(self, strtab: bytes, offset: int) -> str:
        """从字符串表中获取字符串"""
        if offset >= len(strtab):
            return ""
        end = strtab.find(b'\x00', offset)
        if end == -1:
            end = len(strtab)
        return strtab[offset:end].decode('utf-8', errors='replace')
    
    def _parse_symbols(self):
        """解析符号表"""
        # 查找符号表节区
        for sh in self.section_headers:
            if sh.sh_type == SectionHeaderType.SHT_SYMTAB:
                self._parse_symbol_section(sh, False)
            elif sh.sh_type == SectionHeaderType.SHT_DYNSYM:
                self._parse_symbol_section(sh, True)
    
    def _parse_symbol_section(self, sh: SectionHeader, is_dynamic: bool):
        """解析符号表节区"""
        # 获取字符串表
        if sh.sh_link < len(self.section_headers):
            strtab_sh = self.section_headers[sh.sh_link]
            strtab = self.data[strtab_sh.sh_offset:
                              strtab_sh.sh_offset + strtab_sh.sh_size]
            if is_dynamic:
                self.dynstr = strtab
            else:
                self.strtab = strtab
        else:
            strtab = b""
        
        # 解析符号
        offset = sh.sh_offset
        entry_size = 16 if self.is_32bit else 24
        
        for i in range(sh.sh_size // entry_size):
            self._seek(offset + i * entry_size)
            
            if self.is_32bit:
                sym = self._parse_symbol_32(strtab)
            else:
                sym = self._parse_symbol_64(strtab)
            
            if is_dynamic:
                self.dynamic_symbols.append(sym)
            else:
                self.symbols.append(sym)
    
    def _parse_symbol_32(self, strtab: bytes) -> ELFSymbol:
        """解析 32 位符号"""
        st_name = self._read_word()
        st_value = self._read_addr()
        st_size = self._read_word()
        st_info = self._read(1)[0]
        st_other = self._read(1)[0]
        st_shndx = self._read_half()
        
        name = self._get_string(strtab, st_name)
        
        return ELFSymbol(
            st_name=st_name,
            st_info=st_info,
            st_other=st_other,
            st_shndx=st_shndx,
            st_value=st_value,
            st_size=st_size,
            name=name
        )
    
    def _parse_symbol_64(self, strtab: bytes) -> ELFSymbol:
        """解析 64 位符号"""
        st_name = self._read_word()
        st_info = self._read(1)[0]
        st_other = self._read(1)[0]
        st_shndx = self._read_half()
        st_value = self._read_addr64()
        st_size = self._read_xword()
        
        name = self._get_string(strtab, st_name)
        
        return ELFSymbol(
            st_name=st_name,
            st_info=st_info,
            st_other=st_other,
            st_shndx=st_shndx,
            st_value=st_value,
            st_size=st_size,
            name=name
        )
    
    def _parse_dynamic(self):
        """解析动态链接信息"""
        for sh in self.section_headers:
            if sh.sh_type == SectionHeaderType.SHT_DYNAMIC:
                self._parse_dynamic_section(sh)
        
        # 也可以从 PT_DYNAMIC 段解析
        for ph in self.program_headers:
            if ph.p_type == ProgramHeaderType.PT_DYNAMIC:
                # 如果还没有从节区解析，则从段解析
                if not self.dynamics:
                    self._parse_dynamic_segment(ph)
    
    def _parse_dynamic_section(self, sh: SectionHeader):
        """解析动态链接节区"""
        offset = sh.sh_offset
        entry_size = 8 if self.is_32bit else 16
        
        for i in range(sh.sh_size // entry_size):
            self._seek(offset + i * entry_size)
            
            if self.is_32bit:
                d_tag = self._read_sword()
                d_val = self._read_word()
            else:
                d_tag = self._read_sxword()
                d_val = self._read_xword()
            
            self.dynamics.append(ELFDynamic(d_tag=d_tag, d_val=d_val))
            
            if d_tag == DynamicTag.DT_NULL:
                break
    
    def _parse_dynamic_segment(self, ph: ProgramHeader):
        """从段解析动态链接信息"""
        offset = ph.p_offset
        entry_size = 8 if self.is_32bit else 16
        num_entries = ph.p_filesz // entry_size
        
        self._seek(offset)
        
        for _ in range(num_entries):
            if self.is_32bit:
                d_tag = self._read_sword()
                d_val = self._read_word()
            else:
                d_tag = self._read_sxword()
                d_val = self._read_xword()
            
            self.dynamics.append(ELFDynamic(d_tag=d_tag, d_val=d_val))
            
            if d_tag == DynamicTag.DT_NULL:
                break
    
    def _parse_relocations(self):
        """解析重定位表"""
        for sh in self.section_headers:
            if sh.sh_type == SectionHeaderType.SHT_REL:
                self._parse_rel_section(sh)
            elif sh.sh_type == SectionHeaderType.SHT_RELA:
                self._parse_rela_section(sh)
    
    def _parse_rel_section(self, sh: SectionHeader):
        """解析 Rel 重定位表"""
        offset = sh.sh_offset
        entry_size = 8 if self.is_32bit else 16
        
        for i in range(sh.sh_size // entry_size):
            self._seek(offset + i * entry_size)
            
            if self.is_32bit:
                r_offset = self._read_word()
                r_info = self._read_word()
            else:
                r_offset = self._read_addr64()
                r_info = self._read_xword()
            
            self.relocations.append(ELFRelocation(
                r_offset=r_offset,
                r_info=r_info
            ))
    
    def _parse_rela_section(self, sh: SectionHeader):
        """解析 Rela 重定位表"""
        offset = sh.sh_offset
        entry_size = 12 if self.is_32bit else 24
        
        for i in range(sh.sh_size // entry_size):
            self._seek(offset + i * entry_size)
            
            if self.is_32bit:
                r_offset = self._read_word()
                r_info = self._read_word()
                r_addend = self._read_sword()
            else:
                r_offset = self._read_addr64()
                r_info = self._read_xword()
                r_addend = self._read_sxword()
            
            self.relocations.append(ELFRelocationA(
                r_offset=r_offset,
                r_info=r_info,
                r_addend=r_addend
            ))
    
    def get_section_data(self, sh: SectionHeader) -> bytes:
        """获取节区数据"""
        if sh.is_nobits:
            return b'\x00' * sh.sh_size
        return self.data[sh.sh_offset:sh.sh_offset + sh.sh_size]
    
    def get_interpreter(self) -> Optional[str]:
        """获取解释器路径（动态链接器）"""
        for ph in self.program_headers:
            if ph.is_interpreter:
                data = self.data[ph.p_offset:ph.p_offset + ph.p_filesz]
                return data.rstrip(b'\x00').decode('utf-8', errors='replace')
        return None
    
    def get_needed_libraries(self) -> List[str]:
        """获取所需共享库列表"""
        libraries = []
        for dyn in self.dynamics:
            if dyn.d_tag == DynamicTag.DT_NEEDED:
                lib_name = self._get_string(self.dynstr, dyn.d_val)
                libraries.append(lib_name)
        return libraries
    
    def get_symbol_by_name(self, name: str) -> Optional[ELFSymbol]:
        """根据名称查找符号"""
        for sym in self.symbols:
            if sym.name == name:
                return sym
        for sym in self.dynamic_symbols:
            if sym.name == name:
                return sym
        return None
    
    def get_loadable_segments(self) -> List[ProgramHeader]:
        """获取可加载段列表"""
        return [ph for ph in self.program_headers if ph.is_loadable]
    
    def __repr__(self) -> str:
        return (f"ELFParser(arch={'32' if self.is_32bit else '64'}bit, "
                f"endian={'little' if self.is_little_endian else 'big'}, "
                f"type={self.header.e_type if self.header else 'unknown'}, "
                f"machine={self.header.e_machine if self.header else 'unknown'})")
