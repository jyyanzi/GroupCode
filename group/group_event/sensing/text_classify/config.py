#-*- coding: UTF-8 -*-

import os
import re
import csv
import sys
import scws
from decimal import *


abs_path = '/home/ubuntu12/GroupEvent/group_event/group_event/sensing/topic'

name_list = ['art','computer','economic','education','environment','medicine',\
            'military','politics','sports','traffic','life',\
            'anti-corruption','employment','fear-of-violence','house',\
            'law','peace','religion','social-security']

zh_category = [u'文体类_娱乐',u'科技类',u'经济类',u'教育类',u'民生类_环保',u'民生类_健康',\
        u'军事类',u'政治类_外交',u'文体类_体育',u'民生类_交通',u'其他类',\
        u'政治类_反腐',u'民生类_就业',u'政治类_暴恐',u'民生类_住房',u'民生类_法律',\
        u'政治类_地区和平',u'政治类_宗教',u'民生类_社会保障']

number_dict = {'life': 7317, 'law': 20075, 'computer': 4900, 'house': 24381, 'peace': 9666, 'politics': 3817, 'fear-of-violence': 8391, \
                'sports': 4204, 'environment': 3852, 'religion': 15885, 'economic': 6361, 'traffic': 3425, 'anti-corruption': 19934,\
                'military': 4364, 'medicine': 3137, 'art': 7163, 'education': 5341, 'employment': 13925, 'social-security': 9793}

cx_dict = ['an','Ng','n','nr','ns','nt','nz','vn','@']#关键词词性词典
eng2chi_dict = { name_list[i]:zh_category[i]for i in range(len(name_list))}

## 加载分词工具

SCWS_ENCODING = 'utf-8'
SCWS_RULES = '/usr/local/scws/etc/rules.utf8.ini'
CHS_DICT_PATH = '/usr/local/scws/etc/dict.utf8.xdb'
CHT_DICT_PATH = '/usr/local/scws/etc/dict_cht.utf8.xdb'
IGNORE_PUNCTUATION = 1


ABSOLUTE_DICT_PATH = os.path.abspath(os.path.join(abs_path, './dict'))
CUSTOM_DICT_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'userdic.txt')
EXTRA_STOPWORD_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'stopword.txt')
EXTRA_EMOTIONWORD_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'emotionlist.txt')
EXTRA_ONE_WORD_WHITE_LIST_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'one_word_white_list.txt')
EXTRA_BLACK_LIST_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'black.txt')


def load_scws():
    s = scws.Scws()
    s.set_charset(SCWS_ENCODING)

    s.set_dict(CHS_DICT_PATH, scws.XDICT_MEM)
    s.add_dict(CHT_DICT_PATH, scws.XDICT_MEM)
    s.add_dict(CUSTOM_DICT_PATH, scws.XDICT_TXT)

    # 把停用词全部拆成单字，再过滤掉单字，以达到去除停用词的目的
    s.add_dict(EXTRA_STOPWORD_PATH, scws.XDICT_TXT)
    # 即基于表情表对表情进行分词，必要的时候在返回结果处或后剔除
    s.add_dict(EXTRA_EMOTIONWORD_PATH, scws.XDICT_TXT)

    s.set_rules(SCWS_RULES)
    s.set_ignore(IGNORE_PUNCTUATION)
    return s

def load_one_words():
    one_words = [line.strip('\r\n') for line in file(EXTRA_EMOTIONWORD_PATH)]
    return one_words

def load_black_words():
    one_words = [line.strip('\r\n') for line in file(EXTRA_BLACK_LIST_PATH)]
    return one_words

single_word_whitelist = set(load_one_words())
black_word = set(load_black_words())



def load_train():#读取生成之后的tfidf文档，对新的用户进行话题分类

    domain_dict = dict()
    domain_count = dict()
    for i in name_list:
        reader = csv.reader(file(abs_path + '/topic_dict/%s_tfidf.csv' % i, 'rb'))
        word_dict = dict()
        count = 0
        n = 0
        for f,w_text in reader:
            f = f.strip('\xef\xbb\xbf')
            word_dict[str(w_text)] = Decimal(f)
            count = count + Decimal(f)
            n = n + 1
            if n >= int(number_dict[i]*0.5):
                break
        domain_dict[i] = word_dict
        domain_count[i] = count

    len_dict = dict()
    total = 0
    for k,v in domain_dict.items():
        len_dict[k] = len(v)
        total = total + len(v)
    
    return domain_dict,domain_count,len_dict,total

DOMAIN_DICT,DOMAIN_COUNT,LEN_DICT,TOTAL = load_train()



def sta_dict():  #标准化话题字典

    topic_dict = dict()
    for name in name_list:
        topic_dict[name] = 0

    return topic_dict

TOPIC_DICT = sta_dict()
    

def cut_filter(text):
    pattern_list = [r'\（分享自 .*\）', r'http://\w*']
    for i in pattern_list:
        p = re.compile(i)
        text = p.sub('', text)
    return text

def re_cut(w_text):#根据一些规则把无关内容过滤掉
    
    w_text = cut_filter(w_text)
    w_text = re.sub(r'[a-zA-z]','',w_text)
    a1 = re.compile(r'\[.*?\]' )
    w_text = a1.sub('',w_text)
    a1 = re.compile(r'回复' )
    w_text = a1.sub('',w_text)
    a1 = re.compile(r'\@.*?\:' )
    w_text = a1.sub('',w_text)
    a1 = re.compile(r'\@.*?\s' )
    w_text = a1.sub('',w_text)
    if w_text == u'转发微博':
        w_text = ''

    return w_text