
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
3) Nginx hosting
4) Couch db hosting
5) UI/UX hosting

Details:
1. File Sender : Can perform following 2 actions: 
	a) Sends file to a peer using gRPC call
	b) Can also send a file from local drive as requested by ‘File receiver’ service

2. File receiver: Can perform following 2 actions: 
	a) Accept and saves file sent by ‘File sender’ service into it’s local drive,
	b) Send request to another peer’s ‘File Sender’ service to send her a file

3. Nginx hosting: Peers will be talking with each other for sending and receiving files using ‘File sender’ and ‘file receiver’ services. Nginx hosting container will host nginx which will take care of TLS termination and routing:
	1. grpc call to/from ‘file receiver’ service
	2. grpc call to/from ‘file sender’ services. 
	3. peer’s couch db document replication with host ‘couch db’
	4. localhost browser call for user creation and file fetching for that user

4. Couch db hosting: All peers will have couch db hosting container. This ‘couch db hosting’ container will not only host documents db for host, but also work in master-master configuration for peer document replication

5. UI/UX hosting: This service will host UI/UX through web browser to perform following:
	1. On boarding new user. Provide an interface to user to enter 'user name', 'passphrase' and 'confirm passphrase'. If 'passphrase' matches with 'confirm passphrase' only then request will be send to backend UI/UX container. The onboarding page should look pretty with some logo highlighting 'mydrive' project
	2. Passphrase rotation: Giving user an option to rotate passphrase
	3. Showing user his 'tree' of files and directories. User should be able to add files to his basket which he wants to download from p2p storage. As per design, only owner of the file will be able to fetch his file from peers.

Note:
1. Services such as ‘File Sender’, ‘File Receiver’ and 'UI/UX Service' will be directly talking to ‘Couch DB hosting’ . 
2. Docker compose will be used to orchestrate docker containers