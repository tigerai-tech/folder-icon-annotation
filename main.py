import argparse
import os

from rich.console import Console
from rich.prompt import Prompt, IntPrompt

from src.task_list_flow import TaskListFlow

# 初始化全局变量
console = Console()
project_root = os.path.abspath(os.path.dirname(__file__))


def show_menu():
    """显示主菜单"""
    console.print("\n[bold]===== 文件夹图标标注工具 =====\n[/bold]")
    console.print("1. [cyan]全流程处理[/cyan] (爬取、分类、标记)")
    console.print("2. [cyan]图像分类[/cyan]")
    console.print("3. [cyan]图像标记[/cyan]")
    console.print("4. [cyan]查看配置[/cyan]")
    console.print("5. [cyan]修改配置[/cyan]")
    console.print("6. [red]退出[/red]")
    
    return IntPrompt.ask("\n请选择操作 [1-6]", choices=["1", "2", "3", "4", "5", "6"])


def interactive_mode(env: str):
    """
    交互式命令行模式
    
    Args:
        env: 环境名称
    """
    # 设置环境
    if env is None:
        env = 'dev'
    flow = TaskListFlow(env=env, project_root=project_root)
    while True:
        choice = show_menu()
        if choice == 1:
            flow.full_process_flow()
        elif choice == 2:
            flow.classify_images()
        elif choice == 3:
            gallery_path = Prompt.ask("请输入需要标签化的图片文件夹的全路径")
            flow.tag_images(gallery_path)
        elif choice == 4:
            strprint = flow.print_config()
            console.print(f"  {strprint}")
        elif choice == 5:
            console.print("暂不支持")
        elif choice == 6:
            console.print("[bold green]感谢使用，再见！[/bold green]")
            break


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='文件夹图标标注工具')
    parser.add_argument('--env', type=str, default='dev', help='运行环境 (dev, prod)')
    parser.add_argument('--url', type=str, help='要爬取的网站URL')
    parser.add_argument('--classify', action='store_true', help='只执行图像分类')
    parser.add_argument('--tag', action='store_true', help='只执行图像标记')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    interactive_mode(args.env)