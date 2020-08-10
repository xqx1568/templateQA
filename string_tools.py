# coding=utf-8
import re

import pickle

import Levenshtein
import numpy as np
from bert_serving.client import BertClient
from jieba import posseg

import load_sources

bc = BertClient(ip="9.135.12.47",port=8080, port_out=443)#,port=8080,port_out=443)


# from transformers import BertModel, BertTokenizer, BertConfig
def str_handle(strin):
    strin = re.sub("[,，()（）\"‘“”、\\-/：:?？_]", "",strin)
    return strin
def Jaccard(a,b):
    if a ==None or b == None :
        raise TypeError("NONETYPE")
    if not isinstance(a,str) or not isinstance(b,str):
        raise TypeError("need str type")
    if a == b:
        return 1.0
    intersection = len(list(set(a).intersection(b)))
    union = (len(a) + len(b)) - intersection
    return 1.0*(intersection / union)
def getSim(liststr,str2,base=0):
    ans=0
    if str2.startswith('<'):
        str2 =str2[1:-1]
    for str1 in liststr:
        if len(str1)>1 and len(str2)<10 and str1 in str2:
            return 1
        if load_sources.synonyms[str1] == load_sources.synonyms[str2]:
            return 1
    if base == 1:
        return 0
    for str1 in liststr:
        if str1.startswith('<'):
            str1 = str2[1:-1]
        score = getSimilarity(str1,str2)
        if score>ans:
            ans = score
    return ans
def getSimilarity(str1,str2,tag=True):#tag为true：忽略大小写
    if str1 =='':
        if str2=='':
            return 1
        else:
            return 0
    if str1.endswith('?') or str1.endswith('？'):
        str1 = str1[:-1]
    if str2.endswith('?') or str2.endswith('？'):
        str2 = str2[:-1]

    if tag:
        str1 =str1.lower()
        str2 =str2.lower()
    if str1==str2 or load_sources.synonyms[str1] == load_sources.synonyms[str2]:
        return 1
    jac = Jaccard(str1,str2)
    lev =Levenshtein.ratio(str1,str2)
    bert_s =bert_similar(str1,str2)
    score = 0.35*jac+0.35*lev+0.3*bert_s #TODO 权重
    return score
def cosine(a, b):
    return a.dot(b) / (np.linalg.norm(a) * np.linalg.norm(b))

def bert_similar(str1,str2,tag=True):
    if str1.endswith('?') or str1.endswith('？'):
        str1 = str1[:-1]
    if str2.endswith('?') or str2.endswith('？'):
        str2 = str2[:-1]
    if tag:
        str1 =str1.lower()
        str2 =str2.lower()
    emb = np.array(bc.encode([str1, str2]))
    return cosine(emb[0],emb[1])
# fi=open('../datasets/otherdata/stop_words.txt','r',encoding='utf-8')
# stop_words =fi.readlines()
# stop_words =[ss.strip() for ss in stop_words]
# stop_words = set(stop_words)
def getKeyWord_single(question,entitylist,stop_words):
    # entitylist = [e[1:-1].split('_')[0] for e in entitylist]
    cut = posseg.cut(question)
    Keywords_List=[]
    print(question)

    for word,ctag in cut:
        print(word+':'+ctag)
        if word in stop_words:
            continue
        tag=False
        for e in entitylist:
            if e ==word or word in e:
                tag =True
                break
        if tag :
            continue

        if 'n' in ctag or ctag == 'ws' or ctag == 'v':
            Keywords_List.append(word)
    return Keywords_List

def getKeyWord():
    corpus =pickle.load(open('../datasets/questions/task1-4_2020.pkl', 'rb'))
    for sample in corpus:
        getKeyWord_single(sample)
def merge_stop_word():
    fi = open('../datasets/otherdata/scu_stopwords.txt','r',encoding='utf-8')
    fi1 = open('../datasets/otherdata/cn_stopwords.txt','r',encoding='utf-8')
    fi2= open('../datasets/otherdata/hit_stopwords.txt','r',encoding='utf-8')
    fi3 = open('../datasets/otherdata/baidu_stopwords.txt','r',encoding='utf-8')
    st = open('../datasets/otherdata/stop_words_1.txt','r',encoding='utf-8')
    data = set(fi.readlines())
    for x in fi1:
        data.add(x)
    for x in fi2:
        data.add(x)
    for x in fi3:
        data.add(x)
    for x in st:
        data.add(x)
    fo = open('../datasets/otherdata/stop_words.txt','w',encoding='utf-8')
    for x in data:
        fo.write(x)
    fi.close()
    fi1.close()
    fi2.close()
    fi3.close()

if __name__ == '__main__':
    corpus = pickle.load(open('../datasets/tempfiles/test_nel_v1.pkl', 'rb'))
    for sample in corpus:
        for a, b in sample['entitymap_f'].items():
            for bi in b:
                print(type(bi[1]))
    # getKeyWord()
    # i=0
    # while(i<100):
    #     print(getSimilarity('灭亡', '战役走向覆灭'))
    #     i+=1
    # # mentiondic = {}

    # str1 ='湖上草的'
    # str2 ='检测'
    # str3 = '检查项目'
    # print((bert_similar(str1,str2)-0.7)*2)
    # print(Jaccard(str1,str2))
    # print(Levenshtein.ratio(str1,str2))
    # print(getSimilarity(str1,str2))
    # print()
    # print((bert_similar(str1,str3)-0.7)*2)
    # print(Jaccard(str1,str3))
    # print(Levenshtein.ratio(str1,str3))
    # print(getSimilarity(str1,str3))
    # # getKeyWord_single('<ENTITY>中X母亲的住所是哪里？',[],stop_words)
    # pass