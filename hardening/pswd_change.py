# Create a script that takes a text file containing a list of 
# user names and changes the password for each user. It then must
# output the username and new password to a text file.

import os
import sys


if __name__ == "__main__":
    # Check if the user has entered the correct number of arguments
    if len(sys.argv) != 2:
        print("Usage: python change_passwords.py <filename>")
        sys.exit(1)

    # Check if the file exists
    if not os.path.exists(sys.argv[1]):
        print("Error: File '{}' not found".format(sys.argv[1]))
        sys.exit(2)

    # check if program is being run as root
    if os.geteuid() != 0:
        print("Error: Run as root")
        sys.exit(3)

    usr = open(sys.argv[1], 'r')
    usrs = usr.readlines()

    new_password = input("Enter new password: ")
    second_password = input("Enter new password again: ")
    if new_password != second_password:
        print("Passwords do not match")
        sys.exit(1)
    for i in range(len(usrs)):
        if input(f"Would you like to change {usrs[i].strip()}'s password? (y/n)\n") == 'y':
            os.system("yes {} | sudo passwd {}".format(
                new_password,
                usrs[i].strip()
                )
            )
        else:
            print(f"{usrs[i]}'s password not changed")

    usr.close()
