#
#   elf_loader/elf_constants.py
#   ELF 格式常量定义
#   参考了 ELF Specification Version 1.2
#
#   By GoutouStdio
#   @ 2022~2026 GoutouStdio. Open all rights.


from enum import IntEnum, IntFlag

# ==================== ELF 魔数和标识 ====================
ELFMAG = b'\x7fELF'  # ELF 魔数
SELFMAG = 4          # 魔数长度

# 文件类别
class ELFClass(IntEnum):
    ELFCLASSNONE = 0      # 无效类别
    ELFCLASS32 = 1        # 32 位对象
    ELFCLASS64 = 2        # 64 位对象

# 数据编码
class ELFData(IntEnum):
    ELFDATANONE = 0       # 无效数据编码
    ELFDATA2LSB = 1       # 小端模式
    ELFDATA2MSB = 2       # 大端模式

# 操作系统/ABI 标识
class ELFOSABI(IntEnum):
    ELFOSABI_NONE = 0         # UNIX System V ABI
    ELFOSABI_HPUX = 1         # HP-UX
    ELFOSABI_NETBSD = 2       # NetBSD
    ELFOSABI_GNU = 3          # GNU/Linux，带GNU的Linux
    ELFOSABI_LINUX = 3        # Linux (历史别名，现在应该是 ELFOSABI_GNU)
    ELFOSABI_SOLARIS = 6      # Solaris
    ELFOSABI_AIX = 7          # IBM AIX
    ELFOSABI_IRIX = 8         # IRIX
    ELFOSABI_FREEBSD = 9      # FreeBSD
    ELFOSABI_TRU64 = 10       # Compaq TRU64 UNIX
    ELFOSABI_MODESTO = 11     # Novell Modesto
    ELFOSABI_OPENBSD = 12     # OpenBSD
    ELFOSABI_ARM_AEABI = 64   # ARM EABI
    ELFOSABI_ARM = 97         # ARM
    ELFOSABI_STANDALONE = 255 # Standalone (embedded) application

# ==================== 文件类型 ====================
class ELFType(IntEnum):
    ET_NONE = 0        # 无文件类型
    ET_REL = 1         # 可重定位文件
    ET_EXEC = 2        # 可执行文件
    ET_DYN = 3         # 共享目标文件
    ET_CORE = 4        # 核心文件
    ET_LOOS = 0xfe00   # 操作系统特定范围开始
    ET_HIOS = 0xfeff   # 操作系统特定范围结束
    ET_LOPROC = 0xff00 # 处理器特定范围开始
    ET_HIPROC = 0xffff # 处理器特定范围结束

