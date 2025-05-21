import unittest
from unittest.mock import patch, MagicMock, call
from mbpprice.search import MBPSearch

# Helper MockResponse class
class MockResponse:
    def __init__(self, text, status_code):
        self.text = text
        self.status_code = status_code

class TestMBPSearch(unittest.TestCase):
    @patch('requests.get')
    def test_ptt_search_list_successful(self, mock_get):
        ptt_search_page_html = """
        <div class="r-ent">
            <div class="title">
                <a href="/bbs/MacShop/M.123.A.XYZ.html">[販售] Macbook Pro 13 2020 M1</a>
            </div>
        </div>
        """
        # Adjusted HTML for easier parsing by current methods
        ptt_item_page_html = """
        <div id="main-container">
            [物品型號]：Macbook Pro 13
            [規格]：M1/8G/256G
            [保固日期]：2023/10/10
            [原始發票]：無
            [隨機配件]：原廠盒裝配件
            [照片連結]：
            [拍賣連結]：
            [連絡方式]：站內信
            [交易地點]：台北
            [交易方式]：面交
            [交易價格]：30000
            [其他備註]：螢幕顯示：13吋 Retina
                        處理器：Apple M1 (also matches i5|i7 due to search_string)
                        記憶體：8GB
                        儲存空間：256GB SSD
                        電池循環：50次
                        時間：2020/10/10 (This line helps get_year_ptt)
        </div>
        """

        mock_get.side_effect = [
            MockResponse(ptt_search_page_html, 200),
            MockResponse(ptt_item_page_html, 200)
        ]

        search = MBPSearch(channel='ptt')
        results = search.list(limit=1)

        self.assertEqual(len(results), 1)
        record = results[0]
        self.assertEqual(record['price'], 30000)
        self.assertEqual(record['year'], 2020) 
        self.assertEqual(record['bat_count'], 50)
        self.assertEqual(record['screen'], 13)
        self.assertTrue(record['cpu']) # Will be 'M1' or first match of i5/i7
        self.assertEqual(record['ram'], 8)
        self.assertEqual(record['hdd'], 256)
        self.assertTrue(record['url'].endswith('/bbs/MacShop/M.123.A.XYZ.html'))

        expected_calls = [
            call('https://www.ptt.cc/bbs/MacShop/search?q=macbook+pro&page=0'),
            call('https://www.ptt.cc/bbs/MacShop/M.123.A.XYZ.html')
        ]
        mock_get.assert_has_calls(expected_calls, any_order=False)

    @patch('requests.get')
    def test_ptt_search_item_parsing_failure(self, mock_get):
        # Test case where the item page doesn't contain expected data
        ptt_search_page_html = """
        <div class="r-ent">
            <div class="title">
                <a href="/bbs/MacShop/M.BAD.ITEM.html">[販售] Macbook Pro - Incomplete</a>
            </div>
        </div>
        """
        ptt_item_page_html_bad = """
        <div id="main-container">
            This is a bad item page, no valid data.
            [交易價格]：N/A
        </div>
        """
        mock_get.side_effect = [
            MockResponse(ptt_search_page_html, 200),
            MockResponse(ptt_item_page_html_bad, 200)
        ]
        search = MBPSearch(channel='ptt')
        results = search.list(limit=1)
        self.assertEqual(len(results), 0, "Should return empty list if item parsing fails validity check")


    def test_ebay_initialization(self):
        search = MBPSearch(channel='ebay')
        self.assertEqual(search.channel, 'ebay')
        self.assertIn('ebay', search.endpoints)
        self.assertIn('ebay', search.parsing_methods)
        self.assertIn('ebay', search.search_url_templates)

    @patch('requests.get')
    def test_ebay_search_list_stubbed(self, mock_get):
        mock_get.return_value = MockResponse("<html><body>Some eBay search results</body></html>", 200)

        search = MBPSearch(channel='ebay')
        results = search.list(limit=1)
        self.assertEqual(len(results), 0)
        
        # For limit=1, the loop for pages runs for page=0, page=1, page=2.
        # page_num_for_url for eBay is page + 1. So, it requests pages 1, 2, 3.
        # Safety break: page (internal, 0-indexed) > limit * 2
        # Page 0: url_page 1. results=0. page becomes 1. 1*2=2. 1<=2.
        # Page 1: url_page 2. results=0. page becomes 2. 2<=2.
        # Page 2: url_page 3. results=0. page becomes 3. 3>2. Break.
        expected_ebay_calls = [
            call('https://www.ebay.com/sch/i.html?_nkw=macbook+pro&_pgn=1'),
            call('https://www.ebay.com/sch/i.html?_nkw=macbook+pro&_pgn=2'),
            call('https://www.ebay.com/sch/i.html?_nkw=macbook+pro&_pgn=3'),
        ]
        mock_get.assert_has_calls(expected_ebay_calls, any_order=False)
        self.assertEqual(mock_get.call_count, 3)


    def test_unsupported_channel_no_endpoint(self):
        search = MBPSearch(channel='unknown_channel_no_endpoint')
        with self.assertRaisesRegex(NotImplementedError, "Channel unknown_channel_no_endpoint is not supported."):
            search.list(limit=1)

    def test_unsupported_channel_no_url_template(self):
        search = MBPSearch(channel='channel_no_template')
        # Add to endpoints but not to search_url_templates
        search.endpoints['channel_no_template'] = 'http://someurl.com'
        # Ensure it's not in search_url_templates (it shouldn't be by default)
        if 'channel_no_template' in search.search_url_templates:
            del search.search_url_templates['channel_no_template']

        with self.assertRaisesRegex(NotImplementedError, "Search URL template for channel channel_no_template not defined."):
            search.list(limit=1)

    @patch('requests.get')
    def test_list_method_handles_no_content_from_get_content(self, mock_get):
        mock_get.return_value = MockResponse(None, 200) # get_content returns '' if resp.text is None
                                                       # or if status_code is not 200
        
        search_ptt = MBPSearch(channel='ptt')
        results_ptt = search_ptt.list(limit=1)
        self.assertEqual(len(results_ptt), 0)
        # Ensure it was called for PTT
        mock_get.assert_called_with('https://www.ptt.cc/bbs/MacShop/search?q=macbook+pro&page=0')
        
        mock_get.reset_mock()
        mock_get.return_value = MockResponse(None, 200)
        search_ebay = MBPSearch(channel='ebay')
        results_ebay = search_ebay.list(limit=1)
        self.assertEqual(len(results_ebay), 0)
        # Ensure it was called for eBay (at least the first page)
        self.assertTrue(any(c == call('https://www.ebay.com/sch/i.html?_nkw=macbook+pro&_pgn=1') for c in mock_get.call_args_list))


if __name__ == '__main__':
    unittest.main()
