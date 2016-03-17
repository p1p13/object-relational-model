from flask import Flask,render_template,request,redirect,url_for,flash,jsonify
app=Flask(__name__)

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base,Restaurant,MenuItem

from flask import session as login_session
import random,string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import urllib2
import urllib
from flask import make_response

CLIENT_ID=json.loads(open('client_secrets.json','r').read())['web']['client_id']


engine=create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind=engine
DBSession=sessionmaker(bind=engine)
session=DBSession()

@app.route('/')
def showLogin():
	state=''.join(random.choice(string.ascii_uppercase+string.digits)for x in xrange(32))
	login_session['state']=state
	return 	render_template('login.html',STATE=state)
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
	restaurant=session.query(Restaurant).filter_by(id=restaurant_id).one()
	items=session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
	return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id,menu_id):
	item=session.query(MenuItem).filter_by(id=menu_id).one()
	return jsonify(MenuItems=item.serialize)

@app.route('/restaurant')
def restaurant():
	return "hi"


@app.route('/')
@app.route('/restaurant/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
	restaurant=session.query(Restaurant).first()
	items=session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
	return render_template('menu.html',restaurant=restaurant,items=items)

@app.route('/restaurant/<int:restaurant_id>/new/',methods=['GET','POST'])
def newMenuItem(restaurant_id):
	if request.method=='POST':
		newItem=MenuItem(name=request.form['name'],restaurant_id=restaurant_id)
		session.add(newItem)
		session.commit()
		flash("new menu item created!")
		return redirect(url_for('restaurantMenu',restaurant_id=restaurant_id))
	else:
		return render_template('newmenuitem.html',restaurant_id=restaurant_id)

	

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit/',methods=['GET','POST'])
def editMenuItem(restaurant_id,menu_id):
	editedItem=session.query(MenuItem).filter_by(id=menu_id).one()
	if request.method=='POST':
		if request.form['name']:
			editedItem.name=request.form['name']
		session.add(editedItem)
		session.commit()
		flash("menu item edited!")
		return redirect(url_for('restaurantMenu',restaurant_id=restaurant_id))
	else:
		return render_template('editmenuitem.html',restaurant_id=restaurant_id,menu_id=menu_id,i=editedItem)
	return "page to edit menu item"

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete/',methods=['GET','POST'])
def deleteMenuItem(restaurant_id,menu_id):
	deleteItem=session.query(MenuItem).filter_by(id=menu_id).one()
	if request.method=='POST':
		session.delete(deleteItem)
		session.commit()
		flash("menu item deleted!")
		return redirect(url_for('restaurantMenu',restaurant_id=restaurant_id))
	else:
		return render_template('deletemenuitem.html',i=deleteItem)

@app.route('/gconnect',methods=['POST'])
def gconnect():
	if request.args.get('state')!=login_session['state']:
		print request.args.get('state')
		print login_session['state']
		response=make_response(	json.dumps('invalid stae parameter'),401)
		response.headers['Content-Type']='application/json'
		return response

	code=request.data
	try:
		oauth_flow=flow_from_clientsecrets('client_secrets.json',scope='')
		oauth_flow.redirect_uri='postmessage'
		credentials=oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		print FlowExchangeError
		response=make_response(	json.dumps('failed '),401)
		response.headers['Content-Type']='application/json'
		return response

	access_token=credentials.access_token
	url=('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
	h=httplib2.Http()
	result=json.loads(h.request(url,'GET')[1])
	if result.get('error') is not None:
		print "bye"
		response=make_response(json.dumps(result.get('error')),500)
		response.headers['Content-Type']='application/json'

	gplus_id=credentials.id_token['sub']
	if result['user_id']!=gplus_id :

		response=make_response(	json.dumps("token's user_id doesn't match given user_id"),401)
		response.headers['Content-Type']='application/json'
		return response

	if result['issued_to']!=CLIENT_ID :

		response=make_response(	json.dumps("token's client_id doesn't match given client_id"),401)
		response.headers['Content-Type']='application/json'
		return response

	stored_access_token=login_session.get('access_token')
	stored_gplus_id=login_session.get('gplus_id')
	if stored_access_token  is not None and gplus_id==stored_gplus_id :
		response=make_response(	json.dumps("current user is already connected"),200)
		response.headers['Content-Type']='application/json'

	login_session['access_token']=credentials.access_token
	

	userinfo_url="https://www.googleapis.com/oauth2/v1/userinfo"
	params={'access_token':credentials.access_token,'alt':'json'}
	answer=requests.get(userinfo_url,params=params)

	data=json.loads(answer.text)

	login_session['username']=data['name']
	login_session['picture']=data['picture']


	output=""
	output+='<h1>Welcome,'
	output+=login_session['username']
	output+='!</h1>'
	output+='<img src="'
	output+=login_session['picture']
	output+='"style="width:300px; height:300px;border-radius:150px;-webkit-border-radius:150px;-moz-border-radius:150px;">'
	flash("you are now logged in as %s"%login_session['username'])
	print output
	print login_session['access_token']
	return output
	print "hello"

@app.route("/gdisconnect")
def gdisconnect():
	access_token=login_session['access_token']
	if access_token is None:
		response=make_response(json.dumps('current user not connected'),401)
		response.headers['Content-Type']='application/json'
		return response
	print access_token
	url="https://accounts.google.com/o/oauth2/revoke?token=%s"%access_token
	
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	if result['status']=='200':
		print "yo"
		del login_session['access_token']
		del login_session['username']
		del login_session['picture']
		response=make_response(json.dumps('Successfully disconnected'),200)
		response.headers['Content-Type']='application/json'
		return response
	else:
		print result
		response=make_response(json.dumps('failed to revoke token'),400)
		response.headers['Content-Type']='application/json'
		return response

if __name__=='__main__':
	app.secret_key='p1p13420mentalist'
	app.debug=True
	app.run()