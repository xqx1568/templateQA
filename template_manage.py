#相关计算参数
from bean import SlotMode

para1=0.5
def templateChoose(goalmap,entlist,Sources):
    '''
    利用已知的信息匹配模板并打分
    :param goalmap:
    :param entmap:
    :param relmap:
    :return:
    '''
    scoremap = {}
    tmap=[]
    for ent in entlist:
        if ent.type in tmap:
            slotmode =tmap[ent.type]
        else:
            slotmode = SlotMode(ent.type)
        slotmode.value.append(entlist)
        slotmode.scorelist.append(ent.score) #ent的分数作为槽值的分数
        tmap[ent.type]=slotmode
    templatemap ={}
    for slot in tmap.values():
        templatelist =slot.relatetemplate
        if len(templatelist)==1: #如果只有一个对应的槽，给予高置信度
            template = Sources.templatemap[templatelist[0]]
        else:
            for tempname in templatelist:
                template = Sources.templatemap[tempname]
                if tempname in templatemap:
                #如果是单个槽多个ent，选择分数最高的ent填入，如果是多槽则分别填入计算分数
                    pass
    for tname in goalmap:
        goalmap[tname]=goalmap[tname]*para1
    return Sources.templatemap[templatemap.keys()[0]]
def template_fillslot(template,entlist):
    '''
    将所得的槽值填入，并进行可行性测试得到查询语句
    :return:
    '''
