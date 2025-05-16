import asyncio
import os
import re
import shutil

import aiofiles
from aiofiles import os as aios
import numpy as np
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

from src.utils.config_holder import get_config_holder
from src.utils.file_util import get_file_util


def predict_image_vgg16(model, img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = preprocess_input(img_array)  # 使用VGG16专用预处理
    img_array = np.expand_dims(img_array, axis=0)
    return model.predict(img_array)[0][0]

def predict_image_effnet(model, img_path):
    img = image.load_img(img_path, target_size=(300, 300))  # 默认输入尺寸
    img_array = image.img_to_array(img)
    img_array = preprocess_input(img_array)  # EfficientNet专用预处理
    img_array = np.expand_dims(img_array, axis=0)
    return model.predict(img_array)[0][0]

def predict_image_resnet50(model, img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0  # 必须与训练相同的归一化
    img_array = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_array)
    return prediction[0][0]  # 返回概率值


async def async_copy(src, dst, chunk_size=128 * 1024):
    async with aiofiles.open(src, 'rb') as f_src:
        async with aiofiles.open(dst, 'wb') as f_dst:
            while True:
                chunk = await f_src.read(chunk_size)
                if not chunk:
                    break
                await f_dst.write(chunk)



class CNNFineTunedClassifier:
    """
    模型训练： https://github.com/jimmy-pink/colab-playground/blob/main/pre-trained/vgg16.ipynb
    """

    def __init__(self, config, fileutil):
        self.images_path = fileutil.project_root + config['crawler']['compressed_output_dir']
        models_path = fileutil.project_root + config['classifier']['models_path']
        self.model_name = config['classifier']['model_name']
        self.model = load_model(models_path + self.model_name)
        self.output_classified_path = fileutil.project_root + config['classifier']['classified_out_dir_positive']
        self.output_negative = fileutil.project_root  +  config['classifier']['classified_out_dir_negative']
        print(self.images_path, self.output_negative, self.output_classified_path)

        self.image_pattern = config['common']['image_pattern']
        def clear_directory(directory):
            if os.path.exists(directory):
                shutil.rmtree(directory)
            os.makedirs(directory)
        clear_directory(self.output_classified_path)
        clear_directory(self.output_negative)

    async def classify_single_file_async(self, item):
        item_path = os.path.join(self.images_path, item)

        match = re.search(self.image_pattern, item)
        if not match:
            return

        try:
            if "ResNet50" in self.model_name:
                prediction = predict_image_resnet50(self.model, item_path)
            elif "EfficientNetB" in self.model_name:
                prediction = predict_image_effnet(self.model, item_path)
            else:
                prediction = predict_image_vgg16(self.model, item_path)
        except Exception as e:
            print(f"Error parsing {item_path}: {e}")
            return
        print(f"pred: {prediction}")
        dst_dir = self.output_classified_path if prediction > 0.5 else self.output_negative
        dst = os.path.join(dst_dir, item)

        try:
            os.makedirs(dst_dir, exist_ok=True)  # 用同步版本更稳
            await async_copy(item_path, dst)
            print(f"{'✅' if prediction > 0.5 else '❌'} {item_path} → {dst} (Score: {prediction:.4f})")
        except Exception as e:
            print(f"❌ 拷贝失败: {item_path} -> {dst}: {e}")

    async def do_classify_async(self):
        tasks = [self.classify_single_file_async(item) for item in os.listdir(self.images_path)]
        await asyncio.gather(*tasks, return_exceptions=True)

    def do_classify(self):
        asyncio.run(self.do_classify_async())
        print(f"所有执行完毕")



if __name__ == "__main__":

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    print(project_root)
    file_util = get_file_util(project_root=project_root)
    config_holder = get_config_holder(env='dev', config_dir=project_root + os.sep + "config")
    CNNFineTunedClassifier(config_holder.get_config('application'), file_util).do_classify()