# ==================== 机器架构 ====================
class ELFMachine(IntEnum):
    EM_NONE = 0          # 无机器
    EM_M32 = 1           # AT&T WE 32100
    EM_SPARC = 2         # SPARC
    EM_386 = 3           # Intel 80386
    EM_68K = 4           # Motorola 68000
    EM_88K = 5           # Motorola 88000
    EM_IAMCU = 6         # Intel MCU
    EM_860 = 7           # Intel 80860
    EM_MIPS = 8          # MIPS I Architecture
    EM_S370 = 9          # IBM System/370 Processor
    EM_MIPS_RS3_LE = 10  # MIPS RS3000 Little-endian
    EM_PARISC = 15       # Hewlett-Packard PA-RISC
    EM_VPP500 = 17       # Fujitsu VPP500
    EM_SPARC32PLUS = 18  # Enhanced instruction set SPARC
    EM_960 = 19          # Intel 80960
    EM_PPC = 20          # PowerPC
    EM_PPC64 = 21        # 64-bit PowerPC
    EM_S390 = 22         # IBM System/390 Processor
    EM_SPU = 23          # IBM SPU/SPC
    EM_V800 = 36         # NEC V800
    EM_FR20 = 37         # Fujitsu FR20
    EM_RH32 = 38         # TRW RH-32
    EM_RCE = 39          # Motorola RCE
    EM_ARM = 40          # ARM 32-bit architecture (AARCH32)
    EM_ALPHA = 41        # Digital Alpha
    EM_SH = 42           # Hitachi SH
    EM_SPARCV9 = 43      # SPARC Version 9
    EM_TRICORE = 44      # Siemens TriCore embedded processor
    EM_ARC = 45          # Argonaut RISC Core, Argonaut Technologies Inc.
    EM_H8_300 = 46       # Hitachi H8/300
    EM_H8_300H = 47      # Hitachi H8/300H
    EM_H8S = 48          # Hitachi H8S
    EM_H8_500 = 49       # Hitachi H8/500
    EM_IA_64 = 50        # Intel IA-64 processor architecture
    EM_MIPS_X = 51       # Stanford MIPS-X
    EM_COLDFIRE = 52     # Motorola ColdFire
    EM_68HC12 = 53       # Motorola M68HC12
    EM_MMA = 54          # Fujitsu MMA Multimedia Accelerator
    EM_PCP = 55          # Siemens PCP
    EM_NCPU = 56         # Sony nCPU embedded RISC processor
    EM_NDR1 = 57         # Denso NDR1 microprocessor
    EM_STARCORE = 58     # Motorola Star*Core processor
    EM_ME16 = 59         # Toyota ME16 processor
    EM_ST100 = 60        # STMicroelectronics ST100 processor
    EM_TINYJ = 61        # Advanced Logic Corp. TinyJ embedded processor family
    EM_X86_64 = 62       # AMD x86-64 architecture
    EM_PDSP = 63         # Sony DSP Processor
    EM_PDP10 = 64        # Digital Equipment Corp. PDP-10
    EM_PDP11 = 65        # Digital Equipment Corp. PDP-11
    EM_FX66 = 66         # Siemens FX66 microcontroller
    EM_ST9PLUS = 67      # STMicroelectronics ST9+ 8/16 bit microcontroller
    EM_ST7 = 68          # STMicroelectronics ST7 8-bit microcontroller
    EM_68HC16 = 69       # Motorola MC68HC16 Microcontroller
    EM_68HC11 = 70       # Motorola MC68HC11 Microcontroller
    EM_68HC08 = 71       # Motorola MC68HC08 Microcontroller
    EM_68HC05 = 72       # Motorola MC68HC05 Microcontroller
    EM_SVX = 73          # Silicon Graphics SVx
    EM_ST19 = 74         # STMicroelectronics ST19 8-bit microcontroller
    EM_VAX = 75          # Digital VAX
    EM_CRIS = 76         # Axis Communications 32-bit embedded processor
    EM_JAVELIN = 77      # Infineon Technologies 32-bit embedded processor
    EM_FIREPATH = 78     # Element 14 64-bit DSP Processor
    EM_ZSP = 79          # LSI Logic 16-bit DSP Processor
    EM_MMIX = 80         # Donald Knuth's educational 64-bit processor
    EM_HUANY = 81        # Harvard University machine-independent object files
    EM_PRISM = 82        # SiTera Prism
    EM_AVR = 83          # Atmel AVR 8-bit microcontroller
    EM_FR30 = 84         # Fujitsu FR30
    EM_D10V = 85         # Mitsubishi D10V
    EM_D30V = 86         # Mitsubishi D30V
    EM_V850 = 87         # NEC v850
    EM_M32R = 88         # Mitsubishi M32R
    EM_MN10300 = 89      # Matsushita MN10300
    EM_MN10200 = 90      # Matsushita MN10200
    EM_PJ = 91           # picoJava
    EM_OPENRISC = 92     # OpenRISC 32-bit embedded processor
    EM_ARC_COMPACT = 93  # ARC International ARCompact processor
    EM_XTENSA = 94       # Tensilica Xtensa Architecture
    EM_VIDEOCORE = 95    # Alphamosaic VideoCore processor
    EM_TMM_GPP = 96      # Thompson Multimedia General Purpose Processor
    EM_NS32K = 97        # National Semiconductor 32000 series
    EM_TPC = 98          # Tenor Network TPC processor
    EM_SNP1K = 99        # Trebia SNP 1000 processor
    EM_ST200 = 100       # STMicroelectronics ST200 microcontroller
    EM_IP2K = 101        # Ubicom IP2xxx microcontroller family
    EM_MAX = 102         # MAX Processor
    EM_CR = 103          # National Semiconductor CompactRISC microprocessor
    EM_F2MC16 = 104      # Fujitsu F2MC16
    EM_MSP430 = 105      # Texas Instruments embedded microcontroller msp430
    EM_BLACKFIN = 106    # Analog Devices Blackfin (DSP) processor
    EM_SE_C33 = 107      # S1C33 Family of Seiko Epson processors
    EM_SEP = 108         # Sharp embedded microprocessor
    EM_ARCA = 109        # Arca RISC Microprocessor
    EM_UNICORE = 110     # Microprocessor series from PKU-Unity Ltd. and MPRC of Peking University
    EM_EXCESS = 111      # eXcess: 16/32/64-bit configurable embedded CPU
    EM_DXP = 112         # Icera Semiconductor Inc. Deep Execution Processor
    EM_ALTERA_NIOS2 = 113 # Altera Nios II soft-core processor
    EM_CRX = 114         # National Semiconductor CompactRISC CRX microprocessor
    EM_XGATE = 115       # Motorola XGATE embedded processor
    EM_C166 = 116        # Infineon C16x/XC16x processor
    EM_M16C = 117        # Renesas M16C series microprocessors
    EM_DSPIC30F = 118    # Microchip Technology dsPIC30F Digital Signal Controller
    EM_CE = 119          # Freescale Communication Engine RISC core
    EM_M32C = 120        # Renesas M32C series microprocessors
    EM_TSK3000 = 131     # Altium TSK3000 core
    EM_RS08 = 132        # Freescale RS08 embedded processor
    EM_SHARC = 133       # Analog Devices SHARC family of 32-bit DSP processors
    EM_ECOG2 = 134       # Cyan Technology eCOG2 microprocessor
    EM_SCORE7 = 135      # Sunplus S+core7 RISC processor
    EM_DSP24 = 136       # New Japan Radio (NJR) 24-bit DSP Processor
    EM_VIDEOCORE3 = 137  # Broadcom VideoCore III processor
    EM_LATTICEMICO32 = 138 # RISC processor for Lattice FPGA architecture
    EM_SE_C17 = 139      # Seiko Epson C17 family
    EM_TI_C6000 = 140    # The Texas Instruments TMS320C6000 DSP family
    EM_TI_C2000 = 141    # The Texas Instruments TMS320C2000 DSP family
    EM_TI_C5500 = 142    # The Texas Instruments TMS320C55x DSP family
    EM_TI_ARP32 = 143    # Texas Instruments Application Specific RISC Processor, 32bit fetch
    EM_TI_PRU = 144      # Texas Instruments Programmable Realtime Unit
    EM_MMDSP_PLUS = 160  # STMicroelectronics 64bit VLIW Data Signal Processor
    EM_CYPRESS_M8C = 161 # Cypress M8C microprocessor
    EM_R32C = 162        # Renesas R32C series microprocessors
    EM_TRIMEDIA = 163    # NXP Semiconductors TriMedia architecture family
    EM_QDSP6 = 164       # QUALCOMM DSP6 Processor
    EM_8051 = 165        # Intel 8051 and variants
    EM_STXP7X = 166      # STMicroelectronics STxP7x family of configurable and extensible RISC processors
    EM_NDS32 = 167       # Andes Technology compact code size embedded RISC processor family
    EM_ECOG1 = 168       # Cyan Technology eCOG1X family
    EM_ECOG1X = 168      # Cyan Technology eCOG1X family
    EM_MAXQ30 = 169      # Dallas Semiconductor MAXQ30 Core Micro-controllers
    EM_XIMO16 = 170      # New Japan Radio (NJR) 16-bit DSP Processor
    EM_MANIK = 171       # M2000 Reconfigurable RISC Microprocessor
    EM_CRAYNV2 = 172     # Cray Inc. NV2 vector architecture
    EM_RX = 173          # Renesas RX family
    EM_METAG = 174       # Imagination Technologies META processor architecture
    EM_MCST_ELBRUS = 175 # MCST Elbrus general purpose hardware architecture
    EM_ECOG16 = 176      # Cyan Technology eCOG16 family
    EM_CR16 = 177        # National Semiconductor CompactRISC CR16 16-bit microprocessor
    EM_ETPU = 178        # Freescale Extended Time Processing Unit
    EM_SLE9X = 179       # Infineon Technologies SLE9X core
    EM_L10M = 180        # Intel L10M
    EM_K10M = 181        # Intel K10M
    EM_AARCH64 = 183     # ARM 64-bit architecture (AARCH64)
    EM_AVR32 = 185       # Atmel Corporation 32-bit microprocessor family
    EM_STM8 = 186        # STMicroeletronics STM8 8-bit microcontroller
    EM_TILE64 = 187      # Tilera TILE64 multicore architecture family
    EM_TILEPRO = 188     # Tilera TILEPro multicore architecture family
    EM_CUDA = 190        # NVIDIA CUDA architecture
    EM_TILEGX = 191      # Tilera TILE-Gx multicore architecture family
    EM_CLOUDSHIELD = 192 # CloudShield architecture family
    EM_COREA_1ST = 193   # KIPO-KAIST Core-A 1st generation processor family
    EM_COREA_2ND = 194   # KIPO-KAIST Core-A 2nd generation processor family
    EM_ARC_COMPACT2 = 195 # Synopsys ARCompact V2
    EM_OPEN8 = 196       # Open8 8-bit RISC soft processor core
    EM_RL78 = 197        # Renesas RL78 family
    EM_VIDEOCORE5 = 198  # Broadcom VideoCore V processor
    EM_78KOR = 199       # Renesas 78KOR family
    EM_56800EX = 200     # Freescale 56800EX Digital Signal Controller (DSC)
    EM_BA1 = 201         # Beyond BA1 CPU architecture
    EM_BA2 = 202         # Beyond BA2 CPU architecture
    EM_XCORE = 203       # XMOS xCORE processor family
    EM_MCHP_PIC = 204    # Microchip 8-bit PIC(r) family
    EM_INTEL205 = 205    # Reserved by Intel
    EM_INTEL206 = 206    # Reserved by Intel
    EM_INTEL207 = 207    # Reserved by Intel
    EM_INTEL208 = 208    # Reserved by Intel
    EM_INTEL209 = 209    # Reserved by Intel
    EM_KM32 = 210        # KM211 KM32 32-bit processor
    EM_KMX32 = 211       # KM211 KMX32 32-bit processor
    EM_KMX16 = 212       # KM211 KMX16 16-bit processor
    EM_KMX8 = 213        # KM211 KMX8 8-bit processor
    EM_KVARC = 214       # KM211 KVARC processor
    EM_CDP = 215         # Paneve CDP architecture family
    EM_COGE = 216        # Cognitive Smart Memory Processor
    EM_COOL = 217        # Bluechip Systems CoolEngine
    EM_NORC = 218        # Nanoradio Optimized RISC
    EM_CSR_KALIMBA = 219 # CSR Kalimba architecture family
    EM_Z80 = 220         # Zilog Z80
    EM_VISIUM = 221      # Controls and Data Services VISIUMcore processor
    EM_FT32 = 222        # FTDI Chip FT32 high performance 32-bit RISC architecture
    EM_MOXIE = 223       # Moxie processor family
    EM_AMDGPU = 224      # AMD GPU architecture
    EM_RISCV = 243       # RISC-V

