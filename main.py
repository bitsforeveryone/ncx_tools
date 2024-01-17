import argparse
import sqlalchemy as db
import signal
from termcolor import colored
import asyncio
import daemon.pidfile
import daemon
import time
import os


class ReverseShell:
    def __init__(self, remote_host : str, remote_port : int, local_host : str, local_port : int):
        self.remote_host = remote_host
        self.local_host = local_host
        self.remote_port = remote_port
        self.local_port = local_port
        self.last_alive = None
        self.task_queue = asyncio.Queue()

class Victim:
    def __init__(self, ip_or_hostname):
        pass

engine = None
metadata = None
conn = None

def listener():
    while True:
        #sleep for 5 seconds
        time.sleep(5)
        

def signal_handler(sig, frame):
    print('\nControl-C detected, exiting...')
    # Close the database connection
    conn.commit()
    conn.close()
    # Exit the program
    exit(0)
    
def list_victims():
    # Get the victims
    victims_query = db.select(victims)
    # Execute the query
    victims_result = conn.execute(victims_query)
    # Print the results
    print("Victims:")
    print("\tID:\tIP:\t\tComment:\t")
    print("--------------------------------------------------")
    for victim in victims_result:
        #print bullet point
        print(colored("*", 'red'), end='\t')
        print(colored(f"{victim[0]}", 'green'), end='\t')
        print(colored(f"{victim[1]}", 'blue'), end='\t')
        print(colored(f"{victim[2]}", 'yellow'))
    print("--------------------------------------------------")

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
    parser.add_argument('--db', type=str, default='./bermuda_state.db')
    args = parser.parse_args()
    # check if the daemon is running
    if os.path.exists('/tmp/bemuda.pid'):
        print("Daemon already running...connecting")
    else:
        print("Daemon not running, launching...")
        pid = os.fork()
        if pid == 0:
            with daemon.DaemonContext(pidfile=daemon.pidfile.PIDLockFile('/tmp/bemuda.pid')):
                listener()
        
    # Connect to the database
    engine = db.create_engine(f'sqlite:///{args.db}')
    conn = engine.connect()
    metadata = db.MetaData()
    
    victims = db.Table(
        "Victim",
        metadata,
        db.Column("id", db.Integer, primary_key=True),
        db.Column("ip", db.String),
        db.Column("comment", db.String, default="")
    )
    active_backdoors = db.Table(
        "ActiveBackdoor",
        metadata,
        db.Column("id", db.Integer, primary_key=True),
        db.Column("victim_id", db.Integer, db.ForeignKey("Victim.id")),
        db.Column("ip", db.String),
        db.Column("port", db.Integer),
        db.Column("type", db.String),
        db.Column('last_alive', db.DateTime, default=db.func.current_timestamp()),
        db.Column("comment", db.String, default="")
    )
    # Create the tables
    metadata.create_all(engine)
    
    print(f"Connected to database located at {args.db}")
    while True:
        # Get the command
        command = input(">>> ")
        # split the command
        command = command.split()
        if len(command) == 0:
            continue
        elif command[0] == "help":
            print("Available commands: help, exit")
        elif command[0] == "exit":
            break
        elif command[0] == "list" or command[0] == "ls" or command[0] == "show":
            list_victims()
        elif command[0] == "new" or command[0] == "add" or command[0] == "create":
            if len(command) < 2:
                print("Usage: new victim_ip_or_hostname [comment]")
                continue
            # Create the new victim
            comment = ""
            if len(command) > 2:
                comment = " ".join(command[2:])
            conn.execute(victims.insert().values(ip=command[1], comment=comment))
            list_victims()
        elif command[0] == "delete" or command[0] == "del" or command[0] == "rm":
            if len(command) < 2:
                print("Usage: delete victim_id")
                continue
            conn.execute(victims.delete().where(victims.c.id == command[1]))
            list_victims()
        else:
            print(f"Unknown command {command[0]}")
        #commit changes
        conn.commit()
    conn.close()