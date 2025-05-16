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
│   ├── task/ # 任务入口
│   │   └── tag_task.py # 给图片贴标签的任务
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