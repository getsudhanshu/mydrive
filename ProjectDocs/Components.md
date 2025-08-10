
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
