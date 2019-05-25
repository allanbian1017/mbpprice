# MBPPrice

MBPPrice用來抓取二手Macbook Pro的價格和相關資訊

## Example

```python
from mbpprice.search import MBPSearch


results = MBPSearch('ptt').list(limit=10)
for item in results:
    print('URL: {}'.format(item['url']))
    print('價格: {}'.format(item['price']))
    print(
        '年份: {} / 螢幕尺寸: {} / 電池循環: {}'.format(item['year'], item['screen'], item['bat_count']))
    print(
        'CPU: {} / RAM: {} / 硬碟容量: {}'.format(item['cpu'], item['ram'], item['hdd']))
    print()
```