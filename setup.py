from termcolor import colored
import redis
import docker 
if __name__ == "__main__":
    #check if the .env file exists, if
    #select whether the user is hosting the server or connecting to it
    choice = ""
    while True:
        choice = input("Are you hosting the server? (y/n): ")
        if choice == "y" or choice == "n":
            break
        else:
            print("Please enter a valid choice")
    i