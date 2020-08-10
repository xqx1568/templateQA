from neo4j import GraphDatabase
import time
import itertools
#neo4j
from sklearn.utils.extmath import cartesian

driver = GraphDatabase.driver("bolt://10.68.48.80:7687", auth=("neo4j", "111"))
session = driver.session()
stop_word=["参保及缴费","待遇"]
def getRelationNum(entity):
    '''根据实体名，得到与之相连的关系数量'''
    query= "match p=(a:Entity)-[r1:Relation]-() where a.name=$name return count(DISTINCT r1)"
    res = session.run(query,name=entity)
    ans = 0
    for record in res:
        ans = record.values()[0]
    return ans
def getEntityC(entity):#TODO
    '''根据实体名，得到它出现的次数'''
    query = "match p=(a:Entity)-[r1:Relation]-() where a.name=$name return count(p)"
    res = session.run(query, name=entity)
    ans = 0
    for record in res:
        ans = record.values()[0]
    return ans
def getRelOFE(entity):
    '''根据实体名，得到所有相关的relation'''
    query = "match p=(a:Entity)-[r1:Relation]-() where a.name=$name return DISTINCT r1.name"
    res = session.run(query, name=entity)
    ans = []
    for record in res:#每个record是一个key value的有序序列
        print(record)
        ans.append([record['r1.name']])
    return ans
def findPath(entitys):
    '''找到节点之间的路径'''
    ans = ''

    start=[]
    for elsit in entitys:

        if start==[]:
            start=elsit
        else:
            start=itertools.product(start,elsit)
    for car_d in start:
        ans+=findPath_1(car_d)
        ans+='\n'
    return ans
def findPath_1(entitys):
    query = "MATCH p="
    for i in range(0,len(entitys)):
        query+="(e{i})-[*]-".format(i=i)
    query+=">(leaf) WHERE "
    for i in range(0,len(entitys)):
        query+="e{i}.name = \"{ent}\"".format(i=i,ent=entitys[i])
        if i!=len(entitys)-1:
            query+=" AND "
    query+=" RETURN extract(r IN nodes(p) | r)"
    # query = "MATCH p=(e1)-[*]-(e2)-[*]->(leaf) WHERE e1.name = \"{e1}\" AND e2.name = \"{e2}\" RETURN extract(r IN nodes(p) | r)".format(
    #     e1=e1, e2=e2)
    print(query)
    res = session.run(query)
    stra = ''
    path = []
    i = 0
    for record in res:
        print("record:{record}".format(record=record
                                ))
        tmplist = []
        strb = ''
        record = record[0]
        for nu in range(i, len(record)):
            x = record[nu]
            if x['name'] in stop_word:
                continue
            tmplist.append(x['name'])
            if x['name'] == entitys[-1]:
                stra = "的".join(tmplist) + "：\n"
                tmplist = []
                i = nu + 1
                continue
            if x['name'] in x:
                strb = "\t" + "的".join(tmplist) + ":" + x[x['name']]
            if strb!="" and nu == len(record) - 1:
                path.append(strb)
    ans = stra + "\n".join(path)
    if ans == '':
        ans='不好意思，暂时无法回答您的问题'
    return ans.strip()
def hasPath(e1,e2):
    query = "MATCH p=(e1)-[*]->(e2) WHERE e1.name = \"{e1}\" and e2.name = \"{e2}\" RETURN length(p)".format(
        e1=e1,e2=e2)
    try:
        res = session.run(query)
        for record in res:
            if record[0] != 0:
                return True
    except:
        pass
    return False
def findPath1(e1,e2,e3):
    '''找到两个节点之间的路径'''
    query = "MATCH p=(e1)-[*]->(e2)-[*]->(e3)-[*]->(leaf) WHERE e1.name = \"{e1}\" AND e2.name = \"{e2}\" AND e3.name = \"{e3}\" RETURN extract(r IN nodes(p) | r)".format(e1=e1,e2=e2,e3=e3)
    print(query)
    res = session.run(query)
    stra = ''
    path = []
    ans = ''
    i = 0
    for record in res:
        tmplist = []
        strb = ''
        record = record[0]
        for nu in range(i, len(record)):

            x = record[nu]
            if x['name'] in stop_word or x['name']==e3:
                continue
            tmplist.append(x['name'])
            if x['name'] == e2:
                tmplist.append(e3)
                stra = "的".join(tmplist) + "：\n"
                tmplist = []
                i = nu + 1
                continue
            if x['name'] in x:
                strb = "\t" + "的".join(tmplist) + ":" + x[x['name']]
            if nu == len(record) - 1:
                path.append(strb)

    return stra + "\n".join(path)
def findLength(e1,e2):
    query ="MATCH p=shortestpath((p1)-[*..10]-(p2)) where p1.name =\"{p1}\" AND p2.name = \"{p2}\" RETURN length(p)".format(p1=e1,p2=e2)
    try:
        res = session.run(query)
        for record in res:
            return record[0]
    except:
        pass
    return 0
def findPathFromRoot(e1):
    query = "MATCH p=(root)-[*]->(e1) WHERE e1.name = \"{e1}\" RETURN extract(r IN nodes(p) | r)".format(
        e1=e1)
    res = session.run(query)
    stra = ''
    path = []
    ans = ''
    i = 0
    print(query)
    print(res)
    for record in res:
        print(record)
        # tmplist = []
        # strb = ''
        # record = record[0]
        # for nu in range(i, len(record)):
        #     x = record[nu]
        #     if x['name'] in stop_word:
        #         continue
        #     tmplist.append(x['name'])
        #     if x['name'] == e2:
        #         stra = "的".join(tmplist) + "：\n"
        #         tmplist = []
        #         i = nu + 1
        #         continue
        #
        #     if x['name'] in x:
        #         strb = "\t" + "的".join(tmplist) + ":" + x[x['name']]
        #     if nu == len(record) - 1:
        #         path.append(strb)

    return stra + "\n".join(path)
def getAllent(path = '..\data\ent.txt'):
    writer = open(path,'w',encoding='utf-8')
    query = "MATCH (n) return distinct n.name"
    res = session.run(query)
    i=0
    for record in res:
        i+=1
        if record['n.name'] == None:
            continue
        writer.write(record['n.name']+'\n')
    print(i)
    writer.close()
if __name__ == '__main__':
    # getAllent()
    findLengthFromRoot('缴费标准')
    # a =findPath1('上海','失业人员','缴费标准')
    # findPathFromRoot('参保及缴费')
    # findPath1('上海','退休人员70岁以下','征缴基数')
    # getRelOFE('征缴基数')