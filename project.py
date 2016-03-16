from flask import Flask,render_template,request,redirect,url_for,flash,jsonify
app=Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base,Restaurant,MenuItem

from flask import session as login_session
import random,string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response


engine=create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind=engine
DBSession=sessionmaker(bind=engine)
session=DBSession()

@app.route('/login')
def showLogin():
	state=''.join(random.choice(string.ascii_uppercase+string.digits)for x in xrange(32))
	login_session['state']=state
	return 	render_template('login.html')
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
	restaurant=session.query(Restaurant).filter_by(id=restaurant_id).one()
	items=session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
	return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id,menu_id):
	item=session.query(MenuItem).filter_by(id=menu_id).one()
	return jsonify(MenuItems=item.serialize)


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



if __name__=='__main__':
	app.secret_key='p1p13420mentalist'
	app.debug=True
	app.run()