'''
KBQA入口
槽识别、填槽、转sparql查询
'''
import load_sources
from getmention import get_mention
from kb_tools import findPath, findLength
from string_tools import str_handle

from nlu import getEntCandidate, getGoal, entDisambiguation, getRel
from template_manage import templateChoose

from kb_tools import hasPath
class Talk:
    def __init__(self):
        pass
        #在此处初始化各种文件
    def getAnswer(self,sentence):#问答接口
        # sentence = str_handle(sentence)
        #1.通过ner得到mention
        mentionlist=get_mention(sentence)
        #简单使用在句中的位置给entity排序
        tmap={}
        for mention  in mentionlist:
            index = sentence.index(mention)
            tmap[mention] = index
        tlist = sorted(tmap.items(),key=lambda x:x[1],reverse=False)
        mentionlist=[tm[0] for tm in tlist]

        entitys,iquestion = getEntCandidate(mentionlist,question)
        # entitys =entDisambiguation(entitys,question) #将relation存到对应的ent中
        # relations = getRel(entitys)
        # goallist = getGoal(sentence)
        # template = templateChoose(goallist,entitys,relations,self.Sources)


        #如果没有说明地区，展示北京地区的结果
        #TODO 策略二：也可以展示所有地区的结果
        print(entitys)
        tag=False
        for ent in entitys[0]:
            if ent in load_sources.root_name:
                tag=True
                break
        if not  tag:
            for loc in load_sources.root_name:
                tt = entitys[0][0]
                if hasPath(loc,tt):
                    entitys.insert(0, [loc])
                    break
        #从root开始选取有向最短路径,保证后面的路径搜索
        for i in range(1,len(entitys)-1):
            tmplen =10
            k = i+1
            for j in range(i+1,len(entitys)):
                ll=findLength(entitys[i][0],entitys[j][0])
                if ll<tmplen:
                    tmplen = ll
                    k=j
                    if ll==1:
                        break
            entitys[j],entitys[k] = entitys[k],entitys[j]
        reply = self.ask_bot(entitys)
        return reply
    def ask_bot(self,entitys):#在这里进行问答搜索和后处理
        return findPath(entitys)
if __name__ == '__main__':
    talk = Talk()
    question = '大学生应该如何缴费？'
    answer = talk.getAnswer(question)

    print(answer)
    # while True:
    #     question = input('Please input your question:')
    #     answer=talk.getAnswer(question)