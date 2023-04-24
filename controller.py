from dal import UserDao
from datetime import datetime
import logging
import hashlib
from flask import (
    Flask,
    request,
    render_template,
    redirect,
    session,
    url_for,
    send_file,
    jsonify
)
import shutil
import os 
import subprocess

# logging.basicConfig(filename="log.txt")

app = Flask(__name__)

# Set the secret key for the session
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Create an instance of the UserDao
user_dao = UserDao()



@app.route('/')
def home():
    return redirect(url_for('login'))
   


@app.route('/login', methods=['GET', 'POST'])
def login():

    error = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verify the password
        if user_dao.verify_password(username, password):
            # Store the username in the session
            session['username'] = username

            # Log the login action
            with open('app.log', 'a') as f:
                f.write(f"{datetime.now()} - {username} logged in\n")

            # Return welcome message and redirect to app.html
            return redirect(url_for('file_browser'))
             
            #return render_template('app.html', username=username, message='Welcome to your homespace!')
                     
        else:
            error = 'Invalid username or password'

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    # retrieve the username from the session
    username = session.get('username')
    if username:
        # remove the user's session information
        session.pop('username', None)
        # Log the logout action
        with open('app.log', 'a') as f:
             f.write(f"{datetime.now()} - {username} logged out\n")
    # redirect the user to the login page
    return redirect(url_for('login'))



@app.route('/files')
def files():
    # retrieve the username from the session
    username = session.get('username')
    if username:
        # Call the files_count method of UserDao to get the file count, total size, and
        files_count = user_dao.files_count(username)
        
        return render_template('app.html', file_count=files_count)
    else:
         return jsonify({'error': 'User not authenticated'}), 401


@app.route('/dirs')
def directories():
    # retrieve the username from the session
    username = session.get('username')
    if username:
        # Call the count_directories method of UserDao to get the directories count
        directories_count = user_dao.count_directories(username)
        return render_template('app.html', directories_count=directories_count)
    else:
        return jsonify({'error': 'User not authenticated'}), 401
    

@app.route('/space')
def space():
    # retrieve the username from the session
    username = session.get('username')
    if username:
        # Call the get_user_space method of UserDao to get the space used by the user
        used_space = user_dao.get_user_space(username)
        print(used_space) # print used_space to see its value
        space_used_int = float(used_space.split()[0]) # convert space used string to float
        space_used_str = f"{space_used_int:.1f} GB" # add "GB" to the end of the space used string
        return render_template('app.html', space_used=space_used_str)
    else:
        return jsonify({'error': 'User not authenticated'}), 401
 
 

@app.route('/select')
def select():
    username = session.get('username')
    if username:
        file_path = request.args.get('file')
        full_path = os.path.join(os.getcwd(), file_path)
        if os.path.isdir(full_path):
            os.chdir(full_path)
            files = os.listdir()
            subdirectories = [f for f in files if os.path.isdir(os.path.join(full_path, f))]
            return render_template('app.html', files=files, subdirectories=subdirectories, current_dir=file_path,os=os)
        elif os.path.isfile(full_path):
            if full_path.endswith('.txt') or full_path.endswith('.log') or full_path.endswith('.py') :
                # redirect to the view route to display the file content
                return redirect(url_for('view', file=full_path))
            else:
                return jsonify({'error': 'Invalid file type'})
        else:
            return jsonify({'error': 'Invalid file path'})
    else:
        return jsonify({'error': 'User not authenticated'}), 401


# view text files
@app.route('/view')
def view():
    # get the file content
    with open(request.args.get('file')) as f:
        return f.read().replace('\n', '<br>')
 
# handle 'cd' command
@app.route('/cd')
def cd():
    # run 'level up' command
    os.chdir(request.args.get('path'))
    
    # redirect to file manager
    return redirect('/file_manager')


    
    
def search_recursive(directory, search_query):
    matching_files = []
    if '.' in search_query:
        # search for files by extension
        find_command = f"find {directory} -type f -not -path '*/\.*' -iname '*{search_query}*' -exec basename {{}} \\;"
    else:
        # search for directories by name
        find_command = f"find {directory} -type d -not -path '*/\.*' -iname '*{search_query}*' -exec basename {{}} \\;"
    try:
        output = subprocess.check_output(find_command, shell=True, stderr=subprocess.DEVNULL)
        output = output.decode('utf-8').strip()
        if output:
            matching_files = output.split('\n')
    except subprocess.CalledProcessError:
        pass
    return matching_files


@app.route('/file_browser')
def file_browser():
    # retrieve the username from the session
    username = session.get('username')
    if username:
        # retrieve the 'path' query parameter from the request
        path = os.path.expanduser('~')

        # retrieve the 'search' query parameter from the request
        search_query = request.args.get('search')
        
        # execute the ls command to get the directory listing
        listing = subprocess.check_output(['ls', '-l', path]).decode('utf-8')

        # parse the directory listing into a list of tuples
        files = []
        matching_files = []
        if search_query:
            matching_files = search_recursive(path, search_query)
        else:
            for line in listing.split('\n')[1:]:
                if line:
                    parts = line.split()
                    file_path = os.path.join(path, parts[-1])
                    size = int(parts[4])
                    last_modified = datetime.strptime(' '.join(parts[5:8])+f" {datetime.today().year}", '%b %d %H:%M %Y')

                    file_type = 'File'
                    if parts[0][0] == 'd':
                        file_type = 'Directory'

                    files.append((file_path, last_modified, size, file_type))

        # pass the 'os' module to the template
        return render_template('app.html', files=files, matching_files=matching_files, path=path, os=os, username=username, search_query=search_query)
    else:
        return redirect(url_for('login'))

    
if __name__ == '__main__':
    app.run(debug=True)

