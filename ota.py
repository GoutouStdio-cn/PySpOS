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
import urllib.request
import urllib.error
import hashlib

# 槽位定义
SLOT_A = "slot_a"
SLOT_B = "slot_b"
CURRENT_SLOT_FILE = "current_slot"

# 更新包相关配置
OTA_PACKAGE_DIR = "ota"
OTA_PACKAGE_NAME = "update.zip"
VERSION_FILE = "version.txt"
UPDATE_LOG = "update_log.json"

# 云端更新服务器配置
OTA_SERVER_URL = "https://goutoustdio-cn.github.io/PySpOS/ota/"
REMOTE_VERSION_FILE = "version.json"
REMOTE_UPDATE_FILE = "update.zip"

# 版本比较函数
def compare_versions(v1: str, v2: str) -> int:
    try:
        parts1 = list(map(int, v1.split('.')))
        parts2 = list(map(int, v2.split('.')))
        max_len = max(len(parts1), len(parts2))
        parts1.extend([0] * (max_len - len(parts1)))
        parts2.extend([0] * (max_len - len(parts2)))
        for p1, p2 in zip(parts1, parts2):
            if p1 > p2:
                return 1
            elif p1 < p2:
                return -1
        return 0
    except Exception:
        return 0

# 从云端获取最新版本信息
def fetch_remote_version() -> dict:
    try:
        url = OTA_SERVER_URL + REMOTE_VERSION_FILE
        printk.info(f"正在从云端获取版本信息: {url}")
        
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            printk.ok("成功获取云端版本信息")
            return data
    except urllib.error.URLError as e:
        printk.error(f"网络错误: {e}")
        return None
    except json.JSONDecodeError as e:
        printk.error(f"版本信息格式错误: {e}")
        return None
    except Exception as e:
        printk.error(f"获取云端版本失败: {e}")
        return None

# 下载更新包
def download_update_package(remote_url: str, local_path: str) -> bool:
    try:
        printk.info(f"开始下载更新包: {remote_url}")
        
        downloaded = [0]
        def progress_hook(block_num, block_size, total_size):
            downloaded[0] = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded[0] / total_size) * 100)
                print(f"\r下载进度: {percent:.1f}% ({downloaded[0]}/{total_size} bytes)", end='', flush=True)
        
        urllib.request.urlretrieve(remote_url, local_path, progress_hook)
        print()
        printk.ok("更新包下载完成")
        return True
    except urllib.error.URLError as e:
        printk.error(f"下载失败: {e}")
        return False
    except Exception as e:
        printk.error(f"下载过程中出错: {e}")
        return False

# 验证更新包完整性
def verify_update_package(package_path: str, expected_hash: str = None) -> bool:
    try:
        if expected_hash:
            printk.info("正在验证更新包完整性...")
            sha256_hash = hashlib.sha256()
            with open(package_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(chunk)
            calculated_hash = sha256_hash.hexdigest()
            
            if calculated_hash == expected_hash:
                printk.ok("更新包完整性验证通过")
                return True
            else:
                printk.error("更新包校验和不匹配")
                return False
        else:
            printk.warn("未提供校验和，跳过完整性验证")
            return True
    except Exception as e:
        printk.error(f"验证更新包失败: {e}")
        return False

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

# 验证更新包
def verify_update_compatibility() -> bool:
    current_ver = get_current_version()
    update_ver = get_update_version()
    
    comparison = compare_versions(update_ver, current_ver)
    if comparison > 0:
        return True
    elif comparison == 0:
        printk.warn("更新包版本与当前版本相同")
        return False
    else:
        printk.warn("更新包版本低于当前版本")
        return False

# 从云端检查更新
def check_cloud_update() -> dict:
    remote_info = fetch_remote_version()
    if not remote_info:
        return None
    
    current_ver = get_current_version()
    remote_ver = remote_info.get('version', '0.0.0')
    
    comparison = compare_versions(remote_ver, current_ver)
    
    if comparison > 0:
        printk.info(f"发现新版本: {remote_ver} (当前: {current_ver})")
        return {
            'has_update': True,
            'current_version': current_ver,
            'remote_version': remote_ver,
            'download_url': remote_info.get('download_url', OTA_SERVER_URL + REMOTE_UPDATE_FILE),
            'sha256': remote_info.get('sha256'),
            'release_notes': remote_info.get('release_notes', '')
        }
    else:
        printk.info(f"当前已是最新版本: {current_ver}")
        return {
            'has_update': False,
            'current_version': current_ver,
            'remote_version': remote_ver
        }

# 从云端下载并安装更新
def download_and_install_update() -> bool:
    update_info = check_cloud_update()
    if not update_info or not update_info['has_update']:
        printk.info("没有可用的更新")
        return False
    
    if not printk.confirm(f"是否下载并安装版本 {update_info['remote_version']}？"):
        return False
    
    os.makedirs(OTA_PACKAGE_DIR, exist_ok=True)
    package_path = os.path.join(OTA_PACKAGE_DIR, OTA_PACKAGE_NAME)
    
    if not download_update_package(update_info['download_url'], package_path):
        return False
    
    if not verify_update_package(package_path, update_info.get('sha256')):
        return False
    
    return install_update()

# 回滚到上一个版本
def rollback_update() -> bool:
    current = get_current_slot()
    other = get_other_slot()
    
    printk.info(f"当前槽位: {current} ({get_version(current)})")
    printk.info(f"目标槽位: {other} ({get_version(other)})")
    
    if not printk.confirm("是否回滚到上一个版本？"):
        return False
    
    if not switch_slot():
        printk.error("回滚失败")
        return False
    
    printk.ok("回滚成功，重启后生效")
    return True

# 查看更新历史
def view_update_history() -> None:
    for slot in [SLOT_A, SLOT_B]:
        log_path = os.path.join(slot, UPDATE_LOG)
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r') as f:
                    log_data = json.load(f)
                print(f"\n{slot} 更新历史:")
                print(f"  从版本: {log_data.get('from_version', '未知')}")
                print(f"  到版本: {log_data.get('to_version', '未知')}")
                print(f"  安装时间: {log_data.get('install_time', '未知')}")
            except Exception as e:
                printk.error(f"读取更新历史失败: {e}")
        else:
            print(f"\n{slot} 无更新历史")

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