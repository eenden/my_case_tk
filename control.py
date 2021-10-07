from requests import get
from json import loads
from pprint import pprint
import csv
from bs4 import BeautifulSoup as Bs


def get_prices(tickers, date):
	prices = {}
	for ticker in tickers:
		price = {}
		start_date = end_date = date
		req = f'https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/{ticker[1]}.json?from={start_date}&till={end_date}'
		r = get(req)
		if r.ok:
			data = loads(r.text)
			if data:
				prices[ticker[1]] = {
										'price': data['history']['data'][0][11], 
										'title': ticker[0], 
										'count':ticker[2],
										'sum': round(data['history']['data'][0][11] * int(ticker[2]), 2)
									}
	s = sum([s['sum'] for s in prices.values()])

	for price in prices.values():
		price['part'] = round(price['sum'] / s * 100, 4)

	return prices

def load_tickers(filename):
	try:
		with open(filename, 'r') as f:
			rows = [row for row in csv.reader(f, delimiter=';')]
			for row in rows:
				row.extend(['', ''])
			return rows
	except Exception as err:
		return None

def save_as_tickers(filename, rows):
	with open(filename, 'w') as f:
		writer = csv.writer(f, delimiter=';')
		for row in rows:
			writer.writerow(row)


def get_data(date, tickers):
	if tickers:
		prices = get_prices(tickers, date)
		if prices:
			return(prices)


def smartlab_import(url):
	r = get(url)
	results = []
	if r.ok:
		soup = Bs(r.text, 'lxml')
		if soup:
			table = soup.find('table',{'csv-download-data':'russian_shares'})
			if table:
				rows = table.find_all('tr')
				for row in rows[1:]:
					columns = row.find_all('td')
					title = columns[1].a.text
					ticker = columns[2].text
					count = columns[7].text
					results.append([title, ticker, count])
	return results


if __name__ == '__main__': 
	data = smartlab_import('https://smart-lab.ru/q/portfolio/badpidgin/10736/')
	pprint(data)

	
				

