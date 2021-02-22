import paramiko
from paramiko import SSHClient
import time
import socket
import sys



class SSHUtilities():


    def __init__(self, serverIP, serverSshUsername, serverSshPassword):
        self.server = serverIP
        self.user_name = serverSshUsername
        self.password = serverSshPassword
        self.timeout = 600
        self.output = {}
        self.ssh_client, self.shell = None, None


    def connect_ssh(self):
        try:
            self.output.clear()
            ssh_client = SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=self.server, username=self.user_name, password=self.password, timeout=300)
            shell = ssh_client.invoke_shell()
            shell.settimeout(self.timeout)
            self.shell = shell
            self.ssh_client = ssh_client
            self.execute_cmd("\n")
        except paramiko.ssh_exception.ChannelException as e:
            raise Exception("Failed to open connection", e)
        except paramiko.ssh_exception.AuthenticationException as e:
            raise Exception("verify Entered user name and password", e)
        except paramiko.ssh_exception.SSHException as e:
            raise Exception("Failed to SSH to host ", e)

    def execute_cmd(self, cmd, prompt="~]# ", cmd_timeout=600):
        channel = self.shell
        if cmd_timeout != 600:
            channel.settimeout(cmd_timeout)
        output = str()
        try:
            channel.send(cmd + "\n")
            while True:
                output += channel.recv(999999).decode()
                time.sleep(2)
                if output.endswith(prompt):
                    break
        except socket.timeout as e:
            raise Exception("Did not get expected prompt in {} sec ".format(self.timeout), e)
        return output

    def disconnect(self):
        session = self.ssh_client
        session.close()

    def execute_cmds(self, cmd_list):
        try:
            self.connect_ssh()
            response = {}
            for cmd in cmd_list:
                output = self.execute_cmd(cmd)
                response[cmd] = output
            self.output = response
        finally:
            print('disconnect')
            self.disconnect()

    def get_output(self):
        print("disconnect")
        return self.output

serverIP = sys.argv[1]
serverSshUsername = sys.argv[2]
serverSshPassword = sys.argv[3]
ssh_obj = SSHUtilities(serverIP, serverSshUsername, serverSshPassword)
cmd_list = ['pwd', 'ip tunnel add tun4 mode ipip remote 10.64.101.159 local '+serverIP+' dev eth0', 'ifconfig tun4 10.21.254.1 netmask 255.255.255.252 pointopoint 10.21.254.2', 'ifconfig tun4 mtu 1500 up', 'sysctl -w net.ipv4.ip_forward=1', 'route add -net 10.10.0.0 netmask 255.255.0.0 gw 10.21.254.2 tun4']
ssh_obj.execute_cmds(cmd_list)
print(ssh_obj.output)
