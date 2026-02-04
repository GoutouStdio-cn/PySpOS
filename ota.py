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
import logk
from pathlib import Path
import json
import urllib.request
import urllib.error
import hashlib

# 获取启动时间
boot_time = logk.get_boot_time()

# 槽位定义
SLOT_A = "slot_a"                           # 槽位A
SLOT_B = "slot_b"                           # 槽位B
CURRENT_SLOT_FILE = "current_slot"          # 当前槽位记录文件

# 更新包相关配置
OTA_PACKAGE_DIR = "ota"                     # 更新包存放目录
OTA_PACKAGE_NAME = "update.zip"             # 更新包文件名
VERSION_FILE = "version.txt"                # 版本信息文件名
UPDATE_LOG = "update_log.json"              # 更新日志文件名

# 云端更新服务器配置
OTA_SERVER_URL = "https://pyspos.us.ci/ota/" # 加速！！！
REMOTE_VERSION_FILE = "version.json"        # 云端版本信息文件名
REMOTE_UPDATE_FILE = "update.zip"           # 云端更新包文件名

# 必要的文件
REQUIRED_CORE_FILES = [
    "kernel.py", "main.py", "fs.py", "printk.py", "logk.py", 
    "recovery.py", "ota.py", "btcfg.py", "pyspos.py", "parse_spf.py",
    "version.txt", "current_slot"
]

# 必要的文件夹
REQUIRED_DIRS = ["apps", "etc", "spfapps"]

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
    max_retries = 3
    retry_interval = 1
    
    logk.printl("ota", "检查更新...", boot_time)
    
    methods = [
        ("requests", _fetch_with_requests),
        ("urllib", _fetch_with_urllib),
        ("curl", _fetch_with_curl),
    ]
    
    for method_name, method_func in methods:
        logk.printl("ota", f"使用 {method_name} 获取版本", boot_time)
        for attempt in range(max_retries):
            try:
                url = OTA_SERVER_URL + REMOTE_VERSION_FILE
                logk.printl("ota", f"连接服务器 ({attempt + 1}/{max_retries})", boot_time)
                
                start_time = time.time()
                data = method_func(url)
                end_time = time.time()
                
                response_size = len(str(data))
                logk.printl("ota", f"获取版本耗时: {end_time - start_time:.2f}秒, 大小: {response_size} bytes", boot_time)
                
                if data:
                    logk.printl("ota", f"{method_name} 获取成功", boot_time)
                    return data
            except Exception as e:
                logk.printl("ota", f"{method_name} 错误: {e}", boot_time)
                if attempt < max_retries - 1:
                    logk.printl("ota", f"{retry_interval}秒后重试", boot_time)
                    time.sleep(retry_interval)
                else:
                    logk.printl("ota", f"{method_name} 重试失败", boot_time)
                    break
    
    logk.printl("ota", "网络失败，使用本地版本", boot_time)
    local_version_file = os.path.join("docs", "ota", "version.json")
    if os.path.exists(local_version_file):
        try:
            with open(local_version_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logk.printl("ota", "加载本地版本成功", boot_time)
            return data
        except Exception as e:
            logk.printl("ota", f"加载本地版本失败: {e}", boot_time)
            return None
    else:
        logk.printl("ota", "本地版本文件不存在", boot_time)
        return None

# 使用requests库获取云端文件
def _fetch_with_requests(url: str) -> dict:
    try:
        import requests
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # 检查HTTP错误
        return response.json()
    except ImportError:
        raise Exception("requests库未安装")
    except Exception as e:
        raise

# 使用urllib获取云端文件
def _fetch_with_urllib(url: str) -> dict:
    import urllib.request
    with urllib.request.urlopen(url, timeout=5) as response:
        data = json.loads(response.read().decode('utf-8'))
        return data

# 使用curl命令获取云端文件
def _fetch_with_curl(url: str) -> dict:
    import subprocess
    import json
    result = subprocess.run(
        ['curl', '-s', url],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        raise Exception(f"curl命令失败: {result.stderr}")

# 下载更新包
def download_update_package(remote_url: str, local_path: str) -> bool:
    try:
        logk.printl("ota", f"下载更新包: {remote_url}", boot_time)
        
        downloaded = [0]
        start_time = time.time()
        
        def progress_hook(block_num, block_size, total_size):
            downloaded[0] = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded[0] / total_size) * 100)
                if int(percent) % 5 == 0:
                    print(f"\r下载进度: {percent:.1f}% ({downloaded[0]}/{total_size} bytes)", end='', flush=True)
        
        urllib.request.urlretrieve(remote_url, local_path, progress_hook)
        print()
        end_time = time.time()
        
        if os.path.exists(local_path):
            file_size = os.path.getsize(local_path)
            logk.printl("ota", f"下载完成,耗时: {end_time - start_time:.2f}秒, 大小: {file_size} bytes", boot_time)
        else:
            logk.printl("ota", f"下载完成,耗时: {end_time - start_time:.2f}秒", boot_time)
        
        return True
    except urllib.error.URLError as e:
        logk.printl("ota", f"下载失败: {e}", boot_time)
        return False
    except Exception as e:
        logk.printl("ota", f"下载错误: {e}", boot_time)
        return False

