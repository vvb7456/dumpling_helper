"""
饺子助手

通过模拟键盘和鼠标操作，实现向多个指定QQ群自动发送同一张图片的功能。
脚本依赖于屏幕图像识别和底层键盘事件模拟。
"""
import os
import time
import tkinter as tk
from tkinter import filedialog

import pyautogui
import pydirectinput
import pyperclip

# --- 全局配置 ---
GROUP_FILE = "groups.txt"
pyautogui.PAUSE = 0.2
pydirectinput.PAUSE = 0.2


def load_groups_from_file(filename: str) -> list:
    """从文本文件中加载群列表，过滤空行。"""
    if not os.path.exists(filename):
        print(f"错误：群组文件 '{filename}' 不存在。")
        return []
    
    with open(filename, 'r', encoding='utf-8') as f:
        groups = [line.strip() for line in f if line.strip()]
        
    if not groups:
        print(f"错误：'{filename}' 文件为空或不包含有效群组。")
    return groups


def select_image() -> str:
    """弹出文件选择框让用户选择图片，并返回其绝对路径。"""
    root = tk.Tk()
    root.withdraw()
    print("正在打开文件选择窗口...")
    file_path = filedialog.askopenfilename(
        title="请选择要发送的图片",
        filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif"), ("All files", "*.*")]
    )
    return file_path


def find_and_click(image_file: str, confidence=0.85, timeout=10) -> bool:
    """在屏幕上查找指定图像并点击。"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            location = pyautogui.locateCenterOnScreen(image_file, confidence=confidence)
            if location:
                pyautogui.click(location)
                print(f"成功点击图像: '{image_file}'")
                return True
        except pyautogui.ImageNotFoundException:
            time.sleep(0.5)
        except Exception as e:
            print(f"查找图像时发生未知错误: {e}")
            return False
    
    print(f"错误：超时未能在屏幕上找到 '{image_file}'")
    return False


def main():
    """脚本主执行函数。"""
    # 1. 初始化和准备
    target_groups = load_groups_from_file(GROUP_FILE)
    if not target_groups:
        input("按 Enter 键退出...")
        return
    print(f"成功加载 {len(target_groups)} 个目标群聊。")

    image_path_to_send = select_image()
    if not image_path_to_send:
        print("未选择任何图片，脚本已退出。")
        return

    dir_path, file_name = os.path.split(image_path_to_send)
    print(f"已选择图片:\n  -> 文件夹: {dir_path}\n  -> 文件名: {file_name}")
    print("脚本将在5秒后开始，请确保QQ是当前活动窗口...")
    time.sleep(5)

    # 2. 循环发送
    for i, group_name in enumerate(target_groups, 1):
        print(f"\n--- 处理中 ({i}/{len(target_groups)}): {group_name} ---")

        # 2.1. 激活并清空搜索框
        pydirectinput.keyDown('ctrl')
        pydirectinput.press('f')
        pydirectinput.keyUp('ctrl')
        time.sleep(1.5)  # 关键延迟，等待UI焦点切换

        pydirectinput.keyDown('ctrl')
        pydirectinput.press('a')
        pydirectinput.keyUp('ctrl')
        pydirectinput.write(group_name, interval=0.1)
        time.sleep(2)

        # 2.2. 进入群聊
        pydirectinput.press('enter')
        time.sleep(2.5)

        # 2.3. 点击发送图片按钮
        if not find_and_click('image_button.png'):
            print(f"未能发送到群 '{group_name}'，跳过。")
            continue
        time.sleep(2)

        # 2.4. 在文件对话框中选择图片
        pyperclip.copy(dir_path)
        pydirectinput.keyDown('ctrl'); pydirectinput.press('l'); pydirectinput.keyUp('ctrl')
        pydirectinput.keyDown('ctrl'); pydirectinput.press('v'); pydirectinput.keyUp('ctrl')
        pydirectinput.press('enter')
        time.sleep(1)

        pydirectinput.keyDown('alt'); pydirectinput.press('n'); pydirectinput.keyUp('alt')
        pyperclip.copy(file_name)
        pydirectinput.keyDown('ctrl'); pydirectinput.press('v'); pydirectinput.keyUp('ctrl')
        pydirectinput.press('enter')
        time.sleep(1.5)

        # 2.5. 确认发送
        pydirectinput.press('enter')
        print(f"成功向 '{group_name}' 发送图片！")
        time.sleep(3)

    print("\n所有任务已完成！")


if __name__ == "__main__":
    main()