import urllib.request
urls = [
    'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&q=80',
    'https://images.unsplash.com/photo-1541888946425-d81bb19240f5?w=800&q=80',
    'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800&q=80',
    'https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=800&q=80',
    'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&q=80',
    'https://images.unsplash.com/photo-1586864387967-d02ef85d93e8?w=800&q=80',
    'https://images.unsplash.com/photo-1621905251918-48416bd8575a?w=800&q=80',
    'https://images.unsplash.com/photo-1565814329452-e1efa11c5b89?w=800&q=80',
]
for i,u in enumerate(urls):
    try:
        urllib.request.urlretrieve(u, f'prod_{i+1}.jpg')
        print('ok', i)
    except Exception as e:
        print('err', e)
