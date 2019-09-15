"""
utils for storage app
"""

import os
import datetime
from urllib.parse import unquote
from django.utils import timezone


from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OrderSystem.settings')
application = get_wsgi_application()


# 将字符串转换为整数
def str2int(string):
    if string:
        try:
            num = int(string)
        except ValueError:
            num = 0
    else:
        num = 0

    return num


# 将字符串转换为浮点数
def str2float(string):
    if string:
        try:
            num = float(string)
        except ValueError:
            num = 0
    else:
        num = 0

    return num


# 将字符串转换为布尔值. 仅当 空值, False 和 `false` 时返回 False
def str2bool(string):
    if not string:
        return False

    if string == 'false':
        return False

    return True


# 将日期转化为 `YYYY年mm月dd日` 的格式
def date2str(date):
    if isinstance(date, str):
        date = str2date(date)
    try:
        # readable_date = date.strftime('%Y年%m月%d日')
        readable_date = date.strftime('%m/%d/%Y')
    except Exception:
        readable_date = date
    return readable_date


# 将字符串日期转换为 datetime 类型
def str2date(string):
    try:
        # date = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S+08:00')
        date = datetime.datetime.strptime(string, '%m/%d/%Y')
    except ValueError:
        try:
            date = datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                date = datetime.datetime.strptime(string, '%m/%d/%YT%H:%M:%S+08:00')
            except ValueError:
                return string
    return date
    # return timezone.make_aware(date)


# 文件内容迭代器
def file_iterator(filename, chunk_size=512):
    with open(filename, 'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break


# 获取由波浪号分隔的日期的日期间隔, 格式如: '2018-01-01 ~ 2018-01-07'
def get_tilde_splitted_date_range(date_range):
    format_ = '%m/%d/%Y'
    date_range = unquote(date_range)
    dates = date_range.split('~')
    min_ = datetime.datetime.strptime(dates[0].replace(' ', ''), format_)
    max_ = datetime.datetime.strptime(dates[1].replace(' ', ''), format_)

    if min_ > max_:
        min_, max_ = max_, min_

    max_ = max_.replace(hour=23, minute=59, second=59)

    # min_ = timezone.make_aware(min_)
    # max_ = timezone.make_aware(max_)

    return min_, max_


# 格式化日期
def format_date_str(date):
    formatted = date
    if '年' in date:
        try:
            formatted = datetime.datetime.strptime(date, '%Y年%m月%d日')
        except Exception:
            try:
                formatted = datetime.datetime.strptime(date, '%Y年%m月%d')
            except Exception:
                pass
    else:
        try:
            formatted = datetime.datetime.strptime(date, '%Y-%m-%d')
        except Exception:
            pass

    try:
        time = formatted.strftime('%Y-%m-%d')
    except Exception:
        time = formatted

    return time


# 百分数转为int
def percent_to_int(string):
    if "%" in string:
        # newint = int(string.strip("%")) / 100
        newint = int(string.strip("%"))
        return newint
    else:
        # print("你输入的不是百分比！")
        return 0


if __name__ == '__main__':
    # date = "10/02/2019"
    # time = str2date(date)
    # print(time.strftime('%m/%d/%Y'))
    # print(type(time))
    # print(date2str(time))
    # range_time = "10/20/2019 ~ 10/30/2019"
    # print(get_tilde_splitted_date_range(range_time))

    a = "50%"
    b = "80%"

    # 比较大小
    if percent_to_int(a) > percent_to_int(b):
        print("a > b")
    elif percent_to_int(a) < percent_to_int(b):
        print("a < b")
    elif percent_to_int(a) == percent_to_int(b):
        print("a = b")
    else:
        print("输入有误，无法比较")
