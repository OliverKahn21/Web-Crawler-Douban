###########################爬取数据
import re
import random
import requests
import time
import pandas as pd
import json
from bs4 import BeautifulSoup
import time
import jieba
import codecs
import os

data=pd.read_excel(u'电影名称&输出格式.xlsx',sheet=u'电影名称')
moive=list(data[u'影片名'])

def getProxyIp():
    proxy = []
    for i in range(1,3):
        header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.4549.400 QQBrowser/9.7.12900.400'}
        req = requests.get(url='http://www.xicidaili.com/nt/{0}'.format(i), headers=header)
        r = req.text
        soup = BeautifulSoup(r,'html.parser',from_encoding='utf-8')
        table = soup.find('table', attrs={'id': 'ip_list'})
        tr = table.find_all('tr')[1:]
        #解析得到代理ip的地址，端口，和类型
        for item in tr:
            tds =  item.find_all('td')
            temp_dict = {}
            ip = "{0}:{1}".format(tds[1].get_text().lower(), tds[2].get_text())
            proxy.append(ip)
    return proxy
proxies=getProxyIp()

##############################获取豆瓣电影id
idlist=[]

moive=m3
for i in moive:
    url = 'https://www.douban.com/search?q=%s' % (i)
#     print url
    res=requests.get(url).text

    sid=re.findall("sid: [0-9]{8},",res)[1]
    idlist.append(sid.split(':')[1].strip().replace(',',''))
    #print idlist
#
def pcinfo(html):
    movie=re.findall(r'<h1>(.*?) 短评</h1>',html)
    #while movie==None:
        #continue
    get_id = re.findall(r'<a.+people.+">(.+)</a>',html)
    get_comments = re.findall(r'<p class="">(.+)', html)
    get_date = re.findall(r'201[0-9]-[0-9]+-[0-9]+', html, re.S)
    get_votes = re.findall(r'<span class="votes">(.+)</span>', html)
    movies=movie*len(get_id)
    zd=[movies,get_comments,get_date,get_votes,get_id]
    result=pd.DataFrame(zd)
    result=result.T
    return(result)
header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.4549.400 QQBrowser/9.7.12900.400'}
comment=[] 
for j in idlist:
    len1 = len(proxies)-1
    for p in range(0,25):
        proxie = {
            "http":"1.2.3.4:2222"
        }
        index = random.randint(0, len1)
        proxie["http"] = proxies[index]
        print (j)

        url = 'https://movie.douban.com/subject/'+str(j)+'/'+'comments?start=' + str(p) + '&limit=20&sort=new_score&status=P'
        print(url)  
        html =requests.get(url,headers=header,proxies=proxie,timeout=100).text
        print(html)
        dbdata=pcinfo(html)
        comment.append(dbdata)
        time.sleep(10)
analysis=pd.concat(comment,names=['movie','comment','date','votes','userid'])
data=analysis.dropna()

###########################################情感得分析
data.index=range(0,29000)
sentiment_dict = {}


sentiment_dict = {}


def init_source():
    # 情感词dict
    with codecs.open('sentiment_score.txt',encoding='utf-8') as f6:
        sentiment_list = f6.readlines()
        for sentiment in sentiment_list:
            print (sentiment)
            if sentiment.strip()=="":
                continue
            tmp_sentiment = sentiment.split(" ")
            sentiment_dict[tmp_sentiment[0]] = tmp_sentiment[1]
comment=list(data['comment'])
comment[0]
def analysis_comment():
    '''
    数据清洗并分词
    :return:
    '''
    stopwords = [line.strip() for line in codecs.open('stopword.txt', encoding='utf-8').readlines()]
    word_lines = []
    for line in comment:
            if line == "":
                continue
            comments = list(jieba.cut(str(line)))
            n_comments = []
            for word in comments:
                # 去除停用词
                if word in stopwords:
                    continue
                else:
                    n_comments.append(word)
                    total_words.append(word)
            word_lines.append(n_comments)
            print (",".join(n_comments))
    return word_lines
data['fcresult']=analysis_comment()

def return_score_list(word_line):
    senWord = []
    sen_list = sentiment_dict.keys()
    for word in word_line:
        if word in sen_list:
            score = sentiment_dict[word].replace('\n','')
            print(score)
            senWord.append(float(score))
    return sum(senWord)
init_source()
sumscore=[]
for i in range(len(data['fcresult'])):
    sumscore.append(return_score_list(data['fcresult'][i]))
data['sumscore']=sumscore
name=['movie','comment', 'date', 'votes', 'userid', 'sumscore']
data[name].to_excel('情感得分结果.xlsx')
