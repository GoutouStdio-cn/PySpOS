"""
ELF 执行流程详解
================

本文档详细说明 PySpOS 如何加载和执行 ELF 文件

┌─────────────────────────────────────────────────────────────────┐
│                    ELF 执行完整流程                              │
└─────────────────────────────────────────────────────────────────┘

1. ELF 文件结构
===============

ELF 文件由以下部分组成：

┌──────────────────┐
│   ELF Header     │  ← 文件头，包含魔数、架构、入口点等信息
├──────────────────┤
│ Program Headers  │  ← 程序头表，描述如何加载到内存
├──────────────────┤
│   .text Section  │  ← 代码段
├──────────────────┤
│   .data Section  │  ← 数据段
├──────────────────┤
│   .rodata Sect.  │  ← 只读数据
├──────────────────┤
│  Section Headers │  ← 节头表，描述各个节
└──────────────────┘

2. 加载过程
==========

步骤 1: 解析 ELF 头
-------------------
ELFParser.parse() 读取 ELF 头部信息：

- 魔数验证: 0x7f 'E' 'L' 'F'
- 架构判断: 32位还是64位
- 字节序: 小端还是大端
- 入口点: 程序开始执行的地址
- 程序头位置和数量

步骤 2: 解析程序头
------------------
ELFParser.parse_program_headers() 解析每个段：

类型包括：
- PT_LOAD: 需要加载到内存的段
- PT_DYNAMIC: 动态链接信息
- PT_INTERP: 解释器路径

每个 PT_LOAD 段包含：
- p_offset: 文件中的偏移
- p_vaddr: 虚拟内存地址
- p_filesz: 文件大小
- p_memsz: 内存大小（可能大于文件大小，包含 BSS）
- p_flags: 权限（读/写/执行）

步骤 3: 加载到内存
------------------
ELFLoader.load() 将段加载到模拟内存：

for each PT_LOAD segment:
    1. 分配内存空间 (p_memsz)
    2. 从文件读取数据到内存
    3. 填充剩余空间为 0 (BSS段)
    4. 设置内存权限

示例：
┌────────────────────────────────────────────────────────────┐
│ 文件偏移    虚拟地址      大小      权限    内容           │
├────────────────────────────────────────────────────────────┤
│ 0x1000  →  0x401000   0x1234    R-X    .text 代码段      │
│ 0x3000  →  0x403000   0x0100    RW-    .data 数据段      │
└────────────────────────────────────────────────────────────┘

步骤 4: 设置栈和堆
-----------------
ELFLoader._setup_stack():
    - 分配栈空间（默认 1MB）
    - 设置栈顶指针 (RSP)
    - 初始化栈内容（参数、环境变量等）

ELFLoader._setup_heap():
    - 分配堆空间
    - 设置堆指针 (BRK)

3. 执行过程
===========

步骤 1: 初始化 CPU 状态
-----------------------
CPUEmulator 初始化寄存器：

- RIP = 入口点地址
- RSP = 栈顶地址
- RBP = 0
- RAX, RBX, RCX, RDX = 0
- 其他寄存器 = 0

步骤 2: 指令执行循环
--------------------
CPUEmulator.run() 主循环：

while running:
    1. 从 RIP 读取指令字节
    2. 解码指令（操作码、操作数）
    3. 执行指令
    4. 更新 RIP
    5. 检查中断/系统调用

步骤 3: 指令解码
----------------
decode_instruction() 解析 x86_64 指令：

指令格式：
┌────────┬────────┬────────┬────────┬────────┬─────────┐
│ Prefix │  REX   │ Opcode │ ModR/M │  SIB   │ Displacement │
└────────┴────────┴────────┴────────┴────────┴─────────┘

示例指令解码：

mov rax, 1          → 48 C7 C0 01 00 00 00
├─ 48: REX.W (64位操作数)
├─ C7: MOV r/m, imm32
├─ C0: ModR/M (目标: RAX)
└─ 01 00 00 00: 立即数 1

syscall             → 0F 05
├─ 0F: 两字节操作码前缀
└─ 05: SYSCALL 指令

步骤 4: 系统调用处理
--------------------
当执行 SYSCALL 指令时：

1. 从 RAX 读取系统调用号
2. 从 RDI, RSI, RDX... 读取参数
3. 调用 SyscallEmulator 处理
4. 将返回值写入 RAX

常见系统调用：

┌─────────┬────────────┬─────────────────────────────┐
│ 调用号  │   名称     │         功能                 │
├─────────┼────────────┼─────────────────────────────┤
│    0    │ sys_read   │ 读取文件                    │
│    1    │ sys_write  │ 写入文件（输出到终端）       │
│    2    │ sys_open   │ 打开文件                    │
│    3    │ sys_close  │ 关闭文件                    │
│   60    │ sys_exit   │ 退出进程                    │
│    9    │ sys_mmap   │ 内存映射                    │
│   12    │ sys_brk    │ 调整堆大小                  │
└─────────┴────────────┴─────────────────────────────┘

4. 完整执行示例
==============

程序代码（汇编）：
─────────────────
section .text
global _start

_start:
    mov rax, 1          ; sys_write
    mov rdi, 1          ; stdout
    mov rsi, msg        ; 消息地址
    mov rdx, 14         ; 消息长度
    syscall             ; 调用系统
    
    mov rax, 60         ; sys_exit
    mov rdi, 0          ; 退出码
    syscall             ; 退出

msg: db "Hello from ELF!", 10

执行过程：
─────────
1. 加载 ELF → 内存布局:
   0x401000: mov rax, 1
   0x401007: mov rdi, 1
   0x40100E: mov rsi, 0x401030
   0x401015: mov rdx, 14
   0x40101C: syscall
   0x40101E: mov rax, 60
   0x401025: mov rdi, 0
   0x40102C: syscall
   0x401030: "Hello from ELF!\n"

2. CPU 执行:
   RIP=0x401000 → 执行 mov rax, 1 → RAX=1
   RIP=0x401007 → 执行 mov rdi, 1 → RDI=1
   RIP=0x40100E → 执行 mov rsi, 0x401030 → RSI=0x401030
   RIP=0x401015 → 执行 mov rdx, 14 → RDX=14
   RIP=0x40101C → 执行 syscall

3. 系统调用处理:
   RAX=1 → sys_write
   参数: fd=1, buf=0x401030, count=14
   → 输出 "Hello from ELF!"
   → RAX=14 (返回写入字节数)

4. 继续执行:
   RIP=0x40101E → 执行 mov rax, 60 → RAX=60
   RIP=0x401025 → 执行 mov rdi, 0 → RDI=0
   RIP=0x40102C → 执行 syscall

5. 退出处理:
   RAX=60 → sys_exit
   参数: status=0
   → 设置 running=False
   → 返回 ExecutionResult(exit_code=0)

5. 内存管理
===========

虚拟内存布局：
─────────────
┌──────────────────┐ 0xFFFFFFFFFFFFFFFF
│     内核空间      │
├──────────────────┤ 0x7FFFFFFFFFFF
│     栈空间        │ ← RSP 指向这里
│       ↓          │    向下增长
├──────────────────┤
│                  │
│     空闲空间      │
│                  │
├──────────────────┤
│       ↑          │    向上增长
│     堆空间        │ ← BRK 指向这里
├──────────────────┤
│     BSS 段        │
├──────────────────┤
│     数据段        │
├──────────────────┤
│     代码段        │ ← RIP 指向这里
└──────────────────┘ 0x400000

内存访问：
─────────
Memory 类提供：
- read_byte(addr) / write_byte(addr, value)
- read_word(addr) / write_word(addr, value)
- read_dword(addr) / write_dword(addr, value)
- read_qword(addr) / write_qword(addr, value)
- read_bytes(addr, size) / write_bytes(addr, data)

段权限检查：
───────────
- PROT_READ (1):  可读
- PROT_WRITE (2): 可写
- PROT_EXEC (4):  可执行

6. 文件描述符管理
=================

SyscallEmulator 维护文件描述符表：

fd_table = {
    0: stdin,   # 标准输入
    1: stdout,  # 标准输出 → 重定向到捕获缓冲区
    2: stderr,  # 标准错误
    3+: 打开的文件
}

sys_write(1, buf, count) 执行流程：
1. 检查 fd=1 是否有效
2. 从内存读取 count 字节
3. 写入 stdout.buffer
4. 返回写入字节数

7. 错误处理
===========

常见错误：
─────────
1. Page Fault: 访问未映射的内存地址
   → 检查段是否正确加载
   → 检查地址计算是否正确

2. Invalid Instruction: 无法解码的指令
   → 检查指令集支持
   → 检查 REX 前缀处理

3. Division by Zero: 除零错误
   → 检查除法指令的操作数

8. 调试技巧
===========

1. 使用 readelf 查看 ELF 结构：
   $ readelf -h program.elf    # 查看头部
   $ readelf -l program.elf    # 查看程序段
   $ readelf -S program.elf    # 查看节

2. 使用 objdump 反汇编：
   $ objdump -d program.elf    # 反汇编代码

3. 在代码中添加调试输出：
   - 打印 RIP 和指令字节
   - 打印寄存器状态
   - 打印内存访问

9. 性能优化
===========

1. 指令缓存：缓存已解码的指令
2. 内存页表：使用页表管理内存
3. JIT 编译：将热点代码编译为本地代码
4. 直接线程：使用 computed goto 加速指令分发

"""

print(__doc__)
