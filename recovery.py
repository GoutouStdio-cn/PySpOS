#
#   recovery.py
#   简易的模拟恢复模式
#
#   2026/1/23 By GoutouStdio
#   @2022~2026 GoutouStdio. Open all rights.

import main
import kernel
import logk
import shutil
import os
import gc
import ota

# 主程序
def recovery_main(jumpinfo) -> str:
    kernel.screen_clear() # 清屏
    logk.printl("recovery", f"跳入到recovery, jumpinfo={jumpinfo}", main.boot_time)
    logk.printl("recovery", "欢迎使用PySpOS Recovery，输入help获取可用命令", main.boot_time)
    while 1:
        prompt = input("recovery> ")    # 我们recovery的提示符

        if prompt == "help":
            print("help     打印本帮助信息")
            print("erase    清除bootcfg和pycache信息")
            print("optimize 调用GC垃圾回收，让性能更高（实验性的）")
            print("ota_check  检查是否有可用的更新")
            print("ota_update 下载并安装更新")
            print("ota_status 查看OTA更新状态")
            print("ota_rollback 回滚到上一个版本")
            print("ota_clean  清理更新包文件")
            print("exit     退出Recovery\n")
        elif prompt == "erase":
            # 清除bootcfg和pycache信息
            if os.path.isdir("etc"):
                shutil.rmtree("etc")
            else:
                logk.printl("recovery", "etc文件夹已经清除了", main.boot_time)
            
            if os.path.isdir("__pycache__"):
                shutil.rmtree("__pycache__")
            else:
                logk.printl("recovery", "pycache文件夹已经清除了", main.boot_time)
            
            # 清除槽位内容
            slots = ["slot_a", "slot_b"]
            for slot in slots:
                if os.path.isdir(slot):
                    shutil.rmtree(slot)
                    logk.printl("recovery", f"槽位 {slot} 已清除", main.boot_time)
                else:
                    logk.printl("recovery", f"槽位 {slot} 已经清除了", main.boot_time)
            
            gc.collect()
            logk.printl("recovery", "清除完成，请重启程序\n", main.boot_time)
        elif prompt == "exit":
            break
        elif prompt == "optimize":
            # 触发GC垃圾回收2次
            gc.collect()
            gc.collect(2)
            logk.printl("recovery", "GC垃圾回收执行完毕！\n", main.boot_time)
        elif prompt == "ota_check":
            logk.printl("recovery", "检查是否有可用的更新...", main.boot_time)
            update_info = ota.check_cloud_update()
            if update_info:
                if update_info['has_update']:
                    print(f"发现新版本: {update_info['remote_version']}")
                    print(f"当前版本: {update_info['current_version']}")
                    print(f"更新内容: {update_info['release_notes']}")
                else:
                    print(f"当前已是最新版本: {update_info['current_version']}")
            print()
        elif prompt == "ota_update":
            logk.printl("recovery", "下载并安装更新...", main.boot_time)
            result = ota.download_and_install_update()
            if result:
                print("更新已成功安装，重启后生效\n")
            else:
                print("更新失败\n")
        elif prompt == "ota_status":
            logk.printl("recovery", "查看OTA更新状态...", main.boot_time)
            status = ota.get_ota_status()
            print(f"当前槽位: {status['current_slot']}")
            print(f"当前版本: {status['current_version']}")
            print(f"其他槽位: {status['other_slot']}")
            print(f"其他版本: {status['other_version']}")
            print(f"是否有更新: {'是' if status['has_update'] else '否'}")
            if status['update_version']:
                print(f"更新版本: {status['update_version']}")
            print()
        elif prompt == "ota_rollback":
            logk.printl("recovery", "回滚到上一个版本...", main.boot_time)
            result = ota.rollback_update()
            if result:
                print("回滚成功，重启后生效\n")
            else:
                print("回滚失败\n")
        elif prompt == "ota_clean":
            logk.printl("recovery", "清理更新包文件...", main.boot_time)
            ota.clean_update_package()
            print()
        else:
            print(f"找不到 {prompt} 命令")
    
    logk.printl("recovery", "Recovery已退出", main.boot_time)
    

