# MBPPrice

MBPPrice用來抓取二手Macbook Pro的價格和相關資訊

## Setup

```bash
pip install mbpprice
```

## Utility

```bash
# 搜尋 PTT 二手 Macbook Pro 資訊
python3 -m mbpprice search ptt
```

## Example

```python
from mbpprice.search import MBPSearch


results = MBPSearch('ptt').list(limit=10)
for (i, item) in enumerate(results):
    print('{:03d}: {}'.format(i, item['url']))
    print('價格: {}'.format(item['price']))
    print(
        '年份: {} / 螢幕尺寸: {} / 電池循環: {}'.format(item['year'], item['screen'], item['bat_count']))
    print(
        'CPU: {} / RAM: {} / 硬碟容量: {}'.format(item['cpu'], item['ram'], item['hdd']))
    print()

```