# ==================== 段类型 (p_type) ====================
class ProgramHeaderType(IntEnum):
    PT_NULL = 0          # 未使用条目
    PT_LOAD = 1          # 可加载段
    PT_DYNAMIC = 2       # 动态链接信息
    PT_INTERP = 3        # 解释器路径
    PT_NOTE = 4          # 辅助信息
    PT_SHLIB = 5         # 保留
    PT_PHDR = 6          # 程序头表位置
    PT_TLS = 7           # 线程局部存储段
    PT_LOOS = 0x60000000 # 操作系统特定范围开始
    PT_HIOS = 0x6fffffff # 操作系统特定范围结束
    PT_LOPROC = 0x70000000 # 处理器特定范围开始
    PT_HIPROC = 0x7fffffff # 处理器特定范围结束

# GNU 堆栈段类型
PT_GNU_STACK = 0x6474e551
PT_GNU_RELRO = 0x6474e552
PT_GNU_PROPERTY = 0x6474e553

# ==================== 段标志 (p_flags) ====================
class ProgramHeaderFlags(IntFlag):
    PF_X = 1             # 可执行
    PF_W = 2             # 可写
    PF_R = 4             # 可读
    PF_MASKOS = 0x0ff00000  # 操作系统特定掩码
    PF_MASKPROC = 0xf0000000 # 处理器特定掩码

