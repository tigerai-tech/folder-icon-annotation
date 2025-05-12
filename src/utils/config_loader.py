import os
import yaml
import re
from typing import Dict, Any

from src.utils.file_util import FileUtil


class ConfigLoader:
    runtime_env = ''

    def __init__(self, config_dir: str = 'config', env: str = None):
        """
        初始化 ConfigLoader，读取配置文件目录。

        :param config_dir: 配置文件目录的路径，默认为 'config'
        :param env: 运行环境，例如 'dev', 'prod'，默认为 None
        """
        self.config_dir = FileUtil.get_project_root() + os.sep + config_dir
        self.configs = {}
        self.env = env

    def load_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        加载配置目录下的所有配置文件，并按照文件名的第一个单词进行分组。
        
        例如: 
        - tagger_conf.yaml 和 tagger_conf-dev.yaml 都会被归类到 'tagger' 下
        - application_config.yaml 会被归类到 'application' 下
        
        如果设置了环境变量，优先使用对应环境的配置
        
        :return: 配置信息的字典，格式为 {config_name: config_dict}
        """
        config_map = {}
        
        # 获取配置目录下所有yaml文件
        for filename in os.listdir(self.config_dir):
            if filename.endswith('.yaml'):
                # 提取文件名的第一个单词作为配置名
                config_name = filename.split('_')[0]
                
                # 检查是否是特定环境的配置
                is_env_config = False
                env_name = None
                
                # 检查是否包含环境后缀 (例如 -dev)
                match = re.search(r'-([\w]+)\.yaml$', filename)
                if match:
                    is_env_config = True
                    env_name = match.group(1)
                
                # 读取配置文件内容
                config_path = os.path.join(self.config_dir, filename)
                with open(config_path, 'r') as file:
                    config = yaml.safe_load(file)
                
                # 如果是特定环境的配置，且与当前环境匹配，则覆盖默认配置
                if self.env and is_env_config and env_name == self.env:
                    config_map[config_name] = config
                # 如果不是特定环境的配置，且该配置名尚未存在于映射中，则添加
                elif not is_env_config and config_name not in config_map:
                    config_map[config_name] = config
        
        self.configs = config_map
        return config_map

    def load_config(self, config_file: str) -> Dict[str, Any]:
        """
        从指定的配置文件中加载配置信息。

        :param config_file: 配置文件的名称，例如 'base_config.yaml'
        :return: 配置信息的字典
        """
        config_path = os.path.join(self.config_dir, config_file)

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件 {config_path} 不存在")

        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        # 提取文件名的第一个单词作为配置名
        config_name = config_file.split('_')[0].split('.')[0]
        self.configs[config_name] = config
        return config

    def get_config(self, config_name: str) -> Dict[str, Any]:
        """
        获取已加载的配置信息。

        :param config_name: 配置名称，例如 'tagger'
        :return: 配置信息的字典
        """
        if config_name not in self.configs:
            # 尝试查找匹配的配置文件
            config_files = [f for f in os.listdir(self.config_dir) if f.startswith(f"{config_name}_")]
            if not config_files:
                raise FileNotFoundError(f"未找到名为 {config_name} 的配置文件")
            
            # 如果有环境变量，优先查找环境特定配置
            if self.env:
                env_config_files = [f for f in config_files if f.endswith(f"-{self.env}.yaml")]
                if env_config_files:
                    return self.load_config(env_config_files[0])
            
            # 否则使用默认配置
            default_config_files = [f for f in config_files if not '-' in f]
            if default_config_files:
                return self.load_config(default_config_files[0])
            
            # 如果默认配置不存在，使用任意匹配的配置
            return self.load_config(config_files[0])
        
        return self.configs[config_name]

    def get_value(self, config_name: str, key: str, default: Any = None) -> Any:
        """
        从指定的配置中获取特定键的值。

        :param config_name: 配置名称，例如 'tagger'
        :param key: 配置键
        :param default: 如果键不存在时的默认值
        :return: 配置键的值
        """
        config = self.get_config(config_name)
        return config.get(key, default)

    @classmethod
    def set_env(cls, env: str):
        """
        设置当前运行环境

        :param env: 环境名称，例如 'dev', 'prod'
        """
        cls.runtime_env = env


# 示例用法
if __name__ == "__main__":
    # 设置环境为开发环境
    ConfigLoader.set_env('dev')
    
    # 初始化配置加载器，指定环境
    config_loader = ConfigLoader(env=ConfigLoader.runtime_env)
    
    # 加载所有配置
    all_configs = config_loader.load_all_configs()
    print("All configs:", list(all_configs.keys()))
    
    # 获取特定配置
    tagger_config = config_loader.get_config('tagger')
    print("Tagger Config:", tagger_config.keys())
    
    # 获取应用配置中特定键的值
    app_config = config_loader.get_config('application')
    tagger_provider = config_loader.get_value('tagger', 'providers.google_ai.model')
    print("Tagger Provider Model:", tagger_provider)
