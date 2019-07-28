import os
import utils
from datetime import datetime
from config import serverConfig, localConfig
from ssh_client import sshClient

sftpSession = sshClient.open_sftp()

# create MySQL dumps in server backup dir
serverDatabaseBackupDir = serverConfig["database"]["backup_dir"]
try:
    sftpSession.stat(serverDatabaseBackupDir)
except FileNotFoundError:
    sftpSession.mkdir(serverDatabaseBackupDir, mode=448)  # 0x700 = 448

print("Creating MySQL dumps into server {0} directory ... ".format(
    serverDatabaseBackupDir))
mySqlConfig = serverConfig["database"]["mysql"]
for databaseConfig in mySqlConfig:
    createSqlDumpCmd = "mysqldump -q -u {0} -h {1} -p{2} ".format(
        databaseConfig["username"], databaseConfig["host"], databaseConfig["password"])
    createSqlDumpCmd += "{0} | gzip -9 > {1}"

    for dbName in databaseConfig["dbnames"]:
        dumpFileName = "{0}_{1}.sql.gz".format(
            dbName, datetime.now().strftime("%Y_%m_%d"))
        dumpFilePath = os.path.join(serverDatabaseBackupDir, dumpFileName)

        mySqlDumpCmd = createSqlDumpCmd.format(dbName, dumpFilePath)
        stdin, stdout, stderr = sshClient.exec_command(mySqlDumpCmd)
        if not stdout.channel.recv_exit_status():
            print("Created SQL dump for {0} DB".format(dbName))
        else:
            print("Can not create SQL dump for {0} DB".format(dbName))

# delete database dumps older than serverDatabaseBackupExpirationDays
databaseDumpsList = sftpSession.listdir(path=serverDatabaseBackupDir)
serverDatabaseBackupExpirationDays = serverConfig["database"]["backup_expiration_days"]
print("Delete database dumps from {0} older than {1}".format(
    serverDatabaseBackupDir, serverDatabaseBackupExpirationDays))
utils.deleteFilesOlderThanExpirationDays(databaseDumpsList, serverDatabaseBackupDir,
                                         serverDatabaseBackupExpirationDays, sftpSession)

# copy database dumps from serverDatabaseBackupDir to localDatabaseBackupDir
localDatabaseBackupDir = localConfig["database"]["backup_dir"]
if not os.path.isdir(localDatabaseBackupDir):
    os.mkdir(localDatabaseBackupDir)

print("Copy MySQL dumps from server {0} to local {1} directory".format(
      serverDatabaseBackupDir, localDatabaseBackupDir))
for databaseDump in databaseDumpsList:
    pathToRemoteFile = os.path.join(serverDatabaseBackupDir, databaseDump)
    pathToLocalFile = os.path.join(localDatabaseBackupDir, databaseDump)

    if not os.path.isfile(pathToLocalFile):
        sftpSession.get(pathToRemoteFile, pathToLocalFile)

        # preserve timestamp
        fileAttrs = sftpSession.stat(pathToRemoteFile)
        os.utime(pathToLocalFile, (fileAttrs.st_atime, fileAttrs.st_mtime))

# delete database dumps older than localDatabaseBackupExpirationDays
print("Delete database dumps from {0} older than {1}".format(
    localDatabaseBackupDir, serverDatabaseBackupExpirationDays))
utils.deleteFilesOlderThanExpirationDays(
    os.listdir(localDatabaseBackupDir), localDatabaseBackupDir,
    localConfig["database"]["backup_expiration_days"], os)

# close sftp, ssh connection
sftpSession.close()
sshClient.close()
