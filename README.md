
# Introduction

Email Engine is an Django app which will be having features like third-party login through Oauth, email data sync up to elasticsearch, api for email creation, email search etc. 

# Installation Guide
This project requires the following tools to get started:

- Docker 
- Docker compose

To get started, install Docker and Docker compose on your local computer if you don't have them already.

# Getting started
## Clone the repository into a new folder and then switch to code directory
```
$ git clone https://github.com/sumanth2905/email_engine.git
$ cd email_engine
```
## Outlook OAuth Integration
**Azure AD App Registration** 

Go to [Azure Portal](https://portal.azure.com/).

Register a new app and note the `client_id` and `client_secret`.

Add API permissions for **Microsoft Graph** (
`User.Read`, `Mail.Read`, `Mail.ReadWrite`, `openid`, `offline_access`, `email`)

Set the `redirect_uri` to point to your backend URL (e.g., `http://localhost:8000/api/outlook/callback/`).


## Build and run application

**Step 1: Build the Docker images**
```
$ docker compose build
```

**Step 2: Start the services**
```
$ docker compose up
```
This command will start the Django application and Elasticsearch service. You can access the Django application at ``http://localhost:8000``

## Environment Variables
Make sure to set the following environment variables in a `.env` file or directly in your Docker Compose file:

```
# Django settings
DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=True  # Set to False in production
DJANGO_ALLOWED_HOSTS=localhost  # Add your domain in production
CLIENT_ID=azure_client_id
CLIENT_SECRET=client_secret
TENANT=tenant_id
```

## Database Migrations

Run the following command to apply database migrations

```
$ docker compose run web python manage.py makemigrations
$ docker compose run web python manage.py migrate
```
## Create a Superuser

To create a superuser for accessing the Django admin panel, execute below command

```
$ docker compose run web python manage.py createsuperuser
```

## Oauth setup in admin-panel
Login to your admin panel and add a new entry into social application table with client_id and client_secret obtained from Azure.

## Accessing the Application

**Django Admin:** http://localhost:8000/admin \
**Login url:** http://localhost:8000/acconts/

## Stopping the Application
To stop the running application, use:
```
$ docker compose down
```

# Future Enhancements
- Resolution of tenant issue while email sync
- Implementation of kafka aggent between django and elasticsearch to avoid load on elasticsearch
