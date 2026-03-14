#
#   elf_loader/elf_runner.py
#   ELF 程序运行器
#
#   By GoutouStdio
#   @ 2022~2026 GoutouStdio. Open all rights.

from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import logging

from .elf_parser import ELFParser
from .elf_loader import ELFLoader, LoadedSegment
from .cpu_emulator import CPUEmulator, SyscallInterrupt
from .syscall_emulator import SyscallEmulator

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """执行结果"""
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    instruction_count: int = 0
    execution_time: float = 0.0
    memory_usage: int = 0
    
    def __str__(self) -> str:
        return f"ExecutionResult(exit_code={self.exit_code}, instructions={self.instruction_count})"


class ELFRunner:
    """ELF 程序运行器"""
    
    def __init__(self, elf_path: str, base_addr: Optional[int] = None):
        """
        初始化 ELF 运行器
        
        Args:
            elf_path: ELF 文件路径
            base_addr: 加载基址（可选，用于位置无关的可执行文件）
        """
        self.elf_path = elf_path
        self.base_addr = base_addr
        
        # 解析 ELF 文件
        self.parser: Optional[ELFParser] = None
        
        # 加载器
        self.loader: Optional[ELFLoader] = None
        
        # CPU 模拟器
        self.cpu: Optional[CPUEmulator] = None
        
        # 系统调用模拟器
        self.syscall_emulator: Optional[SyscallEmulator] = None
        
        # 执行状态
        self.is_loaded = False
        self.is_running = False
        
        # 输出捕获
        self.stdout_buffer: List[str] = []
        self.stderr_buffer: List[str] = []
        
        # 自定义系统调用处理器
        self.custom_syscall_handlers: Dict[int, Callable] = {}
    
    def load(self) -> bool:
        """
        加载 ELF 文件
        
        Returns:
            是否成功加载
        """
        try:
            # 读取 ELF 文件
            with open(self.elf_path, 'rb') as f:
                data = f.read()
            
            # 解析 ELF 文件
            self.parser = ELFParser(data)
            
            if not self.parser.parse():
                logger.error(f"Failed to parse ELF file: {self.elf_path}")
                return False
            
            # 检查是否可执行
            if self.parser.header.e_type != 2:  # ET_EXEC
                logger.warning(f"ELF file is not executable (type={self.parser.header.e_type})")
                # 仍然尝试加载，因为可能是共享库
            
            # 检查机器类型
            machine = self.parser.header.e_machine
            if machine not in (3, 62):  # EM_386, EM_X86_64
                logger.error(f"Unsupported machine type: {machine}")
                return False
            
            # 创建加载器
            self.loader = ELFLoader(self.parser, self.base_addr)
            
            # 加载到内存
            if not self.loader.load():
                logger.error("Failed to load ELF into memory")
                return False
            
            # 创建系统调用模拟器
            self.syscall_emulator = SyscallEmulator(self.loader)
            
            # 设置输出捕获
            self._setup_output_capture()
            
            # 创建 CPU 模拟器
            self.cpu = CPUEmulator(self.loader, self._handle_syscall)
            
            self.is_loaded = True
            logger.info(f"Successfully loaded ELF: {self.elf_path}")
            logger.info(f"  Entry point: 0x{self.loader.entry_point:08x}")
            logger.info(f"  Architecture: {'x86_64' if not self.parser.is_32bit else 'i386'}")
            logger.info(f"  Base address: 0x{self.loader.base_addr:08x}")
            
            return True
            
        except FileNotFoundError:
            logger.error(f"ELF file not found: {self.elf_path}")
            return False
        except Exception as e:
            logger.error(f"Error loading ELF file: {e}")
            return False
    
    def _setup_output_capture(self) -> None:
        """设置输出捕获"""
        # 使用 syscall_emulator 的缓冲区
        # stdout_buffer 和 stderr_buffer 已经在 syscall_emulator 中初始化
        pass
    
    def _handle_syscall(self, number: int, *args) -> int:
        """
        处理系统调用
        
        Args:
            number: 系统调用号
            *args: 参数列表
            
        Returns:
            系统调用返回值
        """
        # 检查是否有自定义处理器
        if number in self.custom_syscall_handlers:
            return self.custom_syscall_handlers[number](*args)
        
        # 使用系统调用模拟器处理
        return self.syscall_emulator.handle_syscall(number, *args)
    
    def run(self, 
            argv: Optional[List[str]] = None,
            envp: Optional[Dict[str, str]] = None,
            max_instructions: Optional[int] = None) -> ExecutionResult:
        """
        运行 ELF 程序
        
        Args:
            argv: 命令行参数列表
            envp: 环境变量字典
            max_instructions: 最大执行指令数
            
        Returns:
            执行结果
        """
        import time
        
        if not self.is_loaded:
            if not self.load():
                return ExecutionResult(exit_code=-1, 
                                      stderr="Failed to load ELF file")
        
        # 准备参数
        if argv is None:
            argv = [self.elf_path]
        
        if envp is None:
            import os
            envp = dict(os.environ)
        
        # 清空输出缓冲区
        self.syscall_emulator.stdout_buffer.clear()
        self.syscall_emulator.stderr_buffer.clear()
        
        # 设置参数和环境变量
        self.cpu.set_argv_envp(argv, envp)
        
        # 执行程序
        self.is_running = True
        start_time = time.time()
        
        try:
            exit_code = self.cpu.run(max_instructions)
        except SystemExit as e:
            exit_code = e.code if e.code is not None else 0
        except Exception as e:
            from elf_loader.cpu_emulator import SyscallInterrupt
            if not isinstance(e, SyscallInterrupt):
                logger.error(f"Execution error: {e}")
                exit_code = -1
            else:
                raise
        finally:
            self.is_running = False
        
        execution_time = time.time() - start_time
        
        # 收集结果
        stdout_text = b''.join(self.syscall_emulator.stdout_buffer).decode('utf-8', errors='replace')
        stderr_text = b''.join(self.syscall_emulator.stderr_buffer).decode('utf-8', errors='replace')
        result = ExecutionResult(
            exit_code=exit_code,
            stdout=stdout_text,
            stderr=stderr_text,
            instruction_count=self.cpu.instruction_count,
            execution_time=execution_time,
            memory_usage=self._calculate_memory_usage()
        )
        
        logger.info(f"Program execution completed: {result}")
        
        return result
    
    def _calculate_memory_usage(self) -> int:
        """计算内存使用量"""
        if not self.loader:
            return 0
        
        total = 0
        for region in self.loader.memory.values():
            total += len(region.data)
        return total
    
    def step(self) -> bool:
        """
        单步执行一条指令
        
        Returns:
            是否继续执行
        """
        if not self.is_loaded:
            return False
        
        try:
            ip = self.cpu._get_ip()
            name, length, operands = self.cpu.decoder.decode(self.cpu.memory, ip)
            result = self.cpu._execute(name, length, operands)
            self.cpu.instruction_count += 1
            return result != 'exit'
        except SyscallInterrupt as e:
            result = self._handle_syscall(e.number, *e.syscall_args)
            self.cpu._set_reg(0, result)
            return True
        except SystemExit:
            return False
        except Exception as e:
            logger.error(f"Step error: {e}")
            return False
    
    def get_state(self) -> Dict[str, Any]:
        """获取当前执行状态"""
        if not self.cpu:
            return {}
        
        return {
            'loaded': self.is_loaded,
            'running': self.is_running,
            'cpu': self.cpu.get_state(),
            'memory_regions': len(self.loader.memory) if self.loader else 0,
        }
    
    def register_syscall_handler(self, number: int, handler: Callable) -> None:
        """
        注册自定义系统调用处理器
        
        Args:
            number: 系统调用号
            handler: 处理函数
        """
        self.custom_syscall_handlers[number] = handler
    
    def set_stdin(self, data: str) -> None:
        """
        设置标准输入
        
        Args:
            data: 输入数据
        """
        if self.syscall_emulator:
            self.syscall_emulator.stdin = data
    
    def get_stdout(self) -> str:
        """获取标准输出"""
        return ''.join(self.stdout_buffer)
    
    def get_stderr(self) -> str:
        """获取标准错误"""
        return ''.join(self.stderr_buffer)
    
    def dump_memory(self, addr: Optional[int] = None, 
                   size: int = 256) -> bytes:
        """
        转储内存
        
        Args:
            addr: 起始地址（默认为入口点）
            size: 大小
            
        Returns:
            内存数据
        """
        if not self.cpu:
            return b''
        
        if addr is None:
            addr = self.loader.entry_point if self.loader else 0
        
        try:
            return self.cpu.memory.read_bytes(addr, size)
        except Exception as e:
            logger.error(f"Memory dump error: {e}")
            return b''
    
    def dump_registers(self) -> Dict[str, int]:
        """转储寄存器状态"""
        if not self.cpu:
            return {}
        
        state = self.cpu.get_state()
        registers = state.get('registers', {})
        
        # 转换为可读格式
        result = {}
        is_64bit = state.get('is_64bit', True)
        
        if is_64bit:
            reg_names = ['RAX', 'RCX', 'RDX', 'RBX', 'RSP', 'RBP', 'RSI', 'RDI',
                        'R8', 'R9', 'R10', 'R11', 'R12', 'R13', 'R14', 'R15',
                        'RIP', 'RFLAGS'] # 熟悉的基本寄存器 他妈了个逼spaceos在这炸的
        else:
            reg_names = ['EAX', 'ECX', 'EDX', 'EBX', 'ESP', 'EBP', 'ESI', 'EDI',
                        'EIP', 'EFLAGS']
        
        for i, name in enumerate(reg_names):
            if i in registers:
                result[name] = registers[i]
        
        return result
    
    def disassemble(self, addr: Optional[int] = None, 
                   count: int = 10) -> List[Tuple[int, str, int, List]]:
        if not self.cpu:
            return []
        
        if addr is None:
            addr = self.cpu._get_ip()
        
        result = []
        current_addr = addr
        
        for _ in range(count):
            try:
                name, length, operands = self.cpu.decoder.decode(
                    self.cpu.memory, current_addr
                )
                result.append((current_addr, name, length, operands))
                current_addr += length
            except Exception as e:
                break
        
        return result


