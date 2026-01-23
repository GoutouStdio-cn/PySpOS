# getroot.py - 获取 ROOT 权限的应用程序
import api

api.api_info("准备获取 ROOT 权限...")
api.set_rootstate(True) # 设置root状态为真
api.api_ok("已获取 ROOT 权限！")
print("注意：此 APP 获取到的 ROOT 权限仅在当前运行期间有效，重启后将失效。")