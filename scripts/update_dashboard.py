path = r'sohanlal_dashboard.html'
with open(path) as f:
    s = f.read()

old = '''        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
                'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
                sans-serif;
            background-color: #f5f7fa;
            color: #333;
        }'''
new = '''        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
                'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
                sans-serif;
            background: linear-gradient(rgba(245, 247, 250, 0.92), rgba(245, 247, 250, 0.92)), url('hardware_bg_2.jpg');
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
            color: #333;
        }'''
if old in s:
    s = s.replace(old, new)
    with open(path,'w') as f:
        f.write(s)
    print('done')
else:
    print('skip')
