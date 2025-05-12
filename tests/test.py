input_arr = ["folder item1", "icon item2", "item3", "folder item4", "icon item5", "folder"]
ignore_tag_text_list = ['folder', 'icon']

arr = []
for item in input_arr:
    if item in ignore_tag_text_list:
        continue
    for it in ignore_tag_text_list:
        if item.__contains__(it):
            item = item.replace(it, '')
    item = item.replace(' ', '')
    print(item)
    arr.append(item)

print(arr)