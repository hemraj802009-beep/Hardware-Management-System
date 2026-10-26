path = r'sharma_premium.html'
with open(path, encoding='utf-8') as f:
    s = f.read()
s = s.replace('<li><a href="sharma_dashboard.html">Admin Panel</a></li>', '')
s = s.replace('Admin Panel', '')
s = s.replace('Admin Dashboard', '')
with open(path, 'w', encoding='utf-8') as f:
    f.write(s)
print('ok')
