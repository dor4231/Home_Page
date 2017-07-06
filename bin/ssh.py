import paramiko
from scp import SCPClient
import os
from time import sleep


class Appliance(object):
	
	def __init__(self, ipaddr, user_name, passwd):
		self.ipaddr = ipaddr
		self.user_name = user_name
		self.passwd = passwd
		self.ssh_client = paramiko.client.SSHClient()
	
	def appliance_connect(self):
		self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.ssh_client.connect(self.ipaddr,
							   username=self.user_name, 
							   password=self.passwd)
		return self.ssh_client.invoke_shell()
							   
# 		connect(self, hostname, 
# 					  port=22, 
# 					  username=None, 
# 					  password=None, 
# 					  pkey=None, 
# 					  key_filename=None, 
# 					  timeout=None, 
# 					  allow_agent=True, 
# 					  look_for_keys=True, 
# 					  compress=False, 
# 					  sock=None, 
# 					  gss_auth=False, 
# 					  gss_kex=False, 
# 					  gss_deleg_creds=True, 
# 					  gss_host=None, 
# 					  banner_timeout=None)

# 		exec_command(self, # command, 
# 						   bufsize=-1, 
# 						   timeout=None, 
# 						   get_pty=False)



class DUT(Appliance):

	def __init__(self, ipaddr, user_name, passwd, oc):
		super(DUT, self).__init__(ipaddr, user_name, passwd)
		self.oc = oc
			
	def change_to_bash(self):
		shell = self.appliance_connect()
		
		shell.send('clish\n')
		
		shell.send('lock database override\n')
		shell.send('set user admin shell /bin/bash\n')
		shell.send('save config\n')
		
		shell.send('exit\n')
		self.ssh_client.close()
	
	def connectivity_check(self, file_name):
		shell = self.appliance_connect()
		
		
		
		self.ssh_client.close()
		
	
	def send_file(self, file_path, target_path="~/"):
		shell = self.appliance_connect()
		sftp = SCPClient(self.ssh_client.get_transport())
		sftp.put(file_path, target_path, recursive=True)
		
		file_name = file_path.split("/")[-1]
		shell.send('chmod 777 ' + file_name + '\n')
		shell.send('dos2unix ' + file_name + '\n')
		
		sftp.close()
		self.ssh_client.close()
		
	def collect_info(self):
		pass
		
	def get_info(self):
		pass
		

class Console(Appliance):

	def console_connect(self, dut_port):
		dor = ""
		shell = self.appliance_connect()
		# while not shell.recv_ready():
		# 	dor = dor + shell.recv(9999)

		shell.send("oc " + dut_port + "\n")
		sleep(5)
		
		# print "dor: " + dor 
		dor = shell.recv(9999)
		
		if "kill" in dor:
			print "Killing connection..."
			shell.send("yes\n")
			sleep(10)
		else:
			sleep(5)

		return shell
				
	
	def first_setup(self, ipaddr, oc):
		"""Sets the management IP Address and change the shell to /bin/bash
		via console connection.
		"""
		pause = 1
		shell = self.console_connect(oc)
		ip = ipaddr.split(".")
		success = False
		timeout = 100
		data = ""

		while not success and timeout >= 0:
			# shell.send('\n')
			if not shell.recv_ready():
				print "%d NOT READY!" % timeout
				timeout -= 1
			else:
				data = shell.recv(9999)

			print data
			if "Login" in data:
				print "LOGIN!"
				shell.send('admin\n')
				sleep(5)
			elif "Password" in data:
				print "PASSWORD!"
				sleep(pause)
				shell.send('admin\n')
				success = True
			else:
				print "Loop: %r" % timeout
				timeout -= 1
		
		print "LOOP ENDED!"
		sleep(pause);
		
		shell.send('set interface Mgmt ipv4-address ' + ipaddr + \
				 'mask-length 24\n')
		sleep(pause)
		static_route =  ip[0] + "." + ip[1] + "." + ip[2] + ".1 on"
		shell.send('set static-route default nexthop gateway address %s' % 
			static_route)
		sleep(pause)
		shell.send("save config\n")
		sleep(pause)
		shell.send('exit\n')
		sleep(pause)
		
		print "Disconnecting..."

		shell.close()

	def first_time_wizard(self, hostname):
		shell = self.appliance_connect()

		shell.send("config_system--config-string ")
		shell.send("\"hostname=%d&" % hostname)
		shell.send("domainname=checkpoint.com&")
		shell.send("timezone='Asia/Jerusalem'&")
		shell.send("ftw_sic_key=aaaa&")
		shell.send("install_security_gw=true&")
		shell.send("gateway_daip=false&")
		shell.send(" install_ppak=true&")
		shell.send("gateway_cluster_member=false&")
		shell.send("proxy='194.29.36.43'&")
		shell.send("primary='194.29.40.221'&")
		shell.send("install_security_managment=false\"")

		shell.close()

		 
		


	def connection_test(self, ipaddr, oc):
		print "Connecting"
		shell = self.console_connect(oc)
		ip = ipaddr.split(".")
		shell.send('\n')
		shell.send('admin\n')
		shell.send('zubur1\n')
		sleep(int(ipaddr))
		shell.send("exit\n")
		print "Channel closed!"
		shell.close()