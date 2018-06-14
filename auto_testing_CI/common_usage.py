import os
import os.path
import paramiko
from scp import SCPClient


class CommonUsage():
	def check_file_exist(self, file):
		if os.path.isfile(file) and os.access(file, os.R_OK):
			print "File exists and is readable"
		else:
			print "Either file is missing or is not readable"
			return 1
	
	def python_scp_get_files(self, remote_host, src, destination):
		ssh = paramiko.SSHClient()
		ssh.load_system_host_keys()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(remote_host)
		# SCPCLient takes a paramiko transport as an argument
		scp = SCPClient(ssh.get_transport())
		scp.get(src, destination)
		scp.close()

