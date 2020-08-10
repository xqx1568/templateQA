'''
载入各种数据并初始化
'''
# -*- coding:utf-8 -*-

#对于每一个类，存储对应的ent和relation
#建立倒排索引
import os

root_name=["北京","上海","深圳"]
def loadSynonyms():
    newmap = {}
    newmap1={}
    i = 0
    with open('data/synonyms.txt','r') as fi:
        data = fi.readlines()
        for datai in data:
            arr = datai.strip().split('\t')
            newmap1 [i] =arr
            for word in arr:
                newmap[word] = i
            i += 1
            arr1 = [word.replace('人员','').replace('医保','') for word in arr ]
            newmap1 [i] =arr1
            for word in arr1:
                newmap[word] = i
            i += 1
        # 用map存储，相同意义的词映射到相同的id
    return newmap,newmap1


def getTriggerDic():
    '''
    预处理得到每个触发词对应的所有模板
    :return:
    '''
def loadEnt():
    with open('..\data\ent.txt','r',encoding='utf-8') as fi:
        data =fi.readlines()
        data = [datai.strip() for datai in data]
        datai = list.copy(data)
        dic=dict(zip(data,datai))
    return dic
def getMentiondic():
    ''' 获得 bert_ner 的结果'''
    # 建立空字典
    result = {}
    with open('data/match_1.txt', "r", encoding='utf-8') as fi:
        data =fi.readlines()
        for datai in data[1:]:
            arr = datai.split(' ',1)
            question = arr[0]
            mentions = arr[1].strip()[1:-1]
            mentionlist = mentions.split(',')
            mentionlist=[mention.strip()[1:-1] for mention in mentionlist]
            result[question] =mentionlist
    return result
all_ent = loadEnt()
def extractMSet():
    # '''读入长mention词典'''
    # with open('../datasets/predata/extraMentionlist.txt', 'r', encoding='utf-8') as inputfile:
    #     allmention = inputfile.readlines()
    #     allmention = [mention.strip().lower() for mention in allmention]
    #     # print(allmention)
    # return set(allmention)
    return [ent for ent in all_ent if len(ent)>4]
synonyms,synonyms_reverseDic = loadSynonyms()
print(synonyms)
print(synonyms_reverseDic)
triggerdic = getTriggerDic()
allmentiondic =getMentiondic()
extractMSet=extractMSet()
# class Sources:
#     def __init__(self):
#         self.all_ent= self.loadEnt()
#         # self.all_type = self.loadType()
#         self.synonyms = self.loadSynonyms()
#         self.triggerdic = self.getTriggerDic()
#     def loadSynonyms(self):
#         newmap={}
#         i=0
#         with open('data/synonyms.txt') as fi:
#             data= fi.readlines()
#             for datai in data:
#                 arr = datai.split('\t')
#                 for word in arr:
#                     newmap[word] = i
#                 i+=1
#              #用map存储，相同意义的词映射到相同的id
#         return newmap
#     def getTriggerDic(self):
#         '''
#         预处理得到每个触发词对应的所有模板
#         :return:
#         '''
#         pass
#     def loadEnt(self):
#         with open('..\data\ent.txt','r',encoding='utf-8') as fi:
#             data =fi.readlines()
#             data = [datai.strip() for datai in data]
#         return data