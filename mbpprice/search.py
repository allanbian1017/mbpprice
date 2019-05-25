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
        if channel != 'ptt':
            msg = 'Channel {} does not support right now'.format(channel)
            raise Exception(msg)

        self.endpoint = 'https://www.ptt.cc'

    def list(self, limit=10):
        """List MBP data

        Returns:
            array -- [MBP prices]
        """
        results = []
        page = 0
        while len(results) < limit:
            content = self.get_content(
                self.endpoint + '/bbs/MacShop/search?q=macbook+pro&page=' + str(page))

            if content:
                doc = pq(content)

                for item in doc('div.r-ent'):
                    div = pq(item)
                    node = div('div.title').find('a').attr('href')
                    url = self.endpoint + node

                    record = self.parse_mbp_data(url)
                    if record is None:
                        continue

                    # if value in record is missing then drop this record
                    valid = True
                    for key in record:
                        if not bool(record[key]):
                            valid = False

                    if valid:
                        results.append(record)

            page += 1

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

    def parse_mbp_data(self, url):
        """Parse MBP data with given url

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
            'price': self.get_price(lines),
            'year': self.get_year(lines),
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

    def get_price(self, lines):
        """Get MBP price

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

    def get_year(self, lines):
        """Get MBP year

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
