#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import os
from papapa2 import down
from pymongo import MongoClient
import datetime

class mzitu():
	def __init__(self):
		client = MongoClient()
		db = client['meinvxiezhen']
		self.meizitu_collection = db['meizitu'] ##在meizixiezhenji这个数据库中，选择一个集合

		self.title = '' ##用来保存页面主题
		self.href = '' ##用来保存页面地址
		self.img_urls = [] ##初始化一个 列表 用来保存图片地址

	def all_url(self, url):
		html = down.get(url, 3)
		# headers = {'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}##浏览器请求头（大部分网站没有这个请求头会报错、请务必加上哦）
		# all_url = 'http://www.mzitu.com/all'
		# start_html = requests.get(all_url, headers=headers)
		#start_html.encoding = 'gbk'

		soup = BeautifulSoup(html.text, 'lxml')

		all_a = soup.find('div', class_='all').find_all('a')

		for a in all_a:

			# 获取标题
			self.title = a.get_text()

			# 监测创建目录
			print(u'开始保存：', self.title)
			self.mkdir()

			# 路径
			self.href = a['href']

			# 判断url是否已经进行爬虫
			if self.meizitu_collection.find_one({'主题页面':self.href}):
				print('这个页面已经爬过了')
			else:
				self.html()
				
	def html(self):
		html = down.get(self.href, 3)
		html_soup = BeautifulSoup(html.text, 'lxml')
		max_span = html_soup.find('div', class_='pagenavi').find_all('span')[-2].get_text()
		page_num = 0
		for page in range(1, int(max_span) + 1):
			page_num = page_num + 1
			page_url = self.href + '/' + str(page)
			self.img(page_url, max_span, page_num)

	def img(self, page_url, max_span, page_num):
		img_html = down.get(page_url, 3)
		image_soup = BeautifulSoup(img_html.text, 'lxml')
		img_url = image_soup.find('div', class_='main-image').find('img')['src']
		self.img_urls.append(img_url)

		if int(max_span) == page_num:
			post = {
				'标题':self.title,
				'主题页面':self.href,
				'图片地址':self.img_urls,
				'获取时间':datetime.datetime.now()
			}
			self.meizitu_collection.save(post)
			print('存入数据成功')
		self.save(img_url)

	def save(self, img_url):
		name = img_url[-9:-4]
		img = down.get(img_url, 3)
		with open(str(self.title) + '/' + name, 'wb') as fp:
			fp.write(img.content)

	def mkdir(self):
		if not os.path.exists(self.title):
			print(u'创建文件夹')
			os.makedirs(self.title)
			return True
		else:
			print(u'文件夹已经存在')

Mzitu = mzitu() ##实例化
Mzitu.all_url('http://www.mzitu.com/all')

