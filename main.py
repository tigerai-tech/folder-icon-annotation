from metaflow import FlowSpec, step, Parameter
from src.utils.config_holder import get_config_holder
from src.utils.file_util import get_file_util
from src.tag_task import TagTask
import os


class ImageAnnotationTaskFlow(FlowSpec):
    """图像注释处理流程"""
    env = Parameter('env',
                    help='选择环境',
                    default='dev',
                    type=str)

    def __init__(self):
        super().__init__()
        self.project_root = None

    @step
    def start(self):
        """任务启动步骤"""
        print("任务开始........")
        # 设置项目根目录
        self.project_root = os.path.abspath(os.path.dirname(__file__))
        
        self.next(self.classification)

    @step
    def classification(self):
        """对图片进行分类处理"""
        print("开始图片分类...")
        # 这里实现图片分类的逻辑
        
        self.next(self.label_images)

    @step
    def label_images(self):
        """为图片添加标签"""
        print("开始为图片添加标签...")
        
        # 创建标签任务，传入环境和项目根目录
        tag_task = TagTask(env=self.env, project_root=self.project_root)
        
        # 为图片贴标签
        image_tags = tag_task.tag_images()
        
        # 记录处理结果
        self.image_count = len(image_tags)
        self.tagged_count = len([path for path, tags in image_tags.items() if tags])
        
        # 使用标签重命名图片
        renamed_files = tag_task.rename_images_with_tags(image_tags)
        self.renamed_count = len(renamed_files)
        
        print(f"图片标记完成: 共处理 {self.image_count} 张图片，成功标记 {self.tagged_count} 张，重命名 {self.renamed_count} 张")
        
        self.next(self.end)

    @step
    def end(self):
        """任务结束步骤"""
        print("执行成功========")
        print(f"处理结果统计:")
        print(f"- 标记图片数量: {self.tagged_count}/{self.image_count}")
        print(f"- 重命名图片数量: {self.renamed_count}")


if __name__ == '__main__':
    ImageAnnotationTaskFlow()
