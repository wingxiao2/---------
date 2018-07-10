
# coding: utf-8

# In[13]:



import requests 
from Crypto.Cipher import AES
from bs4 import BeautifulSoup
from lxml import etree
import base64
import json
import os
import time
import csv
import re

headers={    #请求头部
   'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}
#获得参数
def get_params(PageNum):
    #pageNum为传入的页数,offset为评论的偏移量
    PageNum = (PageNum-1)*20
    #第一个参数
    first_param = "{ rid: \"R_SO_4_418603077\", offset: "+str(PageNum)+", total: \"false\", limit: \"20\", csrf_token: \"\" }"
    second_param = "010001" # 第二个参数
    #第三个参数
    forth_param = "0CoJUm6Qyw8W8jud"
    first_key = forth_param
    #只要是16位就可以
    second_key ='nienienienienien'
    h_encText = AES_encrypt(first_key,first_param)
    h_encText = AES_encrypt(second_key,h_encText)
    return h_encText


#解密过程，参考了py3.6的aes加密，此处容易出现编码问题，谨慎
def AES_encrypt(key, text):
    iv = '0102030405060708'
    pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
    text = pad(text)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    encrypt_aes = encryptor.encrypt(text)
    encrypt_text = base64.b64encode(encrypt_aes).decode('utf8')
    return encrypt_text
#这个值通过分析没有影响，直接进行引用
def get_encSecKey():
    encSrcKey = "6469da86a183fc2fc9df65ac98f67138c8d3048d0626714fe646ecb564d4f8cd386a9c9618bb8a4f2929e50ba32e8991266aba783975e39cc7cf8a61cc3ba76c81c64a3414f38d604ca1bf9f4647c29cd92d5b362eff15cf7bb1e3a52df798a52aafac2f09420a68af9686e2c1a294ccf426b5aac64899486011fc7eca8e79b8"
    return encSrcKey

#获得评论json的数据
def get_json(url, params, encSecKey):
    data = {
         "params": params,
         "encSecKey": encSecKey
    }
    response = requests.post(url, headers=headers, data=data)
    return response.content

# 抓取热门评论，返回热评列表
def get_hot_comments(url):
    hot_comments_list = []
    
    hot_comments_list.append(u"歌曲名 \n")
    params = get_params(1) # 第一页
    encSecKey = get_encSecKey()
    json_text = get_json(url,params,encSecKey)
    json_dict = json.loads(json_text)
    hot_comments = json_dict['hotComments'] # 热门评论
    #print("共有%d条热门评论!" % len(hot_comments))
    for item in hot_comments:
            comment1 = item['content'] # 评论内容
            comment=comment1.replace('\n',' ')
            likedCount = item['likedCount'] # 点赞总数
            #comment_time = item['time'] # 评论时间(时间戳)
            #userID = item['user']['userID'] # 评论者id
            nickname = item['user']['nickname'] # 昵称
            #avatarUrl = item['user']['avatarUrl'] # 头像地址
            #此处只爬取热评 所以将其它的信息全部注释掉了
            #comment_info = str(nickname) + " " + str(avatarUrl) + " " + str(comment_time) + " " + str(likedCount) + " " + comment + u"\n"
            comment_info =str(nickname) + " " + str(likedCount) + " " + comment + u"\n"
            comment_info =comment + u"\n\n"
            hot_comments_list.append(comment_info)
    return hot_comments_list
    print(hot_comments_list)
    
    
# 抓取某一首歌的全部评论
def get_all_comments(url):
    all_comments_list = [] # 存放所有评论
    #all_comments_list.append(u"用户ID 用户昵称 用户头像地址 评论时间 点赞总数 评论内容\n") # 头部信息
    params = get_params(1)
    encSecKey = get_encSecKey()
    json_text = get_json(url,params,encSecKey)
    json_dict = json.loads(json_text)
    comments_num = int(json_dict['total'])
    if(comments_num % 20 == 0):
        page = comments_num / 20
    else:
        page = int(comments_num / 20) + 1
    print("共有%d页评论!" % page)
    for i in range(page):  # 逐页抓取
        params = get_params(i+1)
        encSecKey = get_encSecKey()
        json_text = get_json(url,params,encSecKey)
        json_dict = json.loads(json_text)
        if i == 0:
            print("共有%d条评论!" % comments_num) # 全部评论总数
        for item in json_dict['comments']:
            comment = item['content'] # 评论内容
            likedCount = item['likedCount'] # 点赞总数
            comment_time = item['time'] # 评论时间(时间戳)
            #userID = item['user']['userId'] # 评论者id
            nickname = item['user']['nickname'] # 昵称
            avatarUrl = item['user']['avatarUrl'] # 头像地址
            comment_info =+nickname + u" " + avatarUrl + u" " + str(comment_time) + u" " + ustr(likedCount) + u" " + comment + u"\n"
            all_comments_list.append(comment_info)
        print("第%d页抓取完毕!" % (i+1))
    return all_comments_list

# 将评论写入文本文件
def save_to_file(list,filename):
        with open(filename,'a',encoding='utf-8') as f:
            f.writelines(list)
        print("写入文件成功!")

# 分两种写入方式，此处增加踩csv   将评论写入csv文件
def save_to_csv(list,filecsv):
        with open(filecsv,'a+',encoding='utf-8',newline='') as f:
            w=csv.writer(csvfile)
            w.writerow(list)
        print("写入文件成功!")
        

    
       
        

        
        
if __name__ == "__main__":
    start_time = time.time() # 开始时间
    #id=506092654
    #歌单链接
    link= "https://music.163.com/discover/toplist" 
    r=requests.get(link,headers=headers)
    soup=BeautifulSoup(r.text,"lxml")
    main=soup.find('ul',{'class':'f-hide'})
    #歌单的网页结构不同，此处我爬取的首页
    list_id=soup.find('h2',{'class':'f-ff2'}).text
    if not os.path.exists("D:\python git\\"+str(list_id)):  
        #此处为文件路径，可以自行替换
        os.makedirs("D:\python git\\"+str(list_id)) 
    
    for music_all in main.find_all('a'):
        music1=str(music_all)
        music=music1.replace(' ','')
        #先将空格去掉
        music_id=re.findall(r'[1-9][0-9]{4,}',music)
        #匹配歌曲id
        music_name=re.findall(r'\>\S{1,}\<',music)
    
        #匹配歌曲歌名
        music1_id=' '.join(music_id)
        music1_name=' '.join(music_name)
        name=music1_name[1:-1]#正则匹配的时候带着符号，此处把符号去掉
        id=music1_id
        #url1='https://music.163.com/song?id='+str(id)+''
        url='http://music.163.com/weapi/v1/resource/comments/R_SO_4_' + str(id)+ '?csrf_token='   #歌评url

        filename = "D:\python git\\"+str(list_id)+"\\"+str(name)+".txt"
        #filecsv = "D:\python git\网易云音乐爬取\\"+str(id)+".csv"
    
    
        all_comments_list = get_hot_comments(url)
        save_to_file(all_comments_list,filename)
        #save_to_file(all_comments_list,filecsv)
    
    
    
    end_time = time.time() #结束时间
    print("程序耗时%f秒." % (end_time - start_time))


# In[6]:




