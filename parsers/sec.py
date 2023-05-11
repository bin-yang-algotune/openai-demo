import datetime
from typing import Dict

import requests
from requests.adapters import HTTPAdapter, Retry
from faker import Faker

RETRY_MAX_NUM = 10
RETRY_BACKOFF_FACTOR = 0.1

# https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#module-urllib3.util.retry
RETRY_DEFAULT = Retry(
    total=RETRY_MAX_NUM,
    backoff_factor=RETRY_BACKOFF_FACTOR,
    status_forcelist=[403, 500, 502, 503, 504],
)

EDGAR_SEARCH_HOST = 'efts.sec.gov'
EDGAR_SEARCH_URL = "https://{}/LATEST/search-index".format(EDGAR_SEARCH_HOST)


def gen_req_header(use_random_agent: bool = True) -> Dict[str, str]:
    """
    generate http request header

    :param use_random_agent:
    :return:
    """
    if use_random_agent:
        fake_user = Faker()
        agent = "{} {} {}".format(
            fake_user.first_name(),
            fake_user.last_name(),
            fake_user.email()
        )
    else:
        # default uses browser setting
        agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    headers = {
        "User-Agent": agent,
        "Accept-Encoding": "gzip, deflate",
        "Host": EDGAR_SEARCH_HOST
    }
    return headers


def gen_edgar_custom_search_param(
        entity_name: str,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
        query: str = "",
        filing_id: str = None,
        from_index: int = None,
) -> Dict[str, str]:
    """
    generate custom search parameter for using edgar

    :param entity_name:
    :param start_date:
    :param end_date:
    :param query:
    :param filing_id:
    :param from_index:
    :return:
    """
    json_request = {
        "entityName": entity_name,
        "q": query
    }
    if start_date is not None or end_date is not None:
        json_request['dateRange'] = 'custom'
        if start_date is not None:
            start_date_str = start_date.strftime('%Y-%m-%d')
            json_request['startdt'] = start_date_str
        if end_date is not None:
            end_date_str = end_date.strftime('%Y-%m-%d')
            json_request['enddt'] = end_date_str
    if filing_id is not None:
        json_request['forms'] = filing_id
    if from_index is not None:
        json_request['from'] = from_index
    return json_request


def run_edgar_search_by_entity_and_date_range(
        entity_name: str,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
        query: str = "",
        input_retry: Retry = None,
        from_index: int = None
):
    """
    run single edgar search request
    :param entity_name:
    :param start_date:
    :param end_date:
    :param query:
    :param input_retry:
    :param from_index:
    :return:
    Usage:
    >>> entity_name = 'BERKSHIRE HATHAWAY INC'
    >>> start_date = datetime.date(2020, 1, 1)
    >>> end_date = datetime.date(2020, 10, 1)
    >>> input_retry = None
    >>> query = ""
    >>> from_index = None
    """
    if input_retry is None:
        input_retry = RETRY_DEFAULT
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=input_retry))

    req_header = gen_req_header(use_random_agent=True)
    json_request = gen_edgar_custom_search_param(
        entity_name=entity_name,
        start_date=start_date,
        end_date=end_date,
        query=query,
        from_index=from_index
    )
    resp = session.post(
        EDGAR_SEARCH_URL, json=json_request, headers=req_header
    )
    resp.raise_for_status()
    result_json = resp.json()
    session.close()
    return result_json


def get_filing_url_list():
    pass
