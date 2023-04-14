import os
from newsplease import NewsPlease, SimpleCrawler

from googleapiclient.discovery import build

G_API_KEY = os.getenv('G_API_KEY')
CUSTOM_SEARCH_KEY = 'e6127f0892b2643b7'


def g_search_raw(term: str,
                 **kwargs):
    """

    :param term:
    :param kwargs:
    :return:
    usage:
    >>> term = 'tesla stock'
    >>> kwargs = {'dateRestrict':'d5', 'gl':'us'}
    >>> g_search_raw(term, **kwargs)
    """
    service = build("customsearch", "v1", developerKey=G_API_KEY)
    cse = service.cse()
    res = cse.list(q=term, cx=CUSTOM_SEARCH_KEY, **kwargs).execute()
    item_list = []
    if 'items' in res.keys():
        item_list = res['items']
    return item_list
