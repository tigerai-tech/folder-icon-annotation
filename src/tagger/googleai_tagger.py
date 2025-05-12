from abc import ABC

from google import genai

from src.tagger.base_tagger import BaseTagger


class GoogleAITagger(BaseTagger, ABC):

    def __init__(self, config: dict):
        super().__init__(config)

    def tagger_name(self):
       return "google_ai"

    def tag_image(self, image_abs_path: str) -> any:
        api_key = self.private_config['api_key']
        model = self.private_config['model']
        prompt = self.config['common_tagging_prompt']
        client = genai.Client(api_key=api_key)
        my_file = client.files.upload(file=image_abs_path)

        response = client.models.generate_content(
            model=model,
            contents=[my_file, prompt],
        )
        res = response.text if response is not None else ""
        return res


    def postprocess_tags(self, raw_tags: any) -> list[str]:
        """
        标签后处理方法。子类可以重写此方法以实现特定的后处理逻辑。

        :param raw_tags: 生成的原始标签及其置信度
        :return: 后处理后的标签字典
        """
        # 默认的后处理逻辑，子类可以覆盖
        # 例如，可以在这里过滤掉置信度低于某个阈值的标签
        arr = raw_tags.split(",")
        return arr
