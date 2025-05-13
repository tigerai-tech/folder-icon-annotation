# folder-icon-annotation
Folder Icon Images annotation

## Features

- Web Scraping: get folder icon images from the Internet
- Images Classification: use DNN models to classify images
- Data Annotation / Labeling: Label every remaining image 
- set core labels as image name
- zip and export for folder-icon-management



## Project Structure
```text
project_root/
├── config/
│   ├── base_config.yaml
│   ├── crawler_config.yaml
│   ├── classifier_config.yaml
│   ├── tagger_config.yaml
│   └── api_keys.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   └── models/
├── src/
│   ├── __init__.py
│   ├── crawler/
│   │   ├── __init__.py
│   │   ├── base_crawler.py
│   │   ├── website1_crawler.py
│   │   └── website2_crawler.py
│   ├── classifier/
│   │   ├── __init__.py
│   │   ├── base_classifier.py
│   │   ├── pretrained_classifier.py
│   │   ├── transfer_learning_classifier.py
│   │   └── openai_classifier.py
│   ├── tagger/
│   │   ├── __init__.py
│   │   ├── base_tagger.py
│   │   ├── image_feature_tagger.py
│   │   ├── openai_tagger.py
│   │   └── googleai_tagger.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config_loader.py
│   │   ├── data_loader.py
│   │   └── model_loader.py
├── tests/
│   ├── __init__.py
│   ├── test_crawler.py
│   ├── test_classifier.py
│   └── test_tagger.py
├── main.py
└── requirements.txt
```

## 运行
```shell
python3 main.py run
```

## 配置系统

项目使用了集中化的配置管理系统，支持环境特定的配置。

### 配置文件

配置文件存放在 `config/` 目录下，使用 YAML 格式：

- 标准配置文件: `<name>_<type>.yaml`（如 `tagger_conf.yaml`）
- 环境特定配置: `<name>_<type>-<env>.yaml`（如 `tagger_conf-dev.yaml`）

当指定环境时，环境特定配置会与标准配置合并。合并规则如下：

1. 如果环境特定配置文件不存在，则使用标准配置文件
2. 如果环境特定配置文件存在，则将其与标准配置文件合并，环境特定配置的值会覆盖标准配置的值
3. 如果环境特定配置文件中某个键不存在，会从标准配置文件中读取
4. 对于嵌套配置，会进行深度合并

例如，如果 `tagger_conf.yaml` 包含完整配置，而 `tagger_conf-dev.yaml` 只包含需要修改的部分配置项，系统会自动从标准配置获取缺失的项。

### 配置加载

项目提供了两个配置相关的类：

1. **ConfigLoader**: 用于从文件中加载配置
2. **ConfigHolder**: 用于在程序启动时加载配置并存储在静态变量中

### 环境特定配置

运行时指定环境：

```shell
python3 main.py run --env dev
```
