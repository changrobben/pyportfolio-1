#coding:utf-8
from django.http import HttpResponse
from django.shortcuts import render_to_response
import pymongo
from base.pf_interface import *
import base.widget

def get_my_portfolio(user):
	pdata = []
	holding = get_holding('daly')
	for v in holding:
		price = get_price(v['q'])
		sname = get_sname(v['q']) + "(" + v['q'] + ")"
		row = [sname, v['am'], str(price), str(v['price'])]
		row.append(str(price * v['am']))
		gain = (price - v['price']) * v['am']
		row.append(str(gain))
		pdata.append( row )
	return pdata


COL_NAME = [u'名称', u'持股', u'现价', u'成本价', u'市值', u'盈利']

def get_page(req):
	pdata = get_my_portfolio('daly')
	html_data = base.widget.gen_data_table({'col_name':COL_NAME, 'rows':pdata})
	mp = {}
	mp['data'] = html_data
	mp['cash_cny'] = str(get_cash('daly', 'CNY'))
	mp['cash_usd'] = str(get_cash('daly', 'USD'))
	return render_to_response('portfolio.html', mp)