# ==================== 节区类型 (sh_type) ====================
class SectionHeaderType(IntEnum):
    SHT_NULL = 0              # 未使用节区
    SHT_PROGBITS = 1          # 程序数据
    SHT_SYMTAB = 2            # 符号表
    SHT_STRTAB = 3            # 字符串表
    SHT_RELA = 4              # 带加数的重定位表
    SHT_HASH = 5              # 符号哈希表
    SHT_DYNAMIC = 6           # 动态链接信息
    SHT_NOTE = 7              # 注释信息
    SHT_NOBITS = 8            # 不占空间的节区(BSS)
    SHT_REL = 9               # 重定位表
    SHT_SHLIB = 10            # 保留
    SHT_DYNSYM = 11           # 动态符号表
    SHT_INIT_ARRAY = 14       # 初始化函数指针数组
    SHT_FINI_ARRAY = 15       # 终止函数指针数组
    SHT_PREINIT_ARRAY = 16    # 预初始化函数指针数组
    SHT_GROUP = 17            # 节区组
    SHT_SYMTAB_SHNDX = 18     # 扩展节区索引
    SHT_LOOS = 0x60000000     # 操作系统特定范围开始
    SHT_HIOS = 0x6fffffff     # 操作系统特定范围结束
    SHT_LOPROC = 0x70000000   # 处理器特定范围开始
    SHT_HIPROC = 0x7fffffff   # 处理器特定范围结束
    SHT_LOUSER = 0x80000000   # 应用程序特定范围开始
    SHT_HIUSER = 0xffffffff   # 应用程序特定范围结束

