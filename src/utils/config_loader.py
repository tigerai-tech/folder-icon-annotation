import os
import yaml
import re
from typing import Dict, Any
from copy import deepcopy


class ConfigLoader:
    """
    配置加载器，负责从配置文件加载配置信息。
    """
    
    def __init__(self, config_dir: str = 'config', env: str = None, project_root: str = None):
        """
        初始化 ConfigLoader，读取配置文件目录。

        :param config_dir: 配置文件目录的路径，默认为 'config'
        :param env: 运行环境，例如 'dev', 'prod'，默认为 None
        :param project_root: 项目根目录路径，如果提供，则配置目录相对于项目根目录
        """
        self.env = env
        self.__yaml_file_paths = []
        
        # 确定配置目录的绝对路径
        if project_root:
            self.config_dir = os.path.join(project_root, config_dir)
        else:
            # 如果没有提供项目根目录，则假设config_dir是绝对路径或相对于当前工作目录
            self.config_dir = config_dir
            
        self.configs = {}

    def _deep_merge(self, base_dict: Dict[str, Any], override_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        深度合并两个字典，override_dict 中的值会覆盖 base_dict 中的值。
        
        :param base_dict: 基础字典
        :param override_dict: 覆盖字典
        :return: 合并后的字典
        """
        result = deepcopy(base_dict)
        for key, value in override_dict.items():
            # 如果两个字典的值都是字典类型，则递归合并
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                # 否则直接覆盖
                result[key] = value
        return result

    def load_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        加载配置目录下的所有配置文件，并按照文件名的第一个单词进行分组。
        
        例如: 
        - tagger_conf.yaml 和 tagger_conf-dev.yaml 都会被归类到 'tagger' 下
        - application_config.yaml 会被归类到 'application' 下
        
        对于环境特定的配置，会将其与默认配置进行合并，环境配置的值会覆盖默认配置的值
        
        :return: 配置信息的字典，格式为 {config_name: config_dict}
        """
        # 保存默认配置和环境特定配置的映射
        default_configs = {}
        env_configs = {}
        
        # 获取配置目录下所有yaml文件
        for filename in os.listdir(self.config_dir):
            if not filename.endswith('.yaml'):
                continue

            # 提取文件名的第一个单词作为配置名
            config_name = filename.split('_')[0]
            
            # 检查是否包含环境后缀 (例如 -dev)
            match = re.search(r'-([\w]+)\.yaml$', filename)
            
            # 读取配置文件内容
            config_path = os.path.join(self.config_dir, filename)
            self.__yaml_file_paths.append(config_path)
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file) or {}
            
            if match:  # 是环境特定配置
                env_name = match.group(1)
                if self.env and env_name == self.env:
                    # 如果与当前环境匹配，保存到环境特定配置映射
                    env_configs[config_name] = config
            else:  # 是默认配置
                default_configs[config_name] = config
        
        # 合并默认配置和环境特定配置
        merged_configs = {}
        
        # 首先添加所有默认配置
        for config_name, config in default_configs.items():
            merged_configs[config_name] = config
        
        # 然后使用环境特定配置覆盖默认配置
        for config_name, env_config in env_configs.items():
            if config_name in merged_configs:
                # 如果存在默认配置，则合并
                merged_configs[config_name] = self._deep_merge(merged_configs[config_name], env_config)
            else:
                # 如果不存在默认配置，则直接使用环境特定配置
                merged_configs[config_name] = env_config
        
        self.configs = merged_configs
        return merged_configs

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
            config = yaml.safe_load(file) or {}

        return config

    def get_config(self, config_name: str) -> Dict[str, Any]:
        """
        获取已加载的配置信息。
        如果配置尚未加载，则尝试加载默认配置和环境特定配置，并将它们合并。

        :param config_name: 配置名称，例如 'tagger'
        :return: 配置信息的字典
        """
        if config_name in self.configs:
            return self.configs[config_name]
            
        # 尝试查找匹配的配置文件
        config_files = [f for f in os.listdir(self.config_dir) if f.startswith(f"{config_name}_")]
        if not config_files:
            raise FileNotFoundError(f"未找到名为 {config_name} 的配置文件")
        
        # 查找默认配置文件
        default_config = {}
        default_config_files = [f for f in config_files if not '-' in f]
        if default_config_files:
            default_config = self.load_config(default_config_files[0])
        
        # 如果有环境变量，查找并合并环境特定配置
        if self.env:
            env_config_files = [f for f in config_files if f.endswith(f"-{self.env}.yaml")]
            if env_config_files:
                env_config = self.load_config(env_config_files[0])
                # 合并默认配置和环境特定配置
                merged_config = self._deep_merge(default_config, env_config)
                self.configs[config_name] = merged_config
                return merged_config
        
        # 如果没有环境特定配置或没有指定环境，则使用默认配置
        self.configs[config_name] = default_config
        return default_config

    def get_value(self, config_name: str, key: str, default: Any = None) -> Any:
        """
        从指定的配置中获取特定键的值。

        :param config_name: 配置名称，例如 'tagger'
        :param key: 配置键，支持点号分隔的嵌套键，例如 'providers.google_ai.model'
        :param default: 如果键不存在时的默认值
        :return: 配置键的值
        """
        config = self.get_config(config_name)
        
        # 处理嵌套键，例如 'providers.google_ai.model'
        if '.' in key:
            parts = key.split('.')
            current = config
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return default
            return current
            
        return config.get(key, default)

    def print_all_configs(self) -> str:
        config_full_str = ""
        for fp in self.__yaml_file_paths:
            fn = os.path.basename(fp)
            config_full_str += f"\n\n================配置文件：{fn}==================\n"
            with open(fp, 'r') as file:
                config_full_str+=file.read()
        return config_full_str