import paramiko
import time
import os

class SSHCanary:
	def __init__(self, config_file):
		self.config_file = config_file
		self.ip_addresses = set()
		self.ssh_clients = {}
		self.last_login_info = {}
		self.last_modified = None
		self.private_key = None
		self.username = "ubuntu"  # Default username, can be changed in the config file

	def read_config(self):
		if not os.path.exists(self.config_file):
			print(f"Config file {self.config_file} not found.")
			return False

		modified = os.path.getmtime(self.config_file)
		if self.last_modified == modified:
			return False  # No change in the file

		self.last_modified = modified
		with open(self.config_file, 'r') as file:
			lines = file.readlines()
			self.private_key = paramiko.RSAKey.from_private_key_file(lines[0].strip())
			self.username = lines[1].strip()
			self.ip_addresses = set(line.strip() for line in lines[2:])
		return True

	def connect_to_machines(self):
		for ip in self.ip_addresses:
			if ip not in self.ssh_clients:
				try:
					client = paramiko.SSHClient()
					client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
					client.connect(ip, username=self.username, pkey=self.private_key)
					self.ssh_clients[ip] = client
					print(f"Connected to {ip}")
				except Exception as e:
					print(f"Failed to connect to {ip}: {e}")

	def check_new_logins(self):
		command = 'last -n 1'
		for ip, client in self.ssh_clients.items():
			try:
				stdin, stdout, stderr = client.exec_command(command)
				login_info = stdout.read().decode('utf-8').strip()
				if ip not in self.last_login_info or self.last_login_info[ip] != login_info:
					self.last_login_info[ip] = login_info
					print(f"New login on {ip}: {login_info}")
			except Exception as e:
				print(f"Error checking logins on {ip}: {e}")
				self.ssh_clients.pop(ip, None)

	def run(self):
		while True:
			if self.read_config():
				self.connect_to_machines()
			self.check_new_logins()
			time.sleep(10)  # Check every 10 seconds

if __name__ == '__main__':
	canary = SSHCanary('config.txt')
	canary.run()
