#   
#   ota.py
#   PySpOS OTA更新以及槽位模块
#
#   By GoutouStdio
#   @2022~2026 GoutouStdio. Open all rights.

import os
import shutil
import zipfile
import time
import printk
from pathlib import Path
import json

# 槽位定义
SLOT_A = "slot_a"
SLOT_B = "slot_b"
CURRENT_SLOT_FILE = "current_slot"  # 记录当前激活槽位的文件

# 更新包相关配置
OTA_PACKAGE_DIR = "ota"
OTA_PACKAGE_NAME = "update.zip"
VERSION_FILE = "version.txt"  # 版本文件
UPDATE_LOG = "update_log.json"  # 更新日志

# 获取当前的槽位
def get_current_slot() -> str:
    if os.path.exists(CURRENT_SLOT_FILE):
        with open(CURRENT_SLOT_FILE, 'r') as f:
            slot = f.read().strip()
            if slot in [SLOT_A, SLOT_B]:
                return slot
    # 如果没有，默认使用槽位_A
    set_current_slot(SLOT_A)
    return SLOT_A

# 设置激活的槽位
def set_current_slot(slot: str) -> None:
    if slot in [SLOT_A, SLOT_B]:
        with open(CURRENT_SLOT_FILE, 'w') as f:
            f.write(slot)
        printk.info(f"已设置当前槽位为: {slot}")

# 获取其他槽位
def get_other_slot() -> str:
    return SLOT_B if get_current_slot() == SLOT_A else SLOT_A

# 检查是否有更新（这个以后可以抓取云端内容检查）
def check_for_update() -> bool:
    package_path = os.path.join(OTA_PACKAGE_DIR, OTA_PACKAGE_NAME)
    return os.path.exists(package_path) and os.path.isfile(package_path)

# 获取指定槽位里的PySpOS版本
def get_version(slot: str) -> str:
    version_path = os.path.join(slot, VERSION_FILE)
    if os.path.exists(version_path):
        with open(version_path, 'r') as f:
            return f.read().strip()
    return "未知版本"

# 获取当前槽位里PySpOS版本
def get_current_version() -> str:
    return get_version(get_current_slot())

# 获取更新包版本
def get_update_version() -> str:
    package_path = os.path.join(OTA_PACKAGE_DIR, OTA_PACKAGE_NAME)
    try:
        with zipfile.ZipFile(package_path, 'r') as zip_ref:
            if VERSION_FILE in zip_ref.namelist():
                with zip_ref.open(VERSION_FILE) as f:
                    return f.read().decode().strip()
    except Exception as e:
        printk.error(f"读取更新包版本失败: {str(e)}")
    return "未知版本"

# 验证更新包（不太完善这个，这个以后改进）
def verify_update_compatibility() -> bool:
    current_ver = get_current_version()
    update_ver = get_update_version()
    
    # 对比版本号
    try:
        current_parts = list(map(int, current_ver.split('.')))
        update_parts = list(map(int, update_ver.split('.')))
        return update_parts > current_parts
    except Exception:
        printk.warn("版本格式不正确！")
        return False

# 将更新包安装到另一槽位
def install_update() -> bool:
    if not check_for_update():
        printk.error("未找到更新包")
        return False
    
    # 版本兼容性检查
    if not verify_update_compatibility():
        printk.error("更新包版本不兼容（低于或等于当前版本）")
        return False
    
    package_path = os.path.join(OTA_PACKAGE_DIR, OTA_PACKAGE_NAME)
    target_slot = get_other_slot()
    current_ver = get_current_version()
    update_ver = get_update_version()
    
    printk.info(f"开始安装更新: {current_ver} -> {update_ver}")
    printk.info(f"目标槽位: {target_slot}")
    
    # 清空目标槽位
    if os.path.exists(target_slot):
        try:
            shutil.rmtree(target_slot)
            printk.info(f"已清空目标槽位 {target_slot}")
        except Exception as e:
            printk.error(f"清空目标槽位失败: {str(e)}")
            return False
    
    # 创建目标槽位目录
    os.makedirs(target_slot, exist_ok=True)
    
    # 解压更新包到目标槽位
    try:
        with zipfile.ZipFile(package_path, 'r') as zip_ref:
            zip_ref.extractall(target_slot)
        printk.info("更新包解压完成")
    except Exception as e:
        printk.error(f"解压更新包失败: {str(e)}")
        return False
    
    # 记录更新日志
    try:
        log_path = os.path.join(target_slot, UPDATE_LOG)
        log_data = {
            "from_version": current_ver,
            "to_version": update_ver,
            "install_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        printk.info("更新日志已记录")
    except Exception as e:
        printk.warn(f"记录更新日志失败: {str(e)}")
    
    printk.ok(f"更新已成功安装到 {target_slot}")
    return True

# 切换槽位
def switch_slot() -> bool:
    current = get_current_slot()
    target = get_other_slot()
    
    # 检查目标槽位是否有效（至少包含核心文件）
    required_files = ["kernel.py", "main.py", "fs.py"]
    valid = True
    for file in required_files:
        if not os.path.exists(os.path.join(target, file)):
            printk.error(f"目标槽位 {target} 缺少核心文件: {file}")
            valid = False
    
    if not valid:
        printk.error("槽位切换失败：目标槽位不完整")
        return False
    
    set_current_slot(target)
    printk.ok(f"槽位已切换至 {target}，重启后生效")
    return True

# 获取OTA更新状态
def get_ota_status() -> dict:
    return {
        "current_slot": get_current_slot(),
        "current_version": get_current_version(),
        "other_slot": get_other_slot(),
        "other_version": get_version(get_other_slot()),
        "has_update": check_for_update(),
        "update_version": get_update_version() if check_for_update() else None
    }

# 清理更新包文件
def clean_update_package() -> None:
    package_path = os.path.join(OTA_PACKAGE_DIR, OTA_PACKAGE_NAME)
    if os.path.exists(package_path):
        try:
            os.remove(package_path)
            printk.ok("已删除更新包文件")
        except Exception as e:
            printk.error(f"删除更新包失败: {str(e)}")
    else:
        printk.info("无更新包可清理")