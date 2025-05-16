import os
from abc import ABC
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotImageClassification
from transformers import BlipProcessor, BlipForConditionalGeneration

from src.tagger.base_tagger import BaseTagger


class ClipAttributeAnalyzer:
    """
    类用于使用CLIP模型分析图像的各种属性，如主题、颜色、形状等。
    """

    def __init__(self, model_name="openai/clip-vit-base-patch32",
                 blip_model_name="Salesforce/blip-image-captioning-base"):
        """
        初始化CLIP属性分析器。
        
        Args:
            model_name (str): CLIP模型的Hugging Face模型名称
            blip_model_name (str): BLIP模型的Hugging Face模型名称
        """
        print(f"加载CLIP模型: {model_name}")
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = AutoModelForZeroShotImageClassification.from_pretrained(model_name)

        # 初始化BLIP模型（懒加载，只在需要时加载）
        self.blip_processor = None
        self.blip_model = None
        self.blip_model_name = blip_model_name

        # 定义各种属性的候选标签
        self.attribute_candidates = {
            "purpose": [
                "document", "file", "application",
                "music", "video", "photo", "image", "text",
                "note", "database", "workspace", "settings",
                "book", "download", "cloud", "lock", "user",
                "mail", "message", "calendar", "contacts", "chat",
                "archive", "code", "folder", "game", "map",
                "project", "script", "sound", "backup", "template"
            ],
            "color": [
                "blue", "red", "green", "yellow", "orange",
                "purple", "pink", "black", "white", "gray",
                "brown", "teal", "navy", "gold", "silver",
                "cyan", "magenta", "lime", "olive", "maroon",
                "coral", "crimson", "indigo", "violet", "beige",
                "turquoise", "amber", "azure", "lavender", "ivory"
            ],
            "shape": [
                "rounded", "curved", "sharp", "rectangular",
                "square", "circular", "oval", "triangular", "hexagonal",
                "star", "irregular", "flat", "3D", "glossy", "matte",
                "geometric", "abstract", "symmetric", "asymmetric", "diamond",
                "heart", "wave", "spiral", "arrow", "shield",
                "cylindrical", "spherical", "floral", "organic", "crystal"
            ],
            # 扩展了主题候选列表，包含更多样的主题
            "subject": [
                # 原有的文件夹类图标主题
                "folder", "document", "music", "video", "photo",
                "file", "data", "app", "settings", "cloud",
                "user", "security", "download", "upload", "trash",
                "book", "message", "mail", "calendar", "contact",

                # 添加自然物体
                "flower", "rose", "tree", "leaf", "plant",
                "mountain", "sun", "moon", "star", "cloud",
                "water", "fire", "earth", "air", "light",

                # 添加动物
                "dog", "cat", "bird", "fish", "butterfly",
                "lion", "tiger", "elephant", "horse", "whale",

                # 添加食物
                "apple", "coffee", "cake", "pizza", "drink",
                "fruit", "vegetable", "bread", "candy", "juice",

                # 添加物品
                "phone", "computer", "camera", "pen", "key",
                "lock", "clock", "car", "house", "door",
                "window", "chair", "table", "lamp", "mirror",

                # 添加抽象图标
                "heart", "star", "arrow", "circle", "square",
                "triangle", "diamond", "hexagon", "spiral", "wave",

                # 添加符号和标志
                "check", "warning", "error", "info", "question",
                "plus", "minus", "play", "pause", "stop",
                "sync", "refresh", "search", "home", "menu"
            ]
        }

        # 定义每种属性的提示词
        self.attribute_prompts = {
            "subject": "a folder icon with a {} as the main subject",
            "color": "a folder icon with {} as the main color",
            "shape": "a folder icon with a {} shape design",
            "purpose": "a folder icon used for storing {}"
        }

        # 颜色组合提示词，用于检测双色或多色图标
        self.color_combination_prompts = [
            "a folder icon with {} and {} as the main colors",
            "a folder icon combining {} and {} colors",
            "a bi-color folder icon with {} and {}"
        ]

        # 定义通用主题提示
        self.general_subject_prompt = "This image contains {}"

    def _ensure_blip_model(self):
        """确保BLIP模型已加载"""
        if self.blip_processor is None or self.blip_model is None:
            print(f"加载BLIP模型: {self.blip_model_name}")
            self.blip_processor = BlipProcessor.from_pretrained(self.blip_model_name)
            self.blip_model = BlipForConditionalGeneration.from_pretrained(self.blip_model_name)

    def detect_text_with_blip(self, image):
        """
        使用BLIP模型从图像中检测文本内容。
        
        Args:
            image: PIL图像对象
            
        Returns:
            检测到的文本列表
        """
        try:
            # 确保BLIP模型已加载
            self._ensure_blip_model()

            # 处理图像
            inputs = self.blip_processor(image, return_tensors="pt")

            # 生成描述
            with torch.no_grad():
                # 使用不同的提示来引导模型关注文本
                text_prompts = [
                    "a folder icon with text that says",
                    "the text on this icon reads",
                    "this icon contains the text"
                ]

                results = []
                for prompt in text_prompts:
                    # 添加提示词引导模型
                    inputs["input_ids"] = self.blip_processor(
                        images=image,
                        text=prompt,
                        return_tensors="pt"
                    ).input_ids

                    # 生成文本
                    outputs = self.blip_model.generate(
                        **inputs,
                        max_length=30,
                        num_beams=5,
                        early_stopping=True
                    )
                    generated_text = self.blip_processor.decode(outputs[0], skip_special_tokens=True)

                    # 处理生成的文本
                    # 移除提示词部分
                    if prompt in generated_text:
                        clean_text = generated_text.replace(prompt, "").strip()
                    else:
                        clean_text = generated_text.strip()

                    # 检查是否有有效文本
                    if clean_text and len(clean_text) > 1:
                        results.append(clean_text)

            # 处理结果以提取实际文本
            if results:
                # 分析结果，选择最可能的文本
                # 简单起见，我们这里取最长的结果
                best_result = max(results, key=len)

                # 清理文本，去除常见的说明性语句
                clean_phrases = [
                    "the text", "that says", "which says",
                    "containing text", "with the text",
                    "displaying", "showing", "reads"
                ]

                for phrase in clean_phrases:
                    best_result = best_result.replace(phrase, "").strip()

                # 如果文本包含引号，尝试提取引号中的内容
                if '"' in best_result:
                    quoted_parts = best_result.split('"')
                    if len(quoted_parts) >= 3:  # 至少有一对引号
                        best_result = quoted_parts[1]  # 取第一对引号中的内容

                return [best_result] if best_result else []

            return []

        except Exception as e:
            print(f"使用BLIP检测文本失败: {e}")
            return []

    def analyze_attribute(self, image, attribute_type):
        """
        分析图像的特定属性。
        
        Args:
            image: PIL图像对象
            attribute_type: 属性类型("subject", "color", "shape", "purpose")
            
        Returns:
            检测到的属性值列表
        """
        if attribute_type == "text":
            # 特殊处理: 使用BLIP进行文本检测
            return self.detect_text_with_blip(image)

        if attribute_type not in self.attribute_candidates:
            print(f"未知的属性类型: {attribute_type}，默认使用'subject'")
            attribute_type = "subject"

        candidate_labels = self.attribute_candidates[attribute_type]
        prompt_template = self.attribute_prompts[attribute_type]

        # 格式化候选文本
        candidate_texts = [prompt_template.format(label) for label in candidate_labels]

        # 准备CLIP模型的输入
        inputs = self.processor(
            text=candidate_texts,
            images=image,
            return_tensors="pt",
            padding=True
        )

        # 运行推理
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)

        # 获取前3个预测结果
        top_count = min(3, len(candidate_labels))
        top_probs, top_indices = torch.topk(probs[0], k=top_count)

        # 格式化结果
        results = []
        for i, (prob, idx) in enumerate(zip(top_probs, top_indices)):
            if prob > 0.1:  # 只包含概率显著的结果
                results.append(candidate_labels[idx])

        return results

    def analyze_general_subject(self, image):
        """
        使用更通用的方法分析图像中的主题。
        这允许CLIP更灵活地识别图像中的主要对象，
        而不是局限于预定义类别。
        
        Args:
            image: PIL图像对象
            
        Returns:
            检测到的主题列表
        """
        # 使用通用主题提示和CLIP的零样本能力
        # 这里我们查询一些更通用的类别
        general_categories = [
            "flower", "animal", "vehicle", "food", "building",
            "landscape", "person", "furniture", "technology", "art",
            "nature", "object", "symbol", "plant", "tool"
        ]

        candidate_texts = [self.general_subject_prompt.format(cat) for cat in general_categories]

        # 准备CLIP模型的输入
        inputs = self.processor(
            text=candidate_texts,
            images=image,
            return_tensors="pt",
            padding=True
        )

        # 运行推理
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)

        # 获取最匹配的一般类别
        top_prob, top_idx = torch.topk(probs[0], k=1)
        top_category = general_categories[top_idx]

        # 如果概率太低，直接返回空
        if top_prob < 0.15:
            return []

        # 根据顶级类别，使用更具体的子类别
        specific_subcategories = {
            "flower": ["rose", "tulip", "sunflower", "daisy", "lily", "orchid", "poppy", "lotus"],
            "animal": ["dog", "cat", "bird", "fish", "lion", "tiger", "elephant", "bear", "horse"],
            "vehicle": ["car", "bus", "truck", "bicycle", "motorcycle", "train", "airplane", "ship"],
            "food": ["apple", "pizza", "cake", "coffee", "bread", "sandwich", "salad", "burger"],
            "technology": ["computer", "phone", "laptop", "camera", "headphones", "speaker", "tablet"],
            "symbol": ["heart", "star", "arrow", "check", "cross", "question", "exclamation"]
        }

        # 如果没有子类别，就返回通用类别
        if top_category not in specific_subcategories:
            return [top_category]

        # 查询具体子类别
        subcategories = specific_subcategories[top_category]
        sub_candidates = [self.general_subject_prompt.format(sub) for sub in subcategories]

        # 准备CLIP模型的输入
        sub_inputs = self.processor(
            text=sub_candidates,
            images=image,
            return_tensors="pt",
            padding=True
        )

        # 运行推理
        with torch.no_grad():
            sub_outputs = self.model(**sub_inputs)
            sub_logits = sub_outputs.logits_per_image
            sub_probs = sub_logits.softmax(dim=1)

        # 获取最匹配的子类别
        sub_top_prob, sub_top_idx = torch.topk(sub_probs[0], k=1)

        # 如果子类别概率太低，就使用通用类别
        if sub_top_prob < 0.15:
            return [top_category]

        # 返回最匹配的子类别
        return [subcategories[sub_top_idx]]

    def analyze_color_combinations(self, image):
        """
        分析图像中的颜色组合。专门处理多色图标。
        
        Args:
            image: PIL图像对象
            
        Returns:
            检测到的颜色列表，可能包含多个颜色
        """
        colors = self.attribute_candidates["color"]

        # 首先获取最有可能的几个单色
        single_color_results = self.analyze_attribute(image, "color")

        # 如果只检测到一种或没有颜色，直接返回
        if len(single_color_results) <= 1:
            return single_color_results

        # 检测颜色组合
        # 从检测到的单色中选择前两个进行组合测试
        top_colors = single_color_results[:2]

        # 为每种组合创建候选文本
        combination_texts = []
        for color1 in colors:
            for color2 in colors:
                if color1 != color2:
                    # 对每种提示模板创建一个查询
                    for prompt in self.color_combination_prompts:
                        combination_texts.append(prompt.format(color1, color2))

        # 准备CLIP模型的输入
        inputs = self.processor(
            text=combination_texts,
            images=image,
            return_tensors="pt",
            padding=True
        )

        # 运行推理
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)

        # 获取最佳组合
        top_prob, top_idx = torch.topk(probs[0], k=1)
        best_combination = combination_texts[top_idx]

        # 如果组合的置信度显著高于单色（相对值大于1.5倍），则增强颜色列表
        if top_prob > 0.2:
            # 从最佳组合文本中提取颜色
            for color in colors:
                if color not in single_color_results and color in best_combination:
                    single_color_results.append(color)

            # 确保不超过三种颜色
            if len(single_color_results) > 3:
                single_color_results = single_color_results[:3]

        return single_color_results

    def analyze_image(self, image_path):
        """
        分析图像的多个属性。
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            包含检测到的属性的字典
        """
        # 打开图像
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            print(f"打开图像失败: {e}")
            return {}

        # 分析不同属性
        results = {}

        # 首先检测文本 - 这可能是图标中最明显的特征
        results["text"] = self.detect_text_with_blip(image)

        # 然后分析形状和用途
        for attr_type in ["shape", "purpose"]:
            try:
                attr_results = self.analyze_attribute(image, attr_type)
                results[attr_type] = attr_results
            except Exception as e:
                print(f"分析属性 {attr_type} 失败: {e}")
                results[attr_type] = []

        # 使用增强的颜色分析
        try:
            results["color"] = self.analyze_color_combinations(image)
        except Exception as e:
            print(f"分析颜色失败: {e}")
            results["color"] = []

        # 最后用两种方法分析主题，并合并结果
        try:
            # 使用预定义候选项
            subject_results = self.analyze_attribute(image, "subject")

            # 使用通用主题分析
            general_results = self.analyze_general_subject(image)

            # 合并结果，去除重复
            results["subject"] = list(set(subject_results + general_results))
        except Exception as e:
            print(f"分析主题失败: {e}")
            results["subject"] = []

        return results


