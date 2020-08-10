# -*- coding: utf-8 -*-
import pickle
import jieba
import csv
from jieba import posseg
import re
from itertools import islice
# lac =thulac.thulac()
from tqdm import tqdm

#收集train里面的所有mention 当无mention时，试图利用词典解决(利用了分词结果，一般不会出现此情况
import load_sources

contact_word= (['和', '、', '与', '以及', '又是', '并且', '且', '还', '还有', '而且', '且有', '又'])

stop_prop=[]
uesless_entity=[]

stop_mention=['人员','医保']
def get_mention(question):
    '''获得所有可能的mention'''
    uent=''
    for te in uesless_entity:
        if te in question:
            uent =te
            break
    ner_result = get_predict_mention(question)
    # print(mentionlist)
    lmentionlist = get_long_mention(question)
    for mention in lmentionlist:
        tlist =[]
        for mention_s in ner_result:
            if mention_s in mention:
                tlist.append(mention_s)
        if len(tlist)>1:
            for mention_s in tlist:
                ner_result.remove(mention_s)
        if mention not in ner_result:
            ner_result.append(mention)
    ner_result = get_rule_mention(ner_result,question) #entity_special内存的是只需召回长得一样的mention
    #TODO cheack
    cut = posseg.cut(question)
    tmplist=[]
    tt = " ".join(ner_result)
    for x,y in cut:
        tmplist.append((x,y))
    if len(tmplist)- len(ner_result)>2: #将未找到的并列的mention提出
        i=0
        while i<len(tmplist)-2:
            pre = tmplist[i][0]
            cur = tmplist[i+1][0]
            nex = tmplist[i+2][0]
            if cur in contact_word:
                if pre in tt and nex not in tt:
                    i+=3
                    ner_result.append(nex)
                    continue
                elif pre not in tt and nex in tt:
                    i+=3
                    ner_result.append(pre)
                    continue
            i+=1
    if len(ner_result)==0:
        for word,tag in tmplist:
            if 'n' in tag  or tag == 'i'  or tag == 'j' or tag == 'l':
                ner_result.append(word)
    #如果识别的ent和re冲突，保留re

    return [e1 for e1 in ner_result if e1 not in stop_mention]

def get_long_mention(sentence, maxlen=30):
    '''利用正向最大匹配获取长实体可能对应的mention
    此函数处理最小长度5，最大长度30的mention
    （可以调整长度）
    '''
    sentence = re.sub('\".+?\"|《.+?》|“.+?”', '', sentence)
    if re.search('(\?|!|.|！|。|？)$', sentence):
        sentence = sentence[:-1]
    mentionlist = []
    while len(sentence) > 0:
        i = min(len(sentence), maxlen)
        while i > 5:
            segstr = sentence[:i]
            if segstr.lower() in load_sources.extractMSet:
                mentionlist.append(segstr)
                sentence = sentence[i:]
                break
            else:
                i -= 1
        sentence = sentence[1:]
    return mentionlist
def get_rule_mention(mentionlist,question):
    '''根据规则获取mention'''
    mentioncandidate = re.findall('\".+?\"|《.+?》|“.+?”', question)
    mentioncandidate = [mention for mention in mentioncandidate]
    for mention in mentioncandidate:
        if mention in mentionlist:
            continue
        x =''
        for mention_s in mentionlist:
            if mention_s in mention and question.count(mention_s) == 1:#重复并且可以根据规则过滤
                x=mention_s
                break
        if x !='':
            mentionlist.remove(x)
            mentionlist.append(mention)

    tmp = re.findall('[a-z][a-z\s.,!！_]+',question) #获取所有英文和符号组成的子串
    for mention_s in tmp:
        tag=False
        tlist=[]
        for mention in mentionlist:
            if mention in mention_s:
                tlist.append(mention)
            elif mention_s in mention:
                tag = True
                break
        for t in tlist:
            mentionlist.remove(t)
        if not tag:
            mentionlist.append(mention_s)
    tmp = re.findall('\d+年\d+月\d+日|\d+年\d+月\d+号|\d+\.\d+\.\d+|\d+-\d+-\d+|\d+月\d+日|\d+月\d+号|\d+年\d+月|\d+年|\d+',question)

    for mention_s in tmp:
        tag = False
        if mention_s.isdigit():# 如果为纯数字且在别的mention里出现了就把它忽略
            tag =True
        for mention in mentionlist:
            if mention in mention_s:
                mentionlist.remove(mention)
                mentionlist.append(mention_s)
                break
            elif mention_s in mention:
                if not tag:
                    mentionlist.remove(mention)
                    mentionlist.append(mention_s)
                    break
    return mentionlist

def get_predict_mention(question):
    # TODO 调用ner模型
    # 现在：读取ner结果
    if question in load_sources.allmentiondic:
        return load_sources.allmentiondic[question]
    return []

if __name__ == '__main__':
    pass


