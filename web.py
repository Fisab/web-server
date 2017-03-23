import socket, re, os
from threading import Thread

curPath = '/home/pi/Documents/webServer'

def clearReq(req):
	r = []
	for i in req:
		if len(i) > 0:
			r.append(i)
	return r

def encode(text):
	return bytes(text.encode('utf-8'))

def create_header(type, length):
	headers = {}
	headers['Content-type'] = type
	headers['Content-length'] = length
	headers_text = "\n".join([ "%s: %s"%(k,v) for k,v in headers.items()])
	return headers_text

def main_page():
	ls = os.listdir(curPath)
	dir = []
	for i in ls:
		if i.split('.')[1] == 'html':
			dir.append(i)
	html = open('index.html', 'r').read()
	list = ''
	for i in dir:
		list += '<li><a href="'+i+'">'+i+'</a></li>\n'
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

def img(path, conn, req):
	file = path[path.rfind('/')+1:len(path)]
	size = os.stat(curPath+path).st_size

	img = open(path[1:], 'rb').read()

	headers_text = create_header('image/'+file.split('.')[1], size)
	print(headers_text)
	conn.send(encode("HTTP/1.1 200 OK\n%s\n\n%s")%(encode(headers_text), img))
	conn.close()

def html(path, conn, req):
	file = path[path.rfind('/')+1:len(path)]

	if file == 'get.html':
		html = get_visible(req)
	elif file == 'index.html':
		html = main_page()
	else:
		html = open(file, 'r').read()

	headers_text = create_header('text/html; charset=utf-8', len(html))
	conn.send(encode("HTTP/1.1 200 OK\n%s\n\n%s"%(headers_text, html)))
	conn.close()

def not_found(conn):
	html = open('404.html', 'r').read()
	headers_text = create_header('text/html; charset=utf-8', len(html))
	conn.send(encode("HTTP/1.1 200 OK\n%s\n\n%s"%(headers_text, html)))
	conn.close()

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
	req_str = ''
	while True:
		c = str(conn.recv(1).decode('utf-8'))
		req_str += c
		if req_str.find('\r\n\r\n') != -1:
			break

	req = clearReq(req_str.split('\r\n'))
	#print(req[0])
	a = re.match('^(\w+)\s(.*)\s(HTTP.*?)', req.pop(0))
	path = a.group(2)
	method = a.group(1)

	if method == 'POST':#Not supported
		conn.close()
		return

	if path == '/':
		path = '/index.html'

	exist = check_existance(path)
	if exit == False:
		not_found(conn)

	type = path.split('.')[1]
	if type == 'html':
		html(path, conn, req)
	elif type == 'png':
		img(path, conn, req)
	else:
		not_found(conn)


if __name__ == '__main__':
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(('', 9778))
	sock.listen(1)

	while True:
		conn, addr = sock.accept()
		print(str(addr) + " - connected")
		http(conn)

