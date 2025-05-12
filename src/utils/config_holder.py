from typing import Dict, Any, Optional

from src.utils.config_loader import ConfigLoader


class ConfigHolder:
    """
    配置持有者，用于程序启动时加载配置，并将配置存放在静态变量中，
    方便在程序的任何地方访问配置。
    """
    # 配置存储
    _configs: Dict[str, Dict[str, Any]] = {}
    # 当前环境. 有环境特有配置，使用特有的， 没有，使用不带环境后缀的默认配置文件
    _env: str = None
    # 配置是否已加载
    _initialized: bool = False
    # 配置加载器
    _loader: Optional[ConfigLoader] = None

    @classmethod
    def init(cls, env: str = None, config_dir: str = 'config'):
        """
        初始化配置持有者，加载所有配置。
        
        :param env: 环境名称，例如 'dev', 'prod'
        :param config_dir: 配置文件目录路径，默认为 'config'
        """
        cls._env = env
        # 设置配置加载器的环境
        ConfigLoader.set_env(env)
        # 创建配置加载器
        cls._loader = ConfigLoader(config_dir=config_dir, env=env)
        # 加载所有配置
        cls._configs = cls._loader.load_all_configs()
        cls._initialized = True
        return cls

    @classmethod
    def get_config(cls, config_name: str) -> Dict[str, Any]:
        """
        获取指定名称的配置。
        
        :param config_name: 配置名称，例如 'tagger'
        :return: 配置信息的字典
        """
        if not cls._initialized:
            raise RuntimeError("ConfigHolder 尚未初始化，请先调用 init 方法")
        
        if config_name not in cls._configs:
            # 尝试从加载器动态加载
            if cls._loader:
                cls._configs[config_name] = cls._loader.get_config(config_name)
            else:
                raise KeyError(f"未找到名为 {config_name} 的配置")
                
        return cls._configs[config_name]

    @classmethod
    def get_value(cls, config_name: str, key: str, default: Any = None) -> Any:
        """
        从指定的配置中获取特定键的值。
        
        :param config_name: 配置名称，例如 'tagger'
        :param key: 配置键，支持点号分隔的嵌套键，例如 'providers.google_ai.model'
        :param default: 如果键不存在时的默认值
        :return: 配置键的值
        """
        config = cls.get_config(config_name)
        
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

    @classmethod
    def get_env(cls) -> str:
        """
        获取当前环境。
        
        :return: 当前环境名称
        """
        if not cls._initialized:
            raise RuntimeError("ConfigHolder 尚未初始化，请先调用 init 方法")
        
        return cls._env

    @classmethod
    def reload(cls) -> None:
        """
        重新加载所有配置。
        """
        if not cls._initialized or not cls._loader:
            raise RuntimeError("ConfigHolder 尚未初始化，请先调用 init 方法")
        
        cls._configs = cls._loader.load_all_configs()
