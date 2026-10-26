path = r'sharma_pro.html'
with open(path, encoding='utf-8') as f:
    s = f.read()
imgs = ['prod_1.jpg','prod_2.jpg','prod_3.jpg','prod_4.jpg','prod_5.jpg','prod_6.jpg','prod_7.jpg','prod_8.jpg']
idx = 0
import re
# Replace hardware_bg_2.jpg
def repl(m):
    global idx
    if idx < len(imgs):
        res = "url('" + imgs[idx] + "')"
        idx += 1
        return res
    return m.group(0)
s2 = re.sub(r"url\('hardware_bg_2\.jpg'\)", repl, s)
s2 = re.sub(r'url\("hardware_bg_2\.jpg"\)', repl, s2)
with open(path,'w', encoding='utf-8') as f:
    f.write(s2)
print(idx)
