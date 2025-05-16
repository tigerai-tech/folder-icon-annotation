


"""
1. search_url 查询分类 图片集
2. 逐个图片集下载图片列表  url=base_url/{集合名} 保存到输出目录
"""
import asyncio
import os
import re
from abc import ABC
from urllib.parse import urlparse,quote

import aiohttp
from crawl4ai import AsyncWebCrawler
from PIL import Image # 用于格式检测和压缩
from src.crawler.base_crawler import BaseCrawler
from src.utils.config_holder import get_config_holder
from src.utils.file_util import get_file_util

# 定义正则表达式
pattern = r'.*\.(jpg|jpeg|png|JPEG|JPG|PNG)$'
base_url = "https://getdrawings.com/"
search_url = f"{base_url}search/"

def compress_png_losslessly(image_path, output_path):
    try:
        with Image.open(image_path) as img:
            # optimize=True 会尝试减少文件大小
            # compress_level 控制压缩程度 (0-9)，9 为最大压缩，但可能更慢
            img.save(output_path, "PNG", optimize=True, compress_level=9)
        print(f"Losslessly compressed {image_path} to {output_path}")
    except Exception as e:
        print(f"Error compressing {image_path}: {e}")

def optimize_jpeg_losslessly(image_path, output_path):
    try:
        with Image.open(image_path) as img:
            # 对于JPEG，optimize=True 尝试优化霍夫曼表等
            # quality=100 意图是最高质量，但JPEG本质是有损的
            # progressive=True 可以使大图在加载时逐步显示，有时也能减小文件大小
            img.save(output_path, "JPEG", quality=100, optimize=True, progressive=True)
        print(f"Optimized {image_path} to {output_path}")
    except Exception as e:
        print(f"Error optimizing {image_path}: {e}")

class GetDrawingsCrawler(BaseCrawler, ABC):

    def __init__(self, config, fileutil, keyword="folder icon"):
        super().__init__(config, fileutil)
        self.icon_collection = None
        self.compressed_output_path = fileutil.project_root +  config['crawler']['compressed_output_dir']
        # 关键字， 非常关键 这是爬取图片分类的搜索关键词
        self.keyword = keyword

    def crawler_name(self):
        return "get_drawings"

    async def download_image(self, url, need_compress=False):
        # 清理URL以获取合适的文件名
        parsed_url = urlparse(url)
        file_name = os.path.basename(parsed_url.path)
        if not file_name:  # 如果无法从URL中获取有效文件名，则给出默认名称
            file_name = "default.jpg"
        file_path = os.path.join(self.output_path, file_name)
        compressed_file_path = os.path.join(self.compressed_output_path, file_name)
        # 异常处理
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        # 写入文件前检查输出路径是否存在以及是否可写
                        if not os.path.exists(self.output_path):
                            os.makedirs(self.output_path)
                        with open(file_path, 'wb') as f:
                            f.write(content)
                        if need_compress:
                            img_format = Image.open(file_path).format
                            if img_format == 'PNG':
                                # 选择一种PNG压缩方式
                                compress_png_losslessly(file_path, compressed_file_path)
                                # 或者使用ZopfliPNG (更强但更慢)
                                # compress_png_with_zopfli(original_file_path, compressed_file_path)
                            elif img_format == 'JPEG':
                                # 选择一种JPEG优化方式
                                optimize_jpeg_losslessly(file_path, compressed_file_path)
                                # 或者使用 mozjpeg_lossless_optimization
                                # optimize_jpeg_with_mozjpeg(original_file_path, compressed_file_path) # 注意函数签名和行为
                        print(f"Downloaded and compressed {url} to {compressed_file_path}")
                    else:
                        print(f"Failed to download {url}, status code: {response.status}")
        except Exception as e:
            print(f"Error downloading {url}: {e}")

    async def search_collection(self):
        async with AsyncWebCrawler(verbose=True) as crawler:
            # 爬取指定的URL
            result = await crawler.arun(
                url= search_url + quote(self.keyword),  # 替换为目标图片网站的URL
            )
            # 打印提取的内容或进一步处理结果
            self.icon_collection = []
            links = result.links['internal']
            if links is not None and len(links) > 0:
                for link in links:
                    if link is not None and link['href'] is not None and base_url in link['href'] and self.keyword in link['text'].lower():
                        self.icon_collection.append(link['href'])

            async def crawl_each_collection(url):
                # 爬取一个集合的图片链接
                col_ret = await crawler.arun(
                    url=url,  # 替换为目标图片网站的URL
                    css_selector="img",  # 使用CSS选择器定位所有图片元素
                    download_media=True,  # 启用媒体下载功能
                    media_dir="./images"  # 设置下载图片的目标目录
                )
                # 打印提取的内容或进一步处理结果
                images = col_ret.media['images']
                images_urls = []
                for image in images:
                    match = re.search(pattern, image['src'])
                    if match:
                        images_urls.append(image['src'])
                for image_url in images_urls:
                    await self.download_image(image_url)

            semaphore = asyncio.Semaphore(10)  # 最多同时运行 10 个任务

            async def limited_crawl(url):
                async with semaphore:
                    return await crawl_each_collection(url)

            tasks = [limited_crawl(url) for url in self.icon_collection]
            results = await asyncio.gather(*tasks)


    def do_crawl(self):
        asyncio.run(self.search_collection())



if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    print(project_root)
    file_util = get_file_util(project_root=project_root)
    config_holder = get_config_holder(env='dev', config_dir=project_root+os.sep+"config")
    GetDrawingsCrawler(config=config_holder.get_config("application"), fileutil= file_util, keyword='windows folder icon').do_crawl()

