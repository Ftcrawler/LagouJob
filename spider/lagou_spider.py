import logging
import time
import urllib.parse

import requests

from entity.job import Job
from spider.jobdetail_spider import crawl_job_detail
from util.excel_helper import write_excel

logging.basicConfig(format="%(asctime)s-%(name)s-%(levelname)s-%(message)s\t", level=logging.DEBUG)


def crawl_jobs(positionName):
    """crawl the job info from lagou H5 web pages"""
    joblist = list()
    max_page_number = get_max_pageNo(positionName)
    cookies = get_cookies()

    for i in range(1, max_page_number + 1):
        request_url = 'https://m.lagou.com/search.json?city=%E5%85%A8%E5%9B%BD&positionName=' + urllib.parse.quote(
            positionName) + '&pageNo=' + str(i) + '&pageSize=15'
        headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Host': 'm.lagou.com',
            'Referer': 'https://m.lagou.com/search.html',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive'
        }
        response = requests.get(request_url, headers=headers, cookies=cookies)
        if response.status_code == 200:
            for each_item in response.json()['content']['data']['page']['result']:
                job = Job(each_item['positionId'], each_item['positionName'], each_item['city'],
                          each_item['createTime'], each_item['salary'],
                          each_item['companyId'], each_item['companyName'], each_item['companyFullName'])
                joblist.append(job)
                crawl_job_detail(each_item['positionId'], positionName)
            print('crawling page %d done...' % i)
            time.sleep(3)
        elif response.status_code == 403:
            logging.error('request is forbidden by the server...')
        else:
            logging.error(response.status_code)

    return joblist


def get_cookies():
    """return the cookies after your first visit"""
    headers = {
        'Host': 'm.lagou.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4'
    }
    url = 'https://m.lagou.com/'
    response = requests.get(url, headers=headers, timeout=10)

    return response.cookies


def get_max_pageNo(positionName):
    """return the max page number of a specific job"""
    cookies = get_cookies()
    request_url = 'https://m.lagou.com/search.json?city=%E5%85%A8%E5%9B%BD&positionName=' + urllib.parse.quote(
        positionName) + '&pageNo=1&pageSize=15'
    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Host': 'm.lagou.com',
        'Referer': 'https://m.lagou.com/search.html',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive'
    }
    response = requests.get(request_url, headers=headers, cookies=cookies, timeout=10)
    if response.status_code == 200:
        max_page_no = int(int(response.json()['content']['data']['page']['totalCount']) / 15 + 1)

        return max_page_no
    elif response.status_code == 403:
        logging.error('request is forbidden by the server...')

        return 0
    else:
        logging.error(response.status_code)

        return 0


if __name__ == '__main__':
    jobname = '人工智能'
    joblist = crawl_jobs(jobname)
    write_excel(joblist, jobname)
