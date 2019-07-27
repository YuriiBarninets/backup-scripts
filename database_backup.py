import paramiko
import json
import os
import utils
from datetime import datetime
from config import serverConfig, localConfig

# setup SSH connection
sshConfig = serverConfig["ssh"]
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(serverConfig["host"], sshConfig["port"],
            sshConfig["username"], sshConfig["password"])
sftp = ssh.open_sftp()

# create MySQL dumps in server backup dir
serverDatabaseBackupDir = serverConfig["database"]["backup_dir"]
try:
    sftp.stat(serverDatabaseBackupDir)
except FileNotFoundError:
    sftp.mkdir(serverDatabaseBackupDir, mode=448)  # 0x700 = 448

mySqlConfig = serverConfig["database"]["mysql"]
for databaseConfig in mySqlConfig:
    createSqlDumpCmd = "mysqldump -q -u {0} -h {1} -p{2} ".format(
        databaseConfig["username"], databaseConfig["host"], databaseConfig["password"])
    createSqlDumpCmd += "{0} | gzip -9 > {1}"

    for dbName in databaseConfig["dbnames"]:
        dumpFileName = "{0}_{1}.sql.gz".format(
            dbName, datetime.now().strftime("%Y_%m_%d"))
        dumpFilePath = os.path.join(serverDatabaseBackupDir, dumpFileName)

        mySqlDumpCommand = createSqlDumpCmd.format(dbName, dumpFilePath)
        stdin, stdout, stderr = ssh.exec_command(mySqlDumpCommand)
        if not stdout.channel.recv_exit_status():
            print("Created SQL dump for {0} DB".format(dbName))
        else:
            print("Can not create SQL dump for {0} DB".format(dbName))

# delete database dumps older than serverDatabaseBackupExpirationDays
databaseDumpsList = sftp.listdir(path=serverDatabaseBackupDir)
serverDatabaseBackupExpirationDays = serverConfig["database"]["backup_expiration_days"]
utils.deleteFilesOlderThanExpirationDays(databaseDumpsList, serverDatabaseBackupDir,
                                         serverDatabaseBackupExpirationDays, sftp)

# copy database dumps from serverDatabaseBackupDir to localDatabaseBackupDir
localDatabaseBackupDir = localConfig["database"]["backup_dir"]
if not os.path.isdir(localDatabaseBackupDir):
    os.mkdir(localDatabaseBackupDir)

for databaseDump in databaseDumpsList:
    pathToRemoteFile = os.path.join(serverDatabaseBackupDir, databaseDump)
    pathToLocalFile = os.path.join(localDatabaseBackupDir, databaseDump)

    if not os.path.isfile(pathToLocalFile):
        sftp.get(pathToRemoteFile, pathToLocalFile)

        # preserve timestamp
        fileAttrs = sftp.stat(pathToRemoteFile)
        os.utime(pathToLocalFile, (fileAttrs.st_atime, fileAttrs.st_mtime))

# delete database dumps older than localDatabaseBackupExpirationDays
utils.deleteFilesOlderThanExpirationDays(
    os.listdir(localDatabaseBackupDir), localDatabaseBackupDir,
    localConfig["database"]["backup_expiration_days"], os)

# close sftp, ssh connection
sftp.close()
ssh.close()