# GNU 属性节区
SHT_GNU_ATTRIBUTES = 0x6ffffff5
SHT_GNU_HASH = 0x6ffffff6
SHT_GNU_LIBLIST = 0x6ffffff7
SHT_CHECKSUM = 0x6ffffff8
SHT_GNU_VERDEF = 0x6ffffffd
SHT_GNU_VERNEED = 0x6ffffffe
SHT_GNU_VERSYM = 0x6fffffff

# ==================== 节区标志 (sh_flags) ====================
class SectionHeaderFlags(IntFlag):
    SHF_WRITE = 0x1           # 可写
    SHF_ALLOC = 0x2           # 占用内存
    SHF_EXECINSTR = 0x4       # 可执行指令
    SHF_MERGE = 0x10          # 可合并
    SHF_STRINGS = 0x20        # 包含空终止字符串
    SHF_INFO_LINK = 0x40      # sh_info 包含节区索引
    SHF_LINK_ORDER = 0x80     # 保留链接顺序
    SHF_OS_NONCONFORMING = 0x100  # 非标准操作系统特定处理
    SHF_GROUP = 0x200         # 节区是组的一部分
    SHF_TLS = 0x400           # 线程局部存储
    SHF_COMPRESSED = 0x800    # 压缩节区
    SHF_MASKOS = 0x0ff00000   # 操作系统特定掩码
    SHF_MASKPROC = 0xf0000000 # 处理器特定掩码

