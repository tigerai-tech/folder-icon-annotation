import argparse
import os

from prefect import flow, task
from rich.console import Console
from rich.prompt import Prompt, IntPrompt

from src.utils.config_holder import get_config_holder
from src.utils.file_util import get_file_util

# 初始化全局变量
console = Console()
project_root = os.path.abspath(os.path.dirname(__file__))
config_holder = None


def setup_environment(env: str = 'dev'):
    """
    设置环境和加载配置
    
    Args:
        env: 环境名称，如 'dev', 'prod'
    """
    global config_holder
    
    # 显示项目信息
    console.print(f"[bold green]文件夹图标标注工具[/bold green] - 环境: [cyan]{env}[/cyan]")
    
    # 设置项目根目录
    file_util = get_file_util(project_root=project_root)
    
    # 初始化配置
    config_holder = get_config_holder(env=env)
    
    console.print(f"配置已加载，当前环境: [cyan]{config_holder.get_env() or '默认'}[/cyan]")
    return config_holder


@task
def crawl_images(url: str):
    """
    从给定URL爬取图像
    
    Args:
        url: 要爬取的网站URL
    """
    console.print(f"[bold]正在从 {url} 爬取图像...[/bold]")
    # TODO: 实现爬虫逻辑
    console.print("[green]爬取完成![/green]")


@task
def classify_images():
    """分类图像任务"""
    console.print("[bold]正在分类图像...[/bold]")
    # TODO: 实现图像分类逻辑
    console.print("[green]分类完成![/green]")


@task
def tag_images():
    """为图像添加标签任务"""
    console.print("[bold]正在为图像添加标签...[/bold]")
    
    # TODO: 实现标签逻辑
    # 加载输入目录
    input_dir = config_holder.get_value('application', 'input_image_dir', 'data/input')
    console.print(f"输入目录: [cyan]{input_dir}[/cyan]")
    
    # 获取当前使用的标签器
    tagger_provider = config_holder.get_value('application', 'tagger.use_provider', 'clip')
    console.print(f"使用标签器: [cyan]{tagger_provider}[/cyan]")
    
    # TODO: 创建TagTask实例并处理图片
    
    console.print("[green]标签添加完成![/green]")


@flow(name="全流程处理")
def full_process_flow(url: str):
    """
    执行完整的图像处理流程：爬取、分类、标记
    
    Args:
        url: 要爬取的网站URL
    """
    crawl_images(url)
    classify_images()
    tag_images()
    console.print("[bold green]全流程处理完成![/bold green]")


@flow(name="图像分类流程")
def classification_flow():
    """执行图像分类流程"""
    classify_images()
    console.print("[bold green]图像分类完成![/bold green]")


@flow(name="图像标记流程")
def tagging_flow():
    """执行图像标记流程"""
    tag_images()
    console.print("[bold green]图像标记完成![/bold green]")


def print_config():
    """打印当前配置"""
    if not config_holder:
        console.print("[red]配置尚未加载[/red]")
        return
    
    console.print("\n[bold]当前配置:[/bold]")
    
    # 获取所有配置
    configs = {}
    
    # 获取应用配置
    try:
        app_config = config_holder.get_config('application')
        configs['application'] = app_config
    except:
        pass
    
    # 获取标签器配置
    try:
        tagger_config = config_holder.get_config('tagger')
        configs['tagger'] = tagger_config
    except:
        pass
    
    # 打印配置
    for space, config in configs.items():
        console.print(f"\n[bold cyan]{space}[/bold cyan] 配置:")
        if isinstance(config, dict):
            for key, value in config.items():
                console.print(f"  [yellow]{key}[/yellow]: {value}")
        else:
            console.print(f"  {config}")


def update_config():
    """交互式更新配置"""
    if not config_holder:
        console.print("[red]配置尚未加载[/red]")
        return
    
    # 显示可用的配置空间
    spaces = []
    try:
        config_holder.get_config('application')
        spaces.append('application')
    except:
        pass
    
    try:
        config_holder.get_config('tagger')
        spaces.append('tagger')
    except:
        pass
    
    if not spaces:
        console.print("[red]没有找到可用的配置空间[/red]")
        return
    
    # 用户选择配置空间
    console.print("\n[bold]可用的配置空间:[/bold]")
    for i, space in enumerate(spaces, 1):
        console.print(f"  {i}. [cyan]{space}[/cyan]")
    
    choice = IntPrompt.ask("请选择要修改的配置空间 [1-{}]".format(len(spaces)), choices=[str(i) for i in range(1, len(spaces)+1)])
    selected_space = spaces[choice-1]
    
    # 获取所选配置空间的内容
    config = config_holder.get_config(selected_space)
    console.print(f"\n[bold cyan]{selected_space}[/bold cyan] 当前配置:")
    for key, value in config.items():
        console.print(f"  [yellow]{key}[/yellow]: {value}")
    
    # 用户输入要修改的键
    key = Prompt.ask("\n请输入要修改的配置键")
    
    # 验证键是否存在
    current_value = None
    if '.' in key:
        # 处理嵌套键
        parts = key.split('.')
        current = config
        valid_key = True
        for part in parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                valid_key = False
                break
            current = current[part]
        
        if valid_key and parts[-1] in current:
            current_value = current[parts[-1]]
    else:
        if key in config:
            current_value = config[key]
    
    if current_value is not None:
        console.print(f"当前值: [yellow]{current_value}[/yellow]")
    else:
        console.print("[yellow]新建配置项[/yellow]")
    
    # 用户输入新值
    new_value = Prompt.ask("请输入新值")
    
    # 尝试转换值类型
    if new_value.lower() in ['true', 'false']:
        new_value = new_value.lower() == 'true'
    elif new_value.isdigit():
        new_value = int(new_value)
    elif new_value.replace('.', '', 1).isdigit() and new_value.count('.') == 1:
        new_value = float(new_value)
    
    # 更新配置
    if '.' in key:
        # 处理嵌套键
        parts = key.split('.')
        current = config
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = new_value
    else:
        config[key] = new_value
    
    console.print(f"[green]配置已更新: [yellow]{key}[/yellow] = {new_value}[/green]")


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
    setup_environment(env)
    
    while True:
        choice = show_menu()
        
        if choice == 1:
            url = Prompt.ask("请输入要爬取的网站URL")
            full_process_flow(url)
        elif choice == 2:
            classification_flow()
        elif choice == 3:
            tagging_flow()
        elif choice == 4:
            print_config()
        elif choice == 5:
            update_config()
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
    parser.add_argument('--interactive', action='store_true', help='交互式模式')
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    if args.interactive or (not args.url and not args.classify and not args.tag):
        # 默认或明确指定交互式模式
        interactive_mode(args.env)
    else:
        # 命令行模式
        setup_environment(args.env)
        
        if args.url:
            full_process_flow(args.url)
        elif args.classify:
            classification_flow()
        elif args.tag:
            tagging_flow()
