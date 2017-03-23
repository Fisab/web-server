import socket, re
from threading import Thread

def clearReq(req):
	r = []
	for i in req:
		if len(i) > 0:
			r.append(i)
	return r

def sendImg(html):
	imgs = re.findall('<img.*src\s?=".*".*>', html)
	img_src = []
	print(imgs)
	for i in imgs:
		if i.find('-->') == -1:  #   <img src="/f.png">-->
			img_src.append(re.findall('".*"', i))
	
	print(img_src)
	for i in img_src:
		print(i)



def getData(conn):
	req_str = ''
	while True:
		c = str(conn.recv(1).decode('utf-8'))
		req_str += c
		if req_str.find('\r\n\r\n') != -1:
			break

	req = clearReq(req_str.split('\r\n'))
	print(req[0])
	table = ''

	for i in req:
		k = i.split(':', maxsplit = 1)
		if len(k) != 2:
			k.append(' ')
		table += '<tr><td>%s</td><td>%s</td></tr>' %(k[0], k[1])

	html = open('index.html', 'r').read()
	html = html%table

	sendImg(html)

	conn.send(html.encode('utf-8'))
	conn.close()



if __name__ == '__main__':
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(('', 9778))
	sock.listen(1)

	while True:
		conn, addr = sock.accept()
		print(str(addr) + " - connected")
		getData(conn)

