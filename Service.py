import os

# get the user's home directory
home_dir = os.path.expanduser("~")

# navigate to the home directory
os.chdir(home_dir)

# print the contents of the home directory
for item in os.listdir(home_dir):
    print(item)
