import os, time
from flask import Flask, render_template, redirect, json, request
from flask import send_from_directory, session
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash, secure_filename

DEFAULT_UPLOADS_FOLDER = "uploads/"
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'gif'])
PHOTOS_PER_PAGE = 10

app = Flask(__name__)
app.secret_key = 'something-absolutely-kept-19532352-secret' # a secret app key.
app.config['UPLOAD_FOLDER'] = DEFAULT_UPLOADS_FOLDER

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Oracle MySQL DATABASE CONFIGURATION & CONNECTION
# To configure for your database, please set the following
# configuration parameters according to your own settings.
# -------------------
#   Config Param's:
# -------------------
# @my_mysql_db_user    : --your mysql username-- 
# @my_mysql_db_password: --your mysql password--
# @my_mysql_db_host    : --your host-- (if localhost, no need to change)
# @my_mysql_db_name    : --imgcollection-- (don't change!)

mysql = MySQL()
my_mysql_db_user = 'root'
my_mysql_db_password = 'password'
my_mysql_db_host = 'localhost'

# MySQL configurations for the web app
app.config['MYSQL_DATABASE_USER'] = my_mysql_db_user
app.config['MYSQL_DATABASE_PASSWORD'] = my_mysql_db_password
app.config['MYSQL_DATABASE_DB'] = 'imgcollection'
app.config['MYSQL_DATABASE_HOST'] = my_mysql_db_host
mysql.init_app(app)

# MySQL connection handlers
conn = mysql.connect()
cursor = conn.cursor()
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


##! FUNCTION allowed_file
# @brief: Checks whether filename has an allowed extension format.
#
# @param filename: Full name of the file as a String.
# @retval: True  -- if filename is allowed
#          False -- otherwise
#
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


##! THE MAIN PAGE - INDEX.HTML
@app.route('/')
def main():
    if session.get('user'): # if a user has signed in
        user_link_string = "Sign Out (" + str(session['user']) + ")"
        user_href = 'logout'
        return render_template('index.html',
                               user_href = user_href,
                               user_link_string = user_link_string)
    else:
        user_link_string = "Sign In/Sign Up"
        user_href = 'display-signin-or-signup'
        return render_template('index.html',
                               user_href = user_href,
                               user_link_string = user_link_string)


##! PHOTO DISPLAY ROUTINE FOR THE MAIN PAGE
@app.route('/display-photos-main', methods=['POST'])
def display_photos_main():
    _limit = str(PHOTOS_PER_PAGE)
    _offset = request.form['offset']
    
    # Select last 10 photos from the database, given offset
    cursor.execute("SELECT * FROM photo ORDER BY timestamp DESC LIMIT " + _offset + "," + _limit)
    photos = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM photo") # get no of photos in the database
    total_photo_count = cursor.fetchall()[0][0]
    photos_all = []
    for photo in photos:
        # Prepare info for last 10 photos retrieved from the database
        photo_info = {'name': photo[1],
                      'caption': photo[2],
                      'owner': photo[3],
                      'timestamp': photo[4]}
        photos_all.append(photo_info)   
    photos_all.append({'total': total_photo_count}) # also add total no of photos
    return json.dumps(photos_all) # Send photo info to JSON for photo display


##! USER PROFILE PAGE - PROFILE.HTML
@app.route('/profile')
def display_profile():
    if session.get('user'): # if a user has signed in
        user_link_string = "Sign Out (" + str(session['user']) + ")"
        return render_template('profile.html',
                               user_link_string = user_link_string)
    else:
        return render_template('error.html', 
                                   error = 'Please sign in first.')


##! PHOTO DISPLAY ROUTINE FOR THE USER PROFILE PAGE
@app.route('/display-photos-profile')
def display_photos_profile():
    username = str(session['user'])
    # Retrieve user's all photos from the database
    cursor.execute("""SELECT * FROM PHOTO WHERE OWNER=%s""", (username,))
    photos = cursor.fetchall()
    photos_all = []
    for photo in photos:
        photo_info = {'photoid': photo[0],
                      'name': photo[1],
                      'caption': photo[2],
                      'owner': photo[3],
                      'timestamp': photo[4]}
        photos_all.append(photo_info)      
    return json.dumps(photos_all) # Send photo info to JSON for photo display


