from django.shortcuts import render
import socket, traceback
from urllib import parse
from django.forms.models import model_to_dict
from django.shortcuts import redirect
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
import time;
import os;
import io
from django.http import HttpResponse
from loginApp.models import *
from searchApp.models import *
# 存储方式：每一个element包含三个Dict;[{subject:xxx},{predicate:xxx},{object:xxx}]
total_data = []
total_summary_data = []
all_keyword = []
total_data_del = []
pzs = []
minganci = []  # 敏感词列表



#def saving(path,sj):
#	wb_self = Workbook()
#	ws2_self = wb_self.active
#
#	for j in sj:
#		ws2_self.append(j)
#
#	wb_self.save(path)#保存文档

def main(keyword):
    global pzs
    pzs= keyword
    craw = MyCrawler(1)

    try:
        for each_word in pzs:
            craw.getHyperLinks("https://baike.baidu.com/item/{}".format(each_word))
    finally:
        result = package(total_data_del)
    return result

def package(total_data_del):
    result = []
    for item in total_data_del:
        each_element = {'subject': item[0], 'predicate': item[1], 'object': item[2]}
        result.append(each_element)
    return result


class MyCrawler:
    def __init__(self, seeds):
        global total_data
        global total_summary_data
        global all_keyword
        global total_data_del

        total_data = []
        total_summary_data = []
        all_keyword = []
        total_data_del = []
        # 初始化当前抓取的深度
        self.current_deepth = 0
        # 使用种子初始化url队列
        self.linkQuence = linkQuence()
        # 只有一个url
        if isinstance(seeds, str):
            self.linkQuence.addUnvisitedUrl(seeds)
        # 多个url所组成的list
        if isinstance(seeds, list):
            for i in seeds:
                self.linkQuence.addUnvisitedUrl(i)
                # print( "Add the seeds url \"%s\" to the unvisited url list"%str(self.linkQuence.unVisited))

    # 抓取过程主函数
    def crawling(self, crawl_deepth):
        # 循环条件：抓取深度不超过crawl_deepth
        while self.current_deepth <= crawl_deepth:
            # 循环条件：待抓取的链接不空
            now_list = list(self.linkQuence.getUnvisitedUrl())
            for each in now_list:
                print('This deepth has {} links'.format(len(now_list)))
                # visitUrl=self.linkQuence.unVisitedUrlDeQuence()
                self.linkQuence.remove_unVisitedUrlDeQuence(each)
                visitUrl = each
                print("Pop out one url \"%s\" from unvisited url list" % visitUrl)
                if visitUrl is None or visitUrl == "":
                    continue
                # 获取超链接
                links = self.getHyperLinks(visitUrl)
                print("Get %d new links" % len(links))
                # 将url放入已访问的url中
                self.linkQuence.addVisitedUrl(visitUrl)
                print("Visited url count: " + str(self.linkQuence.getVisitedUrlCount()))
                print("Visited deepth: " + str(self.current_deepth))
                for each_link in links:
                    self.linkQuence.addUnvisitedUrl(each_link)

                print("%d unvisited links:" % len(self.linkQuence.getUnvisitedUrl()))
            self.current_deepth += 1

    # 获取源码中得超链接及提取信息
    def getHyperLinks(self, url):
        data = self.getPageSource(url)
        if data != None:
            # BeautiflSoup的简介： http://www.jb51.net/article/65287.htm
            soup = BeautifulSoup(data, 'lxml')
            new_urls = []
            try:
                for link in soup.find('div', class_="lemma-summary").find_all('a'):
                    new_url = (link.get('href'))
                    # new_text = (link.text)
                    # print(new_url,new_text)
                    if new_url != None:
                        new_full_url = 'https://baike.baidu.com' + new_url
                        new_urls.append(new_full_url)

                res_data = {}
                title_node = soup.find('dd', class_="lemmaWgt-lemmaTitle-title").find("h1")
                res_data['title'] = title_node.get_text()
                print(res_data['title'])

                # 简介代码：<div class="lemma-summary" label-module="lemmaSummary">
                summary_node = soup.find('div', class_="lemma-summary")
                res_data['summary'] = summary_node.get_text().replace('\n', '').replace(' ', '').replace('\r',
                                                                                                         '').strip()

                # 类型：
                basic_info_node = soup.find('div', class_="basic-info cmn-clearfix")
                # 根据关键词是否存在于all_keyword判断是否重复
                if res_data['title'] not in all_keyword:
                    all_keyword.append(res_data['title'])
                    if res_data['summary'] != '':

                        total_summary_data.append([res_data['title'], '解释', res_data['summary']])
                        flag = 1

                        # 敏感词判断
                        for each_mingan in minganci:
                            if each_mingan in res_data['summary']:
                                # 存在敏感词则标记为0
                                flag = 0
                                break

                        # 是否存在基本信息
                        if basic_info_node:

                            for each_basic in basic_info_node.find_all('dt'):
                                first_name = each_basic.text.replace('\n', '').replace(' ', '').replace('\r',
                                                                                                        '').strip()
                                next_content = each_basic.find_next_sibling('dd').text.replace('\n', '').replace(' ',
                                                                                                                 '').replace(
                                    '\r', '').strip()

                                # 不管存不存在敏感词，添加到 总列表
                                total_data.append([res_data['title'], first_name, next_content])
                                # 不存在敏感词，把基本信息添加到 敏感词列表
                                if flag:
                                    total_data_del.append([res_data['title'], first_name, next_content])

                return new_urls
            except:
                traceback.print_exc()
                return []

    # 获取网页源码
    def getPageSource(self, url, timeout=100, coding=None):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36   (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36'}
        if url is None:
            return None
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(response.status_code, url)
            return None
        response.encoding = 'utf8'
        return response.text


class linkQuence:
    def __init__(self):
        # 已访问的url集合
        self.visted = []
        # 待访问的url集合
        self.unVisited = []

    # 获取访问过的url队列
    def getVisitedUrl(self):
        return self.visted

    # 获取未访问的url队列
    def getUnvisitedUrl(self):
        return self.unVisited

    # 添加到访问过得url队列中
    def addVisitedUrl(self, url):
        self.visted.append(url)

    # 移除访问过得url
    def removeVisitedUrl(self, url):
        self.visted.remove(url)

    # 未访问过得url出队列
    def unVisitedUrlDeQuence(self):
        try:
            return self.unVisited.pop()
        except:
            return None
            # 未访问过得url出队列

    def remove_unVisitedUrlDeQuence(self, url):
        try:
            return self.unVisited.remove(url)
        except:
            return None

    # 保证每个url只被访问一次
    def addUnvisitedUrl(self, url):
        if url != "" and url not in self.visted and url not in self.unVisited:
            self.unVisited.insert(0, url)

    # 获得已访问的url数目
    def getVisitedUrlCount(self):
        return len(self.visted)

    # 获得未访问的url数目
    def getUnvistedUrlCount(self):
        return len(self.unVisited)

    # 判断未访问的url队列是否为空
    def unVisitedUrlsEnmpy(self):
        return len(self.unVisited) == 0

def index(request):
  username=request.COOKIES.get('username')
  userId=User.objects.filter(username=request.COOKIES.get('username'))[0].id
  result=Tuple.objects.filter(user_id=userId)

  if username:
     print('the username is' + username)
     print('get in the method called index')
     print(os.path.realpath(__file__))
     time_start = time.time();
     keyword=[]
     try:
        if(request.POST.get('keyword')==None):

            return render(request, 'searchingpage.html',locals())
        keyword.append(request.POST.get('keyword'))
        result=main(keyword)
        if(len(result)==0):
            return render(request, 'searchingpage.html',locals())

        time_end = time.time();

        time_result=str(time_end-time_start);
        #global total_data_del
        #file='\File'+"\{}_result.xlsx".format(time.strftime('%Y_%m_%d %H_%M_%S', time.localtime()))
        #filePath=r'E:\mysite'+file
        #print(filePath)
        #saving(filePath,total_data_del)
        print('sum up is')
        print(time_result)

        return render(request, 'resultpage.html', locals())
     except:
        traceback.print_exc()
        return render(request, 'searchingpage.html',locals())
  else:
      return redirect('/loginApp/login/')

def back(request):
    request = redirect('/searchApp/index/')

   # request.set_cookie('username', username)
    return request


def download(request):
    wb_self = Workbook()
    ws2_self = wb_self.active

    username = request.COOKIES.get('username')
    userId = User.objects.filter(username=request.COOKIES.get('username'))[0].id
    result = Tuple.objects.filter(user_id=userId)
    final_result=[]

    for j in result:
       print(j.subject)
       print(j.predicate)
       print(j.obj)
       final_result.append([j.subject,j.predicate,j.obj])

    for j in final_result:

       ws2_self.append(j)

    #写入IO
    res=get_excel_stream(wb_self)

    #设置httpresponse的类型
    response =HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition']='attachment;filename='+parse.quote("excel_name")+'.xls'
    #将文件流写入到response返回
    response.write(res)
    return response

def get_excel_stream(result):
    #stringIO操作的只能是str，如果要操作二进制数据，就需要使用BytesIO
    excel_stream=io.BytesIO()

    result.save(excel_stream)

    res=excel_stream.getvalue()
    excel_stream.close()
    return res


def save(request):
    result=eval(request.POST.get('result'))
    user=User.objects.filter(username=request.COOKIES.get('username')).first()
    userId=user.id
    for i in result:

        tuple = Tuple.objects.create(subject=i.get('subject'), predicate=i.get('predicate'), obj=i.get('object'), user_id=userId)
    return redirect('/searchApp/index')

    #for i in result:
     #   tuple= Tuple.objects.create(subject=i.subject,predicate =i.predicate,obj=i.obj,user_id=user.id)
    #return redirect('/searchApp/index')



def delete(request):
    username = request.COOKIES.get('username')
    if username:

        deleteId=request.POST.get('iId')
        #删除本id下的数据
        Tuple.objects.filter(id=deleteId).delete()
        #如果redirect没有('/searchApp/index')的话，会把之前的URL加在前面
        return redirect('/searchApp/index')
    return redirect('/loginApp/login')

def cancellation(request):
    return redirect('/loginApp/login')


