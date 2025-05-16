import os

from src.tagger.googleai_tagger import GoogleAITagger
from src.utils.config_holder import get_config_holder
from src.utils.file_util import get_file_util

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

config_holder = get_config_holder(env='dev', config_dir = "../../config")
file_util = get_file_util(project_root=root_path)

config = config_holder.get_config("application")

appconfig = config_holder.get_config("application")['classifier']

input_dir = appconfig['classified_out_dir_positive']

img_abs_path = file_util.get_project_root() + "/" + input_dir + "folder368~iphone.png"
tag_arr = GoogleAITagger(config).final_process_image_tagging(img_abs_path)
print(tag_arr)
