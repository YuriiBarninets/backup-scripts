# Backup scripts
Simple scripts to backup databases and other data from a server.

## Usage

### Configuration file
Each script takes as an input a path to a configuration file, so firstly create a simple configuration file e.g. *configuration.json*:
```json
{
  "server": {
    "host": "192.168.1.1",
    "ssh": {
      "username": "admin",
      "password": "ssh_pwd",
      "port": 22
    },
    "database": {
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
      ],
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
}
```

### Usage database_backup.py script
*database_backup.py* script creates MySQL dumps for databases listed in *configuration.json* file and copy them to a local backup dir.

#### 1. Add databases in *configuration.json* file
In *configuration.json* file **mysql** key contains an array with users and databases for which we are going to create backups.
E.g. **sql_user1** manage **db1, db2** and **sql_user2** manage **db3**, so in order to backup **db1, db2, db3** databases we have to add the following to **mysql**:
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

#### 2. Add server, local backup directories and expiration days in *configuration.json* file
Server and local backup directories will contain MySQL dump with databases listed in **mysql** array.

For better understanding why we need to specify server and local backup directories please read what do *database_backup.py* script:
1. Create MySQL dumps for each database, archive it in sql.gz and copy to *server.database.backup_dir*
2. Delete MySQL dumps from *server.database.backup_dir* directory that older than *server.database.backup_expiration_day*
3. Copy MySQL dumps from *server.database.backup_dir* to *local.database.backup_dir* directory
4. Delete MySQL dumps from *local.database.backup_dir* directory that older than *local.database.backup_expiration_day* 
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
