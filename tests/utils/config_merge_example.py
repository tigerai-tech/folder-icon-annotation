import os
import sys
import yaml
from copy import deepcopy

# 添加项目根目录到 Python 路径，以便能够导入 src 模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.utils.config_holder import ConfigHolder
from src.utils.file_util import FileUtil


def create_example_configs():
    """
    创建示例配置文件，用于演示配置合并功能
    """
    config_dir = FileUtil.get_project_root() + os.sep + 'config'
    
    # 创建默认配置文件
    example_conf = {
        'database': {
            'host': 'localhost',
            'port': 5432,
            'username': 'user',
            'password': 'default_password',
            'timeout': 30,
            'pool': {
                'max_size': 10,
                'min_size': 2
            }
        },
        'api': {
            'url': 'https://api.example.com',
            'version': 'v1',
            'timeout': 5
        },
        'logging': {
            'level': 'info',
            'file': 'app.log',
            'max_size': '10MB'
        }
    }
    
    # 创建环境特定配置文件 (只修改部分值)
    example_conf_dev = {
        'database': {
            'host': 'dev-db.example.com',
            'password': 'dev_password',
            'pool': {
                'max_size': 5
            }
        },
        'api': {
            'url': 'https://dev-api.example.com'
        },
        'logging': {
            'level': 'debug'
        }
    }
    
    # 保存配置文件
    with open(os.path.join(config_dir, 'example_conf.yaml'), 'w') as f:
        yaml.dump(example_conf, f)
    
    with open(os.path.join(config_dir, 'example_conf-dev.yaml'), 'w') as f:
        yaml.dump(example_conf_dev, f)
    
    print("示例配置文件已创建:")
    print(f"- {config_dir}/example_conf.yaml")
    print(f"- {config_dir}/example_conf-dev.yaml")


def demo_config_merging():
    """
    演示配置合并功能
    """
    # 显示默认环境配置
    print("\n默认环境配置:")
    print("-" * 50)
    ConfigHolder.init(env=None)
    example_config = ConfigHolder.get_config('example')
    
    print("数据库主机:", ConfigHolder.get_value('example', 'database.host'))
    print("数据库密码:", ConfigHolder.get_value('example', 'database.password'))
    print("数据库连接池最大大小:", ConfigHolder.get_value('example', 'database.pool.max_size'))
    print("API URL:", ConfigHolder.get_value('example', 'api.url'))
    print("日志级别:", ConfigHolder.get_value('example', 'logging.level'))
    
    # 显示开发环境配置 (合并后)
    print("\n开发环境配置 (与默认配置合并后):")
    print("-" * 50)
    ConfigHolder.init(env='dev')
    
    print("数据库主机:", ConfigHolder.get_value('example', 'database.host'))
    print("数据库密码:", ConfigHolder.get_value('example', 'database.password'))
    print("数据库端口:", ConfigHolder.get_value('example', 'database.port'))
    print("数据库连接池最大大小:", ConfigHolder.get_value('example', 'database.pool.max_size'))
    print("数据库连接池最小大小:", ConfigHolder.get_value('example', 'database.pool.min_size'))
    print("API URL:", ConfigHolder.get_value('example', 'api.url'))
    print("API 版本:", ConfigHolder.get_value('example', 'api.version'))
    print("日志级别:", ConfigHolder.get_value('example', 'logging.level'))
    print("日志文件:", ConfigHolder.get_value('example', 'logging.file'))


def cleanup_example_configs():
    """
    清理示例配置文件
    """
    config_dir = FileUtil.get_project_root() + os.sep + 'config'
    example_files = [
        os.path.join(config_dir, 'example_conf.yaml'),
        os.path.join(config_dir, 'example_conf-dev.yaml')
    ]
    
    for file_path in example_files:
        if os.path.exists(file_path):
            os.remove(file_path)
    
    print("\n示例配置文件已清理")


if __name__ == "__main__":
    print("配置合并演示程序")
    print("=" * 50)
    
    try:
        # 创建示例配置文件
        create_example_configs()
        
        # 演示配置合并
        demo_config_merging()
    except Exception as e:
        print(f"演示过程中发生错误: {e}")
    finally:
        # 清理示例配置文件
        cleanup_example_configs() 