
# import packages
from flask import Flask
from flask import render_template_string
from flask import redirect
from flask import request
import os
import subprocess
import shutil

# create web app instance
app = Flask(__name__)

@app.route('/')
def root():
    search_query = request.args.get('search')
    # Get the list of files and folders in the current directory
    file_list = subprocess.check_output('ls -l ', shell=True).decode('utf-8').split('\n')

    # Filter the file list based on the search query
    if search_query:
        if os.path.isdir(search_query):
            find_command = f"find {os.path.abspath(search_query)} -type d -not -path '*/\.*' -exec basename {{}} \\;"
        else:
            find_command = f"find {os.path.abspath(os.path.curdir)} -type f -not -path '*/\.*' -iname '*{search_query}*' -exec basename {{}} \\;"
        matching_files = subprocess.check_output(find_command, shell=True).decode('utf-8').split('\n')
        matching_files.remove('')
    else:
        matching_files = []

    return render_template_string('''
                                  
   <html>
    <head>
      <title>File manager</title>    
      <link rel="stylesheet" href="./static/css/main.css">
    </head>
    <body>
      <div align="center">
        <h1>Local file system</h1>
        <p><strong>CWD: </strong>{{ current_working_directory }}</p>
      </div>

      <form action="/" method="get">
        <label for="search">Search:</label>
        <input type="text" id="search" name="search" value="{{ search_query }}">
        <input type="submit" value="Search">
      </form>
     

      
        {% if matching_files %}
        <h2>Matching files and folders:</h2>
          <ul>
          {% for file in matching_files %}
              {% if file.endswith('.txt') or file.endswith('.py') or file.endswith('.json') %}
              <li><strong><a href="/view?file={{current_working_directory + '/' + file}}">{{file}}</a></strong></li>
              {% else %}
              <li><strong><a href="/select?file={{file}}">{{file}}</a></strong></li>
              {% endif %}
          {% endfor %}
          </ul>
              {% endif %}


      <h2>Directory listing:</h2>
      <li><a href="/cd?path=..">..</a></li>
      


<table>
 <thead>
  <tr>
    <th>Dossier</th>
    <th>Date de modification</th>
    <th>Taille</th>
  </tr>
</thead>
<tbody>
{% for item in file_list[1:-1] %}
  <tr>
    <td>
  {% if '.' not in item.split()[-1] %} 
    <a href="/cd?path={{current_working_directory + '/' + item.split()[-1]}}" style="text-decoration: none">{{ item.split()[-1] }}</a>
  {% elif '.txt' in item.split()[-1] or '.py' in item.split()[-1] or '.json' in item.split()[-1] %}
    <a href="/view?file={{current_working_directory + '/' + item.split()[-1]}}" style="text-decoration: none">{{ item.split()[-1] }}</a>
  {% else %}
    {{ item.split()[-1] }}
  {% endif %}
</td>

    <td>{{ item.split()[5:8] | join(' ') }}</td>
    <td>{{ item.split()[4] }}</td>
  
  </tr>
{% endfor %}
</tbody>
</table>




     
      
    </body>
  </html>
  
  
    ''',  current_working_directory=os.getcwd(), file_list=file_list, matching_files=matching_files, search_query=search_query,os=os)


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



@app.route('/select')
def select():
    file_path = request.args.get('file')
    os.chdir(os.path.join(os.getcwd(), file_path))
    return redirect("/")

# run the HTTP server
if __name__ == '__main__':
    app.run(debug=True, threaded=True)
    
    


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    