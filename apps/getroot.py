# getroot.py - 获取 ROOT 权限的应用程序
import api

# 主函数
def main():
    if api.get_rootstate() or api.get_rootstate_bcfg():
        api.api_warn("当前已处于 ROOT 权限状态，无需重复获取。")
    else:
        api.api_info("准备获取 ROOT 权限...")
        if api.set_rootstate(True): # 设置root状态为真
            api.api_ok("已获取 ROOT 权限！")
        else:
            api.api_error("获取 ROOT 权限失败！")
        print("操作成功完成。")
    print("操作成功完成。")

# 最重要的
if __name__ == "__exec__":
    try:
        main()
    except Exception as e:
        print(f"程序运行出错：{str(e)}")
else:
    raise SystemError("请不要直接运行本程序")