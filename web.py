#!/usr/bin/env python3

import socket
import re
import os
import time
import queue
import gzip
from threading import Thread

curPath = '/home/pi/Documents/webServer'
connections = []
threads = []
q = queue.Queue(maxsize=20)

timeout_time = 3

def clearReq(req):
	r = []
	for i in req:
		if len(i) > 0:
			r.append(i)
	return r

def encode(text):
	return bytes(text.encode('utf-8'))

def main_page():
	ls = os.listdir(curPath)
	dir = []
	for i in ls:
		if i.split('.')[1] == 'html':
			dir.append(i)
	html = open('index.html', 'r').read()
	list = ''
	for i in dir:
		list += '\t<li><a href="'+i+'">'+i+'</a></li>\n\t\t'
	html = html%list
	return html

def get_visible(req):
	table = ''

	for i in req:
		k = i.split(':', maxsplit = 1)
		if len(k) != 2:
			k.append(' ')
		table += '<tr><td>%s</td><td>%s</td></tr>' %(k[0], k[1])

	html = open('get.html', 'r').read()
	html = html%table

	return html

def img(path, conn, req, encode):
	file = path[path.rfind('/')+1:len(path)]
	size = os.stat(curPath+path).st_size

	img = open(path[1:], 'rb').read()

	headers = {}
	headers['Content-type'] = 'image/png'
	headers['Content-length'] = str(size)
	headers['Server'] = 'Fisubus Corporation'
	if encode == True:
		img = gzip.compress(img, 6)
		headers['Content-Encoding'] = 'gzip'
		headers['Content-length'] = len(img)
	headers_text = "\n".join([ "%s: %s"%(k,v) for k,v in headers.items()])

	try:
		conn.send(("HTTP/1.1 200 OK\n%s\r\n\n"%(headers_text)).encode('ascii'))
		conn.send(img)
	except:
		print('send error')

def html(path, conn, req, encode):
	file = path[path.rfind('/')+1:len(path)]

	if file == 'get.html':
		html = get_visible(req)
	elif file == 'index.html':
		html = main_page()
	else:
		html = open(file, 'r').read()

	headers = {}
	headers['Content-type'] = 'text/html; charset=utf-8'
	headers['Content-length'] = len(html)
	headers['Server'] = 'Fisubus Corporation'
	if encode == True:
		html = gzip.compress(bytes(html, 'utf-8'), 6)
		headers['Content-Encoding'] = 'gzip'
		headers['Content-length'] = str(len(html))
	headers_text = "\n".join([ "%s: %s"%(k,v) for k,v in headers.items()])
	try:
		conn.send(("HTTP/1.1 200 OK\n%s\r\n\n"%(headers_text)).encode('ascii'))
		conn.send(html)
	except:
		print('send error', sys.exc_info()[0])

def not_found(conn, encode):
	html = open('404.html', 'r').read()

	headers = {}
	headers['Content-type'] = 'text/html; charset=utf-8'
	headers['Content-length'] = len(html)
	headers['Server'] = 'Fisubus Corporation'
	if encode == True:
		html = gzip.compress(bytes(html, 'utf-8'), 6)
		headers['Content-Encoding'] = 'gzip'
		headers['Content-length'] = len(html)
	headers_text = "\n".join([ "%s: %s"%(k,v) for k,v in headers.items()])
	try:
		conn.send(("HTTP/1.1 404 OK\n%s\r\n\n"%(headers_text)).encode('ascii'))
		conn.send(html)
	except:
		print('send error')

def check_existance(path):
	b = path.rfind('/')
	if b != -1:
		ln = len(path) - b
		file = path[b+1:len(path)]
		path = path[b:-1*ln+1]
	try:
		a = os.listdir(curPath+path)
		for i in a:
			if i == file:
				return True
		return False
	except FileNotFoundError:
		return False

def http(conn):
	conn.settimeout(timeout_time)
	req_str = ''
	try:
		while True:
			c = str(conn.recv(1).decode('utf-8'))
			req_str += c
			if req_str.find('\r\n\r\n') != -1:
				break
	except:
		print('someone have time out')
		return

	req = clearReq(req_str.split('\r\n'))
	
	encode = req_str.split('Accept-Encoding:')[1].split('\n', maxsplit = 1)[0]
	if encode.find('gzip') != -1 and encode.find('deflate') != -1:
		encode = True

	a = re.match('^(\w+)\s(.*)\s(HTTP.*?)', req.pop(0))
	path = a.group(2)
	method = a.group(1)

	if method == 'POST':#Not supported
		connections.remove(i)
		conn.close()
		return

	if path == '/':
		path = '/index.html'

	exist = check_existance(path)
	if exit == False:
		not_found(conn)

	type = path.split('.')[1]
	if type == 'html':
		html(path, conn, req, encode)
	elif type == 'png':
		img(path, conn, req, encode)
	else:
		not_found(conn, encode)

	http(conn)

def t_wait():
	while True:
		sock = q.get()
		http(sock)
		q.task_done()

if __name__ == '__main__':
	for i in range(20):
		threads.append(Thread(target = t_wait).start())

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(('', 9778))
	sock.listen(5)

	while True:
		conn, addr = sock.accept()
		print(str(addr) + " - connected")
		q.put(conn)

