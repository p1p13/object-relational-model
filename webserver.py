from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import cgi

from database_setup import Base,Restaurant,MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine=create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind=engine
DBSession=sessionmaker(bind=engine)
session=DBSession()


class webserverHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/restaurants/new"):
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()
				output=""
				output+="<html><body>"
				output+="<h1>Make a New Restaurant</h1>"
				output+="<form method=POST enctype='multipart/form-data' action='/restaurants/new'><input name='newRestaurantName' type='text' placeholder='New Restaurant Name'><input type='submit' value='create'></form>"
				output+="</body></html>"
				self.wfile.write(output)
				print output
				return
			if self.path.endswith("/delete"):
				restaurantIDPath=self.path.split("/")[2]
				myRestaurantQuery=session.query(Restaurant).filter_by(id=restaurantIDPath).one()
				if myRestaurantQuery!=[]:
					self.send_response(200)
					self.send_header('Content-type','text/html')
					self.end_headers()
					output=""
					output+="<html><body>"
					output+="<h1>Are u sure to delete %s?</h1>"% myRestaurantQuery.name
					
					output+="<form method=POST enctype='multipart/form-data' action='/restaurants/%s/delete'>"%restaurantIDPath
					output+="<input type='submit' value='Delete'></form>"
					output+="</body></html>"
					self.wfile.write(output)

			if self.path.endswith("/edit"):
				restaurantIDPath=self.path.split("/")[2]
				myRestaurantQuery=session.query(Restaurant).filter_by(id=restaurantIDPath).one()
				if myRestaurantQuery!=[]:
					self.send_response(200)
					self.send_header('Content-type','text/html')
					self.end_headers()
					output=""
					output+="<html><body><h1>"
					output+=myRestaurantQuery.name
					output+="</h1>"
					output+="<form method=POST enctype='multipart/form-data' action='/restaurants/%s/edit'>"%restaurantIDPath
					output+="<input name='newRestaurantName' type='text' placeholder='%s'>"%myRestaurantQuery.name
					output+="<input type='submit' value='Rename'></form>"
					output+="</body></html>"
					self.wfile.write(output)
				

			if self.path.endswith("/restaurants"):
				restaurants=session.query(Restaurant).all()
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()
				output=""
				output+="<html><body>"
				output+="<a href='/restaurants/new'> Make a new Restaurant</a></br></br>"
				for restaurant in restaurants:
					output+="</br>"
					output+=restaurant.name
					output+="</br>"
					output+="<a href='/restaurants/%s/edit'>Edit</a>"%restaurant.id
					output+="</br>"
					output+="<a href='/restaurants/%s/delete'>Delete</a>"%restaurant.id


				output+="</body></html>"
				self.wfile.write(output)
				print output
				return

			if self.path.endswith("/hello"):
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()
				output=""
				output+="<html><body>hello!"
				output+="<form method=POST enctype='multipart/form-data' action='/hello'><input name='message' type='text'><input type='submit' value='submit'></form>"
				output+="</body></html>"
				self.wfile.write(output)
				print output
				return
			if self.path.endswith("/hola"):
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()
				output=""
				output+="<html><body>&#161Hola <a href='/hello'>Back to hello</a>"
				output+="<form method=POST enctype='multipart/form-data' action='/hello'><input name='message' type='text'><input type='submit' value='submit'></form>"
				output+="</body></html>"
				self.wfile.write(output)
				print output
				return
		except IOError:
			self.send_error(404,"File Not Found %s" % self.path)

	def do_POST(self):
		try:
			if self.path.endswith("/delete"):
				ctype,pdict=cgi.parse_header(self.headers.getheader('Content-type'))
				
				restaurantIDPath=self.path.split("/")[2]
				myRestaurantQuery=session.query(Restaurant).filter_by(id=restaurantIDPath).one()
				if myRestaurantQuery!=[]:
					
					session.delete(myRestaurantQuery)
					session.commit

					
					self.send_response(301)
					self.send_header('Content-type','text/html')
					self.send_header('Location','/restaurants')
					self.end_headers()
					

			if self.path.endswith("/edit"):
				ctype,pdict=cgi.parse_header(self.headers.getheader('Content-type'))
				if ctype=='multipart/form-data':
					fields=	cgi.parse_multipart(self.rfile,pdict)
				messagecontent=	fields.get('newRestaurantName')
				restaurantIDPath=self.path.split("/")[2]
				myRestaurantQuery=session.query(Restaurant).filter_by(id=restaurantIDPath).one()
				if myRestaurantQuery!=[]:
					myRestaurantQuery.name=messagecontent[0]
					session.add(myRestaurantQuery)
					session.commit

					
					self.send_response(301)
					self.send_header('Content-type','text/html')
					self.send_header('Location','/restaurants')
					self.end_headers()
					

				
			if self.path.endswith("restaurants/new"):
				ctype,pdict=cgi.parse_header(self.headers.getheader('Content-type'))
				if ctype=='multipart/form-data':
					fields=	cgi.parse_multipart(self.rfile,pdict)
				messagecontent=	fields.get('newRestaurantName')

				newRestaurant=Restaurant(name=messagecontent[0])
				session.add(newRestaurant)
				session.commit()




				self.send_response(301)
				self.send_header('Content-type','text/html')
				self.send_header('Location','/restaurants')
				self.end_headers()
				return

			#output+="<form method=POST enctype='multipart/form-data' action='/hello'><input name='message' type='text'><input type='submit' value='submit'></form>"
			#output+="</body></html>"
			#self.wfile.write(output)
			#ctype,pdict=cgi.parse_header(self.headers.getheader('Content-type'))
			#if ctype=='multipart/form-data':
			#	fields=	cgi.parse_multipart(self.rfile,pdict)
			#	messagecontent=	fields.get('message')
			#print output
			#output=""
			#output+="<html>	<body>"
			#output+="<h2>%s</h2>"%messagecontent[0]
		except:
			pass



def main():
	try:
		port=8080
		server=HTTPServer(('',port),webserverHandler)
		print "Web server running on port %s" % port
		server.serve_forever()

	except KeyboardInterrupt:
		print "^C entered ,stopping web server"
		server.socket.close()


if __name__=='__main__':
	main()
