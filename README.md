# imgcollection
A simple web-app for photo upload &amp; display, powered by Flask.

# Introduction

ImgCollection is a simple web application where users can upload images, add captions to their images, and sign up for accounts to edit the captions of their images, or delete them. The main page displays all the photos uploaded by every user, 10 photos per page. Users can navigate through all the photos by using the navigation bar at the bottom of the main page, which consists of page numbers. Each 10 photo (per page) can be seen by scrolling down, with their captions preceding, and the user who uploaded the photo following. The upload page allows anyone (even without signing in) to upload photos (only .jpg, .jpeg, .png, and .gif extensions are allowed). The photos uploaded by the default account (named as anonymous) are displayed as "Uploaded by anonymous". The sign-in & sign-up page allows users to create accounts, and sign into their accounts. The profile page shows all the images uploaded by the particular user, and allows them to edit the captions of their photos (by clicking the pencil mark), or to delete them (by clicking the trash can mark).

# Setup

To setup the web application, first ensure that you have Python 3.5+ and MySQL installed on your system. Also you will need to install Flask and Flask-Mysql packages from pip, by issuing the following two commands:

	pip install flask
	pip install flask-mysql
  
Then, you will need to setup a MySQL database for the application. First, run MySQL from your command prompt (or terminal) with your MySQL username (e.g., root) and password, like the following:

	> mysql --user=root --password=password
  
Then, in mysql command line, create a database called 'imgcollection', with the following command:

	mysql > CREATE DATABASE imgcollection;
  
After creating the database, create two tables named as 'user' and 'photo', by running the db_createTable.sql script as the following:

	mysql > imgcollection < %ABSOLUTE_PATH_TO_WEB_APP_FOLDER%\db_createTable.sql
    
Finally, you need to save 2 stored procedures into the database. To do this, you can run the scripts sp_createUser.sql and sp_uploadPhoto.sql, as similar to above:

	mysql > imgcollection < %ABSOLUTE_PATH_TO_WEB_APP_FOLDER%\sp_createUser.sql
	mysql > imgcollection < %ABSOLUTE_PATH_TO_WEB_APP_FOLDER%\sp_uploadPhoto.sql

Now, the database setup is complete. Now, open 'app.py' with a Python editor. In the source code, you will see a section of comments separated by "# %%%%%%%", explaining Oracle MySQL Database Configuration & Connection. You will see configuration parameters. In the code just below the comments, change the @param my_mysql_db_user to your MySQL user, @param my_mysql_db_password to your MySQL password, and @param my_mysql_db_host to your MySQL host. You will see the following default values, but you need to change them:

	my_mysql_db_user = 'root'
	my_mysql_db_password = 'password'
	my_mysql_db_host = 'localhost'
  
Don't forget to change values above to your own MySQL settings. Now, you can start the web application, by running the following command from your command prompt (or terminal):

	python app.py

Now, open a browser, and navigate to http://localhost:5000, i.e., http://127.0.0.1:5000 (if you use the localhost).