def run_elf(elf_path: str,
            argv: Optional[List[str]] = None,
            envp: Optional[Dict[str, str]] = None,
            max_instructions: Optional[int] = None,
            base_addr: Optional[int] = None) -> ExecutionResult:
    """
    便捷函数：运行 ELF 程序
    
    Args:
        elf_path: ELF 文件路径
        argv: 命令行参数列表
        envp: 环境变量字典
        max_instructions: 最大执行指令数
        base_addr: 加载基址
        
    Returns:
        执行结果
    """
    runner = ELFRunner(elf_path, base_addr)
    return runner.run(argv, envp, max_instructions)


class ELFDebugger:
    """ELF 调试器"""
    
    def __init__(self, runner: ELFRunner):
        """初始化调试器"""
        self.runner = runner
        self.breakpoints: set = set()
        self.watchpoints: Dict[int, int] = {}  # 地址 -> 原始值
        self.is_debugging = False
        self.history: List[Dict] = []
    
    def add_breakpoint(self, addr: int) -> None:
        """添加断点"""
        self.breakpoints.add(addr)
        logger.info(f"Breakpoint added at 0x{addr:08x}")
    
    def remove_breakpoint(self, addr: int) -> None:
        """移除断点"""
        self.breakpoints.discard(addr)
        logger.info(f"Breakpoint removed at 0x{addr:08x}")
    
    def add_watchpoint(self, addr: int) -> None:
        """添加监视点"""
        try:
            original = self.runner.cpu.memory.read_dword(addr)
            self.watchpoints[addr] = original
            logger.info(f"Watchpoint added at 0x{addr:08x} (value=0x{original:08x})")
        except Exception as e:
            logger.error(f"Failed to add watchpoint: {e}")
    
    def check_watchpoints(self) -> List[Tuple[int, int, int]]:
        """
        检查监视点
        
        Returns:
            触发监视点的列表 [(地址, 原值, 新值), ...]
        """
        triggered = []
        for addr, original in self.watchpoints.items():
            try:
                current = self.runner.cpu.memory.read_dword(addr)
                if current != original:
                    triggered.append((addr, original, current))
                    self.watchpoints[addr] = current
            except:
                pass
        return triggered
    
    def run_with_debugging(self, 
                          argv: Optional[List[str]] = None,
                          envp: Optional[Dict[str, str]] = None) -> ExecutionResult:
        """
        在调试模式下运行
        
        Args:
            argv: 命令行参数列表
            envp: 环境变量字典
            
        Returns:
            执行结果
        """
        if not self.runner.is_loaded:
            if not self.runner.load():
                return ExecutionResult(exit_code=-1)
        
        # 准备参数
        if argv is None:
            argv = [self.runner.elf_path]
        if envp is None:
            import os
            envp = dict(os.environ)
        
        self.runner.cpu.set_argv_envp(argv, envp)
        
        self.is_debugging = True
        instruction_count = 0
        
        try:
            while True:
                ip = self.runner.cpu._get_ip()
                
                # 检查断点
                if ip in self.breakpoints:
                    logger.info(f"Breakpoint hit at 0x{ip:08x}")
                    self._debug_prompt()
                
                # 检查监视点
                triggered = self.check_watchpoints()
                for addr, old_val, new_val in triggered:
                    logger.info(f"Watchpoint triggered at 0x{addr:08x}: "
                               f"0x{old_val:08x} -> 0x{new_val:08x}")
                    self._debug_prompt()
                
                # 保存状态历史
                self.history.append({
                    'ip': ip,
                    'registers': dict(self.runner.cpu.state.regs),
                })
                if len(self.history) > 1000:
                    self.history.pop(0)
                
                # 单步执行
                if not self.runner.step():
                    break
                
                instruction_count += 1
                
                # 每 10000 条指令检查一次
                if instruction_count % 10000 == 0:
                    logger.debug(f"Executed {instruction_count} instructions")
        
        except Exception as e:
            logger.error(f"Debug execution error: {e}")
        finally:
            self.is_debugging = False
        
        return ExecutionResult(
            exit_code=self.runner.cpu._get_reg(0),
            stdout=self.runner.get_stdout(),
            stderr=self.runner.get_stderr(),
            instruction_count=instruction_count
        )
    
    def _debug_prompt(self) -> None:
        # 打印当前寄存器状态
        regs = self.runner.dump_registers()
        ip = regs.get('RIP', regs.get('EIP', 0))
        
        print(f"\n=== Debug Break at 0x{ip:08x} ===")
        print("Registers:")
        for name, value in list(regs.items())[:8]:
            print(f"  {name}: 0x{value:016x}")
        
        # 反汇编下一条指令
        disasm = self.runner.disassemble(ip, 1)
        if disasm:
            addr, name, length, operands = disasm[0]
            print(f"\nNext instruction: {name} at 0x{addr:08x}")
        
        print("================================\n")
