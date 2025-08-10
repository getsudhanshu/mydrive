
**What will it do?**

Serves as proxy for accepting and origin of requests

It be at OS level installation - *but for testing we will have it as docker container*
- Allows only listed connections to be able to either send or receive file
	- TLS termination will happen here
- Open for 443(https) and 22(ssh) port only
	- For port 22, it will be pass through
- Rate limiting capability
- Firewall


**Open Points:**

1. TLS termination certificate generation
2. Oauth2 with google authentication?



