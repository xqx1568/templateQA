import json
class Template:
    def __init__(self,jsonstr):
        newdic =json.loads(jsonstr)
        self.name = newdic['name']
        self.slotlist =newdic['slotlist']
        self.triggers = newdic ['triggers']
        self.query = newdic['query']
        self.slotmap = newdic['slotmap']
        self.reply  = newdic['reply']
        self.param = newdic['param']
        self.info = newdic['info']
        self.intence =newdic['intence'] #可能分为 待遇，参保及缴费、一般（普遍适用
class Slot:
    def __init__(self):
        pass
class ERNode: #存储所识别的ent和rel
    '''
    每个entity或relation的存储数据结构
    '''
    def __init__(self,type_name,uri,lable,mention,pop,relnum):
        self.type =type_name #类型 对应template中的slot，用于填槽
        self.uri = uri #在知识库中的表现形式
        self.lable = lable #uri处理之后的形态，用于与mention匹配(若知识库中存在uri对应的label，适用label获得
        self.mention =mention
        self.score= 0 #初始化为0
        #可以预先获取,只有entity有
        self.popscore= pop
        self.relnum = relnum

        self.relscore=0
        self.rel='' #用于预存储分数最高的rel,避免重复计算
        self.rmention=''

class SlotMode:
    '''
    槽的结构
    '''
    def __int__(self,type_name):
        self.name = type_name
        self.relateTemplate  = []
        self.value = []
        self.scorelist=[]

