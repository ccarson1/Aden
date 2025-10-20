#Run Client 

python -m client.main

#Run Server

python -m server.main

#Update project

git fetch origin

git reset --hard origin/main

#Generating a ssl certificate

openssl req -x509 -nodes -days 365 -newkey rsa:4096 -keyout server.key -out server.crt -config openssl.cnf

When running locally an ssl cert needs to be created for the local PC

When running on a remote server sn ssl needs to be created for the remote server

Edit the certs/openssl.cnf before creating a new cert. Change the IP addresses to match your server's IP address.