# 验证更新包完整性
def verify_update_package(package_path: str, expected_hash: str = None) -> bool:
    try:
        if expected_hash:
            logk.printl("ota", "验证更新包", boot_time)
            sha256_hash = hashlib.sha256()
            
            start_time = time.time()
            with open(package_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256_hash.update(chunk)
            calculated_hash = sha256_hash.hexdigest()
            end_time = time.time()
            
            logk.printl("ota", f"验证耗时: {end_time - start_time:.2f}秒", boot_time)
            
            if calculated_hash == expected_hash:
                logk.printl("ota", "验证通过", boot_time)
                return True
            else:
                logk.printl("ota", "校验和不匹配", boot_time)
                return False
        else:
            logk.printl("ota", "跳过验证", boot_time)
            return True
    except Exception as e:
        logk.printl("ota", f"验证失败: {e}", boot_time)
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
        logk.printl("ota", f"已设置当前槽位为: {slot}", boot_time)

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
        logk.printl("ota", "更新包版本与当前版本相同", boot_time)
        return False
    else:
        logk.printl("ota", "更新包版本低于当前版本", boot_time)
        return False

# 从云端检查更新
def check_cloud_update() -> dict:
    logk.printl("ota", "检查云端更新", boot_time)
    remote_info = fetch_remote_version()
    if not remote_info:
        logk.printl("ota", "获取云端版本失败", boot_time)
        return None
    
    current_ver = get_current_version()
    remote_ver = remote_info.get('version', '0.0.0')
    
    logk.printl("ota", f"当前: {current_ver}, 云端: {remote_ver}", boot_time)
    comparison = compare_versions(remote_ver, current_ver)
    
    if comparison > 0:
        logk.printl("ota", f"发现新版本: {remote_ver}", boot_time)
        return {
            'has_update': True,
            'current_version': current_ver,
            'remote_version': remote_ver,
            'download_url': remote_info.get('download_url', OTA_SERVER_URL + REMOTE_UPDATE_FILE),
            'sha256': remote_info.get('sha256'),
            'release_notes': remote_info.get('release_notes', '')
        }
    else:
        logk.printl("ota", "已是最新版本", boot_time)
        return {
            'has_update': False,
            'current_version': current_ver,
            'remote_version': remote_ver
        }

# 从云端下载并安装更新
def download_and_install_update() -> bool:
    update_info = check_cloud_update()
    if not update_info or not update_info['has_update']:
        logk.printl("ota", "无可用更新", boot_time)
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
    
    logk.printl("ota", f"当前槽位: {current} ({get_version(current)})", boot_time)
    logk.printl("ota", f"目标槽位: {other} ({get_version(other)})", boot_time)
    
    if not printk.confirm("是否回滚到上一个版本？"):
        return False
    
    if not switch_slot():
        logk.printl("ota", "回滚失败", boot_time)
        return False
    
    logk.printl("ota", "回滚成功，重启后生效", boot_time)
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
                logk.printl("ota", f"读取更新历史失败: {e}", boot_time)
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
    # 首先尝试从根目录的version.txt文件中读取版本信息
    root_version_file = "version.txt"
    if os.path.exists(root_version_file):
        try:
            with open(root_version_file, 'r') as f:
                return f.read().strip()
        except Exception as e:
            logk.printl("ota", f"读取根目录版本文件失败: {e}", boot_time)
    
    # 如果根目录版本文件不存在，尝试从当前槽位中读取
    slot_version = get_version(get_current_slot())
    if slot_version != "未知版本":
        return slot_version
    
    # 如果都失败了，返回一个默认版本
    return "3.0.0"

# 获取更新包版本
def get_update_version() -> str:
    package_path = os.path.join(OTA_PACKAGE_DIR, OTA_PACKAGE_NAME)
    try:
        with zipfile.ZipFile(package_path, 'r') as zip_ref:
            if VERSION_FILE in zip_ref.namelist():
                with zip_ref.open(VERSION_FILE) as f:
                    return f.read().decode().strip()
    except Exception as e:
        logk.printl("ota", f"读取更新包版本失败: {str(e)}", boot_time)
    return "未知版本"

# 将更新包安装到另一槽位
def install_update() -> bool:
    if not check_for_update():
        logk.printl("ota", "未找到更新包", boot_time)
        return False
    
    if not verify_update_compatibility():
        logk.printl("ota", "版本不兼容", boot_time)
        return False
    
    package_path = os.path.join(OTA_PACKAGE_DIR, OTA_PACKAGE_NAME)
    target_slot = get_other_slot()
    current_ver = get_current_version()
    update_ver = get_update_version()
    
    logk.printl("ota", f"安装更新: {current_ver} -> {update_ver}", boot_time)
    logk.printl("ota", f"目标槽位: {target_slot}", boot_time)
    
    start_time = time.time()
    
    if os.path.exists(target_slot):
        try:
            shutil.rmtree(target_slot)
            logk.printl("ota", f"清空槽位 {target_slot}", boot_time)
        except Exception as e:
            logk.printl("ota", f"清空槽位失败: {str(e)}", boot_time)
            return False
    
    os.makedirs(target_slot, exist_ok=True)
    
    try:
        with zipfile.ZipFile(package_path, 'r') as zip_ref:
            zip_ref.extractall(target_slot)
        logk.printl("ota", "解压完成", boot_time)
    except Exception as e:
        logk.printl("ota", f"解压失败: {str(e)}", boot_time)
        return False
    
    try:
        log_path = os.path.join(target_slot, UPDATE_LOG)
        log_data = {
            "from_version": current_ver,
            "to_version": update_ver,
            "install_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        logk.printl("ota", "日志已记录", boot_time)
    except Exception as e:
        logk.printl("ota", f"记录日志失败: {str(e)}", boot_time)
    
    end_time = time.time()
    logk.printl("ota", f"安装完成: {end_time - start_time:.2f}秒", boot_time)
    return True

# 切换槽位
def switch_slot() -> bool:
    current = get_current_slot()
    target = get_other_slot()
    
    # 检查目标槽位是否有效
    valid = True
    missing_items = []
    
    # 检查核心文件
    for file in REQUIRED_CORE_FILES:
        if not os.path.exists(os.path.join(target, file)):
            missing_items.append(file)
            valid = False
    
    # 检查必要的文件夹
    for directory in REQUIRED_DIRS:
        if not os.path.exists(os.path.join(target, directory)):
            missing_items.append(directory)
            valid = False
    
    if not valid:
        logk.printl("ota", f"槽位切换失败：目标槽位 {target} 缺少: {', '.join(missing_items)}", boot_time)
        return False
    
    set_current_slot(target)
    logk.printl("ota", f"槽位已切换至 {target}", boot_time)
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
            logk.printl("ota", "已删除更新包文件", boot_time)
        except Exception as e:
            logk.printl("ota", f"删除更新包失败: {str(e)}", boot_time)
    else:
        logk.printl("ota", "无更新包可清理", boot_time)

# 初始化OTA
def ota_init() -> bool:
    logk.printl("ota", "正在初始化OTA槽位结构...", boot_time)
    
    # 创建槽位文件夹
    slots = [SLOT_A, SLOT_B]
    for slot in slots:
        if not os.path.exists(slot):
            try:
                os.makedirs(slot)
                logk.printl("ota", f"创建槽位文件夹 {slot} 成功", boot_time)
            except Exception as e:
                logk.printl("ota", f"创建槽位文件夹 {slot} 失败: {str(e)}", boot_time)
                return False
        else:
            logk.printl("ota", f"槽位文件夹 {slot} 已存在", boot_time)
    
    # 确保当前槽位文件存在
    if not os.path.exists(CURRENT_SLOT_FILE):
        try:
            set_current_slot(SLOT_A)
            logk.printl("ota", "设置默认当前槽位为 SLOT_A", boot_time)
        except Exception as e:
            logk.printl("ota", f"设置当前槽位失败: {str(e)}", boot_time)
            return False
    else:
        current_slot = get_current_slot()
        logk.printl("ota", f"当前槽位已设置为: {current_slot}", boot_time)
    
    # 确保版本文件存在
    if not os.path.exists("version.txt"):
        try:
            with open("version.txt", "w") as f:
                f.write("3.0.0")
            logk.printl("ota", "创建版本文件 version.txt 成功", boot_time)
        except Exception as e:
            logk.printl("ota", f"创建版本文件失败: {str(e)}", boot_time)
            return False
    else:
        logk.printl("ota", "版本文件 version.txt 已存在", boot_time)
    
    # 复制根目录文件到当前槽位
    current_slot = get_current_slot()
    logk.printl("ota", f"正在将根目录文件复制到 {current_slot} 槽位...", boot_time)
    
    try:
        # 获取根目录所有文件和文件夹
        root_items = [item for item in os.listdir('.') if item not in [SLOT_A, SLOT_B, OTA_PACKAGE_DIR, '__pycache__', '.git']]
        
        for item in root_items:
            src_path = os.path.join('.', item)
            dest_path = os.path.join(current_slot, item)
            
            if os.path.isfile(src_path):
                shutil.copy2(src_path, dest_path)
            elif os.path.isdir(src_path):
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(src_path, dest_path)
        
        logk.printl("ota", f"根目录文件复制到 {current_slot} 槽位成功", boot_time)
    except Exception as e:
        logk.printl("ota", f"复制文件到槽位失败: {str(e)}", boot_time)
        return False
    
    logk.printl("ota", "OTA槽位结构初始化完成", boot_time)
    return True