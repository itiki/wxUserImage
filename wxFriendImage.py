# -*- coding:utf-8 -*-
import re
import jieba
from wxpy import *
from pyecharts import Pie
from pyecharts import Map
from pyecharts import Page
from pyecharts import WordCloud


class WxFriendImage:
    """
    微信好友画像类
    """

    def __init__(self):
        """
        初始化Bot对象
        """
        self.bot = Bot(cache_path=True)

    def execute(self):
        """
        执行类
        """
        self.friends = self.get_all_friends_object()
        if self.friends is False:
            return False

        sex_dict, province_dict, word_list = self.friends_image_statistic()
        self.render_page(sex_dict, province_dict, word_list)

    def get_all_friends_object(self):
        """
        获取所有好友对象
        """
        if self.bot is None:
            return False
        return self.bot.friends()

    def friends_image_statistic(self):
        """
        好友数据统计
        """
        if self.bot is None or not self.friends:
            return False

        # 统计性别
        sex_dict = {'male': 0, 'female': 0, 'other': 0}

        # 统计省份
        province_dict = {'北京': 0, '上海': 0, '天津': 0, '重庆': 0, '河北': 0, '山西': 0, '吉林': 0, '辽宁': 0, '黑龙江': 0,
 '陕西': 0, '甘肃': 0, '青海': 0, '山东': 0, '福建': 0, '浙江': 0, '台湾': 0, '河南': 0, '湖北': 0, '湖南': 0,
'江西': 0, '江苏': 0, '安徽': 0, '广东': 0, '海南': 0, '四川': 0, '贵州': 0, '云南': 0, '内蒙古': 0, '新疆': 0, '宁夏': 0, '广西': 0, '西藏': 0,
'香港': 0, '澳门': 0}

        # 统计签名
        signature_list = []

        for friend in self.friends[1:]:
            if friend.sex == 1:
                sex_dict['male'] += 1
            elif friend.sex == 2:
                sex_dict['female'] += 1
            else:
                sex_dict['other'] += 1

            friend_province = friend.province.encode('utf-8')
            if friend_province in province_dict.keys():
                province_dict[friend_province] += 1

            friend_signature = friend.signature.strip().replace('span', '').replace('class', '').replace('emoji', '')
            rep = re.compile("1f\d.+")
            friend_signature = rep.sub('', friend_signature)
            signature_list.append(friend_signature)

        # 切词
        signature_text  = "".join(signature_list)
        jieba_word_list = jieba.cut(signature_text, cut_all=True)
        word_text       = " ".join(jieba_word_list)
        word_split      = word_text.split(' ')
        
        # 获取停用词表
        stopword_list   = self.get_stop_word()
        # 过滤停用词
        word_list       = []
        for word in word_split:
            word = word.strip().encode('utf-8')
            if not len(word) or str(word) in stopword_list:
                continue
            word_list.append(word)

        return sex_dict, province_dict, word_list

    def get_sex_pie(self, sex_dict):
        """
        获取性别分布饼状图
        """
        sex_attr = ['男性', '女性', '未知']
        sex_v1   = [float(sex_dict['male']), float(sex_dict['female']), float(sex_dict['other'])]
        pie  = Pie('好友性别比例', width=1000)
        pie.add('', sex_attr, sex_v1, is_label_show=True)
        return pie

    def get_province_map(self, province_dict):
        """
        获取省份地图
        """
        value = province_dict.values()
        attr  = province_dict.keys()
        map = Map("好友全国分布", width=1000, height=600)
        map.add('', attr, value, maptype="china", is_visualmap=True, visual_text_color="#000")
        return map

    def get_wordcloud(self, word_list):
        """
        获取签名词云分布
        """
        # 计算词频
        word_frequence = {}
        for word in word_list:
            if word in word_frequence.keys():
                word_frequence[word] += 1
            else:
                word_frequence[word] = 1

        # 数据归一化
        max_num = max(word_frequence.values())
        for word in word_frequence:
            word_frequence[word] = word_frequence[word] * 100 / max_num

        name  = word_frequence.keys()
        value = word_frequence.values()
        wordcloud = WordCloud("好友签名词云", width=1000, height=620)
        wordcloud.add('', name, value, word_size_range=[20, 100])
        return wordcloud

    def render_page(self, sex_dict, province_dict, word_list):
        """
        渲染页面多图
        """
        page = Page()
        pie = self.get_sex_pie(sex_dict)
        map = self.get_province_map(province_dict)
        wordcloud = self.get_wordcloud(word_list)
        page.add(pie)
        page.add(map)
        page.add(wordcloud)
        page.render()

    def get_stop_word(self):
        """
        获取停用词表
        """
        fp = open('./stopword.dat', 'r')
        stopword_list = []
        for line in fp.readlines():
            line = line.strip()
            if not len(line):
                continue
            stopword_list.append(line)
        fp.close()

        return stopword_list

if __name__ == "__main__":
    obj = WxFriendImage()
    ret = obj.execute()