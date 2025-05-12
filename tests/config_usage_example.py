import os
import sys

from src.utils.file_util import FileUtil

# 添加项目根目录到 Python 路径，以便能够导入 src 模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.utils.config_holder import ConfigHolder


def demo_config_usage():
    """
    演示如何在不同模块中使用 ConfigHolder
    """
    # 在应用的任何地方，无需重新初始化，直接使用配置
    try:
        # 获取应用配置
        input_dir = ConfigHolder.get_value('application', 'input_img_folder_path')
        print(f"输入图片目录: {input_dir}")
        
        # 获取标签配置
        tagging_prompt = ConfigHolder.get_value('tagger', 'common_tagging_prompt')
        print(f"标签提示词: {tagging_prompt[:50]}..." if tagging_prompt else "标签提示词未配置")
        
        # 获取提供者配置
        provider = ConfigHolder.get_value('tagger', 'use_provider')
        key = ConfigHolder.get_value('tagger', 'providers.google_ai.api_key')
        print(f"使用提供者: {provider}, key: {key}")
        
        # 获取忽略标签
        ignore_tags = ConfigHolder.get_value('tagger', 'ignore_tag_text', [])
        print(f"忽略标签: {ignore_tags}")
        
    except RuntimeError as e:
        print(f"错误: {e}")
        print("请确保在使用 ConfigHolder 前，已在应用入口处调用 ConfigHolder.init()")


def initialize_config_for_standalone_script(env='dev'):
    """
    为独立脚本初始化配置
    在独立运行的脚本中，需要手动初始化配置。
    """
    FileUtil.set_project_root('/Users/jimmy/Workspace/AI/folder-icon-annotation')
    print(f"正在初始化配置，环境: {env}")
    ConfigHolder.init(env=env)
    print(f"配置已加载，当前环境: {ConfigHolder.get_env() or '默认'}")


if __name__ == "__main__":
    # 这是一个独立运行的脚本，需要手动初始化配置
    initialize_config_for_standalone_script(env='dev')

    # 演示如何使用配置
    demo_config_usage() 