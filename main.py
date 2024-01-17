import argparse
import sqlite3
import signal
from termcolor import colored
import asyncio

class Backdoor:
    async def __init__(self, remote_host : str, remote_port : int, controller_host : str, controller_port : int) -> ():
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.controller_host = controller_host
        self.controller_port = controller_port
        self.last_seen = None
    async def listener(self) -> ():
        pass
    async def build(self) -> bytes:
        pass
    

conn = None
c = None

def signal_handler(sig, frame):
    print('\nControl-C detected, exiting...')
    # Close the database connection
    conn.close()
    # Exit the program
    exit(0)
    
if __name__ == '__main__':
    #register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    # Print the banner
    colors = ['yellow', 'white', 'grey','black']
    banner = """
    __________                               .___       
\______   \ ___________  _____  __ __  __| _/____   
 |    |  _// __ \_  __ \/     \|  |  \/ __ |\__  \  
 |    |   \  ___/|  | \/  Y Y  \  |  / /_/ | / __ \_
 |______  /\___  >__|  |__|_|  /____/\____ |(____  /
        \/     \/            \/           \/     \/ 
======================================================
Go C3T, Beat Airforce
    """
    for index, c in enumerate(banner):
        print(colored(c, colors[index % len(colors)]), end='')
        
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, default='./bemuda_state.db')
    args = parser.parse_args()
    # Connect to the database
    conn = sqlite3.connect(args.db)
    c = conn.cursor()
    print(f"Connected to database located at {args.db}")
    while True:
        # Get the command
        command = input(">>> ")
        if command == 'exit':
            break
        elif command == 'help':
            print("""
            Commands:
            help - Show this help message
            exit - Exit the program
            """)
        elif command == "":
            continue