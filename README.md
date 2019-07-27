# Backup scripts
Simple scripts to backup databases and other data from a server:
* database_backup.py - create MySQL dumps on a server side and copy them to a local backup directory
* data_rsync.py - transfer data from a server to a local machine directory

## Usage

### Configuration file
Each script takes as an input a path to a configuration file, so firstly create a simple configuration file with server, ssh configurations e.g. [*configuration.json*](https://github.com/YuriiBarninets/backup-scripts/blob/c672e38b364aa44bbeae8210a98e252c105cd6d9/configuration.json#L1-L46)

### Usage database_backup.py script
*database_backup.py* script creates MySQL dumps for databases listed in *configuration.json* file and copy them to a local backup dir.

#### Prerequisites for database_backup.py
Python modules: 
 * paramiko
 * argparser

Utilities:
 * mysqldump

#### 1. Add mysql databases in *configuration.json* file
In *configuration.json* file **mysql** key contains an array with users and databases for which we are going to create backups.
For example, **sql_user1** manage **db1, db2** and **sql_user2** manage **db3**, so in order to backup **db1, db2, db3** databases we have to add the following content to **mysql**:
```json
"mysql": [
        {
          "host": "localhost",
          "username": "sql_user1",
          "password": "user1_pwd",
          "dbnames": ["db1", "db2"]
        },
        {
          "host": "localhost",
          "username": "sql_user2",
          "password": "user2_pwd",
          "dbnames": ["db3"]
        }
      ]
```

#### 2. Add server and local backup directories in *configuration.json* file
Server and local backup directories will contain MySQL dump with databases listed in **mysql** array.

For better understanding why we need to specify server and local backup directories please read what do *database_backup.py* script:
1. Create MySQL dump for each database, archive it in sql.gz and copy to *server.database.backup_dir*
2. Delete MySQL dump from *server.database.backup_dir* directory that older than *server.database.backup_expiration_day*
3. Copy MySQL dumps from *server.database.backup_dir* to *local.database.backup_dir* directory
4. Delete MySQL dump from *local.database.backup_dir* directory that older than *local.database.backup_expiration_day* 
```json
{
  "server": {
      "database": {
        "backup_dir": "/home/server_username/sql_dumps/",
        "backup_expiration_days": 5
      }
    },
  "local": {
    "database": {
      "backup_dir": "/home/local_username/sql_dumps/",
      "backup_expiration_days": 15
    }
}
```

#### 3. Run *database_backup.py* script like this:
```
$ python3 database_backup.py --config_path=/path/to/configuration.json
```

### Usage data_rsync.py script
*data_rsync.py* script using rsync utility for transferring data from a server side to a local machine.

#### Prerequisites for data_rsync.py
Python modules: 
 * pexpect
 * argparser

Utilities:
 * rsync

#### 1. Add server and local sync directories in *configuration.json* file
Server directory | Local directory
--- | ---
/home/server_username/dirname1/ | /home/local_username/dirname1/
/home/server_username/dirname2/ | /home/local_username/dirname2/

We must add the following configurations if we want to transfer content from a server directory to a local directory as shown in a table above:

```json
{
  "server": {
      "data": {
        "sync_dirs": [
          "/home/server_username/dirname1/",
          "/home/server_username/dirname2/"
        ]
      }
    },
  "local": {
    "data": {
      "sync_dirs": [
        "/home/local_username/dirname1/",
        "/home/local_username/dirname2/"
      ]
    }
}
```
This configuration will copy all contents from */home/server_username/dirname1/* and */home/server_username/dirname2/* directories on a server side to corresponding directories */home/local_username/dirname1/* and */home/local_username/dirname2/* on a local machine.

#### 2. Run *data_rsync.py* script like this:
```
$ python3 data_rsync.py --config_path=/path/to/configuration.json
```
