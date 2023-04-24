from dal import UserDao
from datetime import datetime
import os
import subprocess
from flask import (
    Flask,
    request,
    render_template,
    render_template_string,
    redirect,
    session,
    url_for,
    send_file,
    jsonify,
    send_file
)
import shutil
import zipfile
from io import BytesIO
import shutil


# logging.basicConfig(filename="log.txt")

app = Flask(__name__)

@app.route('/browser')
def root():
    search_query = request.args.get('search')

    # Get the list of files and folders in the current directory
    file_list = subprocess.check_output('ls', shell=True).decode('utf-8').split('\n')

    # Filter the file list based on the search query
    matching_files = []
    if search_query:
        matching_files = [file for file in file_list if search_query in file]

    return render_template('browser.html', current_working_directory=os.getcwd(), file_list=file_list, matching_files=matching_files, search_query=search_query,os=os)


@app.route('/select')
def select():
    file_path = request.args.get('file')
    os.chdir(os.path.join(os.getcwd(), file_path))
    return redirect("/")


# handle 'cd' command
@app.route('/cd')
def cd():
    # run 'level up' command
    os.chdir(request.args.get('path'))
    
    # redirect to file manager
    return redirect('/')

# view text files
@app.route('/view')
def view():
    # get the file content
    with open(request.args.get('file')) as f:
        return f.read().replace('\n', '<br>')

# run the HTTP server
if __name__ == '__main__':
    app.run(debug=True, threaded=True)