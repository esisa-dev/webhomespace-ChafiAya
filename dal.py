import crypt
import spwd
import crypt
import spwd


class UserDao:
    def user_exists(self, username):
        try:
            # Get the shadow entry for the user
            shadow_entry = spwd.getspnam(username)
            return True
        except KeyError:
            # User does not exist
            return False

    def authenticate_user(self, username, password):
        try:
            # Get the shadow entry for the user
            shadow_entry = spwd.getspnam(username)

            # Extract the hashed password and salt from the shadow entry
            hashed_password = shadow_entry.sp_pwd
            salt = shadow_entry.sp_salt

            # Generate the hashed password for the given password and salt
            generated_hash = crypt.crypt(password, "$6$" + salt)

            # Compare the generated hash with the stored hashed password
            if generated_hash == hashed_password:
                return True
            else:
                return False
        except KeyError:
            # User does not exist
            return False


if __name__ == '__main__':
    # Create an instance of UserDao
    user_dao = UserDao()

    # Test user existence
    print(user_dao.user_exists('root'))  # Output: True
    print(user_dao.user_exists('nonexistentuser'))  # Output: False

    # Test user authentication
    print(user_dao.authenticate_user('root', 'password'))  # Output: False
    print(user_dao.authenticate_user('root', 'password123'))  # Output: True
    print(user_dao.authenticate_user(
        'nonexistentuser', 'password'))  # Output: False
