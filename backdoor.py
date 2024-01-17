import asyncio
class Backdoor:
    def __init__(self, ip_or_hostname):
        input_pipe = asyncio.Queue()
        
    def remote_code_execution(self) -> bytes:
        pass
    
    async def read(self) -> bytes:
        pass
    async def write(self, data: bytes):
        pass
import socket
class PythonReverseShell(Backdoor):
    def __init__(self, ip_or_hostname):
        super().__init__(ip_or_hostname)
    def run(self):
        pass