# DISPLAY PHOTO UPLOAD PAGE - UPLOAD.HTML
@app.route('/upload')
def show_upload_photo():
    return render_template('upload.html')


# PHOTO UPLOADER ROUTINE: GET THE UPLOADED PHOTO, SAVE TO THE DATABASE
@app.route('/upload-photo', methods=['GET', 'POST'])
def upload_photo():
    if request.method == 'POST':
        # Check whether the photo is uploaded from the webpage
        if 'photo' not in request.files:
            return render_template('error.html', 
                                   error = 'No file part, upload unsuccessful.')
        
        photo = request.files['photo']
        
        # Check whether filename is empty
        if photo.filename == '':
            return render_template('error.html', 
                                   error = 'No file selected, upload unsuccessful.')
        
        # Check whether we now have the photo, and the filename is allowed
        if photo and allowed_file(photo.filename):
            timestamp = int(time.time() * 1000) # give a timestamp to photo
            
            # Determine photo owner
            if session.get('user'):
                photo_owner = str(session['user'])
            else:
                photo_owner = 'anonymous'
            
            # Check whether filename is secure, and also manipulate the
            # filename so that it is standard all across the photos
            photoid = secure_filename(photo.filename)
            photoid = 'imgcollection-' + photo_owner
            photoid += '-' + str(timestamp) + '.'
            photoid += photo.filename.rsplit('.',1)[1].lower()
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photoid))
            
            photo_caption = request.form['img_caption'] # get the caption from HTML form
            if len(photo_caption) > 1024:
                photo_caption = photo_caption[:1024]
            # Save the photo with its name, caption, owner, and timestamp
            # to the database, by calling a stored procedure within the database
            cursor.callproc('sp_uploadPhoto',
                            (photoid, photo_caption, photo_owner, timestamp))
            conn.commit()
            
            return redirect('/') # return to main page
            
        else:
            return render_template('error.html', 
                                   error = 'File extension is not allowed.')


