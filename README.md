# CATALOG Application

This application provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users have the ability to post, edit and delete their own items.
The homepage displays all current categories along with the latest added items. Selecting a specific category shows you all the items available for that category.
Selecting a specific item shows you specific information of that item.
After logging in, a user has the ability to add, update, or delete item info.

There are four parts in this application:

--The HTML (templates)

--The CSS (in the static folder)

--The Flask Application (in the file python.py)

--The application includes authentication/authorization to allow users to login before making changes

--The database (set up with the file database_setup.py and populated with the file lotsofitems.py)


## Prerequisite 

### Lightsail Server
The application was deployed on a server on Lightsail. The application uses Sqlalchemy and Flask.

### Linux Server configuration 
--IP: 54.179.143.72

--SSH Port: 2200

--Amazon Web Services URL: http://ec2-54-179-143-72.ap-southeast-1.compute.amazonaws.com/

## Steps to run the application live on a secure server
### Download private key from Amazon Lightsail console
After the download, rename it as udacity_key.pem and move it into ~/.ssh folder
```
mv udacity_key.pem ~/.ssh
```
### Update and upgrade package source list 
The list of packages is available in /etc/apt/source_list
```
sudo apt-get update
```
```
sudo apt-get upgrade
```
And remove the unnecessary packages:
```
sudo apt-get autoremove
```

### Install new software finger
```
sudo apt-get install finger
```
Check the list of users with the command:
```
finger
```
Check the details about the user ubuntu:
```
finger ubuntu
```
### Add user grader
```
sudo adduser grader
```
Review the user's detail:
```
finger user
```
Review the password entries file. The last line should contain the new user grader.
```
cat /etc/passwd
```

### Attribution of sudo rights
```
sudo ls -al /etc/sudoers.d
```
```
sudo cat /etc/sudoers.d/90-cloud-init-users
```
```
sudo cp /etc/sudoers.d/90-cloud-init-users /etc/sudoers.d/grader
```
```
sudo nano /etc/sudoers.d/grader
```
And then change "ubuntu" into "grader".
(Note: User password expiration: sudo password -e grader)

### Connect with to the server after key encryption
On the LOCAL machine, type:
```
ssh_keygen
```
The ssh_keygen command will generate two files (public key and private key). The file ending with .pub is the public key.

Log on as grader:
```
mkdir .ssh
```
```
touch .ssh/authorized_keys
```
Copy from the LOCAL machine to the SERVER the PUBLIC key. The private key should always stay on the local machine.
copy the content of 
```
cat .ssh/grader.pub (on the local machine)
```
And copy inside the authorized_keys file:
```
nano .ssh/authorized_keys
```
On the server, change file permissions:
```
chmod 700 .ssh
```
```
chmod 644 .ssh/authorized_keys
```

Login from LOCAL machine:
As grader: 
```
ssh -i ~/.ssh/grader grader@54.179.143.72 -p2200
```
Or as ubuntu: 
```
ssh -i ~/.ssh/udacity_key.pem ubuntu@54.179.143.72 -p2200
```

Disable password-based logins:
```
sudo nano /etc/ssh/sshd_config
```
Change "PasswordAuthentication yes" to "PasswordAuthentication no".

The SSHD service, which is listening on all SSH connections needs to be started again to read teh configuration file.
```
sudo service ssh restart
```

### Set up firewalls
We need to add rules and then turn on the firewall.
Deny all incoming requests: 
```
sudo ufw default deny incoming
```
Allow all outgoing requests:
```
sudo ufw default allow outgoing
```
Check the status:
```
sudo ufw status
```
Configure the firewall by allowing ssh,tcp (port 2200), www (port 80), tcp (port 123)
```
sudo ufw allow ssh
```
```
sudo ufw allow 2200/tcp
```
```
sudo ufw allow www
```
```
sudo ufw allow 123/udp
```
Enable the firewall:
```
sudo ufw enable
```
Check the status:
```
sudo ufw status
```
### Install postgresql
```
sudo apt-get install postgresql postgresql-contrib
```
Create superuser postgres
```
sudo su -posgres
```
Open the interactive terminal for working with Postgres
```
psql
```
create user and database:
```
CREATE DATABASE catalog
CREATE USER catalog
\q
```

