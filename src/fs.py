# fs.py - 文件系统操作模块

import os
import shutil
import pathlib

# 当前工作目录
current_dir = os.getcwd()

# 列出当前目录下的文件和文件夹
def list_dir():
    return os.listdir(current_dir)

# 删除目录及其内容
def rm_tree(name):
    shutil.rmtree(name)

# 更改当前工作目录
def change_dir(path):
    global current_dir
    new_path = os.path.abspath(path)
    if os.path.isdir(new_path):
        current_dir = new_path

# 创建新目录
def create_dir(name):
    new_dir = os.path.join(current_dir, name)
    os.makedirs(new_dir, exist_ok=True)

# 创建新文件
def create_file(name, content=''):
    file_path = os.path.join(current_dir, name)
    with open(file_path, 'w') as f:
        f.write(content)

# 读取文件内容
def read_file(name):
    file_path = os.path.join(current_dir, name)
    if os.path.isfile(file_path):
        with open(file_path, 'r', encoding='UTF8') as f:
            return f.read()
    return None

# 写入内容到文件
def write_file(name, content):
    file_path = os.path.join(current_dir, name)
    with open(file_path, 'w') as f:
        f.write(content)

# 删除文件
def delete_file(name):
    file_path = os.path.join(current_dir, name)
    if os.path.isfile(file_path):
        os.remove(file_path)

# 复制文件
def copy_file(src, dest):
    src_path = os.path.join(current_dir, src)
    dest_path = os.path.join(current_dir, dest)
    if os.path.isfile(src_path):
        shutil.copy2(src_path, dest_path)

# 移动文件
def move_file(src, dest):
    src_path = os.path.join(current_dir, src)
    dest_path = os.path.join(current_dir, dest)
    if os.path.exists(src_path):
        shutil.move(src_path, dest_path)

# 获取文件信息
def get_file_info(name):
    file_path = os.path.join(current_dir, name)
    if os.path.exists(file_path):
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'is_dir': os.path.isdir(file_path)
        }
    return None