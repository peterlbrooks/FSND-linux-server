#!/bin/bash


scp -r -i LightsailDefaultPrivateKey-us-east-2.pem -P 2200 ubuntu@18.219.188.90:/var/www/sportsCatalog.wsgi /Users/Peter/developer/FSND-Linux-Server/configs
