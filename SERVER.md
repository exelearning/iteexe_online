# eXe Learning as a web service

## Change domain name

It is advisable to use this application behind a reverse proxy

To change domain name to execute eXe edit the next files and replace:

- exe/webui/oauthpage.py

In line "REDIRECT_URI = 'https://exe.open-phoenix.com/oauth/procomun/callback'" replace "exe.open-phoenix.com" with a new [domain name]. (Line 28)

- images/idp/config.php

Add a [domain name] to the variable "baseurlpath", e.g:
'baseurlpath'           => 'https://exe.open-phoenix.com/simplesamlphp/', (Line 25)

- images/idp/metadata/saml20-sp-remote.php

Replace "https://front.local" with [domain name] in variable $domain_value (Line 2)

- saml_template/settings.json

Replace 'https://front.local' with [domain name] in '"entityId": "https://front.local/saml/metadata/",' (Line 5)
Replace 'https://front.local' with [domain name] in '"url": "https://front.local/saml/acs",' (Line 7)
Replace 'https://front.local' with [domain name] in '"url": "https://front.local/saml/sls",' (Line 11)
Replace 'https://front.local' with [domain name] in '"entityId": "https://front.local/simplesamlphp/saml2/idp/metadata.php",' (Line 19)
Replace 'https://front.local' with [domain name] in '"url": "https://front.local/simplesamlphp/saml2/idp/SSOService.php",' (Line 21)
Replace 'https://front.local' with [domain name] in '"url": "https://front.local/simplesamlphp/saml2/idp/SingleLogoutService.php",' (Line 25)

## Development environment

The development environment of eXe Learning is based in 3 docker containers that can be managed using docker-compose.
So, you need latest versions installed of Docker and Docker compose.

After installing docker and docker-compose, you can build the needed containers executing in your root source directory:

`docker-compose build`

To run the containers, you can execute:

`docker-compose up -d`

Now we have a webserver listening in ports 80 and 443. To test eXe web service with HTTP Basic authentication, visit
[http://localhost](http://localhost) in a browser. You will be asked for a user name and password. By default, we have
defined three users at images/apache2/htpasswd all of them with password "open-phoenix".

For the 443 port, we have configured by default to use SAML as authentication using a configured container with
SimpleSAMLphp as IDP (Identy provider). By default the configured IDP uses Google as authentication source, so we need
to create a new credentials of type "Oauth 2.0 client ID" at
[https://console.developers.google.com/apis/credentials](https://console.developers.google.com/apis/credentials)
(create a new project if needed), setting:

-"Application type": "Web application"
-"Authorised redirect URIs": "https://front.local/simplesamlphp/module.php/authgoogle/linkback.php"

The resulting ClientID and Client secret values of the new credential created needs to be filled at the file
images/idp/authsources.php:159:160

After that, you need to enable Google+ API project for your project, for example visiting the Dashboard and Enable API
link. Search for "Google+ API" and check Enable.

The default configuration of the sample IDP server has configured front.local as hostname. So, we need to add the next
line to our /etc/hosts file:

`127.0.0.1 front.local`

After restarting our docker containers (`docker-compose kill; docker-compose up -d`) you can visit
[https://front.local](https://front.local). Google will prompt the first time to allow eXe to access some user data.
After Google authentication success, the web interface of eXe should be showed.

## Pre/Production environments

TBC