#1. Download and install python https://www.python.org/ (check the boxes to add python to path)

#2. Download and extract repository

#3. Open a command prompt in same directory (window start > cmd)

#4. Create python virtual environment: python -n venv env

#5. cd Aden

#6. pip install -r requirements.txt

#7. python -m client.main

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

