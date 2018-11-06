# -*- coding: utf-8 -*-
import scrapy
import base64
import time 
from urllib.parse import urlencode
import json
import rsa
import random
import binascii
import re



class XlwbSpider(scrapy.Spider):
	name = 'xlwb_user'
	#allowed_domains = ['weibo.com']

	headers = {
	# 'Host':	'login.sina.com.cn',
'Connection':	'keep-alive',
# 'Content-Length':	'624',
#  'Cache-Control':	'max-age=0',
# 'Origin'	:'https://weibo.com',
# 'Upgrade-Insecure-Requests':	'1',
# 'DNT':	'1',
# 'Content-Type':	'application/x-www-form-urlencoded',
'User-Agent':	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
# 'Accept':	'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
# 'Referer':	'https://weibo.com/',
# 'Accept-Encoding':	'gzip, deflate, br',
# 'Accept-Language':	'zh-CN,zh;q=0.9,en;q=0.8',
#'Cookie':	'login=13a0857768fc0c0abafd3d70c0f4538a; SINAGLOBAL=172.16.138.138_1541038556.17115; Apache=172.16.138.138_1541038556.17118; SCF=Ak293onlvowNUZWlI1oLUXcE0wArmO0a9MI21yqrI9z2WpS1ylInhlUjEN9Z4fJ97upo_ry9Qe6mtvO1pSY_jpM.; SUB=_2AkMshu0hdcPxrAZVmf4dzGrrZY5H-jyfU4TXAn7tJhMyAhh77gstqSVutBF-XKfjkkrL3alAhn_FrXpvN8SG_XDW; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9Whh4h34Gi_jawDnV6vY-g4n5JpVF02ReoefShBpeK2p; ULOGIN_IMG=tc-f1d1b49c8fef60b0962feaeaac73a0090ada',

	}

	def start_requests(self):
		url = 'https://login.sina.com.cn/sso/prelogin.php?'
		su = base64.b64encode(b'weifanw_stu@163.com')
		ser_time = int(time.time()*1000)
		param = {'entry':"weibo",'callback':"sinaSSOController.preloginCallBack",'su':su,'rsakt':"mod",'checkpin':'1','client':'ssologin.js(v1.4.19)','_':ser_time}
		pre_url = url + urlencode(param)
		yield scrapy.Request(url=pre_url, callback=self.get_form,meta={'cookiejar':1})
    
	def get_form(self, response):
		res_text = response.text
		res_text = res_text.strip('sinaSSOController.preloginCallBack')
		res_text = res_text.strip('(')
		res_text = res_text.strip(')')
		res_text = json.loads(res_text)
		login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'

		nonce = res_text['nonce']
		pcid = res_text['pcid']
		servertime = res_text['servertime']
		rsakv = res_text['rsakv']
		pubkey = res_text['pubkey']
		su = base64.b64encode(b'weifanw_stu@163.com')
		password = 'wangqiang654321'
		sp = self.get_password(servertime,nonce,password,pubkey)

		FormData = {
'entry': 'weibo',
'gateway': '1',
'from':'', 
'savestate': '0',
'qrcode_flag': 'false',
'useticket': '1',
'pagerefer': 'https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fpassport.weibo.com%2Fwbsso%2Flogout%3Fr%3Dhttps%253A%252F%252Fweibo.com%26returntype%3D1',
'pcid': pcid,
'door': '',
'vsnf': '1',
'su': su,
'service': 'miniblog',
'servertime': str(servertime),
'nonce': nonce,
'pwencode': 'rsa2',
'rsakv': '1330428213',
'sp': sp,
'sr': '1440*900',
'encoding': 'UTF-8',
'prelt': str(random.randint(20,200)),
'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
'returntype': 'META',
			}

		#login_url = 'https://login.sina.com.cn/signup/signin.php?entry=ss'
		yield scrapy.http.FormRequest(login_url,headers=self.headers, formdata=FormData, callback=self.redir,meta={'cookiejar':response.meta['cookiejar']})
	

	def get200_1(self,response):
		# crossdomain_url = response.url
		#print(response.url)
		yield scrapy.Request(url =response.url,callback = self.get302_1,meta={'cookiejar':response.meta['cookiejar']},dont_filter=True)

		#yield scrapy.Request(url=pre_url, callback=self.get_form,meta={'cookiejar':1})

		

	def redir(self,response):
		# print(response.url)
		
		
		# print(response.xpath('//body/script/text()')).extract()
		# print(type(response.text))
		#redir_url = 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack&sudaref=weibo.com'
		redir_url = 'https://passport.weibo.com/wbsso/login?url=https%3A%2F%2Fweibo.com%2Fajaxlogin.php%3Fframelogin%3D1%26callback%3Dparent.sinaSSOController.feedBackUrlCallBack%26sudaref%3Dweibo.com&display=0&'
		w1 = 'ticket%3D'
		w2 = '%26retcode%3D'
		buff = response.url
		pat = re.compile(w1+'(.*?)'+w2,re.S)
		result = pat.findall(buff)
		ticket = result[0].replace('%3D','=')
		param = {'retcode':'0'}
		final_url = redir_url + 'ticket=' + ticket + '&' + urlencode(param)
		
		yield scrapy.Request(url = final_url, meta = {'cookiejar':response.meta['cookiejar']},callback = self.interest)

	def get_password(self,servertime,nonce,password,pubkey):
		#print(password)
		rsaPublickey = int(pubkey, 16)
		para2 = int('10001',16)
		key = rsa.PublicKey(rsaPublickey, para2) #创建公钥
		message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)#拼接明文 js加密文件中得到
		#print(message)
		message = bytes(message,encoding = "utf-8")
		passwd = rsa.encrypt(message, key)#加密
		passwd = binascii.b2a_hex(passwd) #将加密信息转换为16进制。
		#print(passwd)
		return passwd

	def interest(self,response):
		interest_url = 'https://weibo.com/nguide/interest'
		yield scrapy.Request(url = interest_url,meta ={'cookiejar':response.meta['cookiejar']},callback = self.login_success)


	def login_success(self,response):
		#print(response.text)
		# my_name = response.xpath('/script[@type="text/javascript"]/text()').extract()
		# print(my_name)
		base_url = 'https://weibo.com/'
		res_tr1 = r'<script>(.*?)</script>'
		text = response.text
		script_all = re.findall(res_tr1,text)
		script_need = script_all[8]
		#script_need = 'FM.view({"ns":"pl.rightmod.myinfo.index","domid":"v6_pl_rightmod_myinfo","css":["style/css/module/global/W_person_info.css?version=52b47dd3808c22ca"],"js":["home/js/pl/rightmod/myinfo/index.js?version=991667e9fa889b31"],"html":"<div class=\"WB_cardwrap S_bg2\">\n    <div class=\"W_person_info\">\n      <div class=\"cover\" id=\"skin_cover_s\" style=\"background-image:url(https:\/\/img.t.sinajs.cn\/t5\/skin\/public\/profile_cover\/001_s.jpg)\">\n        <div class=\"headpic\"> <a bpfilter=\"page_frame\" href=\"\/6813074814\/profile?rightmod=1&wvr=6&mod=personinfo\" title=\"西交爬虫帆哥\"><img class=\"W_face_radius\" src=\"\/\/tvax3.sinaimg.cn\/default\/images\/default_avatar_male_180.gif\" width=\"60\" height=\"60\" alt=\"西交爬虫帆哥\"><\/a><\/div>\n      <\/div>\n      <div class=\"WB_innerwrap\">\n        <div class=\"nameBox\"><a bpfilter=\"page_frame\" href=\"\/6813074814\/profile?rightmod=1&wvr=6&mod=personinfo\" class=\"name S_txt1\" title=\"西交爬虫帆哥\">西交爬虫帆哥<\/a><a action-type=\"ignore_list\" title=\"微博会员\" target=\"_blank\" href=\"http:\/\/vip.weibo.com\/\"><i class=\"W_icon icon_member_dis\"><\/i><\/a><a action-type=\"\" suda-data=\"key=tblog_grade_float&value=grade_icon_click\" target=\"_blank\" href=\"http:\/\/level.account.weibo.com\/level\/mylevel?from=front\" ><span node-type=\"levelBox\" levelup=\"0\" action-data=\"level=1\" class=\"W_icon_level icon_level_c2\"><span class=\"txt_out\"><span class=\"txt_in\"><span node-type=\"levelNum\" title=\"微博等级1 升级有好礼\" >Lv.1<\/span><\/span><\/span><\/span><\/a><\/div>\n        <ul class=\"user_atten clearfix W_f18\">\n          <li class=\"S_line1\"><a bpfilter=\"page_frame\" href=\"\/6813074814\/follow?rightmod=1&wvr=6\" class=\"S_txt1\"><strong node-type=\"follow\">61<\/strong><span class=\"S_txt2\">关注<\/span><\/a><\/li>\n          <li class=\"S_line1\"><a bpfilter=\"page_frame\" href=\"\/6813074814\/fans?rightmod=1&wvr=6\" class=\"S_txt1\"><strong node-type=\"fans\">1<\/strong><span class=\"S_txt2\">粉丝<\/span><\/a><\/li>\n          <li class=\"S_line1\"><a bpfilter=\"page_frame\" href=\"\/6813074814\/profile?rightmod=1&wvr=6&mod=personnumber\" class=\"S_txt1\"><strong node-type=\"weibo\">0<\/strong><span class=\"S_txt2\">微博<\/span><\/a><\/li>\n        <\/ul>\n      <\/div>\n            <\/div>\n<\/div>\n"})'
		#print(script_need)
		#print('a bpfilter=\\\"page_frame\\\" href=\\\"')
		res_tr2 = r'bpfilter=\\\"page_frame\\\" href=\\\"(.*?)\\\" class='
		#res_tr2 = r'ome/js/pl/r(.*?)od/myinf'
		m_tr = re.findall(res_tr2,script_need)
		m_tr = m_tr[1]
		m_tr = m_tr.replace('/','')
		m_tr = m_tr.replace('\\','/')
		follow_url = base_url + m_tr
		#print(follow_url)
		yield scrapy.Request(url=follow_url,meta ={'cookiejar':response.meta['cookiejar']},callback = self.follow_list)
	

	def follow_list(self,response):
		#找关注者所在script
		text = response.text
		res_tr1 = r'<script>(.*?)</script>'
		script_all = re.findall(res_tr1,text)
		script_need = script_all[-1]
		#print(script_need)
		# 找关注者姓名
		res_tr2 = r'class=\\\"S_txt1\\\" title=\\\"(.*?)\\\" usercard=\\\"id='
		follow_name = re.findall(res_tr2,script_need)
		#print(follow_name)
		#找关注者url
		base_url = 'https://weibo.com/'
		res_tr3 = r'node-type=\\\"screen_name\\\"  href=\\\"(.*?)\\\" class=\\\"S_txt1\\\" t'
		follow_url = re.findall(res_tr3,script_need)
		follow_url_real = []
		for ele in follow_url:
			ele_url = ele.replace('\\','')
			follow_url_real.append(base_url + ele_url)

		exam_url = follow_url_real[0]
		#print(exam_url)
		yield scrapy.Request(url=exam_url, meta ={'cookiejar':response.meta['cookiejar']},callback = self.homepage)

	def homepage(self,response):
		text = response.text
		#查找个人简介所在script
		# res_tr1 = r'<script>(.*?)</script>'
		# script_all = re.findall(res_tr1,text)
		# script_need = script_all[-6]
		# #print(script_need)
		# #昵称
		# res_tr_name = r'<\\\/span><span class=\\\"pt_detail\\\">(.*?)<\\\/span><\\\/li>\\\r\\\n'
		# user_name = re.findall(res_tr_name,script_need)
		# res_tr_loc = r'所在地：<\\\/span><span class=\\\"pt_detail\\\">(.*?)<\\\/span><\\\/li>\\\r\\\n'
		# location = re.findall(res_tr_loc,script_need)
		# res_tr_gen = r'性别：<\/span><span class=\"pt_detail\">(.*?)<\\\/span><\\\/li>\\\r\\\n'
		# gender = re.findall(res_tr_gen,script_need)
		# res_tr_bor = r'生日：<\/span><span class=\"pt_detail\">(.*?)<\\\/span><\\\/li>\\\r\\\n'
		# born_date = re.findall(res_tr_bor,script_need)

		# print(location)



