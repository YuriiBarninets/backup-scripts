import paramiko
import sys
from config import serverConfig

# setup SSH connection
sshConfig = serverConfig["ssh"]
sshClient = paramiko.SSHClient()
sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    sshClient.connect(serverConfig["host"], sshConfig["port"],
                      sshConfig["username"], sshConfig["password"])
except:
    print("Can not setup SSH connection for user {0}".format(
        sshConfig["username"]))
    sys.exit()
