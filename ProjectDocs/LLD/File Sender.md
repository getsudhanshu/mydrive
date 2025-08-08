
**Terminology:** 

1. Peer Network: Machines or nodes participating in p2p file storage service
2. Peer: individual Machine which is part of Peer Network
3. File: Atomic unit of meaningful data uploaded by a user. 
	1. Chunk: A file can be broken down into multiple chunks. Each peer will receive some chunks. but not all chunks to form a file 
	2. segment: Each chunk can be broken down into multiple segments to enable error check during multi part upload. This will be used to resend only corrupt segment(if there will be any) 
	

**Open Points**

- Uses "something" to observe new file in a pre-configured directory
	- what if a file is uploaded few levels inside the parent folder
- If new file is determined and located, break the file into chunks and send to target peers
	- how many chunks? what's chunk size
	- how to pick target peer?
	- how to make sure chunks of a file are spread across evenly such that all chunks don't land up in one target peer
	- how to make sure the chunks also gets replicated saving us from target peer failure or unavailability
- Encryption of chunks before sending such that only file owner can decrypt it later
- 
- 