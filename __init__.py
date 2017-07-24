from flask import Flask, render_template, request, redirect, jsonify, url_for,\
	flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2  # comprehensive client library in Python
import json  # provides an api for converting in memory python objects\
# to a serialized representation - json
from flask import make_response  # converst return value from function \
# into a real response object we can send off to client
import requests  # Apache2 licence http library written in python\
# similar to httplib2 but with some improvements
from functools import wraps  # to create a Flask decorator

app = Flask(__name__)

#CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
CLIENT_ID = json.loads(open('/var/www/catalog/catalog/client_secrets.json', 'r').read())['web']['client_id']

# Connect to Database and create database session
engine = create_engine('postgresql+psycopg2://catalog:aaa@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# create a login decorator function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


# Create a state token to prevent requests
# Store it in the session for later validation
@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase+string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
        # upgrade the authorization code into a credentials project
        # oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow = flow_from_clientsecrets('/var/www/catalog/catalog/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade \
            the authorization code.'))
        response.headers['Content-Type'] = 'application/json'
        return response
    # check that access_token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    # convert the h.request(url, 'GET')[1] (bytes) to string
    # to make sure that anyone using python 2.x.x or 3.x.x 
    # will not fall into error
    result = json.loads(h.request(url, 'GET')[1].decode ("utf8"))
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    # Verify that the access token is used by the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's client ID does not match\
                 app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verrify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that user is not already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already\
                 connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # Add provider to login session
    login_session['provider'] = 'google'
    # see if user exists, if it doesn't make a new one
    # check if email address is already in the database. If not create
    # a new User account. Then store user ID in the login session
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    # Create a greeting message
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;\
            -webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("You are logged in as %s." % login_session['username'])
    return output


@app.route('/gdisconnect/')
def gdisconnect():
    '''
    This function is called by the disconnect() function.
    The user session is completely reset after disconnect function calls
    out the gdisconnect function.
    '''
    # Only disconnect a connected user
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('User not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Execute HTTP GET request to revoke current session
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Send message that the user is diconnected
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason the token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    print 'fb'
    # to protect against cross-state forgery attacks
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print('access_token:'+ access_token)
    # Exchange client token for long-lived server-side token with GET /oauth/
    # access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret=
    # {app-secret}&fb_exchange_token={short-lived-token}
    # app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']
    # ['app_id']
    # app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']
    # ['app_secret']
    app_id = json.loads(open('/var/www/catalog/catalog/fb_client_secrets.json', 'r').read())['web']\
    ['app_id']
    print('app_id: ' + app_id)
    # redirect_uri = json.loads(open('fb_client_secrets.json', 'r').
    #                          read())['web']['redirect_uri']

    # redirect_uri = json.loads(open('/var/www/catalog/catalog/fb_client_secrets.json', 'r').
    #                          read())['web']['redirect_uri']

    app_secret = json.loads(
        open('/var/www/catalog/catalog/fb_client_secrets.json', 'r').read())['web']['app_secret']
    print('app_secret: '+app_secret)
    #url = 'https://graph.facebook.com/oauth/access_token?grant_type=\
    #    fb_exchange_token&client_id=%s&clientsecret=%s&fb_exchange_token=%s&\
    #    redirect_uri=%s' \
    #    % (app_id, app_secret, access_token, redirect_uri)

    url = ('https://graph.facebook.com/v2.8/oauth/access_token?grant_type='
        'fb_exchange_token&client_id=%s&clientsecret=%s&fb_exchange_token=%s') % (app_id, 
        app_secret, access_token)

    print ('url facebook: ' + url)
    #url = ('https://graph.facebook.com/v2.9/oauth/access_token?'
    #       'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
    #       '&fb_exchange_token=%s') % (app_id, app_secret, access_token)

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print('result is :' + result)
    data = json.loads(result)
    print('data is :')
    print data

    # use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.9/me"
    # strip expire tag from access token
    ###token = result.split("&")[0]
    token = 'access_token=' + data['access_token']

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"%url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&\
        height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # check whether user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;\
           -webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect/')
def fbdisconnect():
    '''
    This function is called by the disconnect() function.
    The user session is completely reset after disconnect function calls
    out the fbdisconnect function.
    '''
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "You have been logged out."


@app.route('/disconnect/')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            # remove the access_token
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have been successfully logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in to begin with!")
        return redirect(url_for('showCategories'))


# JSON APIS to view category information
@app.route('/catalog/<string:cat_name>/items/JSON')
def itemsListJSON(cat_name):
    category = session.query(Category).filter_by(name=cat_name).one()
    items = session.query(Item).filter_by(cat_id=category.id).order_by(asc(Item.id))
    return jsonify(items=[i.serialize for i in items])


@app.route('/catalog/JSON')
def catsListJSON():
    categories = session.query(Category).order_by(asc(Category.name))
    return jsonify(categories=[c.serialize for c in categories])


# show all categories
@app.route('/')
@app.route('/catalog/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).order_by(Item.id.desc()).limit(10)
    if 'username' not in login_session:
        return render_template('/publiccategories.html', categories=categories,
                               items=items)
    else:
        return render_template('/categories.html', categories=categories,
                               items=items)


# show the details of one item
@app.route('/catalog/<string:cat_name>/<string:item_title>/',
           methods=['POST', 'GET'])
def showOneItem(cat_name, item_title):
    category = session.query(Category).filter_by(name=cat_name).one()
    item = session.query(Item).filter_by(title=item_title,
                                         category=category).one()
    creator = getUserInfo(item.user_id)
    if 'username' not in login_session or \
            creator.id != login_session['user_id']:
        return render_template('publicOneItem.html', item=item)
    if request.method == 'POST':
        return redirect(url_for('editItem', item_title=item.title,
                                cat_name=cat_name))
    else:
        return render_template('oneItem.html', item=item)


# show the details of all item that belong to a category
@app.route('/catalog/<string:cat_name>/items/')
def showAllItems(cat_name):
    category = session.query(Category).filter_by(name=cat_name).one()
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).filter_by(category=category).\
        order_by(asc(Item.title))
    nb_items = session.query(Item).filter_by(category=category).count()
    if 'username' not in login_session:
        return render_template('publicAllItems.html', categories=categories,
                               category=category, items=items,
                               nb_items=nb_items)
    else:
        return render_template('allItems.html', categories=categories,
                               category=category, items=items,
                               nb_items=nb_items)


@app.route('/catalog/item/new/', methods=['POST', 'GET'])
@login_required
def newItem():
    # With the decorator @login_required, we do not need to re-check whether
    # the user is logged in. The same decorator redirects the user to the
    # login page if the user is not logged in.
    if request.method == 'POST':
        if request.form['title'] and request.form['description'] and\
                request.form['category']:
            title = request.form['title']
            description = request.form['description']
            cat_name = request.form['category']
            category = session.query(Category).filter_by(name=cat_name).one()
            # check that the item is not already saved
            try:
                item = session.query(Item).filter_by(title=title,
                                                     category=category).one()
                print 'none'
                flash('The item is already in the catalog.\
                      Please enter another item.')
                return redirect(url_for('newItem'))
            except NoResultFound:
                print "not none"
                newItem = Item(title=title, description=description,
                               category=category, cat_id=category.id,
                               user_id=login_session['user_id'])
                session.add(newItem)
                session.commit()
                flash('Item %s Successfully Created.' % title)
                return redirect(url_for('showAllItems',
                                        cat_name=category.name))

        else:
            flash('Please fill out all fields.')
            return redirect(url_for('newItem'))
    else:
        categories = session.query(Category).order_by(asc(Category.name))
        return render_template('newItem.html', categories=categories)


@app.route('/catalog/<string:cat_name>/<string:item_title>/edit/',
           methods=['POST', 'GET'])
@login_required
def editItem(item_title, cat_name):
    # With the decorator @login_required, we do not need to re-check whether
    # the user is logged in. The same decorator redirects the user to the
    # login page if the user is not logged in.
    category = session.query(Category).filter_by(name=cat_name).one()
    item = session.query(Item).filter_by(title=item_title,
                                         cat_id=category.id).one()
    categories = session.query(Category).order_by(asc(Category.name))

    if item.user_id != login_session['user_id']:
        return "<script>function myFunction(){alert('Tou are not authorized to \
            edit this restaurant. Please create your own restaurant in order \
            to delete.');}</script><body onload='myFunction()'>"

    if request.method == 'POST':
        if request.form['title']:
            item.title = request.form['title']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category']:
            cat_name = request.form['category']
            category = session.query(Category).filter_by(name=cat_name).one()
            item.category = category
        session.add(item)
        session.commit()
        return redirect(url_for('showAllItems', cat_name=cat_name))
    else:
        return render_template('editItem.html', item=item,
                               cat_name=item.category.name,
                               categories=categories)


@app.route('/catalog/<string:cat_name>/<string:item_title>/delete/',
           methods=['POST', 'GET'])
@login_required
def deleteItem(cat_name, item_title):
    # With the decorator @login_required, we do not need to re-check whether
    # the user is logged in. The same decorator redirects the user to the
    # login page if the user is not logged in.
    item = session.query(Item).filter_by(title=item_title).one()

    if item.user_id != login_session['user_id']:
        return "<script>function myFunction(){alert('Tou are not authorized\
            to edit this menu item. Please create your own menu in order \
            to edit.');}</script><body onload='myFunction()'>"

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showAllItems', cat_name=cat_name))
    else:
        return render_template('deleteItem.html', item=item)


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    # Remember to turn off debugging when application is hosted 
    # in production environment.
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
