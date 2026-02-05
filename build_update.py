import os
import zipfile
import hashlib
import json

# 创建PySpOS更新包
def create_zip_file():
    # 目标zip文件路径，放到docs/ota目录
    zip_path = os.path.join('docs', 'ota', 'PySpOS.zip')
    
    # 确保ota目录存在
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    
    # 要包含的文件和目录（从src目录，不包括docs）
    src_dir = 'src'
    include_items = ['apps', 'spfapps', 'btcfg.py', 'current_slot', 'fs.py', 'kernel.py', 'logk.py', 'main.py', 'ota.py', 'parse_spf.py', 'printk.py', 'pyspos.py', 'recovery.py', 'sync.py', 'version.txt', 'launcher.py']
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in include_items:
            item_path = os.path.join(src_dir, item)
            if os.path.isdir(item_path):
                # 处理目录
                for root, _, files in os.walk(item_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # 使用相对于src的路径作为zip中的路径
                        arcname = os.path.relpath(file_path, src_dir)
                        zipf.write(file_path, arcname)
            elif os.path.isfile(item_path):
                # 处理文件
                arcname = os.path.relpath(item_path, src_dir)
                zipf.write(item_path, arcname)
    
    return zip_path

# 计算文件的SHA256哈希值
def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        # 分块读取文件以处理大文件
        for byte_block in iter(lambda: f.read(4096), b''):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# 获取文件大小
def get_file_size(file_path):
    return os.path.getsize(file_path)

# 更新version.json文件中的实际数据
def update_version_json(zip_path, file_size, sha256):
    version_json_path = os.path.join('docs', 'ota', 'version.json')
    
    if os.path.exists(version_json_path):
        with open(version_json_path, 'r', encoding='utf-8') as f:
            version_data = json.load(f)
        
        # 更新实际数据
        version_data['sha256'] = sha256
        version_data['file_size'] = file_size
        version_data['download_url'] = 'PySpOS.zip'  # 使用本地文件路径
        
        # 写回文件
        with open(version_json_path, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, ensure_ascii=False, indent=2)
        
        print(f"已更新 {version_json_path} 中的实际数据")

# 主函数
def main():
    try:
        print("PySpOS 更新包构建工具")
        print("=" * 50)
        
        # 创建zip文件
        zip_path = create_zip_file()
        print(f"✓ 成功创建更新包: {zip_path}")
        
        # 获取文件大小
        file_size = get_file_size(zip_path)
        print(f"✓ 文件大小: {file_size} 字节")
        
        # 计算SHA256哈希值
        sha256 = calculate_sha256(zip_path)
        print(f"✓ SHA256: {sha256}")
        
        # 输出结果，方便复制
        print("\n--- 更新包信息 ---\n")
        print(f'文件大小: {file_size} 字节')
        print(f'SHA256哈希: {sha256}')
        print(f'下载路径: {os.path.basename(zip_path)}')
        
        # 更新version.json文件
        update_version_json(zip_path, file_size, sha256)
        
        print("\n✓ 构建完成\n")
        print("现在可以通过以下方式访问:")
        print("1. 本地测试: http://localhost:8000/ota/PySpOS.zip")
        print("2. 直接下载: ota/PySpOS.zip")
        print("\n在PySpOS中执行 'ota_update' 命令来安装更新")
        
    except Exception as e:
        print(f"✗ 错误: {e}")

if __name__ == "__main__":
    main()