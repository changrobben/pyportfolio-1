#coding:utf-8
#portfolio api
import db_helper
import datetime
import pymongo

# basic interface ============================

def get_cy_by_qname(qname):
	arr = qname.split('.')
	if len(arr) == 2:
		#open fund, shanghai, shenzhen
		if arr[1] == 'of' or arr[1] == 'ss' or arr[1] == 'sz': 
			return 'CNY'
		elif arr[1] == 'hk':
			return 'HKD'

	return 'USD'


#ev: buy, sell, dividend, cash reward, fee, deposit, withdraw
#cy: 'HKD', 'CNY', 'USD'
#money:  >0 income  <0 cost
def modify_cash(username, money, cy, ev):
	db, client = db_helper.get_db()
	tb = db.cash_holding
	data = tb.find_one({'cy':cy, 'user':username})
	if not data:
		data = {}
		data['user'] = username
		data['cy'] = cy
		data['am'] = 0
	data['am'] = data['am'] + money
	tb.save(data)

	tb = db.cash_log
	tb.insert({'user': username, 'cy': cy, 'ev':ev, 'am': money, 'ts':datetime.datetime.now()})

#amount:  >0 buy  <0 sell
#extra: 
#       'dt':  transaction date
#       'fee':  transaction fee
def insert_stock_trans(username, qname, price, amount, extra):
	data = {}
	data['user'] = username
	fee = extra.get('fee', 0)
	if amount > 0:
		data['act'] = 'buy'
	else:
		data['act'] = 'sell'
	data['ts'] = datetime.datetime.now()
	data['q'] = qname
	data['price'] = price
	data['fee'] = fee
	data['amount'] = amount
	if 'dt' in extra:
		data['dt'] = extra['dt']
	else:
		data['dt'] = datetime.datetime.now()
	db, client = db_helper.get_db()
	tbl = db.transaction
	tbl.insert(data)

	cy = get_cy_by_qname(qname)
	if data['act'] == 'buy':
		money = abs(amount) * price + fee
		modify_cash(username, -money, cy, 'buy')
	else:
		#sell
		money = abs(amount) * price - fee
		modify_cash(username, money, cy, 'buy')

	modify_stock_holding(username, qname, price, amount, fee)

#modify stock holding
#amount:  >0 add holding  <0 decrease holding
def modify_stock_holding(username, qname, price, amount, fee):
	db, client = db_helper.get_db()

	#update holding
	tbl_hold = db.holding
	data = tbl_hold.find_one({'user':username, 'q':qname})
	if not data:
		data = {}
		data['user'] = username
		data['q'] = qname

	old_am = data.get('am', 0)
	old_price = data.get('price', 0)
	new_am = old_am + amount
	new_price = old_price
	if amount > 0:
		#average holding cost
		new_price = (old_price * old_am + price * amount + fee) / new_am

	data['price'] = round(new_price, 2)
	data['am'] = new_am
	tbl_hold.save(data)

#cate: 'stock', 'fund', 'bond', 'insurance'
def update_security_info(qname, chname, cate, xchg):
	db, client = db_helper.get_db()
	tbl = db.security_info

	data = tbl.find_one({'q':qname})
	if not data:
		data = {}
		data['q'] = qname

	data['chname'] = chname
	data['cate'] = cate
	data['xchg'] = xchg
	tbl.save(data)

#update realtime quote
def update_quote(qname, sname, price):
	db, client = db_helper.get_db()
	tbl = db.quotes
	data = tbl.find_one({'q':qname})
	if not data:
		data = {}
		data['q'] = qname
		data['sname'] = sname

	data['price'] = price
	data['ts'] = datetime.datetime.now()
	tbl.save(data)

def get_price(qname):
	db, client = db_helper.get_db()
	tbl = db.quotes
	data = tbl.find_one({'q':qname})
	if not data: return 0
	return data['price']

def get_holding(username):
	db, client = db_helper.get_db()
	tbl = db.holding
	arr = []
	for q in tbl.find({'user':username}):
		arr.append(q)

	return arr


def get_holding_qname(username, cate):
	db, client = db_helper.get_db()
	tbl = db.holding
	arr = []
	for q in tbl.find({'user':username}):
		if cate == 'stock':
			if q['q'].find(".of") < 0:
				arr.append(q['q'])
		elif cate == 'fund':
			if q['q'].find('.of') > 0:
				arr.append(q['q'])
	return arr

def cal_trans_fee(qname, price, am, act):
	cy = get_cy_by_qname(qname)
	if cy == 'CNY':
		return price * am * 0.001
	elif cy == 'USD':
		return 18  #HSBC
	elif cy == 'HKD':
		return 100

def get_sname(qname):
	db, client = db_helper.get_db()
	tbl = db.security_info
	data = tbl.find_one({'q':qname})
	if not data: return ''
	return data['chname']

# High level interface =====================
def get_cash(username, cy):
	db, client = db_helper.get_db()
	tb = db.cash_holding
	data = tb.find_one({'cy':cy, 'user':username})
	return data['am']

def do_buy(user, q, price, am):
	fee = cal_trans_fee(q, price, am, 'buy')
	insert_stock_trans(user, q, price, am, {'fee':fee})

def do_sell(user, q, price, am):
	fee = cal_trans_fee(q, price, am, 'sell')
	insert_stock_trans(user, q, price, -am, {'fee':fee})


if __name__ == '__main__':
	modify_cash('daly', 80000, 'CNY', 'deposit')
	modify_cash('daly', 5000, 'USD', 'deposit')

	update_security_info('000002.sz', u'万科A', 'stock', 'SZ')
	update_security_info('CYOU', u'畅游', 'stock', 'NASDAQ')
	update_security_info('SPY', u'标普500 ETF', 'stock', 'AMEX')
	update_security_info('110037.of', u'易方达纯债A', 'stock', 'AMEX')
	update_security_info('270004.of', u'广发货币A', 'stock', 'AMEX')

	do_buy('daly', '000002.sz', 10.64, 2000)
	do_buy('daly', 'CYOU', 31.5, 60)
	do_buy('daly', 'SPY', 163.8, 15)
	do_buy('daly', '110037.of', 1.045, 3000)
	do_buy('daly', '270004.of', 1.000, 30000)
