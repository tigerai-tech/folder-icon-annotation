from src.tagger.googleai_tagger import GoogleAITagger
from src.utils.file_util import FileUtil
from tests.config_usage_example import initialize_config_for_standalone_script

initialize_config_for_standalone_script()

from src.utils.config_loader import ConfigLoader

config = ConfigLoader().load_config('tagger_conf.yaml')
appconfig = ConfigLoader().load_config('application_config.yaml')['tagger']

input_dir = appconfig['input_image_dir']

img_abs_path = FileUtil.get_project_root() + "/" + input_dir + "folder361~iphone.png"
tag_arr = GoogleAITagger(config).final_process_image_tagging(img_abs_path)
print(tag_arr)
