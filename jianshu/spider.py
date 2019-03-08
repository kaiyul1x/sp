import requests
import json
from lxml import etree

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Host': 'www.jianshu.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
}

BASE_POST_URL = 'https://www.jianshu.com/p/'


def get_info(post_num):
    post_url = BASE_POST_URL + post_num
    resp = requests.get(post_url, headers=headers)
    tree = etree.HTML(resp.content)
    title = tree.xpath("string(//h1[@class='title'])")
    author = tree.xpath(
        "string(//div[@class='post']/div[@class='article']/div[@class='author']/div[@class='info']/span[@class='name'])")
    # views_count = tree.xpath("string(//span[@class='views-count'])")
    csrf_token = tree.xpath("string(/html/head/meta[@name='csrf-token']/@content)")
    page_data = tree.xpath("string(/html/body/script[@data-name='page-data'])")
    page_dict = json.loads(page_data)
    uuid = page_dict.get('note_show').get('uuid')
    views_count = page_dict.get('note').get('views_count')
    return {
        'post_num': post_num,
        'title': title,
        'author': author,
        'views_count': views_count,
        'csrf_token': csrf_token,
        'uuid': uuid,
    }


def increase_views(increase_count, post_num, csrf_token, uuid):
    dheaders = headers.copy()
    dheaders['X-CSRF-Token'] = csrf_token
    dheaders['referer'] = BASE_POST_URL + post_num
    resp_data = {
        'uuid': uuid,
    }
    for i in range(increase_count):
        resp = requests.post(f'https://www.jianshu.com/notes/{post_num}/mark_viewed.json', headers=dheaders,
                             data=resp_data)
        if not (200 <= resp.status_code < 300):
            raise ValueError('解析错误，请检查参数是否正确。')
        yield i / increase_count


if __name__ == '__main__':
    print(get_info("7058d29fd610"))
    # increase_views(1, 'ddc4a6dec8aa', 'VYEWfQr2k6ynr60l6ioDcWs1F2tie5bZ9c5BPJANIQ5apFwN7w+4kSoDxy3F+dwSEn6lE95g6X6op6ofZJM3/Q==', 'd6c7ad46-4a66-41b2-8d13-544ccc39f45e')
