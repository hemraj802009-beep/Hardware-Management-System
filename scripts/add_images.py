path = r'sharma_pro.html'
with open(path, encoding='utf-8') as f:
    s = f.read()

imgs = ['prod_1.jpg','prod_2.jpg','prod_3.jpg','prod_4.jpg','prod_5.jpg','prod_6.jpg','prod_7.jpg','prod_8.jpg']
count = 0

import re
def repl(m):
    global count
    if count < len(imgs):
        url = imgs[count]
        count += 1
        return "background:linear-gradient(rgba(0,0,0,0.04),rgba(0,0,0,0.04)),url('" + url + "');background-size:cover;background-position:center"
    return m.group(0)

s2 = re.sub(r"background:linear-gradient\(rgba\(15,46,26,0\.12\),rgba\(15,46,26,0\.12\)\),url\('hardware_bg_2\.jpg'\);background-size:cover;background-position:center", repl, s)
s2 = re.sub(r"background:linear-gradient\(rgba\(15,46,26,0\.12\),rgba\(15,46,26,0\.12\)\),url\('hardware_bg_2\.jpg'\);background-size:cover", repl, s2)

with open(path,'w', encoding='utf-8') as f:
    f.write(s2)
print('done', count)
