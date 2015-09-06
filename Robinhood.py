import requests
import urllib

class Robinhood(object):

	# All known endpoints as of September 5th, 2015
	endpoints = {
		"accounts": "https://api.robinhood.com/accounts",
		"ach_deposit_schedules": "https://api.robinhood.com/ach/deposit_schedules/",
		"ach_iav_auth": "https://api.robinhood.com/ach/iav/auth/",
		"ach_relationships": "https://api.robinhood.com/ach/relationships/",
		"ach_transfers": "https://api.robinhood.com/ach/transfers/",
		"applications": "https://api.robinhood.com/applications/",
		"dividends": "https://api.robinhood.com/dividends/",
		"document_requests": "https://api.robinhood.com/upload/document_requests/",
		"edocuments": "https://api.robinhood.com/documents/",
		"instruments": "https://api.robinhood.com/instruments/",
		"investment_profile": "https://api.robinhood.com/user/investment_profile/",
		"login": "https://api.robinhood.com/api-token-auth/",
		"margin_upgrades": "https://api.robinhood.com/margin/upgrades/",
		"markets": "https://api.robinhood.com/markets/",
		"notifications": "https://api.robinhood.com/notifications/",
		"orders": "https://api.robinhood.com/orders/",
		"password_reset": "https://api.robinhood.com/password_reset/request/",
		"quotes": "https://api.robinhood.com/quotes/",
		"user": "https://api.robinhood.com/user/",
		"watchlists": "https://api.robinhood.com/watchlists/"
		}

	def __init__(self, username, password, account):
		self.session = requests.session()
		self.account = account
		self.session.headers = {
			"Accept": "*/*",
			"Accept-Encoding": "gzip, deflate",
			"Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",
			"Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
			"X-Robinhood-API-Version": "1.0.0",
			"Connection": "keep-alive",
			"User-Agent": "Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)"
		}
		self.session.headers['Authorization'] = 'Token ' + self.login(username, password)

	def login(self, username, password):
		data = "username=%s&password=%s" % (username, password)
		res = self.session.post(self.endpoints['login'], data = data)
		try:
			return res.json()['token']
		except:
			raise Exception("Could not log in: " + res.text)

	def instrument(self, stock):
		res = self.session.get(self.endpoints['instruments'], params={'query':stock.upper()})
		if res.status_code == 200:
			return res.json()['results']
		else:
			raise Exception("Could not generate instrument object: " + res.text)

	def get_quote(self, stock):
		data = { 'symbols' : stock }
		res = self.session.get(self.endpoints['quotes'], params=data)
		if res.status_code == 200:
			return res.json()['results']
		else:
			raise Exception("Could not retrieve quote: " + res.text)

	def place_order(self, instrument, quantity, side, order_type, bid_price=None, time_in_force="gfd", stop_price=None):
		data = """account=%s&instrument=%s&quantity=%d&side=%s&symbol=%s&time_in_force=%s&trigger=immediate&type=%s""" % (
			urllib.quote('https://api.robinhood.com/accounts/' + self.account + '/'), 
			urllib.unquote(instrument['url']), quantity, side, instrument['symbol'], time_in_force, order_type)
		if order_type == "market":
			data += "&price=%f" % (float(self.get_quote(instrument['symbol'])[0]['bid_price']))
		if order_type == "limit":
			data += "&price=%f" % (float(bid_price))
		##Stop Loss and Stop Limit orders are a work in progress
		##if order_type == "stop_loss":
		##	data += "&stop_price=%f" % (float(stop_price))
		##if order_type == "stop_limit":
		##	data += "&price=%f&stop_price=%f" % (float(bid_price), float(stop_price))
		res = self.session.post(self.endpoints['orders'], data = data)
		if res.status_code == 201:
			res = res.json()
			order_ID = res['url'][res['url'].index("orders")+7:-1]
			return order_ID
		else:
			raise Exception("Could not place order: " + res.text)

	def place_buy_order(self, symbol, quantity, order_type=None, bid_price=None):
		i = self.instrument(symbol)[0]
		side = "buy"
		return self.place_order(i, quantity, side, order_type, bid_price)

	def place_sell_order(self, symbol, quantity, order_type=None, bid_price=None):
		i = self.instrument(symbol)[0]
		side = "sell"
		return self.place_order(i, quantity, side, order_type, bid_price)

	def cancel_order(self, order_ID):
		data = ""
		res = self.session.post(self.endpoints['orders'] + order_ID + "/cancel/")
		if res.status_code == 200:
			return res
		else:
			raise Exception("Could not cancel order: " + res.text)




