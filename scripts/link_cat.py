path = r'sharma_premium.html'
with open(path, encoding='utf-8') as f:
    s = f.read()

# Replace card items
s = s.replace('Cement, TMT &amp; Structural Steel', '<a href="cement_steel.html" style="color:white;text-decoration:none">Cement, TMT &amp; Structural Steel</a>')
s = s.replace('Pipes, Fittings &amp; Plumbing', '<a href="plumbing.html" style="color:white;text-decoration:none">Pipes, Fittings &amp; Plumbing</a>')
s = s.replace('Power Tools &amp; Hand Tools', '<a href="tools.html" style="color:white;text-decoration:none">Power Tools &amp; Hand Tools</a>')
s = s.replace('Electrical, Switches &amp; Wires', '<a href="electrical.html" style="color:white;text-decoration:none">Electrical, Switches &amp; Wires</a>')
s = s.replace('Paints, Putty &amp; Waterproofing', '<a href="paints.html" style="color:white;text-decoration:none">Paints, Putty &amp; Waterproofing</a>')
s = s.replace('Sanitaryware &amp; Bath Fittings', '<a href="sanitary.html" style="color:white;text-decoration:none">Sanitaryware &amp; Bath Fittings</a>')

with open(path, 'w', encoding='utf-8') as f:
    f.write(s)
print('ok')
