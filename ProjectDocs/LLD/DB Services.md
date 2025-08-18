**What will it do?**

Container to host Database services
Database: Couch DB and Pouch DB

**Documents:**
1. UserDetails: Contains details about user such as user id, it's salt etc.

| key                     | Comment                                                                                                                   | Encrypted |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------- | --------- |
| _id                     | To hold userid                                                                                                            | no        |
| salt                    | Unique salt for this user                                                                                                 | no        |
| en_master_kek           | Encrypted master kek                                                                                                      | no        |
| iv                      | Initialization Vector                                                                                                     | no        |
| en_validation_string    | Encrypted validation string                                                                                               | no        |
| passphrase_expiry_ttl   | Passphrase will expire after user configured TTL. <br>Format {'ttl': '10', 'unit': 'day' }<br>Possible unit: min, hr, day | no        |
| source_dir_to_watch     | Source folder or directory to watch for file insertion or modification                                                    | no        |
| target_dir_to_dump      | Directory where files fetched from peers will be dumped. Prefix of this path should not match with 'source_dir_to_watch'  | no        |
| peer_dir_for_storage    | Directory where peer's data will land for storage                                                                         | no        |
| delete_file_from_source | Flag to identify if a file should be deleted as soon as it gets uploaded to makedrive                                     | no        |


2. FilesMetaData: Contains meta data related to files


| key           | Comment                                                                                                                               | Encrypted by master_kek |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| _id           | File id. Generate new id for every change. Use '_id = str(uuid.uuid4())'                                                              | no                      |
| file_entry_ts | Timestamp when entry in made in this table                                                                                            | yes                     |
| file_location | Location of file where it got picked up from. Path should be relative to 'source_dir_to_watch'.                                       | yes                     |
| file_name     | name of the file                                                                                                                      | yes                     |
| file_iv       | File's IV                                                                                                                             | yes                     |
| en_file_dek   | Encrypted file dek                                                                                                                    | no                      |
| delete        | Captures if file is marked for deletion from makedrive i.e. file gets deleted from all peers. Deletion process will run in background | no                      |

3. Peers: Contains meta data related to all peers

| key                 | comment                                |
| ------------------- | -------------------------------------- |
| _id                 | Peer id                                |
| name                | peer name                              |
| host                | peer's public IP                       |
| port                | peer's port to reach out for makedrive |
| path_to_dump_chunks |                                        |





Functionalities:
	1. User creation: user creation with passphrase stored in memory for pre-configured amount of time as maintained in 'passphrase_expiry_ttl'
	2. User validation: Just validation of user by checking user entered passphrase
	3. 

Host Tables
1. User id


