#!/usr/bin/env python3
"""
调试build_update.py的实际运行过程
"""

import os
import json
from datetime import datetime

def simulate_build_update():
    """模拟build_update.py的运行过程"""
    
    print("=== 模拟build_update.py运行过程 ===")
    
    # 模拟用户输入
    current_version = "3.0.1-pre"  # 从src/version.txt读取
    print(f"当前版本: {current_version}")
    
    # 模拟用户选择"发布新版本"
    is_new_version = "1"
    print(f"用户选择: {is_new_version} (发布新版本)")
    
    # 模拟用户输入新版本号
    new_version = "3.1.0"
    print(f"用户输入新版本号: {new_version}")
    
    build_version = new_version
    print(f"构建版本: {build_version}")
    
    # 模拟创建zip文件（这里不实际创建）
    zip_filename = "PySpOS-3.1.0-20260205.zip"
    file_size = 37849
    sha256 = "64e8cd09f351fa37b18eb0c8adab2e8603262628bec6b6ec2487b449bd203298"
    
    print(f"模拟zip文件: {zip_filename}")
    print(f"文件大小: {file_size}")
    print(f"SHA256: {sha256}")
    
    # 现在模拟update_version_json函数
    print("\n=== 模拟update_version_json函数 ===")
    
    version_json_path = os.path.join('docs', 'ota', 'version.json')
    
    # 读取现有数据
    with open(version_json_path, 'r', encoding='utf-8') as f:
        version_data = json.load(f)
    
    print(f"读取到的version.json顶级版本: {version_data['version']}")
    print(f"changelog中的版本: {[entry['version'] for entry in version_data['changelog']]}")
    
    # 检查当前版本是否已在changelog中
    version_exists = False
    for entry in version_data['changelog']:
        print(f"检查: '{entry['version']}' == '{build_version}': {entry['version'] == build_version}")
        if entry['version'] == build_version:
            version_exists = True
            print(f"✓ 找到匹配版本: {build_version}")
            break
    
    if version_exists:
        print(f"\n结果: 版本 {build_version} 已存在于changelog中")
        print("应该显示: '✓ 版本 {build_version} 已存在于changelog中，已更新SHA256和文件大小'")
    else:
        print(f"\n结果: 版本 {build_version} 不在changelog中")
        print("应该显示: '当前版本 {build_version} 不在changelog中'")
        print("然后会要求用户输入更新内容")

def check_actual_build_update():
    """检查实际的build_update.py代码"""
    
    print("\n=== 检查build_update.py代码 ===")
    
    with open('build_update.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查版本检查逻辑
    if "if entry['version'] == version:" in content:
        print("✓ 版本检查逻辑正确: if entry['version'] == version:")
    else:
        print("✗ 版本检查逻辑有问题")
    
    # 检查build_version传递
    if "update_version_json(zip_filename, file_size, sha256, build_version, release_notes_text)" in content:
        print("✓ build_version传递正确")
    else:
        print("✗ build_version传递有问题")

if __name__ == "__main__":
    simulate_build_update()
    check_actual_build_update()