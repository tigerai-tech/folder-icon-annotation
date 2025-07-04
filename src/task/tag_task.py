import asyncio
import glob
import importlib
import json
import math
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Dict, List, Type

from src.tagger.base_tagger import BaseTagger
from src.tagger.googleai_tagger import GoogleAITagger
from src.utils.config_holder import get_config_holder
from src.utils.file_util import get_file_util

lock = threading.Lock()

def rename_images_with_tags(image_tags: Dict[str, List[str]], max_tags: int = 5) -> Dict[str, str]:
    """
    使用标签重命名图片文件。

    :param image_tags: 图片路径到标签列表的映射
    :param max_tags: 文件名中包含的最大标签数量
    :return: 原路径到新路径的映射
    """
    renamed_files = {}

    for image_path, tags in image_tags.items():
        if not tags:
            print(f"跳过没有标签的图片: {os.path.basename(image_path)}")
            continue

        # 获取目录和文件名
        dir_path = os.path.dirname(image_path)
        file_name = os.path.basename(image_path)
        file_ext = os.path.splitext(file_name)[1]

        # 选择前 N 个标签作为文件名
        limited_tags = tags[:max_tags]
        new_name = '_'.join(limited_tags) + file_ext
        new_path = os.path.join(dir_path, new_name)

        try:
            # 重命名文件
            os.rename(image_path, new_path)
            renamed_files[image_path] = new_path
            print(f"重命名: {file_name} -> {new_name}")
        except Exception as e:
            print(f"重命名失败 {file_name}: {str(e)}")

    return renamed_files


