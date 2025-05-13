import re
def remove_non_alpha(s):
    return re.sub(r'[^a-zA-Z0-9]', '', s)
# 示例
input_str = "Hello, World! 123"
cleaned_str = remove_non_alpha(input_str)
print(cleaned_str)  #