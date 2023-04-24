import crypt
import spwd
import subprocess
import os
from prettytable import PrettyTable


class UserDao:

    def __init__(self):
        pass

    def user_exists(self, username):
        try:
            # Get the shadow entry for the user
            shadow_entry = spwd.getspnam(username)
            return True
        except KeyError:
            # User does not exist
            return False

    def verify_password(self, user, password):
    # Use sudo to read the shadow file with root privileges
        cmd = ['sudo', '-S', 'cat', '/etc/shadow']
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=password.encode(), check=True)
        except subprocess.CalledProcessError:
            # The password was incorrect or the user doesn't have permission to read the shadow file
            return False

        # Parse the output of the `sudo cat /etc/shadow` command to get the hashed password for the given user
        for line in proc.stdout.decode().split('\n'):
            fields = line.strip().split(':')
            if fields[0] == user:
                hashed_password = fields[1]
                break
        else:
            raise ValueError("User not found in shadow file")

        # Verify the password against the hashed password
        return crypt.crypt(password, hashed_password) == hashed_password
 
        
    def files_count(self, user):
        cmd = f"find /home/{user} -type f -mtime -1 | wc -l"
        # to handle the sudo 
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        output = result.stdout.strip().split('\n')
        if output[-1]:
            file_count = int(output[-1])
        else:
            file_count = 0

        return file_count

    
    
    def count_directories(self, username):
        """
        Returns the number of directories for the given user.
        """
        user_dir = os.path.join('/home', username)
        if not os.path.isdir(user_dir):
            return 0
        return sum([1 for f in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, f))])



    def get_user_space(self, username):
        user_dir = f'/home/{username}'
        result = subprocess.run(['du', '-sh', user_dir], stdout=subprocess.PIPE)
        space_used = result.stdout.decode('utf-8').split('\t')[0]
        space_used_num = space_used[:-1]  # remove the last character (unit)
        return space_used_num


  

if __name__ == '__main__':
    # Prompt the user for their username and password
    user = input('Enter your username: ')
    password = input('Enter your password: ')

    # Create a UserDao object and use it to verify the password and count the files
    user_dao = UserDao()
    if user_dao.verify_password(user, password):
        print('Password verified')
        file_count = user_dao.files_count(user)
        dirs_count = user_dao.count_directories(user)
        space_used = user_dao.get_user_space(user)
        
        print(f"Number of files: {file_count}")
        print(f"Number of direcs: {dirs_count }")
        print(f"Space used:{space_used}")
        
    else:
        print('Authentification Failure')
        
