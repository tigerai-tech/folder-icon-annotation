import abc

class BaseCrawler(metaclass=abc.ABCMeta):

    def __init__(self, config: dict, fileutil):
        """
        初始化基础标签类。

        :param config: 配置字典。外层是全局公共配置
        """
        self.config = config
        if 'crawler' in config and 'max_threads' in config['crawler']:
            self.max_threads = config['crawler']['max_threads']
        else:
            self.max_threads = 2
        self.fileutil = fileutil
        self.output_path = fileutil.project_root +  config['crawler']['raw_output_image_dir']

    @abc.abstractmethod
    def crawler_name(self):
        pass

    @abc.abstractmethod
    async def do_crawl(self):
        pass

    def crawl_then_save(self):
        pass