class ClipTagger(BaseTagger, ABC):
    """
    使用CLIP模型进行图像标记的标记器实现。
    """

    def __init__(self, config: dict):
        """
        初始化CLIP标记器。
        
        Args:
            config: 配置字典
        """
        super().__init__(config)
        self.analyzer = None

    def tagger_name(self):
        return "clip"

    def _ensure_analyzer(self):
        """确保初始化分析器"""
        if self.analyzer is None:
            model_name = self.private_config.get('model_name', "openai/clip-vit-base-patch32")
            self.analyzer = ClipAttributeAnalyzer(model_name=model_name)

    def tag_image(self, image_path: str) -> dict:
        """
        为给定的图像路径生成标签。
        
        Args:
            image_path: 图像文件的路径
            
        Returns:
            生成的标签字典
        """
        self._ensure_analyzer()

        print(f"使用CLIP分析图像: {os.path.basename(image_path)}")
        attributes = self.analyzer.analyze_image(image_path)

        return attributes

    def postprocess_tags(self, raw_tags: dict) -> list:
        """
        后处理标签。
        
        Args:
            raw_tags: 原始标签字典，键为属性类型，值为标签列表
            
        Returns:
            处理后的标签列表
        """
        # 将所有属性的标签合并到一个列表中
        all_tags = []

        # 首先添加文本标签（如果有）- 这通常是最优先的
        if "text" in raw_tags and raw_tags["text"]:
            all_tags.extend(raw_tags["text"])

        # 然后添加主题标签
        if "subject" in raw_tags:
            all_tags.extend(raw_tags["subject"])

        # 然后添加用途标签
        if "purpose" in raw_tags:
            all_tags.extend(raw_tags["purpose"])

        # 最后添加颜色和形状标签
        if "color" in raw_tags:
            all_tags.extend(raw_tags["color"])

        if "shape" in raw_tags:
            all_tags.extend(raw_tags["shape"])

        # 移除重复标签
        unique_tags = list(set(all_tags))
        return unique_tags


# 测试代码
if __name__ == "__main__":
    # 创建配置
    config = {
        "tagger": {"providers": {
            "clip": {
                "model_name": "openai/clip-vit-base-patch32"
            }
        }}
    }

    # 创建标记器
    tagger = ClipTagger(config)

    # 测试图像
    test_image = "path/to/test/image.jpg"
    if os.path.exists(test_image):
        raw_tags = tagger.tag_image(test_image)
        print("原始标签:", raw_tags)

        processed_tags = tagger.postprocess_tags(raw_tags)
        print("处理后的标签:", processed_tags)
    else:
        print(f"测试图像不存在: {test_image}")