### Clone the git repository and tranfer the client_secrets JSON files (for Facebook and Google)
```
mkdir /var/www/catalog
```
```
mkdir /var/www/catalog/catalog
```
```
sudo git clone https://github.com/GoldAdventurer/CATALOG
```
Move to the folder which contains the two JSON files (on the local computer) after checking that the credentials of the client_secrets file match theÂcredentials on the [Google console](https://console.cloud.google.com/) or [facebook console](https://developers.facebook.com/apps/).

```
sudo scp -v -i ~/.ssh/udacity_key.pem fb_client_secrets.json ubuntu@54.179.143.72:/var/www/app/catalog
```
```
sudo scp -v -i ~/.ssh/udacity_key.pem client_secrets.json ubuntu@54.179.143.72:/var/www/app/catalog
```

Then makes the following changes to project.py:
- Change the name to __init__.py
- Replace all the mentions to the JSON file by the whole path /var/www/catalog/catalog/client_secrest.json
- Replace the sqlite-related lines to `engine = create_engine('postgresql+psycopg2://catalog:aaa@localhost/catalog')`.
aaa is the password for user catalog.
- Add the URL and the IP to the Google and Facebook credentials pages.

### Update the firewall
Now that we have uploaded the two JSON files using ssh we can disable port 22.
```
sudo ufw delete allow ssh
```
```
sudo ufw status
```
### Install and configure Apache
```
sudo apt-get install apache2
```
Install the application handler mod_wsgi:
```
sudo apt-get install libapache2-mod-wsgi
```
Configure Apache:

Edit the file` /etc/apache2/sites-available/000-default.conf` and add inside the text between <VirtualHost *:80> and </VirtualHost>

`        
        ServerName 54.179.143.72

        ServerAdmin grader@54.179.143.72

        <Directory /var/www/catalog/catalog>
            Order allow,deny
            Allow from all
        </Directory>
        <Directory /var/www/catalog/catalog/static>
            Order allow,deny
            Allow from all
        </Directory>

        <Directorymatch "^/.*/\.git/">
            Order deny,allow
            Deny from all
        </Directorymatch>

        WSGIScriptAlias / /var/www/catalog/myapp.wsgi
`

The paragraph starting with "<Directorymatch" prevents Apache from serving the .git directory and ensures the folder is not publicly accessible via a browser. There is another method using the .htaccess file in the .git folder (see below).

Restart Apache
```
sudo apache2ctl restart
```

Write file myapp.wsgi in the folder /var/www/catalog:

`#!/usr/bin/python

import sys

import logging

logging.basicConfig(stream=sys.stderr)

sys.path.insert(0,"/var/www/catalog/")

from catalog import app as application

application.secret_key = "/var/www/catalog/catalog/client_secrets.json"
`
### Install other modules
Upgrade pip at the root level:
```
sudo -H pip install --upgrade pip
```
```
sudo pip install flask
```
```
sudo apt-get install python-psycopg2
```
```
sudo pip install requests
```
google-api-python-client contains httplib and oauth2client:
```
sudo pip install --upgrade google-api-python-client
```
```
sudo pip install SQLAlchemy
```
```
sudo apache2ctl restart
```
### Create the database
```
python database_setup.py
```
Populate the database:
```
python lotsofcategories.py
```

### Access the website

Use the AWS URL: http://ec2-54-179-143-72.ap-southeast-1.compute.amazonaws.com/ or type in: http://54.179.143.72

### Debugging:
Access the error log with:
```
tail -50 /var/log/apache2/error.logÂ is your friend
```
Always restart apache with `sudo apache2ctl restart` whenever a change is made to the files

## Description

### Python Module

The file database_setup.py contains the database schema. The file lotsofitems.py helps to populate the database with one user and many items.

The file project.py contains the functions used to register, authenticate, connect and disconnect a user. It also contains functions to query the database, and redirect the user to different pages.

The application also contains many templates in the folder templates, a css file and a png image in the static folder.

### Assets
The banner was provided through the following website: theicss.org

### Database 

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

### Login and Authentication
The program uses Google and Facebook login methods. The file clients_secrets.json contains the client ID for the Google login and authentication. The application Id for facebook is mentioned in the file login.html.

This program uses JSON files for authentication for both Google and Facebook (respectively client_secrets.json and fb_client_secrets.json). The two JSON files are not included.


### About the .git folder
Two methods can be used to ensure that the .git folder is not accessible via a browser publicly.

[Amend the Apache config file.](https://stackoverflow.com/questions/6142437/make-git-directory-web-inaccessible)

Or [write a .htaccess file in the .git folder.](https://serverfault.com/questions/128069/how-do-i-prevent-apache-from-serving-the-git-directory/325841)

### Useful commands
https://help.ubuntu.com/community/SSH/OpenSSH/InstallingConfiguringTesting
https://unix.stackexchange.com/questions/127886/how-can-i-restart-the-ssh-daemon-on-ubuntu
https://www.digitalocean.com/community/tutorials/how-to-add-and-delete-users-on-an-ubuntu-14-04-vps
http://blog.udacity.com/2015/03/step-by-step-guide-install-lamp-linux-apache-mysql-python-ubuntu.html
https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-14-04
https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
https://serverfault.com/questions/128069/how-do-i-prevent-apache-from-serving-the-git-directory/325841
https://stackoverflow.com/questions/6142437/make-git-directory-web-inaccessible
https://www.digitalocean.com/community/tutorials/how-to-secure-postgresql-on-an-ubuntu-vps
https://serverfault.com/questions/110154/whats-the-default-superuser-username-password-for-postgres-after-a-new-install
https://www.youtube.com/watch?v=HcwK8IWc-a8
http://docs.sqlalchemy.org/en/latest/core/engines.html
https://discussions.udacity.com/t/markedly-underwhelming-and-potentially-wrong-resource-list-for-p5/8587
https://help.github.com/articles/set-up-git/
https://help.ubuntu.com/community/UFW

**Author**

C. D. wrote the code for the functions in tournament.py.

**License**

The files are private domain works.