# ==================== 动态标签 (d_tag) ====================
class DynamicTag(IntEnum):
    DT_NULL = 0              # 标记 _DYNAMIC 数组结束
    DT_NEEDED = 1            # 所需库的名称字符串表偏移
    DT_PLTRELSZ = 2          # PLT 重定位表大小
    DT_PLTGOT = 3            # PLT/GOT 地址
    DT_HASH = 4              # 符号哈希表地址
    DT_STRTAB = 5            # 字符串表地址
    DT_SYMTAB = 6            # 符号表地址
    DT_RELA = 7              # Rela 重定位表地址
    DT_RELASZ = 8            # Rela 重定位表大小
    DT_RELAENT = 9           # Rela 重定位表条目大小
    DT_STRSZ = 10            # 字符串表大小
    DT_SYMENT = 11           # 符号表条目大小
    DT_INIT = 12             # 初始化函数地址
    DT_FINI = 13             # 终止函数地址
    DT_SONAME = 14           # 共享对象名称字符串表偏移
    DT_RPATH = 15            # 库搜索路径字符串表偏移
    DT_SYMBOLIC = 16         # 符号链接标志
    DT_REL = 17              # Rel 重定位表地址
    DT_RELSZ = 18            # Rel 重定位表大小
    DT_RELENT = 19           # Rel 重定位表条目大小
    DT_PLTREL = 20           # PLT 重定位类型
    DT_DEBUG = 21            # 调试信息
    DT_TEXTREL = 22          # 文本重定位标志
    DT_JMPREL = 23           # PLT 重定位表地址
    DT_BIND_NOW = 24         # 立即绑定标志
    DT_INIT_ARRAY = 25       # 初始化函数指针数组地址
    DT_FINI_ARRAY = 26       # 终止函数指针数组地址
    DT_INIT_ARRAYSZ = 27     # 初始化函数指针数组大小
    DT_FINI_ARRAYSZ = 28     # 终止函数指针数组大小
    DT_RUNPATH = 29          # 运行时库搜索路径
    DT_FLAGS = 30            # 标志
    DT_ENCODING = 32         # 编码值开始
    DT_PREINIT_ARRAY = 32    # 预初始化函数指针数组地址
    DT_PREINIT_ARRAYSZ = 33  # 预初始化函数指针数组大小
    DT_SYMTAB_SHNDX = 34     # 符号表节区索引
    DT_LOOS = 0x6000000d     # 操作系统特定范围开始
    DT_HIOS = 0x6ffff000     # 操作系统特定范围结束
    DT_LOPROC = 0x70000000   # 处理器特定范围开始
    DT_HIPROC = 0x7fffffff   # 处理器特定范围结束

# GNU 特定动态标签
DT_GNU_HASH = 0x6ffffef5
DT_TLSDESC_PLT = 0x6ffffef6
DT_TLSDESC_GOT = 0x6ffffef7
DT_GNU_CONFLICT = 0x6ffffef8
DT_GNU_LIBLIST = 0x6ffffef9
DT_CONFIG = 0x6ffffefa
DT_DEPAUDIT = 0x6ffffefb
DT_AUDIT = 0x6ffffefc
DT_PLTPAD = 0x6ffffefd
DT_MOVETAB = 0x6ffffefe
DT_SYMINFO = 0x6ffffeff
DT_VERSYM = 0x6ffffff0
DT_RELACOUNT = 0x6ffffff9
DT_RELCOUNT = 0x6ffffffa
DT_FLAGS_1 = 0x6ffffffb
DT_VERDEF = 0x6ffffffc
DT_VERDEFNUM = 0x6ffffffd
DT_VERNEED = 0x6ffffffe
DT_VERNEEDNUM = 0x6fffffff

# ==================== 符号绑定 (st_info 高 4 位) ====================
class SymbolBinding(IntEnum):
    STB_LOCAL = 0     # 局部符号
    STB_GLOBAL = 1    # 全局符号
    STB_WEAK = 2      # 弱符号
    STB_LOOS = 10     # 操作系统特定范围开始
    STB_HIOS = 12     # 操作系统特定范围结束
    STB_LOPROC = 13   # 处理器特定范围开始
    STB_HIPROC = 15   # 处理器特定范围结束

