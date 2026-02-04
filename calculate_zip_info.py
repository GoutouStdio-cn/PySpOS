import os
import zipfile
import hashlib

# 创建一个临时的PySpOS.zip文件
def create_zip_file():
    zip_path = 'PySpOS.zip'
    
    # 要包含的文件和目录
    include_items = ['apps', 'docs', 'spfapps', 'README.md', 'btcfg.py', 'current_slot', 'fs.py', 'kernel.py', 'logk.py', 'main.py', 'ota.py', 'parse_spf.py', 'printk.py', 'pyspos.py', 'recovery.py', 'sync.py', 'version.txt']
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in include_items:
            if os.path.isdir(item):
                # 处理目录
                for root, _, files in os.walk(item):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, '.')
                        zipf.write(file_path, arcname)
            elif os.path.isfile(item):
                # 处理文件
                zipf.write(item)
    
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

# 主函数
def main():
    try:
        # 创建zip文件
        zip_path = create_zip_file()
        print(f"成功创建文件: {zip_path}")
        
        # 获取文件大小
        file_size = get_file_size(zip_path)
        print(f"文件大小: {file_size} 字节")
        
        # 计算SHA256哈希值
        sha256 = calculate_sha256(zip_path)
        print(f"SHA256: {sha256}")
        
        # 输出结果，方便复制
        print("\n复制以下内容到version.json")
        print(f'"file_size": {file_size},')
        print(f'"sha256": "{sha256}",')
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()