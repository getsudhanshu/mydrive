This project is a p2p file storage service where peers will be a set of pre-configured computers.  These computers can be friends spare laptops with some storage.

Intention is to save personal files in these machines such that it can only be retrieved by owner. 

[[Components]] can be a good starting point

Summary:

i plan to make a p2p file storage server. The project is intended to replace onedrive with free p2p solution where group of friends from different region use their spare laptop/pc and use it as file storage.

File Sender App:
At high level, there will be a demon/process which will keep an eye on a directory and whenever a file in that directory gets changed, it will initiate the 'file sender' process. the app 'file_sender' will be hosted on docker which will first break file into chunks (and chunks into segments if required) then calculate each chunks size. These chunks will also be encrypted so that target peer cannot read the file or recreate the file. It will then send post api request 'check_space' to target peer's app 'file_receiver' which is listening to this API via nginx proxy. The 'check_space' api will first check if it has space to accept the chunks. if yes, it sends appropriate response. Due to safety and security, we will not be sending all chunks of a file to target peer , this is to avoid peer having a complete file even though it's encrypted. Once we get confirmation from target peer that it has space, we will start sending file. we will use sql lite to hold metadata such as which chunk is with which peer, encryption key etc. Based on target peer's response, we will initiate an independent ssh connection between source peer and target peer and start streaming file chunks from source peer to target peer. Once all chunks are spread to all target peers (remember we don't want all chunks of file to land into one target), file_sender app will send PUT api informing target peer that it has send all chunks so that target peer can update it's metadata. 

File Fetcher:
This will also be a container in storage server apart from file sender, file receiver and DB service (3rd tier). whenever a request is raised (thinking of web browser based gui) to fetch a file, the app will query db service to find chunks and which target peer has what chunk. Based on this information it will start sending requests to target peer's file sender app requesting chunks. The file sender will then initiate independent ssh connection nd start sending chunks. Once all chunks are send, file sender will inform file fetcher that it has send all chunks. File fetcher will then combine all chunks, decrypt it and place it in a directory for user to use the file.




