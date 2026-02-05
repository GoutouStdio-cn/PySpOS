#!/usr/bin/env python3
"""
测试用户输入处理
"""

import sys
import io

def test_user_input_processing():
    """测试用户输入处理"""
    
    print("=== 测试用户输入处理 ===")
    
    # 模拟不同的用户输入情况
    test_inputs = [
        "3.1.0",      # 正常输入
        " 3.1.0",     # 前面有空格
        "3.1.0 ",     # 后面有空格
        " 3.1.0 ",    # 前后都有空格
        "3.1.0\n",    # 有换行符
    ]
    
    for test_input in test_inputs:
        # 模拟input().strip()处理
        processed = test_input.strip()
        
        print(f"原始输入: '{repr(test_input)}'")
        print(f"处理后: '{repr(processed)}'")
        print(f"与'3.1.0'比较: {processed == '3.1.0'}")
        print()

def test_version_comparison():
    """测试版本比较"""
    
    print("=== 测试版本比较 ===")
    
    # version.json中的实际版本
    version_in_json = "3.1.0"
    
    # 可能的用户输入
    user_inputs = [
        "3.1.0",      # 正确
        "3.1.0 ",     # 有空格
        "3.1.0\n",    # 有换行
        "3.1.0\t",    # 有制表符
        "3.1.0 ",     # 有空格
    ]
    
    for user_input in user_inputs:
        processed = user_input.strip()
        matches = processed == version_in_json
        
        print(f"用户输入: '{repr(user_input)}'")
        print(f"处理后: '{repr(processed)}'")
        print(f"与JSON中的'{version_in_json}'比较: {matches}")
        if not matches:
            print(f"  ✗ 不匹配！")
        print()

if __name__ == "__main__":
    test_user_input_processing()
    test_version_comparison()