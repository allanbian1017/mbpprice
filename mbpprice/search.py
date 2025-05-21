"""MBP data search module"""
import re
import requests
from pyquery import PyQuery as pq


class MBPSearch():
    """MBPSearch class

    Attributes:
        endpoint (str): Query url endpoint
    """

    def __init__(self, channel):
        self.channel = channel
        self.endpoints = {
            'ptt': 'https://www.ptt.cc',
            'ebay': 'https://www.ebay.com'
        }
        self.search_url_templates = {
            'ptt': '{base_url}/bbs/MacShop/search?q=macbook+pro&page={page_num}',
            'ebay': '{base_url}/sch/i.html?_nkw=macbook+pro&_pgn={page_num}'
        }
        self.parsing_methods = {
            'ptt': {
                'parse_mbp_data': self._parse_mbp_data_ptt,
                'get_price': self._get_price_ptt,
                'get_year': self._get_year_ptt,
            },
            'ebay': {
                'parse_mbp_data': self._parse_mbp_data_ebay,
                'get_price': self._get_price_ebay,
                'get_year': self._get_year_ebay,
            }
        }

    def list(self, limit=10):
        """List MBP data

        Returns:
            array -- [MBP prices]
        """
        results = []
        page = 0
        while len(results) < limit:
            base_url = self.endpoints.get(self.channel)
            if not base_url:
                raise NotImplementedError(f"Channel {self.channel} is not supported.")

            search_template = self.search_url_templates.get(self.channel)
            if not search_template:
                raise NotImplementedError(f"Search URL template for channel {self.channel} not defined.")
            
            # Increment page for PTT (0-indexed) vs eBay (1-indexed)
            page_num_for_url = page + 1 if self.channel == 'ebay' else page
            
            search_url = search_template.format(base_url=base_url, page_num=str(page_num_for_url))
            content = self.get_content(search_url)

            if content:
                doc = pq(content)

                # TODO: This part is PTT specific, need to generalize for eBay
                if self.channel == 'ptt':
                    for item in doc('div.r-ent'):
                        div = pq(item)
                        node = div('div.title').find('a').attr('href')
                        if not node: # handle cases where node might be None
                            continue
                        url = base_url + node

                        channel_parsers = self.parsing_methods.get(self.channel)
                        if not channel_parsers or 'parse_mbp_data' not in channel_parsers:
                            raise NotImplementedError(f"Parsing for channel {self.channel} is not implemented.")
                        
                        parse_mbp_data_func = channel_parsers['parse_mbp_data']
                        record = parse_mbp_data_func(url)
                        if record is None:
                            continue

                        # if value in record is missing then drop this record
                        valid = True
                        for key in record:
                            if not bool(record[key]):
                                valid = False

                        if valid:
                            results.append(record)
                            if len(results) >= limit:
                                return results
                elif self.channel == 'ebay':
                    # Placeholder for eBay item iteration and parsing
                    # Since _parse_mbp_data_ebay returns None, this loop effectively does nothing yet
                    channel_parsers = self.parsing_methods.get(self.channel)
                    if not channel_parsers or 'parse_mbp_data' not in channel_parsers:
                        raise NotImplementedError(f"Parsing for channel {self.channel} is not implemented.")
                    parse_mbp_data_func = channel_parsers['parse_mbp_data']
                    # This will call _parse_mbp_data_ebay, which currently returns None
                    # You'll need to implement actual eBay item extraction here later
                    # For now, this loop won't add any results.
                    # Example: for item in doc('.s-item'): record = parse_mbp_data_func(pq(item).html())
                    pass # Explicitly do nothing for ebay's item parsing in this iteration

            page += 1
            # Break if page is too high to prevent infinite loops for channels not returning data
            if page > limit * 2 and len(results) == 0 : # Heuristic to break
                 print(f"Breaking search for channel {self.channel} after {page} pages with no results.")
                 break


        return results

    @staticmethod
    def get_content(url):
        """Get url content

        Args:
            url (str): Url to get content

        Returns:
            string -- [Url content]
        """
        resp = requests.get(url)

        if resp.status_code == 200:
            return resp.text

        return ''

    @staticmethod
    def search_string(regex, content, group=None):
        """Search string

        Args:
            regex (regular expression): Target regular expression
            content (str): Content to search
            group (int): Match group

        Returns:
            string -- [Target]
        """
        match = re.search(regex, content)
        if match:
            if group:
                return match.group(group)

            return match.group()

        return ''

    @staticmethod
    def search_int(regex, content, group=None):
        """Search int

        Args:
            regex (regular expression): Target regular expression
            content (str): Content to search
            group (int): Match group

        Returns:
            int -- [Target]
        """
        target = MBPSearch.search_string(regex, content, group)
        return int(target) if target else 0

    def _parse_mbp_data_ptt(self, url):
        """Parse PTT MBP data with given url

        Args:
            url (str): MBP data url

        Returns:
            int -- [MBP price]
        """
        body = self.get_content(url)
        if body is None:
            return None

        doc_body = pq(body)
        content = doc_body('#main-container').html()
        lines = content.splitlines()

        record = {
            'url': url,
            'price': self._get_price_ptt(lines),
            'year': self._get_year_ptt(lines),
            'bat_count': self.search_int(
                r'循環\D*(\d+)',
                content,
                1
            ),
            'screen': self.search_int(
                r'(1\d{1})[吋"\']',
                content,
                1
            ),
            'cpu': self.search_string(
                r'i5|i7',
                content
            ),
            'ram': self.search_int(
                r'(8|16)G',
                content,
                1
            ),
            'hdd': self.search_int(
                r'(128|256|512)G',
                content,
                1
            ),
        }
        return record

    def _get_price_ptt(self, lines):
        """Get PTT MBP price

        Args:
            lines (array): MBP detail data split by lines

        Returns:
            int -- [MBP price]
        """
        for line in lines:
            res = re.search(r'交易價格', line)
            if res:
                return self.search_int(r'\d{5}', line)

        return 0

    def _get_year_ptt(self, lines):
        """Get PTT MBP year

        Args:
            lines (array): MBP detail data split by lines

        Returns:
            int -- [MBP year]
        """
        for line in lines:
            res = re.search(r'時間', line)
            year = self.search_int(r'201\d{1}', line)
            if not res and year != 0:
                return year

        return 0

    def _parse_mbp_data_ebay(self, url):
        """Stub for parsing eBay MBP data."""
        # Actual eBay parsing logic will be implemented later.
        # For now, it returns None, so no data will be processed.
        return None

    def _get_price_ebay(self, lines):
        """Stub for getting eBay MBP price."""
        # Actual eBay price extraction logic will be implemented later.
        return 0

    def _get_year_ebay(self, lines):
        """Stub for getting eBay MBP year."""
        # Actual eBay year extraction logic will be implemented later.
        return 0
