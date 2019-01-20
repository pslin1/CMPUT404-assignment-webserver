#!/usr/bin/env python3
#  coding: utf-8 
import socketserver
import os
import datetime

# Copyright 2019 Shu-Jun Pierre Lin, Abram Hindle, Eddie Antonio Santos

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

	def build_301(self, redirect):
		status = "HTTP/1.0 301 Moved Permanently\r\n"

		connection = "Connection: close\r\n"

		location = "Location: http://127.0.0.1:8080" + redirect + "/index.html\r\n"

		byte_form = bytearray(status + connection + location, 'utf-8')

		self.request.sendall(byte_form)


	def build_200(self, requested_path):
		#Credit: toriningen (username)
		# https://stackoverflow.com/a/10114266
		status = "HTTP/1.0 200 OK\r\n"
		# https://www.tutorialspoint.com/python/string_endswith.htm
		if requested_path.endswith(".html"):
			content_type = "Content-Type: text/html\r\n"
		elif requested_path.endswith(".css"):
			content_type = "Content-Type: text/css\r\n"
		#IMPORTANT: the double \r\n at the end is crucial to base.css being requsted, 
		#if it is one \r\n there will be no GET request for the CSS file
		connection = "Connection: close\r\n\r\n"
		#Content always has to go last, whatever before has to be \r\n\r\n
		content = open(requested_path, "r").read()

		byte_form = bytearray(status + content_type + connection + content, 'utf-8')

		self.request.sendall(byte_form)


	def build_404(self):
		status = "HTTP/1.0 404 Not Found\r\n"

		connection = "Connection: close\r\n\r\n"
		content = "This is a 404 error page"

		byte_form = bytearray(status + connection + content, 'utf-8')

		self.request.sendall(byte_form)


	def build_405(self):
		status = "HTTP/1.0 405 Method Not Allowed\r\n"

		connection = "Connection: close\r\n\r\n"
		content = "This is a 405 error page"

		byte_form = bytearray(status + connection + content, 'utf-8')

		self.request.sendall(byte_form)


	def handle(self):
		self.data = self.request.recv(1024).strip()
		#print ("Got a request of: %s\n" % self.data)

		#Parse self.data here, check what it is getting
		#https://www.w3schools.com/python/ref_string_split.asp
		self.split_data = str(self.data).split(" ")

		#This is the content that the user wants
		self.requested_content = self.split_data[1]
		#This is so http://127.0.0.1/index.html and http://127.0.0.1/ both give 200 OK
		#FIX: Now works with all directories, not just root
		if self.requested_content.endswith("/"):
			self.requested_content = self.requested_content + "index.html"

		if self.split_data[0] == "b'GET":
			#Check if client is trying to get to http://127.0.0.1/deep
			#if so, 301 redirect to http://127.0.0.1/deep/index.html
			if self.split_data[1] in ["/deep"]:
				#Handle 301
				self.build_301(self.split_data[1])

			# Credit: Jeremy Grifski
			# https://therenegadecoder.com/code/how-to-check-if-a-file-exists-in-python/
			self.current_directory = os.getcwd()
			
			self.requested_path = self.current_directory + "/www" + self.requested_content

			self.exists = os.path.isfile(self.requested_path)

			#If this path exists
			if self.exists:
				#Handle 200
				#Try to construct a 200 response
				try:
					self.build_200(self.requested_path)
				#If fails, then content type is NOT .css or .html or one of the approved directories
				except UnboundLocalError:
					self.build_404()

			#If requested content does not exist
			else:
				self.build_404()

		#If not a GET request
		else:
			self.build_405()


if __name__ == "__main__":
	HOST, PORT = "localhost", 8080

	socketserver.TCPServer.allow_reuse_address = True
	# Create the server, binding to localhost on port 8080
	server = socketserver.TCPServer((HOST, PORT), MyWebServer)

	# Activate the server; this will keep running until you
	# interrupt the program with Ctrl-C
	server.serve_forever()
