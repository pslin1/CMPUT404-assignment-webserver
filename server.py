#!/usr/bin/env python3
#  coding: utf-8 
import socketserver
import os
import datetime

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
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
		#print("yes 301")
		status = "HTTP/1.0 301 Moved Permanently\r\n"
		date_info = str(datetime.datetime.now()) + "\r\n"
		connection = "Connection: close\r\n"

		location = "Location: http://127.0.0.1:8080" + redirect + "/index.html\r\n"

		byte_form = bytearray(status + date_info + connection + location, 'utf-8')

		self.request.sendall(byte_form)

	def build_200(self, requested_path):
		status = "HTTP/1.0 200 OK\r\n"
		date_info = str(datetime.datetime.now()) + "\r\n"
		if requested_path.endswith(".html"):
			content_type = "Content-Type: text/html\r\n"
		elif requested_path.endswith(".css"):
			#print("CSS requested")
			content_type = "Content-Type: text/css\r\n"
		#IMPORTANT: the double \r\n at the end is crucial to base.css being requsted, 
		#if it is one \r\n there will be no GET request for the CSS file
		connection = "Connection: close\r\n\r\n"
		content = open(requested_path, "r").read()

		print(date_info)

		byte_form = bytearray(status + date_info + content_type + connection + content, 'utf-8')

		self.request.sendall(byte_form)

	def handle(self):
		self.data = self.request.recv(1024).strip()
		print ("Got a request of: %s\n" % self.data)
		#self.request.sendall(bytearray("OK",'utf-8'))
		#self.request.sendall()

		#Parse self.data here, check what it is getting
		self.split_data = str(self.data).split(" ")
		#for item in self.parsed_data:
			#print(item + "\n")

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

			self.current_directory = os.getcwd()
			
			self.requested_path = self.current_directory + "/www" + self.requested_content

			self.exists = os.path.isfile(self.requested_path)

			if self.exists:
				#Handle 200
				self.build_200(self.requested_path)

			#print(self.current_directory)

			#else:
				#DO 404 HERE


		#else:
			#DO 405 HERE

		#301, 404 handler
		#GET / is a 302 redirect

		#handle 200 here

		#construct response and self.request.sendall() it


if __name__ == "__main__":
	HOST, PORT = "localhost", 8080

	socketserver.TCPServer.allow_reuse_address = True
	# Create the server, binding to localhost on port 8080
	server = socketserver.TCPServer((HOST, PORT), MyWebServer)

	# Activate the server; this will keep running until you
	# interrupt the program with Ctrl-C
	server.serve_forever()
