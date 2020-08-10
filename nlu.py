import re
import Levenshtein
import jieba

import load_sources
from bean import ERNode
from kb_tools import getRelOFE


def getGoal(question,templatelist):
    '''
    根据触发词获得相关模板
    :param question:
    :param templatelist:
    :return:
    '''
    redic={}
    for template in templatelist:
        for trigger in template.triggers:
            if trigger in question:
                redic.setdefault(template.name,0)
                redic[template.name] = re[template.name]+1
    return redic
        
def getEntCandidate(ementionlist,question,n=3):#只返回topn的ent
    '''
    :param ementionlist: mentionlist
    :param sources:
    :param n:
    :return relist:
    获得候选entity
    1.别名，缩写等字典
    2.完全匹配
    3.实体完全包含e-mention
    4.编辑距离>0.6
    5.可拓展：
    '''
    pop = 0
    relnum =0
    relist = []
    for mention in ementionlist:
        mention = re.sub('\\s', '', mention)
        if len(mention) == 0:
            continue
        alp_tag = False
        if re.search('[A-Za-z]', mention):
            mention = mention.lower()
            alp_tag = True
        # exmentions = sources.extend_mention(mention)
        if mention in load_sources.synonyms:
            exmentions = load_sources.synonyms_reverseDic[load_sources.synonyms[mention]]
        else:
            exmentions=[mention]
        entitylist = set()
        for exmention in exmentions:
            if "<" + exmention + ">" in load_sources.all_ent:
                entitylist.add(ERNode('',"<" + exmention + ">",mention,mention,pop,relnum))
        print('fuzzy match:')
        print(mention)
        if len(mention) == 1:
            if len(entitylist) != 0:  # mention长度为1只考虑相等的情况
                relist.add(list[entitylist])
            continue
        for exmention in exmentions:
            for entity, m in load_sources.all_ent.items():
                if exmention == m:
                    entitylist.add(ERNode('', entity, exmention, exmention, pop, relnum))
            for entity, m in load_sources.all_ent.items():
                if exmention in m:
                    if re.search('[A-Za-z]', m) and Levenshtein.ratio(m, mention) > 0.6:
                        entitylist.add(ERNode('', entity, m, exmention, pop, relnum))
                    if len(m) - len(
                            exmention) <= 5:  # 可能mention识别不完全，长度差距大的应用额外字典解决，否则此处召回过多无用候选。后期可以在这里加入in question进行过滤
                        entitylist.add(ERNode('', entity, m, exmention, pop, relnum))
                elif m in exmention and Levenshtein.ratio(m, exmention) > 0.6:  #
                    entitylist.add(ERNode('', entity, m, exmention, pop, relnum))
        if len(entitylist) == 0:
            print("not in kb:")
            print(str(exmentions))
        else:  # 无召回将会被过滤
            question = question.replace(mention,'#') #TODO 可能会引入不想要的替换，应改用start end
            relist.append(list(entitylist))
    #temp strategy
    newrelist =[]
    for ll in relist:
        tll=[]
        for e in ll:
           tll.append(e.uri)
        newrelist.append(list(set(tll)))
    return newrelist,question
def entDisambiguation(inlist,question,n=3):
    '''
    :param entmap: mention-entitylist
    :param question:
    :return:
    1.实体流行度（出现的次数以及所连接的不同的prop的数量）
    2.ent_prop和 mention上下文的相似度
    3.mention和ent的str相似度

    策略1：
    先用实体流行度进行过滤
    再用策略2过滤
    最后用相似度排序
    '''
    relist=[]
    for entlist in inlist:
        if len(entlist)==1: #不用排序和处理
            continue
        for ent in entlist:
            ent.popscore = getEntityC()
            ent.relnum = getRelationNum()
        #1
        sortedent =sorted(entlist,key= lambda x:x.popscore,reverse=True)
        basepop = sortedent[0].popscore
        if basepop//100>0:
            i=0
            for ent in sortedent:
                if ent.popscore<basepop/100:
                    break
                    i+=1
            sortedent=sortedent[:i]
        # sortedent2 = sorted(entlist,key=lambda x:x.relnum,reverse=True)
        # basenum = sortedent2[0].relnum
        # for ent in sortedent2:
        #     if ent.relnum-basenum>threshould:#TODO 设定阈值
        #         break
        #     if ent not in sortedent:
        #         sortedent.append(ent)
        #2
        if len(sortedent)>1:
            for ent in sortedent:
                rellist = getRelOFE(ent)  # 获得ent相关的rel
                tmplist = []
                tag=False
                for rel in rellist:
                    if rel in question:
                        if not tag:
                            tmplist=[] #清空前面的储存
                        tmplist.append((rel,rel, 1))
                        tag = True
                    elif tag:
                        continue
                    else:
                        ss0 = 0
                        rm = ''
                        for word in cut:
                            if '#' in word:
                                continue
                            ss = Levenshtein.ratio(rel, word)
                            if ss > 0.6 and ss > ss0:
                                ss0 = ss
                                rm = word
                        if ss0 != 0:
                            tmplist.append((rel,rm, ss0))

                if len(tmplist) > 0:
                    if len(tmplist) > 2:
                        tmplist_s = sorted(tmplist, key=lambda x: x[1], reverse=True)
                        propMap[rm] = tmplist_s[:2]
                    else:
                        propMap[rm] = tmplist
                    cut.remove(rm)  # TODO 设定阈值。如果分数大于阈值，将原句中对应的mention替换，继续搜索
                    #小于阈值则 ent.relscore=0，无过滤意义
        #3
        for ent in sortedent:
            ent.score=getSimilarity(mention,ent)
        sortedent3 = sorted(sortedent,key=lambda x:x.score)

        relist.append(sortedent3[0])
    return relist
def getRel(entmap,question):
    proplist=[]
    for mention,entlist in entmap:
        question = question.replce(mention, '#')
        cut = jieba.lcut() #或者用滑动窗口
        for ent in entlist:
            rellist = getRelOFE(ent)#获得ent相关的rel
            tmplist = []
            for rel in rellist:
                ss0 = 0
                rm = ''
                if rel in question:
                    tmplist.append((rel,1))
                    rm=rel
                else:

                    for word in cut:
                        if '#' in word:
                            continue
                        ss=Levenshtein.ratio(rel,word)
                        if ss>0.6 and ss>ss0:
                            ss0 = ss
                            rm = word
                    if ss0!=0:
                        tmplist.append((rel,ss0))
                if len(tmplist) >0:
                    if len(tmplist)>2:
                        tmplist_s = sorted(tmplist, key=lambda x: x[1], reverse=True)
                        proplist[rm]=tmplist_s[:2]
                    else:
                        proplist[rm]=tmplist
                    cut.remove(rm)#TODO 设定阈值。如果分数大于阈值，将原句中对应的mention替换，继续搜索
    return proplist






