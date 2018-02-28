#!/bin/bash

scp -r -i LightsailDefaultPrivateKey-us-east-2.pem -P 2200 /Users/Peter/developer/FSND-Linux-Server/sportsCatalog/client_secrets.json ubuntu@18.219.188.90:/var/www/sportsCatalog