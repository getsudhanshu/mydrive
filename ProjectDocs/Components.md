
1. SQL Lite as file based database
2. Nginx as reverse proxy and flask as wsgi
3. SSH for file transfer
4. docker / kubernetes for container management
5. Encryption/Decryption Techniques

**Terminology:** 

1. Peer Network: Machines or nodes participating in p2p file storage service
2. Peer: individual Machine which is part of Peer Network
3. File: Atomic unit of meaningful data uploaded by a user. 
	1. Chunk: A file can be broken down into multiple chunks. Each peer will receive some chunks. but not all chunks to form a file 
	2. segment: Each chunk can be broken down into multiple segments to enable error check during multi part upload. This will be used to resend only corrupt segment(if there will be any) 
4. Source Peer: Peer who wants to send file chunks to other peer for storage
5. Target Peer: Peer who will be storing the sent file chunk

**HLSD**

High Level Design can be found here: [[HLSD]]


**Services** 

Following services will be developed as part of this project:
1) File sender 
2) File receiver,
3) DB service, and
4) Nginx hosting
5) Couch db hosting
6) Pouch db hosting

Details:
1. File Sender : Can perform following 2 actions: 
	a) Sends file to a peer using gRPC call
	b) Can also send a file from local drive as requested by ‘File receiver’ service

2. File receiver: Can perform following 2 actions: 
	a) Accept and saves file sent by ‘File sender’ service into it’s local drive,
	b) Send request to another peer’s ‘File Sender’ service to send her a file

3. DB Service: Interacts with Pouch DB as local document database. Also used for user management such as user creation and passphrase rotation

4. Nginx hosting: Peers will be talking with each other for sending and receiving files using ‘File sender’ and ‘file receiver’ services. Nginx hosting container will host nginx which will take care of TLS termination and routing grpc call to either ‘file receiver’ or ‘file sender’ services. Nginx will also route request coming from peer’s ‘pouch db hosting’ to sync with ‘couch db hosting’

5. Couch db hosting: Not all peers will have couch db hosting container. Only few peers will have this service out of multiple peers. This ‘couch db hosting’ will act as backup for all peer’s ‘pouch db hosting’. This service will store documents on local peer disk and should be able to fetch documents if container restarts

6. Pouch db hosting: Ever peer will have an instance of pouch db which will act as a local document database, which will sync with ‘couch db hosting’ for backup. This service will store documents on local peer disk and should be able to fetch documents if container restarts

Services such as ‘File Sender’ and ‘File Receiver’ will be talking to ‘DB Service’ , and ‘DB Service’ will be talking with ‘Pouch DB hosting’ container. Local ‘Pouch DB hosting’ and other Peer’s ‘Pouch DB hosting’ will also be connecting with ‘Couch DB hosting’ as backup.