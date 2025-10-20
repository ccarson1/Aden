#Run Client 

python -m client.main

#Run Server

python -m server.main

#Update project

git fetch origin

git reset --hard origin/main

#Generating a ssl certificate
openssl req -x509 -nodes -days 365 -newkey rsa:4096 -keyout server.key -out server.crt -config openssl.cnf

