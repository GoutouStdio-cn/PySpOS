#!/usr/bin/env python3
"""
调试版本检查问题
"""

import json
import os

def debug_version_check():
    """调试版本检查逻辑"""
    
    # 读取version.json
    version_json_path = os.path.join('docs', 'ota', 'version.json')
    with open(version_json_path, 'r', encoding='utf-8') as f:
        version_data = json.load(f)
    
    print("=== 当前version.json内容 ===")
    print(f"顶级版本: {version_data['version']}")
    print(f"changelog中的版本:")
    for entry in version_data['changelog']:
        print(f"  - '{entry['version']}' (类型: {type(entry['version'])})")
    
    # 测试版本检查
    test_versions = ["3.1.0", "3.0.1-pre", "3.0.0"]
    
    print("\n=== 版本检查测试 ===")
    for test_version in test_versions:
        version_exists = False
        for entry in version_data['changelog']:
            if entry['version'] == test_version:
                version_exists = True
                break
        
        status = "✓ 存在" if version_exists else "✗ 不存在"
        print(f"版本 '{test_version}': {status}")
        
        # 详细比较
        if not version_exists:
            print(f"  详细比较:")
            for entry in version_data['changelog']:
                print(f"    '{entry['version']}' == '{test_version}': {entry['version'] == test_version}")
                print(f"    repr('{entry['version']}') == repr('{test_version}'): {repr(entry['version']) == repr(test_version)}")

if __name__ == "__main__":
    debug_version_check()