class TagTask:
    """
    标签任务类，负责扫描图片目录并使用指定的标签器为图片贴标签。
    """

    def __init__(self, file_util=None, config_holder=None, folder_path=None):
        """
        初始化标签任务类。
        """
        # 初始化工具实例
        self.file_util = file_util
        self.config_holder = config_holder
        
        # 加载配置
        self.tagger_config = self.config_holder.get_config('application')

        # 获取输入图片目录
        self.input_image_dir = self._get_input_image_dir(folder_path)
        
        # 映射标签器名称到标签器类
        self.taggers: Dict[str, Type[BaseTagger]] = self._load_taggers()
        
        # 获取当前使用的标签器名称
        self.current_tagger_name = self.config_holder.get_value("application", "tagger.use_provider", "google_ai")

    def _get_input_image_dir(self, input_folder_path) -> str:
        """
        获取输入图片目录的绝对路径。
        
        如果配置的路径以 '/' 开头，则视为绝对路径，否则视为相对于项目根目录的相对路径。
        
        :return: 输入图片目录的绝对路径
        """
        if input_folder_path is None:
            input_dir = self.config_holder.get_value("application", 'classifier.classified_out_dir_positive', 'data/input')
            input_folder_path = self.file_util.get_absolute_path(input_dir)
        return input_folder_path

    def _load_taggers(self) -> Dict[str, Type[BaseTagger]]:
        """
        加载 tagger 目录下的所有标签器类，并建立名称到类的映射。
        
        :return: 标签器名称到标签器类的映射字典
        """
        taggers = {}
        
        # 搜索 tagger 目录下的所有 Python 文件
        tagger_dir = os.path.join(os.path.dirname(__file__), "../", 'tagger')
        tagger_files = glob.glob(os.path.join(tagger_dir, '*_tagger.py'))
        
        for tagger_file in tagger_files:
            # 排除 base_tagger.py
            if 'base_tagger.py' in tagger_file:
                continue
                
            # 获取文件名（不含路径和扩展名）
            filename = os.path.basename(tagger_file).replace('.py', '')
            
            try:
                # 动态导入模块
                module_name = f"src.tagger.{filename}"
                module = importlib.import_module(module_name)
                
                # 查找模块中的 Tagger 类
                for attr_name in dir(module):
                    if attr_name.endswith('Tagger') and attr_name != 'BaseTagger':
                        tagger_class = getattr(module, attr_name)
                        
                        # 创建临时实例来获取标签器名称
                        try:
                            temp_instance = tagger_class(self.tagger_config)
                            tagger_name = temp_instance.tagger_name()
                            taggers[tagger_name] = tagger_class
                            print(f"已加载标签器: {tagger_name} ({attr_name})")
                        except Exception as e:
                            print(f"无法初始化标签器 {attr_name}: {str(e)}")
            
            except Exception as e:
                print(f"无法加载模块 {module_name}: {str(e)}")
        
        return taggers

    def _get_image_files(self) -> List[str]:
        """
        获取输入目录中的所有图片文件。
        
        :return: 图片文件的绝对路径列表
        """
        # 支持的图片文件扩展名
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.webp']
        image_files = []
        
        # 检查目录是否存在
        if not os.path.exists(self.input_image_dir):
            print(f"警告: 输入图片目录不存在: {self.input_image_dir}")
            return []
            
        # 搜索所有支持的图片文件
        for ext in image_extensions:
            pattern = os.path.join(self.input_image_dir, ext)
            image_files.extend(glob.glob(pattern))
            
        return image_files

    def create_tagger_instance(self, tagger_name: str = None) -> BaseTagger:
        """
        创建指定名称的标签器实例。
        
        :param tagger_name: 标签器名称，如果为 None，则使用当前配置的标签器
        :return: 标签器实例
        """
        if tagger_name is None:
            tagger_name = self.current_tagger_name
            
        if tagger_name not in self.taggers:
            raise ValueError(f"未知的标签器: {tagger_name}")
            
        tagger_class = self.taggers[tagger_name]
        return tagger_class(self.tagger_config)

    def tag_images(self) -> Dict[str, List[str]]:
        """
        为所有图片贴标签。
        
        :return: 图片路径到标签列表的映射
        """
        # 获取图片文件
        image_files = self._get_image_files()
        if not image_files:
            print("没有找到需要标记的图片文件")
            return {}
            
        print(f"找到 {len(image_files)} 个图片文件")
        

        image_tag_json_dict_path = file_util.project_root + self.tagger_config['tagger']['image_tag_dict_path']
        os.makedirs(os.path.dirname(image_tag_json_dict_path), exist_ok=True)
        # 检查文件是否存在，如果不存在则创建一个空的.json文件
        if not os.path.exists(image_tag_json_dict_path):
            with open(image_tag_json_dict_path, 'w') as file:
                json.dump({}, file)  # 创建一个空的JSON对象并写入文件

        # 为每个图片贴标签
        results = self.file_util.read_dict_from_json(image_tag_json_dict_path)

        def split_list_into_n_groups(lst, n):
            group_size = math.ceil(len(lst) / n)
            return [lst[i:i + group_size] for i in range(0, len(lst), group_size)]
        batch_size = 20
        def process_group(image_files, api_key):
            tagger =  GoogleAITagger(self.tagger_config, api_key)
            batch = {}
            for i, image_path in enumerate(image_files):
                print(f"处理图片 {i + 1}/{len(image_files)}: {os.path.basename(image_path)}")
                filename = os.path.basename(image_path)

                def save_batch():
                    with lock:
                        results.update(batch)
                        with open(image_tag_json_dict_path, 'w') as file:
                            json.dump(results, file, indent=4)
                        print(f"======保存一批{len(batch)}个数据======")
                        batch.clear()

                if filename in results and results[filename]:
                    if i+1 >= len(image_files):
                        save_batch()
                    continue
                try:
                    tags = tagger.final_process_image_tagging(image_path)
                    batch[filename] = tags
                    if len(batch) >= batch_size or i+1 >= len(image_files):
                        save_batch()
                    print(f"  标签: {', '.join(tags)}")
                except Exception as e:
                    print(f"  标记失败: {str(e)}")

        async def run():
            api_key_list = self.tagger_config['tagger']['providers']['google_ai']['api_key']
            groups = split_list_into_n_groups(image_files, len(api_key_list))
            with ThreadPoolExecutor(max_workers=len(api_key_list)) as executor:
                loop = asyncio.get_event_loop()
                tasks = [
                    loop.run_in_executor(
                        executor,
                        partial(process_group, group, api_key_list[i])
                    )
                    for i, group in enumerate(groups)
                ]
                await asyncio.gather(*tasks)

        asyncio.run(run())
        print(f"======任务结束，最终标记成功{len(results)}个图片")
        return results


if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    file_util = get_file_util(project_root=project_root)
    config_holder = get_config_holder(env='dev', config_dir=project_root + os.sep + "config")
    TagTask(config_holder=config_holder, file_util=file_util).tag_images()