# DISPLAY ROUTINE FOR EACH UPLOADED IMAGE
@app.route('/uploads/<filename>')
def uploaded_photo(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# DISPLAY SIGN-IN & SIGN-UP PAGE
@app.route('/display-signin-or-signup')
def displaySignInOrSignUp():
    return render_template('signin-signup.html')


# USER SIGN-UP ROUTINE: REGISTER A NEW USER, SAVE TO THE DATABASE
@app.route('/sign-up', methods=['POST'])
def signUp():
    # Get username and password from HTML form
    _name = request.form['inputNewUsername']
    _password = request.form['inputPassword']
    
    # Default username is 'anonymous', so it cannot be taken, check for this
    if _name == 'anonymous':
        sign_up_msg = 'This username cannot be taken! Try another one.'
        return render_template('signin-signup.html',
                        sign_up_msg = sign_up_msg)
    
    # Lenght of the username cannot exceed 64 chars due to database configuration
    if len(_name) > 64:
        sign_up_msg = 'Username too long! Try a shorter one.'
        return render_template('signin-signup.html',
                        sign_up_msg = sign_up_msg)
    
    # Check for username requirements:
    for c in _name:
        if not c.isalnum() and not c==' ' and not c=='_':
            sign_up_msg = 'Username does not match the requirements! Try another one.'
            return render_template('signin-signup.html',
                        sign_up_msg = sign_up_msg)
        
    # Check for password requirements:
    if not ((any(x.isupper() for x in _password) and any(x.islower() for x in _password) 
    and any(x.isdigit() for x in _password) and len(_password) >= 8)):
        sign_up_msg = 'Your password does not match the requirements! Try setting another one.'
        return render_template('signin-signup.html',
                        sign_up_msg = sign_up_msg)
    
    # Save the user to the database
    _hashed_password = generate_password_hash(_password)
    cursor.callproc('sp_createUser', (_name,_hashed_password))
    data = cursor.fetchall()
    if len(data) is 0: # user creation is successful
        conn.commit()
        sign_up_msg  = 'Welcome to ImgCollection, dear ' + str(_name)
        sign_up_msg += "! \nPlease sign in below to continue."
        return render_template('signin-signup.html',
                        sign_up_msg = sign_up_msg)
    else:
        sign_up_msg = 'User cannot be created! \n' + str(data[0])
        return render_template('signin-signup.html',
                        sign_up_msg = sign_up_msg)
    

# USER SIGN-IN: VALIDATE AND SIGN-IN THE USER
@app.route('/validate-login', methods=['POST'])
def validateLogin():
    try:
        # Get the username and password from HTML form
        _username = request.form['inputUsername']
        _password = request.form['inputPassword']
        
        # Check whether the username exists in the database
        conn = mysql.connect()
        cursor = conn.cursor()
        _username = ''.join(e for e in _username if e.isalnum() or e == '_' or e == ' ')
        cursor.execute("""SELECT * FROM user WHERE username=%s""", (_username,))
        data = cursor.fetchall()
        
        if len(data) > 0: # username exists, check whether password is correct
            if check_password_hash(str(data[0][2]),_password):
                session['user'] = data[0][1] # start user session with username
                return redirect('/profile')
            else: #wrong password
                return render_template('error.html', 
                                       error = 'Wrong username/password.')
        else:
            return render_template('error.html', 
                                   error = 'Wrong username/password.')
    
    except Exception as e:
        return render_template('error.html', 
                               error = str(e))


# USER LOG-OUT: SIGN-OUT THE USER 
@app.route('/logout')
def logout():
    session.pop('user', None) # finish the user session
    return redirect('/')


# ROUTINE FOR GETTING PHOTO CAPTION, GIVEN PHOTO ID
@app.route('/get-photo-by-id', methods=['POST'])
def get_photo_by_id():
    try:
        if session.get('user'): # if a user has signed in before
            # Get photoid from HTML form
            _id = request.form['photoid']
            try: #check it is a valid ID
                int_id = int(_id)
            except ValueError:
                return redirect('/profile')
            
            # Retrieve the photo's data from the database
            cursor.execute("""SELECT * FROM photo WHERE photoid=%s""", (_id,))
            photo_data = cursor.fetchall()
            
            photo = []
            photo.append({'photoid':photo_data[0][0], 'caption':photo_data[0][2]})
            return json.dumps(photo) # send photo's id and caption to the JSON
            
        else:
            return render_template('error.html', error = 'Unauthorized Access')
        
    except Exception as e:
        return render_template('error.html', error = str(e))


# ROUTINE FOR UPDATING PHOTO CAPTION, GIVEN PHOTO ID
@app.route('/update-photo-caption', methods=['POST'])
def update_photo_caption():
    try:
        if session.get('user'): # if a user has signed in before
            # Get the modified caption and the photoid from HTML form      
            _caption = request.form['caption']
            _id = request.form['id']
            try: #check it is a valid ID
                int_id = int(_id)
            except ValueError:
                return redirect('/profile')
            
            # Update the photo information in the database
            cursor.execute("""UPDATE photo SET caption=%s WHERE photoid=%s""", (_caption,_id))
            
            if len(cursor.fetchall()) is 0: # no error returned from the database
                conn.commit()
                return json.dumps({'status':'OK'})
            else:
                return json.dumps({'status':'An error occured while updating photo info.'})
    except Exception as e:
        return json.dumps({'status':str(e)})


# ROUTINE FOR DELETING PHOTO, GIVEN PHOTO ID
@app.route('/delete-photo',methods=['POST'])
def delete_photo():
    try:
        if session.get('user'): # if a user has signed in before
            # Get the photoid from HTML form for the photo to be deleted
            _id = request.form['photoid']
            try: #check it is a valid ID
                int_id = int(_id)
            except ValueError:
                return redirect('/profile')
            
            # Delete the photo from the database
            cursor.execute("""DELETE FROM photo WHERE photoid=%s""", (_id,))
 
            if len(cursor.fetchall()) is 0: # no error returned from the database
                conn.commit()
                return json.dumps({'status':'OK'})
            else:
                return json.dumps({'status':'An error occured while deleting.'})
        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return json.dumps({'status':str(e)})


# ENSURE THE WEB APP RUNS WHEN "MAIN" IS CALLED
if __name__ == "__main__":
    app.run()
