import os

class FileUtil:
    # 项目根目录静态变量
    project_root = None

    @staticmethod
    def get_project_root():
        return FileUtil.project_root

    @staticmethod
    def set_project_root(project_root: str):
        """
        设置项目根目录。

        :param project_root: 项目根目录的路径
        """
        FileUtil.project_root = project_root

    @staticmethod
    def read_string_from_file(relative_path: str) -> str:
        """
        从文件相对路径读出字符串值。

        :param relative_path: 文件的相对路径
        :return: 文件内容的字符串
        """
        if FileUtil.project_root is None:
            raise ValueError("项目根目录未设置")

        file_path = os.path.join(FileUtil.project_root, relative_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 {file_path} 不存在")

        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content

    @staticmethod
    def read_file_object(relative_path: str, mode: str = 'r'):
        """
        从文件相对路径读出文件对象。

        :param relative_path: 文件的相对路径
        :param mode: 打开文件的模式，默认为 'r'（读取文本模式）
        :return: 文件对象
        """
        if FileUtil.project_root is None:
            raise ValueError("项目根目录未设置")

        file_path = os.path.join(FileUtil.project_root, relative_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 {file_path} 不存在")

        return open(file_path, mode)
