#!/usr/bin/env python3
"""ELF 测试脚本"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from elf_loader import ELFRunner


def test_elf(elf_path: str, max_instructions: int = 100000) -> bool:
    print(f"\n=== 测试 {os.path.basename(elf_path)} ===\n")
    
    runner = ELFRunner(elf_path)
    
    if not runner.load():
        print("[FAIL] 加载失败")
        return False
    
    print(f"[OK] 加载成功")
    print(f"  入口点: 0x{runner.loader.entry_point:08x}")
    print(f"  架构: x86_64\n")
    
    print("开始执行...")
    start_time = time.time()
    
    try:
        result = runner.run(max_instructions=max_instructions)
        
        elapsed = time.time() - start_time
        
        print(f"\n=== 执行结果 ===")
        print(f"  退出码: {runner.cpu.exit_code if hasattr(runner.cpu, 'exit_code') else result}")
        print(f"  执行指令数: {runner.cpu.instruction_count}")
        print(f"  执行时间: {elapsed:.3f} 秒")
        
        stdout = b''.join(runner.syscall_emulator.stdout_buffer).decode('utf-8', errors='replace')
        if stdout:
            print(f"\n输出:\n{stdout}")
        
        return True
        
    except Exception as e:
        print(f"\n执行错误: {e}")
        stdout = b''.join(runner.syscall_emulator.stdout_buffer).decode('utf-8', errors='replace')
        if stdout:
            print(f"\n已输出:\n{stdout}")
        return False


def main():
    test_files = [
        'splibc/test_simple.elf',
        'splibc/test_splibc.elf',
    ]
    
    results = []
    for elf_path in test_files:
        if os.path.exists(elf_path):
            results.append((elf_path, test_elf(elf_path)))
        else:
            print(f"\n[SKIP] {elf_path} 不存在")
    
    print("\n" + "=" * 50)
    print("测试汇总:")
    for path, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {os.path.basename(path)}")


if __name__ == '__main__':
    main()
