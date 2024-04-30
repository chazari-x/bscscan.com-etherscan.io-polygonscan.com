import random
import threading
from queue import Queue
import requests
import urllib3
from bs4 import BeautifulSoup
from progress.bar import IncrementalBar
from pyuseragents import random as random_useragent

urllib3.disable_warnings()

def load_proxies(fp: str = "proxies.txt"):
    """
    Простая загрузка прокси в список

    :param fp:
    :return: Список с прокси
    """
    proxies = []
    with open(file=fp, mode="r", encoding="utf-8") as File:
        lines = File.read().split("\n")
    for line in lines:
        try:
            proxies.append(f"http://{line}")
        except ValueError:
            pass

    if proxies.__len__() < 1:
        raise Exception("can't load empty proxies file!")

    print("{} proxies loaded successfully!".format(proxies.__len__()))

    return proxies

class PrintThread(threading.Thread):
    def __init__(self, queue, file):
        threading.Thread.__init__(self)
        self.queue = queue
        self.file = file

    def printfiles(self, filename: str, text: str):
        with open(filename, "a", encoding="utf-8") as ff:
            ff.write(text + '\n')

    def run(self):
        while True:
            addr = self.queue.get()
            self.printfiles(self.file, addr)
            self.queue.task_done()

class ProcessThread(threading.Thread):
    def __init__(self, in_queue, out_queue, type):
        CHAIN = {
            'bsc': self.func_bsc,
            'eth': self.func_eth,
            'polygon': self.func_poly,
        }
        threading.Thread.__init__(self)
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.get = CHAIN[type]
        

    def run(self):
        while True:
            addr = self.in_queue.get()
            response = self.get(addr)
            if response != "": self.out_queue.put(response)
            self.in_queue.task_done()
            bar.next()

    def func_bsc(self, adr):
        while True:
            try:
                sess = requests.session()
                sess.proxies = {'all': random.choice(prox)}
                sess.headers = {
                    'user-agent': random_useragent(),
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept': '*/*',
                    'Connection': 'keep-alive',
                }

                sess.verify = False
                req = sess.get(f'https://bscscan.com/txs?a={adr}&f=5')
                if req.status_code != 200: continue
                html = BeautifulSoup(req.text, 'html.parser')
                tx_table = html.find('table', attrs={'class': 'table table-hover table-align-middle mb-0'}).find('tbody')
                trs = tx_table.find_all('tr')
                ans = f'(bscscan.com) {adr} https://bscscan.com/txs?a={adr}&f=5\n'
                t = False
                for el in trs:
                    data = el.find_all('td')
                    if data.__len__() >= 11:
                        t = True
                        ans += f'{data[1].text.strip()} - {data[5].text.strip()} - {data[8].text.strip()} - {data[10].text.strip()}\n'
                if t: return ans
                return ""
            except Exception as e:
                pass


    def func_eth(self, adr):
        while True:
            try:
                sess = requests.session()
                sess.proxies = {'all': random.choice(prox)}
                sess.headers = {
                    'user-agent': random_useragent(),
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept': '*/*',
                    'Connection': 'keep-alive',
                }

                sess.verify = False
                req = sess.get(f'https://etherscan.io/txs?a={adr}&f=5')
                if req.status_code != 200: continue
                html = BeautifulSoup(req.text, 'html.parser')
                tx_table = html.find('table', attrs={'class': 'table table-hover table-align-middle mb-0'}).find('tbody')
                trs = tx_table.find_all('tr')
                ans = f'(etherscan.io) {adr} https://etherscan.io/txs?a={adr}&f=5\n'
                t = False
                for el in trs:
                    data = el.find_all('td')
                    if data.__len__() >= 11:
                        t = True
                        ans += f'{data[1].text.strip()} - {data[5].text.strip()} - {data[8].text.strip()} - {data[10].text.strip()}\n'
                if t: return ans
                return ""
            except Exception as e:
                pass


    def func_poly(self, adr):
        while True:
            try:
                sess = requests.session()
                sess.proxies = {'all': random.choice(prox)}
                sess.headers = {
                    'user-agent': random_useragent(),
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept': '*/*',
                    'Connection': 'keep-alive',
                }

                sess.verify = False
                req = sess.get(f'https://polygonscan.com/txs?a={adr}&f=5')
                if req.status_code != 200: continue
                html = BeautifulSoup(req.text, 'html.parser')
                tx_table = html.find('table', attrs={'class': 'table table-hover table-align-middle mb-0'}).find('tbody')
                trs = tx_table.find_all('tr')
                ans = f'(polygonscan.com) {adr} https://polygonscan.com/txs?a={adr}&f=5\n'
                t = False
                for el in trs:
                    data = el.find_all('td')
                    if data.__len__() >= 11:
                        t = True
                        ans += f'{data[1].text.strip()} - {data[5].text.strip()} - {data[8].text.strip()} - {data[10].text.strip()}\n'
                if t: return ans
                return ""
            except Exception as e:
                pass

prox = load_proxies(input('Path to proxies: '))
# prox = load_proxies('prx.txt')

file = input('Path to file with adr: ')
# file = 'mnemonics copy.txt'

with open(file, encoding="utf-8") as f:
    mnemonic = f.read().splitlines()
print(f'Loaded {len(mnemonic)} address')

threads = int(input('Max threads: '))
# threads = 1

path_to_save = input('Path to save: ')
# path_to_save = 'sac.txt'

CHAIN = {'eth', 'bsc', 'polygon'}
ch = input(f'Select chain {list(CHAIN)}')
while ch not in CHAIN:
    print(f'Chain must be in {list(CHAIN)}')
    ch = input(f'Select chain {list(CHAIN)}')

print('started')
bar = IncrementalBar('Countdown', max=len(mnemonic))

pathqueue = Queue()
resultqueue = Queue()

# spawn threads to process
for i in range(0, threads):
    t = ProcessThread(pathqueue, resultqueue, ch)
    t.daemon = True
    t.start()

# spawn threads to print
t = PrintThread(resultqueue, path_to_save)
t.daemon = True
t.start()

# add paths to queue
for path in mnemonic:
    pathqueue.put(path)

# wait for queue to get empty
pathqueue.join()
resultqueue.join()
