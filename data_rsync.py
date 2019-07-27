import pexpect
from config import serverConfig, localConfig

# -a stands for "archive" and syncs recursively and preserves symbolic links, special and device files,
# modification times, group, owner, and permissions
# -z  Reduce the network transfer by adding compression
# -P combines the flags --progress and --partial. The first of these gives you a progress bar for the transfers
# and the second allows you to resume interrupted transfers
# --delete  delete files from the destination directory if they are removed from the source
rsyncArgs = "-azP --delete"
rsyncCmdPattern = "rsync {0} {1}@{2}:".format(
    rsyncArgs, serverConfig["ssh"]["username"], serverConfig["host"])
rsyncCmdPattern += "{0} {1}"

sourceSyncDirs = serverConfig["data"]["sync_dirs"]
destSyncDirs = localConfig["data"]["sync_dirs"]

# execute rsync command for each pair of sourceSyncDir -> destSyncDir
for sourceSyncDir, destSyncDir in zip(sourceSyncDirs, destSyncDirs):
    rsyncCmd = rsyncCmdPattern.format(sourceSyncDirs, destSyncDirs)
    pexpect.run(rsyncCmd, events={
                '(?i)password': serverConfig["ssh"]["password"] + "\r"})
