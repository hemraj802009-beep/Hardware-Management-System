path = r'sharma_pro.html'
with open(path, 'r', encoding='utf-8') as f:
    s = f.read()
old = '<a class="btn-ghost" href="sharma_dashboard.html"><i class="fas fa-chart-line"></i> View Stock Dashboard</a>'
if old in s:
    s = s.replace(old, '')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(s)
    print('done')
else:
    print('not found')
