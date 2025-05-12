from .base_tagger import BaseTagger
from PIL import Image
import numpy as np
import tensorflow as tf

class PretrainedModelTagger(BaseTagger):
    def __init__(self, config: dict):
        super().__init__(config)
        self.model = self.load_model()

    def load_model(self):
        """
        加载预训练的图像特征模型。
        """
        model_path = self.config.get('model_path', 'path/to/your/model')
        return tf.keras.models.load_model(model_path)

    def preprocess_image(self, image_abs_path: str) -> np.ndarray:
        """
        图像预处理方法，将图像转换为模型输入所需的格式。
        """
        image = Image.open(image_abs_path).resize((224, 224))
        image_array = np.array(image) / 255.0  # 归一化
        image_array = np.expand_dims(image_array, axis=0)  # 添加批量维度
        return image_array

    def tag_image(self, image_path: str) -> list[str]:
        """
        为给定的图像路径生成标签。
        """
        image_array = self.preprocess_image(image_path)
        raw_tags = self.model.predict(image_array)[0]
        tags = self.postprocess_tags(raw_tags)
        # 处理
        return []

    def postprocess_tags(self, raw_tags: np.ndarray) -> dict:
        """
        标签后处理方法，将原始标签转换为字典格式。
        """
        class_labels = self.config.get('class_labels', [])
        tags = {class_labels[i]: float(raw_tags[i]) for i in range(len(raw_tags))}
        return tags
