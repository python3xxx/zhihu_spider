import os
import requests
import re
import urllib.request as request

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36",
    'Accept-Encoding': 'gzip, deflate'
}


def zhihu_spider(question_id):
    # 当页条数
    limit = 10
    # 偏移量
    offset = 0
    # 知乎问题地址
    answer_url = f'https://www.zhihu.com/api/v4/questions/{question_id}/answers'
    # 用于匹配回答内容中的图片
    pic_reg = re.compile('<noscript>.*?data-original="(.*?)".*?</noscript>', re.S)
    # 记录图片数量
    pic_num = 1
    # 循环执行爬虫，直至最后一页
    while True:
        # 请求参数
        data = {
            'include': """data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,is_labeled,is_recognized,paid_info,paid_info_content;data[*].mark_infos[*].url;data[*].author.follower_count,badge[*].topics""",
            'limit': limit,
            'offset': offset,
        }
        response = requests.get(answer_url, params=data, headers=headers)
        resp = response.json()
        # 当前页所有回答
        answers = resp.get('data')
        for answer in answers:
            content = answer['content']
            # 图片url
            pic_urls = re.findall(pic_reg, content)
            # 答主名字
            author_name = answer['author']['name']
            # 将回答中的所有图片写入url.txt
            for i in pic_urls:
                pic_num += 1
                with open('url.txt', 'a', encoding='utf-8') as f:
                    f.write(i + '\t' + author_name + '\n')
        print(f'已获取前 {offset +limit} 个回答，当前图片总数为 {pic_num}')
        paging = resp.get('paging')
        # is_end  = True 已到最后一页
        if paging['is_end']:
            print('爬取完毕')
            break
        offset += limit


def zh_download(question_id):
    img_info = []
    total = 1
    try:
        with open('url.txt', 'r', encoding='utf-8') as f:
            for i in f:
                img = i.replace('\n', '').split('\t')
                img_info.append(img)
                total += 1
    except FileNotFoundError as e:
        zhihu_spider(question_id)
        zh_download(question_id)
    print('----------------------  开始下载  ---------------------- 图片总数：%d' % total)
    num = 0
    for i in img_info:
        img_url = i[0]
        img_author_name = i[1]
        # 获取当前文件所在目录
        path = os.path.dirname(os.path.abspath(__file__)) + os.sep + 'zhihuPic'
        # 创建文件夹 用来存抓取的图片
        if not os.path.exists(path):
            os.makedirs(path)
        filename = path + os.sep + img_author_name + '_' + str(num) + '.jpg'
        try:
            # urllib.request模块提供的urlretrieve()函数。直接将远程数据下载到本地。
            request.urlretrieve(img_url, filename)
            num += 1
        except Exception as e:
            print(f'图片: {img_url} 下载失败...')
            continue
        print(f'图片 {img_url} 下载完成..({num} / {total})')


if __name__ == '__main__':
    zh_download(question_id='26037846')
