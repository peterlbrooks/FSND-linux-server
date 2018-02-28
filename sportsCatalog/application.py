# see all code at https://github.com/udacity/ud330/tree/master/Lesson4/step2
# if want to do oauth with Amazon https://login.amazon.com/website

from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash, make_response
from flask import session as login_session
from sqlalchemy import create_engine, asc, desc, and_
from sqlalchemy.orm import sessionmaker
from models import Base, Category, CategoryItem, User
import random
import datetime
import string
import json
import requests
import httplib2
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

app = Flask(__name__)

showCatalogOption = 1
showCatalogItemsOption = 2

# START Global vars

APPLICATION_NAME = "Catalog App"
G_CLIENT_ID = json.loads(
    open('/var/www/sportsCatalog/client_secrets.json', 'r').read())['web']['client_id']

FB_APP_ID = '755388191315918'

level1_name = "category"
level1_Name = "Category"

leve2_name = "category item"
level2_Name = "Category Item"

# END of global vars

# Connect to Database and create database session
engine = create_engine('postgresql://catalog:catalogu@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Google and FB authentication code uses approach from the lessons
# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # Landing page set in login.html, can't pass via Jinga
    return render_template('login.html', STATE=state, G_CLIENT_ID=G_CLIENT_ID,
                           FB_APP_ID=FB_APP_ID)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    app_id = json.loads(open('/var/www/sportsCatalog/fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('/var/www/sportsCatalog/fb_client_secrets.json', 'r').read())['web']['app_secret']

    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange
        we have to split the token first on commas and select the first
        index which gives us the key : value for the server access token
        then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used
        directly in the graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me''?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output = '!</h1><img src="'
    'login_session[''picture'']'
    ' " style = "width: 300px; height: 300px;border-radius:'
    '150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


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
        oauth_flow = flow_from_clientsecrets('/var/www/sportsCatalog/client_secrets.json', scope='')
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
    if result['issued_to'] != G_CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')

    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
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
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = '<h1>Welcome, '
    'login_session[''username'']!</h1><img src="'
    'login_session[''picture'']'
    ' " style = "width: 300px; height: 300px;border-radius:'
    '150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
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

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Information


@app.route('/catalog/JSON')
def catalogJSON():

    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/category/<categoryName>/<itemName>/JSON')
def itemJSON(categoryName, itemName):

    item = session.query(CategoryItem).filter(and_(
        CategoryItem.name == itemName,
        CategoryItem.categoryOwnerName == categoryName)).one()
    return jsonify(item=item.serialize)

# Methods


# Show all categories
@app.route('/')
@app.route('/catalog/')
@app.route('/category/')
def showCatalog():

    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(CategoryItem).order_by(asc(
        CategoryItem.dateUpdated)).limit(10).all()
    return render_template(
        'catalog.html', categories=categories,
        items=items, option=showCatalogOption)


# Show the category's items
@app.route('/category/<categoryName>/')
@app.route('/category/<categoryName>/items/')
def showCategoryItems(categoryName):

    selectedCategory = session.query(Category).filter_by(
        name=categoryName).one()
    creator = getUserInfo(selectedCategory.creatorID)
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(CategoryItem).filter_by(
        categoryOwnerID=selectedCategory.id).all()
    itemCount = len(items)

    return render_template('catalog.html', categories=categories,
                           items=items, selectedCategory=selectedCategory,
                           creator=creator,
                           option=showCatalogItemsOption,
                           itemCount=itemCount)


# Show an item
@app.route('/category/<categoryName>/item/<itemName>',
           methods=['GET', 'POST'])
def showItem(categoryName, itemName):

    if request.method == 'POST':
        return redirect(url_for('showCatalog', categoryName=categoryName))

    else:
        item = session.query(
            CategoryItem).filter(
            and_(
                CategoryItem.name == itemName,
                CategoryItem.categoryOwnerName == categoryName)).one()
        edit_URL = url_for(
            'editItem', categoryName=categoryName, itemName=itemName)
        delete_URL = url_for(
            'deleteItem', categoryName=categoryName, itemName=itemName)
        cancel_URL = url_for('showCategoryItems', categoryName=categoryName)
        return render_template(
            'showItem.html', categoryName=categoryName,
            item=item, edit_URL=edit_URL, cancel_URL=cancel_URL,
            delete_URL=delete_URL)


# Create a new item
@app.route('/category/<categoryName>/items/new/', methods=['GET', 'POST'])
def newItem(categoryName):

    if 'username' not in login_session:
        flash('You must be logged in to create a New Item')
        return redirect('/category/' + categoryName + '/items/')

    categories = session.query(Category).order_by(asc(Category.name))
    selectedCategory = session.query(Category).filter_by(
        name=categoryName).one()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        if name and description:
            newCategoryID = (request.form.get('category'))
            newCategory = session.query(Category).filter_by(
                id=newCategoryID).one()
            newItem = CategoryItem(
                name=name,
                description=description,
                categoryOwnerID=newCategory.id,
                categoryOwnerName=newCategory.name,
                dateUpdated=datetime.datetime.utcnow(),
                creatorID=login_session['user_id'])
            session.add(newItem)
            session.commit()
            # flash('New  %s Item Successfully Created' % (newItem.name))
            return redirect(url_for('showCatalog'))
        else:
            flash('Please enter data in all fields')
            cancel_URL = url_for(
                'showCategoryItems', categoryName=categoryName)
            return render_template(
                'newItem.html',
                categoryName=categoryName,
                itemName=name, itemDescription=description,
                cancel_URL=cancel_URL, categories=categories)

    else:
        cancel_URL = url_for('showCategoryItems', categoryName=categoryName)
        return render_template(
            'newItem.html', categoryName=categoryName,
            cancel_URL=cancel_URL, categories=categories)


# Edit an item
@app.route('/category/<categoryName>/item/<itemName>/edit',
           methods=['GET', 'POST'])
def editItem(categoryName, itemName):

    edittedItem = session.query(CategoryItem).filter(and_(
        CategoryItem.name == itemName,
        CategoryItem.categoryOwnerName == categoryName)).one()

    if ('username' not in login_session or
            login_session['user_id'] != edittedItem.creatorID):
        flash('Only the creator of an item can edit an item')
        return redirect('/category/' + categoryName + '/item/' + itemName)

    categories = session.query(Category).order_by(asc(Category.name))

    if request.method == 'POST':
        if request.form['name']:
            edittedItem.name = request.form['name']

        if request.form['description']:
            edittedItem.description = request.form['description']

        newCategoryID = (request.form.get('category'))
        newCategory = session.query(Category).filter_by(
            id=newCategoryID).one()

        edittedItem.categoryOwnerName = newCategory.name
        edittedItem.dateUpdated = datetime.datetime.utcnow()
        edittedItem.categoryOwnerID = newCategoryID
        session.add(edittedItem)
        session.commit()
        flash('Item Successfully updated')
        return redirect(url_for(
            'showItem', categoryName=newCategory.name,
            itemName=edittedItem.name))

    else:
        cancel_URL = url_for(
            'showItem', categoryName=categoryName, itemName=itemName)
        return render_template(
            'editItem.html', categoryName=categoryName, categories=categories,
            item=edittedItem, cancel_URL=cancel_URL)


# Delete an item
@app.route('/category/<categoryName>/item/<itemName>/delete',
           methods=['GET', 'POST'])
def deleteItem(categoryName, itemName):

    itemToDelete = session.query(CategoryItem).filter(and_(
        CategoryItem.name == itemName,
        CategoryItem.categoryOwnerName == categoryName)).one()

    if ('username' not in login_session or
            login_session['user_id'] != itemToDelete.creatorID):
        flash('Only the creator of an item can delete an item')
        return redirect('/category/' + categoryName + '/item/' + itemName)

    if login_session['user_id'] != itemToDelete.creatorID:
        returnText = "<script>function myFunction() {alert('Item not deleted"
        returnText += "  - you can only delete items in categories you "
        returnText += "created.');}</script><body onload='myFunction()'>"
        return returnText

    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(
            url_for('showCategoryItems', categoryName=categoryName))

    else:
        cancel_URL = url_for(
            'showItem', categoryName=categoryName, itemName=itemName)
        return render_template('deleteItem.html', item=itemToDelete,
                               cancel_URL=cancel_URL)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():

    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))

    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))


if __name__ == '__main__':

    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run()
