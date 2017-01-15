## CATALOG Application

This application provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users have the ability to post, edit and delete their own items.
The homepage displays all current categories along with the latest added items. Selecting a specific category shows you all the items available for that category.
Selecting a specific item shows you specific information of that item.
After logging in, a user has the ability to add, update, or delete item info.

There are four parts in this application:
--the HTML (templates)
--The CSS (in the static folder)
--The Flask Application (in the file python.py)
--The application includes authentication/authorization to allow users to login before making changes
--The database (set up with the file database_setup.py and populated with the file lotsofitems.py)


### Prerequisite 

#### Use of Vitual Machines
You need to install Vagrant and VirtualBox and then launch the Vagrant VM. 
The application uses Sqlalchemy and Flask.


### Description

#### Python Module

The file database_setup.py contains the database schema. The file lotsofitems.py helps to populate the database with one user and many items.

The file project.py contains the functions used to register, authenticate, connect and disconnect a user. It also contains functions to query the database, and redirect the user to different pages.

The application also contains many templates in the folder templates, a css file and a png image in the static folder.

#### Assets
The banner was provided through the following website: theicss.org

#### Database 

The database contains three tables.

- category : each entry contains an ID (integer) and a name (text). The ID is the primary key.
- item: this table contains all the titles, descriptions, the category ID as well as the ID or the item's creator:
--title (text)
--ID (integer). The ID is the primary key.
--cat_id (integer)
--and user_id (integer). 
  
- user: this table contains four columns:
--the ID (primary key)
--name (text)
--email (text)
--picture (text).

#### Login and Authentication
The program uses Google and Facebook login methods. The file clients_secrets.json contains the client ID for the Google login and authentication. The application Id for facebook is mentioned in the file login.html.

### How to run the code

The steps are:
#### Install Vagrant and VirtualBox


#### Launch the Vagrant VM
You need to launch the Vagrant VM.
```
vagrant up
```
```
vagrant ssh
```

#### Create the database  
You can then run the application within the VM (python /vagrant/catalog/).
```
python database_setup.py
```
Populate the database
```
python lotsofcategories.py
```
run the server
```
python project.py
```

Access and test your application by visiting http://localhost:8000 locally


**Author**

C. D. wrote the code for the functions in tournament.py.

**License**

The files are private domain works.

