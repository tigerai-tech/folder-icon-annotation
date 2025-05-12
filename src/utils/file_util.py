import os

class FileUtil:
    """
    文件工具类，提供文件操作相关功能。
    重新设计为实例模式以支持Metaflow。
    """
    
    def __init__(self, project_root: str = None):
        """
        初始化文件工具类。
        
        :param project_root: 项目根目录的路径
        """
        self.project_root = project_root

    def get_project_root(self) -> str:
        """
        获取项目根目录。
        
        :return: 项目根目录的路径
        """
        if self.project_root is None:
            raise ValueError("项目根目录未设置")
        return self.project_root

    def read_string_from_file(self, relative_path: str) -> str:
        """
        从文件相对路径读出字符串值。

        :param relative_path: 文件的相对路径
        :return: 文件内容的字符串
        """
        file_path = os.path.join(self.get_project_root(), relative_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 {file_path} 不存在")

        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content

    def read_file_object(self, relative_path: str, mode: str = 'r'):
        """
        从文件相对路径读出文件对象。

        :param relative_path: 文件的相对路径
        :param mode: 打开文件的模式，默认为 'r'（读取文本模式）
        :return: 文件对象
        """
        file_path = os.path.join(self.get_project_root(), relative_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 {file_path} 不存在")

        return open(file_path, mode)
        
    def get_absolute_path(self, path: str) -> str:
        """
        获取绝对路径。
        如果给定的路径已经是绝对路径，则直接返回；
        否则，将其视为相对于项目根目录的路径。
        
        :param path: 文件或目录路径
        :return: 绝对路径
        """
        if os.path.isabs(path):
            return path
        return os.path.join(self.get_project_root(), path)


# 工厂函数，用于从Metaflow步骤中获取FileUtil实例
def get_file_util(project_root=None) -> FileUtil:
    """
    获取FileUtil实例。
    
    :param project_root: 项目根目录的路径
    :return: FileUtil实例
    """
    return FileUtil(project_root=project_root)
