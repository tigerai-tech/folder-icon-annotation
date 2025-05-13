from typing import Dict, Any, Optional

from src.utils.config_loader import ConfigLoader


class ConfigHolder:
    """
    配置持有者，用于加载配置并提供访问接口。
    重新设计为实例模式以支持Metaflow。
    """
    
    def __init__(self, env: str = None, config_dir: str = 'config'):
        """
        初始化配置持有者，加载所有配置。
        
        :param env: 环境名称，例如 'dev', 'prod'
        :param config_dir: 配置文件目录路径，默认为 'config'
        """
        self._env = env
        self._config_dir = config_dir
        self._configs = {}
        self._loader = ConfigLoader(config_dir=config_dir, env=env)
        
        # 加载所有配置
        self._configs = self._loader.load_all_configs()

    def get_config(self, config_name: str) -> Dict[str, Any]:
        """
        获取指定名称的配置。
        
        :param config_name: 配置名称，例如 'tagger'
        :return: 配置信息的字典
        """
        if config_name not in self._configs:
            # 尝试从加载器动态加载
            self._configs[config_name] = self._loader.get_config(config_name)
                
        return self._configs[config_name]

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

    def update_value(self, config_name: str, key: str, value: Any) -> bool:
        """
        更新指定配置的特定键值。
        
        :param config_name: 配置名称，例如 'tagger'
        :param key: 配置键，支持点号分隔的嵌套键，例如 'providers.google_ai.model'
        :param value: 要设置的新值
        :return: 是否成功更新
        """
        try:
            # 确保配置已加载
            config = self.get_config(config_name)
            
            # 处理嵌套键，例如 'providers.google_ai.model'
            if '.' in key:
                parts = key.split('.')
                current = config
                # 遍历到倒数第二级
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                # 设置最后一级的值
                current[parts[-1]] = value
            else:
                config[key] = value
                
            return True
        except Exception as e:
            print(f"更新配置失败: {str(e)}")
            return False

    def get_env(self) -> str:
        """
        获取当前环境。
        
        :return: 当前环境名称
        """
        return self._env

    def reload(self) -> None:
        """
        重新加载所有配置。
        """
        self._configs = self._loader.load_all_configs()


# 工厂函数，用于从Metaflow步骤中获取ConfigHolder实例
def get_config_holder(env=None, config_dir='config') -> ConfigHolder:
    """
    获取ConfigHolder实例。
    
    :param env: 环境名称，例如 'dev', 'prod'
    :param config_dir: 配置文件目录路径，默认为 'config'
    :return: ConfigHolder实例
    """
    return ConfigHolder(env=env, config_dir=config_dir)
