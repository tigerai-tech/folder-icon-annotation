from metaflow import FlowSpec, step, Parameter
from src.utils.config_holder import ConfigHolder


class ImageAnnotationTaskFlow(FlowSpec):
    """A flow that fetches news articles and sends them via Telegram."""
    env = Parameter('env',
                         help='选择环境',
                         default='',
                         type=str)

    def __init__(self):
        super().__init__()
        # 初始化配置
        self.init_configs()

    def init_configs(self):
        """初始化配置"""
        # 使用参数中的环境变量初始化配置
        ConfigHolder.init(env=self.env if self.env else None)
        print(f"配置已加载，当前环境: {ConfigHolder.get_env() or '默认'}")

    @step
    def start(self):
        """Fetch news articles from the MediaStack API."""
        print("任务开始........")
        
        # 获取配置示例
        tagger_config = ConfigHolder.get_config('tagger')
        tagger_model = ConfigHolder.get_value('tagger', 'providers.google_ai.model')
        print(f"使用标签模型: {tagger_model}")
        
        self.next(self.end)

    @step
    def end(self):
        """Send the news articles via Telegram."""
        print("执行成功========")


if __name__ == '__main__':
    ImageAnnotationTaskFlow()
