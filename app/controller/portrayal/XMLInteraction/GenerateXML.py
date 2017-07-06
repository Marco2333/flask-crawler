#!/usr/bin/python
#-*-coding:utf-8-*-
'''@author:duncan'''

import xml.dom.minidom
import sys
from ..import config
reload(sys)
sys.setdefaultencoding('utf8')

project_path = config.project_path

# 获取DOM树实现对象
impl = xml.dom.minidom.getDOMImplementation()

# 生成某一用户的XML文件
def GenerateUserXml(twitter_user):

    dom = impl.createDocument(None,'TwitterUser',None)
    root = dom.documentElement

    # 创建子节点
    BasicInfo = dom.createElement('基本信息')
    ImplicitInfo = dom.createElement('隐性属性')
    root.appendChild(BasicInfo)
    root.appendChild(ImplicitInfo)

    # id 节点
    IdE = dom.createElement('user_id')
    IdT = dom.createTextNode(twitter_user.id)
    IdE.appendChild(IdT)
    #
    # 姓名节点标签
    nameE = dom.createElement('name')
    # 标签增加属性
    nameE.setAttribute("coding","utf-8")

    # 姓名标签内容,将编码方式转换一下
    nameT = dom.createTextNode(twitter_user.name.decode('ISO-8859-2').encode('utf-8'))
    # 将内容加入标签中
    nameE.appendChild(nameT)

    # scrren_name 节点
    SNE = dom.createElement('screen_name')
    SNT = dom.createTextNode(twitter_user.screen_name)
    SNE.appendChild(SNT)

    # id 节点
    LoE = dom.createElement('地理位置')
    if twitter_user.location != "" and twitter_user != None:
        LoT = dom.createTextNode(twitter_user.location)
    else:
        LoT = dom.createTextNode("空")
    LoE.appendChild(LoT)

    # 是否认证节点
    VerE = dom.createElement('是否认证过')
    if twitter_user.verified == 1:
        verified = '是'
    else:
        verified = '否'
    VerT = dom.createTextNode(verified)
    VerE.appendChild(VerT)

    # 粉丝数 节点
    FLE = dom.createElement('粉丝数')
    FLT = dom.createTextNode(str(twitter_user.followers_count))
    FLE.appendChild(FLT)

    # 朋友数 节点
    FriendsE = dom.createElement('朋友数')
    FriendsT = dom.createTextNode(str(twitter_user.friends_count))
    FriendsE.appendChild(FriendsT)

    # 推文数 节点
    STE = dom.createElement('推文数')
    STT = dom.createTextNode(str(twitter_user.statuses_count))
    STE.appendChild(STT)

    # 点赞次数数 节点
    FAvE = dom.createElement('点赞数')
    FAvT = dom.createTextNode(str(twitter_user.favourites_count))
    FAvE.appendChild(FAvT)


    # 把基本信息加入到BasicInfo节点中
    BasicInfo.appendChild(IdE)
    BasicInfo.appendChild(nameE)
    BasicInfo.appendChild(SNE)
    BasicInfo.appendChild(LoE)
    BasicInfo.appendChild(VerE)
    BasicInfo.appendChild(FLE)
    BasicInfo.appendChild(FriendsE)
    BasicInfo.appendChild(FAvE)
    BasicInfo.appendChild(STE)

    # 用户类别
    CategoryE = dom.createElement("用户领域")
    CategoryT = dom.createTextNode(twitter_user.category)
    CategoryE.appendChild(CategoryT)

    # 用户心里状态标签
    FeelingE = dom.createElement("近期心理状态")
    FeelingT = dom.createTextNode(config.psychological[twitter_user.psy])
    FeelingE.appendChild(FeelingT)

    # 用户兴趣爱好标签
    InterestE = dom.createElement("兴趣爱好")
    InterestT = dom.createTextNode(twitter_user.interest_tags)
    InterestE.appendChild(InterestT)

    # 用户社交影响力标签
    InfluenceE = dom.createElement("影响力分数")
    InfluenceT = dom.createTextNode(str(twitter_user.influenceScore))
    InfluenceE.appendChild(InfluenceT)

    # 用户社交影响力标签
    RankInfluE = dom.createElement("影响力等级")
    RankInfluT = dom.createTextNode(config.rank_influence[twitter_user.rank_influ])
    RankInfluE.appendChild(RankInfluT)

    # 将隐性属性标签加入到隐性标签中
    ImplicitInfo.appendChild(CategoryE)
    ImplicitInfo.appendChild(FeelingE)
    ImplicitInfo.appendChild(InterestE)
    ImplicitInfo.appendChild(InfluenceE)
    ImplicitInfo.appendChild(RankInfluE)

    # 将用户信息写入文件
    with open(config.XML_path + '%s.xml' % twitter_user.screen_name,'w') as f:
        dom.writexml(f,addindent=" ",newl='\n')

# 生成XML文件
def GenerateUsersXml(users):
    count = 0
    for twitter_user in users:
    # 创建DOM树,'TwitterUsers'为根节点名称
        GenerateUserXml(twitter_user)
        count += 1
        print "finished %d users" % count
