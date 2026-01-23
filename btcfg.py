import json
import sys
import os
import main
import kernel
import shutil
import printk
import hashlib

boot_config = r'%s/etc/bootcfg.json' % os.getcwd()

# 计算配置校验和（排除校验和自身）
def calculate_checksum(cfg):
    cfg_copy = cfg.copy()
    cfg_copy.pop('checksum', None)  # 移除旧校验和
    return hashlib.sha256(json.dumps(cfg_copy, sort_keys=True).encode()).hexdigest()

# 创建/修复 bootcfg 文件
def create_bootcfg():
    print("自动创建或修复 bootcfg 实用工具")
    print("本程序会自动写入：校验开启状态和root关闭状态")
    bootcfg = {} 
    if printk.confirm("\n 是否修复 bootcfg？"):
        if os.path.isdir("etc"):
            shutil.rmtree("etc")
            printk.ok("create_bootcfg: 损坏的引导文件已删除！")
        else:
            pass
    
        printk.info("create_bootcfg: 尝试创建新的引导文件夹")
        os.mkdir("etc")
        printk.ok("create_bootcfg: 引导文件夹创建成功！")
        bootcfg['locked'] = True
        bootcfg['rootstate'] = False
        # 计算并添加校验和
        bootcfg['checksum'] = calculate_checksum(bootcfg)
        printk.ok("create_bootcfg: 成功写入了默认配置！")
        save_bootcfg(bootcfg)
        printk.ok("create_bootcfg: 所有步骤全部完成！")

# 存储引导配置
def save_bootcfg(bootcfg):
    try:
        # 保存前更新校验和
        bootcfg['checksum'] = calculate_checksum(bootcfg)
        with open(boot_config, 'w') as f:
            json.dump(bootcfg, f)
    except Exception as e:
        printk.error(f"保存引导配置时出错: {e}")

# 读取引导配置
def get_bootcfg(cfg):
    return bootcfg[cfg]

# 设置引导配置为 True
def set_bootcfg_to_true(cfg):
    bootcfg[cfg] = True
    save_bootcfg(bootcfg)

# 设置引导配置为 False
def set_bootcfg_to_false(cfg):
    bootcfg[cfg] = False
    save_bootcfg(bootcfg)

# 通用设置引导配置值
def set_bootcfg_value(cfg, value):
    bootcfg[cfg] = value
    save_bootcfg(bootcfg)

# 加载引导配置
def load_bootcfg():
    global bootcfg
    try:
        with open(boot_config, 'r') as f:
            bootcfg = json.load(f)
        
        # 校验和验证
        current_checksum = bootcfg.get('checksum')
        if not current_checksum:
            print("\033[31m配置文件缺少校验和，可能被篡改！\033[0m")
            if printk.confirm("是否尝试新建一个新的 bootcfg（大概率可解决此问题）？"):
                create_bootcfg()
                print("操作成功完成\n")
            else:
                exit()
        
        expected_checksum = calculate_checksum(bootcfg)
        if current_checksum != expected_checksum:
            print("\033[31m配置文件校验失败，可能被篡改！\033[0m")
            if printk.confirm("是否尝试新建一个新的 bootcfg（大概率可解决此问题）？"):
                create_bootcfg()
                print("操作成功完成\n")
            else:
                exit()
        
        return bootcfg
    except FileNotFoundError as e:
        print("\033[31mbootcfg.json 已损坏\033[0m")
        if printk.confirm(f"系统启动失败（原因：{e}），是否尝试自动修复？"):
            create_bootcfg()
            print("操作成功完成\n")
        else:
            pass
        input("按下任意键关闭系统...")
        sys.exit(0)
    except json.JSONDecodeError as e:
        print("\033[31mbootcfg.json 已损坏\033[0m")
        if printk.confirm(f"系统启动失败（原因：{e}），是否尝试自动修复？"):
            create_bootcfg()
            print("操作成功完成\n")
        else:
            pass
        input("按下任意键关闭系统...")
        sys.exit(0)
    except ValueError as e:  # 捕获校验和错误
        print(f"\033[31m检测到非法修改启动配置，拒绝启动，请到售后处理。\033[0m")
        if printk.confirm("是否尝试自动修复系统？"):
            create_bootcfg()
            print("操作成功完成\n")
        else:
            pass
        input("按下任意键关闭系统...")
        sys.exit(0)