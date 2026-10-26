path = r'sharma_pro.html'
with open(path, encoding='utf-8') as f:
    s = f.read()
imgs = ['prod_1.jpg','prod_2.jpg','prod_3.jpg','prod_4.jpg','prod_5.jpg','prod_6.jpg','prod_7.jpg','prod_8.jpg']
import re
count = 0
def repl(m):
    global count
    if count < len(imgs):
        res = "url('" + imgs[count] + "')"
        count += 1
        return res
    return m.group(0)
s2 = re.sub(r"url\('hardware_bg_2\.jpg'\)", repl, s)
with open(path,'w', encoding='utf-8') as f:
    f.write(s2)
print(count)
