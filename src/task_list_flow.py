from src.task.tag_task import TagTask, rename_images_with_tags
from src.utils.config_holder import get_config_holder
from src.utils.file_util import get_file_util


class TaskListFlow:

    def __init__(self, env=None, project_root=None):
        self.label_img_count = None
        self.label_img_expect_count = None
        self.env = env
        self.file_util = get_file_util(project_root=project_root)
        self.config_holder = get_config_holder(env=env)

    def full_process_flow(self, url: str):
        self.crawl_images(url)
        self.classify_images()
        self.tag_images()

    def crawl_images(self, url: str):
        """
        从给定URL爬取图像

        Args:
            url: 要爬取的网站URL
        """
        # TODO: 实现爬虫逻辑
        pass

    def classify_images(self):
        """分类图像任务"""
        # TODO: 实现图像分类逻辑
        pass

    def tag_images(self, image_folder_path=None):
        """为图像添加标签任务"""
        if image_folder_path is not None and len(image_folder_path.strip()) == 0:
            image_folder_path = None
        tag_task = TagTask(self.file_util, self.config_holder, folder_path=image_folder_path)
        # 为图片贴标签
        image_tags = tag_task.tag_images()

        # 记录处理结果
        self.label_img_expect_count = len(image_tags)
        # 使用标签重命名图片
        renamed_files = rename_images_with_tags(image_tags)
        self.label_img_count = len(renamed_files)

    def print_config(self):
        """打印当前配置"""
        if not self.config_holder:
            return

        # 获取所有配置
        configs = {}

        # 获取应用配置
        app_config = self.config_holder.get_config('application')
        configs['application'] = app_config

        # 获取标签器配置
        tagger_config = self.config_holder.get_config('tagger')
        configs['tagger'] = tagger_config

        def dict_to_properties(d, parent_key='', sep='.'):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):  # 如果值是字典，递归调用
                    items.extend(dict_to_properties(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)

        # 打印配置
        config_str = ""
        for space, config in configs.items():

            config_str += f'\n\n===================命名空间：{space}======================\n'
            if isinstance(config, dict):
                properties = dict_to_properties(config)
                # 打印结果
                for k, v in properties.items():
                    config_str += f"{k}: {v}\n"

        return config_str
