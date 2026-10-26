path = r'sharma_pro.html'
with open(path, encoding='utf-8') as f:
    s = f.read()
import re
print(len(re.findall(r'hardware_bg_2', s)))