# ==================== 符号类型 (st_info 低 4 位) ====================
class SymbolType(IntEnum):
    STT_NOTYPE = 0    # 未指定类型
    STT_OBJECT = 1    # 数据对象
    STT_FUNC = 2      # 函数
    STT_SECTION = 3   # 节区
    STT_FILE = 4      # 文件名
    STT_COMMON = 5    # 公共数据
    STT_TLS = 6       # 线程局部存储
    STT_LOOS = 10     # 操作系统特定范围开始
    STT_HIOS = 12     # 操作系统特定范围结束
    STT_LOPROC = 13   # 处理器特定范围开始
    STT_HIPROC = 15   # 处理器特定范围结束

# ==================== 重定位类型 (x86_64) ====================
class RelocationTypeX86_64(IntEnum):
    R_X86_64_NONE = 0           # 无重定位
    R_X86_64_64 = 1             # 直接 64 位
    R_X86_64_PC32 = 2           # PC 相对 32 位有符号
    R_X86_64_GOT32 = 3          # 32 位 GOT 条目
    R_X86_64_PLT32 = 4          # 32 位 PLT 地址
    R_X86_64_COPY = 5           # 复制重定位
    R_X86_64_GLOB_DAT = 6       # 创建 GOT 条目
    R_X86_64_JUMP_SLOT = 7      # 创建 PLT 条目
    R_X86_64_RELATIVE = 8       # 基址相对地址
    R_X86_64_GOTPCREL = 9       # 32 位有符号 PC 相对偏移到 GOT
    R_X86_64_32 = 10            # 直接 32 位零扩展
    R_X86_64_32S = 11           # 直接 32 位符号扩展
    R_X86_64_16 = 12            # 直接 16 位零扩展
    R_X86_64_PC16 = 13          # 16 位有符号 PC 相对
    R_X86_64_8 = 14             # 直接 8 位零扩展
    R_X86_64_PC8 = 15           # 8 位有符号 PC 相对
    R_X86_64_DTPMOD64 = 16      # ID of module containing symbol
    R_X86_64_DTPOFF64 = 17      # Offset in module's TLS block
    R_X86_64_TPOFF64 = 18       # Offset in initial TLS block
    R_X86_64_TLSGD = 19         # 32 位有符号 PC 相对偏移到两个 GOT 条目
    R_X86_64_TLSLD = 20         # 32 位有符号 PC 相对偏移到两个 GOT 条目
    R_X86_64_DTPOFF32 = 21      # Offset in TLS block
    R_X86_64_GOTTPOFF = 22      # 32 位有符号 PC 相对偏移到 GOT 条目
    R_X86_64_TPOFF32 = 23       # Offset in initial TLS block
    R_X86_64_PC64 = 24          # PC 相对 64 位
    R_X86_64_GOTOFF64 = 25      # 64 位 GOT 相对偏移
    R_X86_64_GOTPC32 = 26       # 32 位有符号 PC 相对偏移到 GOT
    R_X86_64_GOT64 = 27         # 64 位 GOT 条目偏移
    R_X86_64_GOTPCREL64 = 28    # 64 位 PC 相对偏移到 GOT 条目
    R_X86_64_GOTPC64 = 29       # 64 位 PC 相对偏移到 GOT
    R_X86_64_GOTPLT64 = 30      # 64 位 GOT 条目用于 PLT
    R_X86_64_PLTOFF64 = 31      # 64 位 GOT 相对偏移到 PLT 条目
    R_X86_64_SIZE32 = 32        # 32 位符号大小
    R_X86_64_SIZE64 = 33        # 64 位符号大小
    R_X86_64_GOTPC32_TLSDESC = 34 # 32 位有符号 PC 相对偏移到 TLS 描述符
    R_X86_64_TLSDESC_CALL = 35  # TLS 描述符重定位标记
    R_X86_64_TLSDESC = 36       # 2x64 位 TLS 描述符
    R_X86_64_IRELATIVE = 37     # 调整间接程序地址

