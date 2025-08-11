**What will it do?**

Docker container which tracks changes to a pre-configured directory such as file creation, file update or file deletion. Once change is detected, it will start process flow as per configuration

Request:


| API    | Type | Payload                                                                                                                 | Response                                                                                                    |
| ------ | ---- | ----------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| upload | POST | {"chunks":[{"id":"c1","size_in_KB":120},{"id":"c2","size_in_KB":200},{"id":"c3","size_in_KB":610}],"request_id":"1234"} | {"chunks":[{"id":"c1","send":"OK"},{"id":"c2","send":"NOTOK"},{"id":"c3","send":"OK"}],"request_id":"1234"} |
|        |      |                                                                                                                         |                                                                                                             |


**Open Points**

- Uses "something" to observe new file in a pre-configured directory
	- what if a file is uploaded few levels inside the parent folder
- If new file is determined and located, break the file into chunks and send to target peers
	- how many chunks? what's chunk size
	- how to pick target peer?
	- how to make sure chunks of a file are evenly spread across peers such that all chunks don't land up in one target peer
	- how to make sure the chunks also gets replicated saving us from target peer failure or unavailability
- Encryption of chunks before sending such that only file owner can decrypt it later
- How to ssh segments(or one whole chunk) such that these segments can be combined by target peer File Receiver.


