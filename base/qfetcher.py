#coding:utf-8
#quote fetcher by Yahoo YQL API

import urllib
import urllib2
import json
import pf_interface

YQL_BASE = 'http://query.yahooapis.com/v1/public/yql?format=json&env=store://datatables.org/alltableswithkeys&'

def fetch_quote(qname_array):
	str_q = '"' + '","'.join(qname_array) + '"'
	yql = 'select Name, Symbol, LastTradePriceOnly from yahoo.finance.quotes where symbol in (%s)' % str_q
	yql = urllib.urlencode({'q':yql})
	yql = yql.replace('+', '%20')
	url = YQL_BASE + yql
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)

	resp_msg = response.read() 
	res = json.loads(resp_msg)
	qres = res['query']['results']['quote']
	for pinfo in qres:
		sym = pinfo['Symbol']
		if sym.find('.') > 0:
			sym = sym.lower()
		pf_interface.update_quote(sym, pinfo['Name'], float(pinfo['LastTradePriceOnly']))


#fecth mutual fund in China ==================================

NETEASE_BASE = 'http://api.money.126.net/data/feed/'

def fetch_fund(qname_array):
	str_q = ','.join(qname_array)
	str_q = str_q.replace('.of', '')  #omit tail .of
	url = NETEASE_BASE + str_q + ',money.api'
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	resp_msg = response.read() 
	resp_msg = resp_msg.replace('_ntes_quote_callback(', '')
	resp_msg = resp_msg[:-2]  #omit );
	res = json.loads(resp_msg)
	for q, pinfo in res.iteritems():
		pf_interface.update_quote(q + '.of', unicode(pinfo['sname']), float(pinfo.get('jz', 1)))

def fetch_holding(username):
	holding = pf_interface.get_holding_qname(username, 'stock')
	if len(holding) > 0:
		fetch_quote(holding)
	
	holding = pf_interface.get_holding_qname(username, 'fund')
	if len(holding) > 0:
		fetch_fund(holding)

fetch_holding('daly')