# ==================== 重定位类型 (i386) ====================
class RelocationTypeI386(IntEnum):
    R_386_NONE = 0          # 无重定位
    R_386_32 = 1            # 直接 32 位
    R_386_PC32 = 2          # PC 相对 32 位
    R_386_GOT32 = 3         # 32 位 GOT 条目
    R_386_PLT32 = 4         # 32 位 PLT 地址
    R_386_COPY = 5          # 复制重定位
    R_386_GLOB_DAT = 6      # 创建 GOT 条目
    R_386_JMP_SLOT = 7      # 创建 PLT 条目
    R_386_RELATIVE = 8      # 基址相对地址
    R_386_GOTOFF = 9        # 32 位 GOT 相对偏移
    R_386_GOTPC = 10        # 32 位 PC 相对偏移到 GOT
    R_386_32PLT = 11        # 32 位 PLT 偏移
    R_386_TLS_TPOFF = 14    # 线程局部存储偏移
    R_386_TLS_IE = 15       # TLS 初始可执行地址
    R_386_TLS_GOTIE = 16    # TLS GOT 条目
    R_386_TLS_LE = 17       # TLS 局部可执行地址
    R_386_TLS_GD = 18       # TLS 全局动态地址
    R_386_TLS_LDM = 19      # TLS 局部动态地址
    R_386_16 = 20           # 直接 16 位
    R_386_PC16 = 21         # PC 相对 16 位
    R_386_8 = 22            # 直接 8 位
    R_386_PC8 = 23          # PC 相对 8 位
    R_386_TLS_GD_32 = 24    # 32 位 TLS GD 偏移
    R_386_TLS_GD_PUSH = 25  # TLS GD 压栈指令
    R_386_TLS_GD_CALL = 26  # TLS GD 调用指令
    R_386_TLS_GD_POP = 27   # TLS GD 弹栈指令
    R_386_TLS_LDM_32 = 28   # 32 位 TLS LDM 偏移
    R_386_TLS_LDM_PUSH = 29 # TLS LDM 压栈指令
    R_386_TLS_LDM_CALL = 30 # TLS LDM 调用指令
    R_386_TLS_LDM_POP = 31  # TLS LDM 弹栈指令
    R_386_TLS_LDO_32 = 32   # 32 位 TLS LDO 偏移
    R_386_TLS_IE_32 = 33    # 32 位 TLS IE 偏移
    R_386_TLS_LE_32 = 34    # 32 位 TLS LE 偏移
    R_386_TLS_DTPMOD32 = 35 # 32 位 TLS DTPMOD 偏移
    R_386_TLS_DTPOFF32 = 36 # 32 位 TLS DTPOFF 偏移
    R_386_TLS_TPOFF32 = 37  # 32 位 TLS TPOFF 偏移
    R_386_SIZE32 = 38       # 32 位符号大小
    R_386_TLS_GOTDESC = 39  # TLS GOT 描述符
    R_386_TLS_DESC_CALL = 40 # TLS 描述符调用
    R_386_TLS_DESC = 41     # TLS 描述符
    R_386_IRELATIVE = 42    # 调整间接程序地址
    R_386_GOT32X = 43       # 32 位 GOT 条目

# ==================== 特殊节区索引 ====================
class SpecialSectionIndex(IntEnum):
    SHN_UNDEF = 0           # 未定义/缺失/无关的引用
    SHN_LORESERVE = 0xff00  # 保留索引范围开始
    SHN_LOPROC = 0xff00     # 处理器特定范围开始
    SHN_HIPROC = 0xff1f     # 处理器特定范围结束
    SHN_LIVEPATCH = 0xff20  # 实时补丁节区
    SHN_ABS = 0xfff1        # 绝对值
    SHN_COMMON = 0xfff2     # 公共符号
    SHN_HIRESERVE = 0xffff  # 保留索引范围结束
