import random, string
from db_format import Base, Category, Item
from flask import Flask, jsonify, request, url_for, render_template, flash, redirect, g, abort
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, asc, desc
from flask import session as login_session

import httplib2, json, requests
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json','r').read())['web']['client_id']
CLIENT_SECRET = json.loads(
    open('client_secrets.json','r').read())['web']['client_secret']
APPLICATION_NAME = "Item Catalog Application"

# Connect to database and creates db session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Creation of anti-forgery state token
@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
        for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# User login using gconnect
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User logout through gdisconnect
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# JSON APIs for database
@app.route('/catalog/JSON')
def showCatalogJSON():
    categories = session.query(Category).order_by(asc(Category.name))
    return jsonify(categories=[i.serialize for i in categories])

@app.route('/catalog/<path:category_name>/JSON')
def showCategoryJSON(category_name):
    category = session.query(Category).filter_by(name=category_name.title()).first()
    items = session.query(Item).filter_by(
        category=category).order_by(asc(Item.name)).all()
    return jsonify(items=[i.serialize for i in items])

@app.route('/catalog/<path:category_name>/<path:item_name>/JSON')
def showItemJSON(category_name,item_name):
    category = session.query(Category).filter_by(name=category_name.title()).first()
    item = session.query(Item).filter_by(name=item_name.title()).first()
    return jsonify(item.serialize)

# Homepage that currently routes to catalog
# Can be changed to be it's own page showing most recent updates or news
@app.route('/')
def showMainPage():
    return redirect(url_for('showCatalog'))

#Shows all categories
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).order_by(asc(Category.name))
    if 'username' in login_session:
        return render_template(
            'catalog.html', 
            categories = categories)
    else:
        return render_template(
            'catalog_public.html',
            categories = categories)

# Creates a new category
@app.route('/catalog/new/', methods=['GET', 'POST'])
def createCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        name = request.form['name']
        check = session.query(Category).filter_by(name=name.title()).all()
        if len(check) > 0:
            flash("Category "+name+" already exists.")
            return redirect(url_for('createCategory'))
        newCategory = Category(name=name.title())
        session.add(newCategory)
        flash('New category %s successfully created' %newCategory.name)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('createcategory.html')

# Shows a category
@app.route('/catalog/<path:category_name>/')
def showCategory(category_name):
    category = session.query(Category).filter_by(name=category_name.title()).first()
    items = session.query(Item).filter_by(
        category=category).order_by(asc(Item.name)).all()
    if 'username' in login_session:
        return render_template(
            'category.html', 
            category = category,
            items = items)
    else:
        return render_template(
            'category_public.html', 
            category = category,
            items = items)

# Edits a category
@app.route('/catalog/<path:category_name>/edit/', methods=['GET', 'POST'])
def editCategory(category_name):
    if 'username' not in login_session:
        return redirect('/login')
    editedCategory = session.query(Category).filter_by(name=category_name.title()).first()
    if request.method == 'POST':
        if request.form['name']:
            name = request.form['name']
            check = session.query(Category).filter_by(name=name.title()).all()
            if len(check) > 0:
                flash("Category "+name+" already exists.")
                return redirect(url_for('editCategory', category_name=category_name))
            editedCategory.name = name.title()
            return redirect(url_for('showCatalog'))
    else:
        return render_template(
            'editcategory.html', category=editedCategory)

# Deletes a category
@app.route('/catalog/<path:category_name>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_name):
    if 'username' not in login_session:
        return redirect('/login')
    deletedCategory = session.query(Category).filter_by(name=category_name.title()).first()
    if request.method == 'POST':
        session.delete(deletedCategory)
        flash('Category %s successfully deleted' %deletedCategory.name)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template(
            'deletecategory.html', category=deletedCategory)

# Creates a new item
@app.route('/catalog/<path:category_name>/new/', methods=['GET', 'POST'])
def createItem(category_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name.title()).first()
    if request.method == 'POST':
        name = request.form['name']
        check = session.query(Item).filter_by(name=name.title()).all()
        if len(check) > 0:
            flash("Item "+name+" already exists.")
            return redirect(url_for('createItem', category_name=category_name))
        newItem = Item(name=name.title(), description=request.form['description'],
            category=category)
        session.add(newItem)
        flash('New item successfully created: %s' %newItem.name)
        session.commit()
        return redirect(url_for('showCategory', category_name = category_name))
    else:
        return render_template('createitem.html', category = category)

# Shows an item
@app.route('/catalog/<path:category_name>/<path:item_name>/')
def showItem(category_name,item_name):
    category = session.query(Category).filter_by(name=category_name.title()).first()
    item = session.query(Item).filter_by(name=item_name.title()).first()
    if 'username' in login_session:
        return render_template(
            'item.html',
            category = category,
            item = item)
    else:
        return render_template(
            'item_public.html',
            category = category,
            item = item)

# Edits an item
@app.route('/catalog/<path:category_name>/<path:item_name>/edit/',
    methods=['GET', 'POST'])
def editItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name.title()).first()
    editedItem = session.query(Item).filter_by(name=item_name.title()).first()
    if request.method == 'POST':
        if request.form['name']:
            name = request.form['name']
            check = session.query(Item).filter_by(name=name).all()
            if len(check) > 0:
                flash("Item "+name+" already exists.")
                return redirect(url_for('editItem', category_name=category_name, item_name=item_name))
            editedItem.name = name.title()
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('showItem', category_name=category_name, item_name=item_name))
    else:
        return render_template(
            'edititem.html',
            category = category,
            item = editedItem)

# Deletes an item
@app.route('/catalog/<path:category_name>/<path:item_name>/delete/',
    methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name.title()).first()
    deletedItem = session.query(Item).filter_by(name=item_name.title()).first()
    if request.method == 'POST':
        session.delete(deletedItem)
        flash('Item %s successfully deleted' %deletedItem.name)
        session.commit()
        return redirect(url_for('showCategory', category_name=category_name))
    else:
        return render_template(
            'deleteitem.html',
            category = category,
            item = deletedItem)



if __name__ == '__main__':
    app.secret_key = CLIENT_SECRET
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
