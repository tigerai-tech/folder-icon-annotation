import abc

class BaseTagger(metaclass=abc.ABCMeta):
    """
    基础标签类，定义了标签生成的基本方法。
    使用策略模式，子类将实现具体的标签生成策略。
    """

    def __init__(self, config: dict):
        """
        初始化基础标签类。

        :param config: 配置字典。外层是全局公共配置
        """
        self.config = config
        # tagger私有配置
        self.private_config = self.config['providers'][self.tagger_name()]

    def load_model(self):
        """
        加载模型。
        """
        pass

    @abc.abstractmethod
    def tagger_name(self):
        pass



    @abc.abstractmethod
    def tag_image(self, image_path: str) -> any:
        """
        为给定的图像路径生成标签。子类必须实现此方法。

        :param image_path: 图像文件的路径
        :return: 一个数组，包含图像标签
        """
        raise NotImplementedError("Method tag_image must be implemented")
    @abc.abstractmethod
    def postprocess_tags(self, raw_tags: any) -> list[str]:
        """
        标签后处理方法。子类可以重写此方法以实现特定的后处理逻辑。

        :param raw_tags: 生成的原始标签及其置信度
        :return: 后处理后的标签字典
        """
        # 默认的后处理逻辑，子类可以覆盖
        # 例如，可以在这里过滤掉置信度低于某个阈值的标签
        pass

    ## 最终方法调用
    def final_process_image_tagging(self, image_abs_path: str) -> list[str]:
        """
        图像预处理方法。子类可以重写此方法以实现特定的预处理逻辑。

        :param image_abs_path: 图像文件的路径
        :return: 预处理后的图像数据
        """
        final_tags = self.postprocess_tags(self.tag_image(image_abs_path))
        return self.__tags_filter(final_tags)

    def __tags_filter(self, input_arr: list[str]) -> list[str]:
        # 去掉不希望看到的tag word
        ignore_tag_text_list = self.config['ignore_tag_text']
        arr = []
        for item in input_arr:
            if item in ignore_tag_text_list:
                continue
            for it in ignore_tag_text_list:
                if item.__contains__(it):
                    item = item.replace(it, '')
            item = item.replace(' ', '')
            arr.append(item)
        arr = list(filter(None, map(lambda x: x.strip(), arr)))
        return arr

    # 向数组添加同义词, 暂不启用，防止图片名过长，在web端app搜索图片处添加同义词支持
    def __add_synonyms(self, arr, thesaurus):
        """
        检查数组 arr 中是否存在给定同义词列表中的任一单词，
        如果存在，则将同义词列表中的其他单词添加到 arr 中。
        :param arr: 初始单词数组
        :param thesaurus: 同义词列表
        :return: 修改后的单词数组
         # 示例用法
        thesaurus = [
            ["image", "picture", "photo"]
        ]
        arr = ["picture", "pink"]
        add_synonyms(arr, thesaurus)
        arr ==> ["picture", "pink", "photo", "image" ]
        """
        for synonyms in thesaurus:
            # 检查 arr 中是否存在同义词组中的任一单词
            if any(word in arr for word in synonyms):
                # 添加同义词组中其他单词到 arr 中
                for word in synonyms:
                    if word not in arr:
                        arr.append(word)
        return arr