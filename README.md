# cookflaskIM

This project is a **NON OFFICIAL** demonstration on how to use the API for **reseller** provided by Ingram Micro.
There is no support for this project, it is **just a demonstration**.

**At this time, I won't add any new features to this project.** it's provide as it.  

**WARNING** this project is not for production, only for test

## Ingram Micro API


#### For Resellers
You must be client of Ingram Micro and have a valid account to use the API.
And you can find the reseller API documentation [here](https://developer.ingrammicro.com/reseller/api-documentation/United_States)
to use the Ingram Micro API, you need to create an account on the API portal and create an application to get the API key and secret.

#### For Vendors
Sorry, I don't have any information about the vendor API. But the process should be similar to the reseller API.

#### Webhooks
The API provides webhooks to get notifications about the changes in the orders, but I didn't implement this feature in this project.
You can test the webhooks using the [webhook.site](https://webhook.site/)
You can find the webhook documentation [here](https://developer.ingrammicro.com/reseller/webhooks)

## Docker Quickstart

This app can be run completely using `Docker` and `docker compose`. **Using Docker is recommended, as it guarantees the application is run using compatible versions of Python and Node**.

There are three main services:

To run the development version of the app

```bash
docker compose up flask-dev
```

The list of `environment:` variables in the `docker compose.yml` file takes precedence over any variables specified in `.env`.
By the way, this is an example of .env 

```text
API_BASE_URL=https://api.ingrammicro.com/sandbox
SESSION_SECRET=your-secret-key
IM_CUSTOMERCONTACT=your-customer-contact
IM_COUNTRYCODE=your-country-code
IM_CUSTOMER_NUMBER=your-customer-number
IM_CORRELATION_ID=your-correlation-id
IM_SENDERID=your-sender-id
PORT=Port-of-your-app-if-needed
```

To run any commands using the `Flask CLI`

```bash
docker compose run --rm manage <<COMMAND>>
```

Therefore, to initialize a database you would run

```bash
docker compose run --rm manage db init
docker compose run --rm manage db migrate
docker compose run --rm manage db upgrade
```

A docker volume `node-modules` is created to store NPM packages and is reused across the dev and prod versions of the application. For the purposes of DB testing with `sqlite`, the file `dev.db` is mounted to all containers. This volume mount should be removed from `docker compose.yml` if a production DB server is used.

Go to `http://localhost:8080`. You will see a pretty welcome screen.

### Running locally

Run the following commands to bootstrap your environment if you are unable to run the application using Docker

```bash
cd IMAPI
pip install -r requirements/dev.txt
npm install
npm run-script build
npm start  # run the webpack dev server and flask server using concurrently
```

Go to `http://localhost:5000`. You will see a pretty welcome screen.

#### Database Initialization (locally)

Once you have installed your DBMS, run the following to create your app's
database tables and perform the initial migration

```bash
flask db init
flask db migrate
flask db upgrade
```

## Deployment

When using Docker, reasonable production defaults are set in `docker compose.yml`

```text
FLASK_ENV=production
FLASK_DEBUG=0
```

Therefore, starting the app in "production" mode is as simple as

```bash
docker compose up flask-prod
```

If running without Docker

```bash
export FLASK_ENV=production
export FLASK_DEBUG=0
export DATABASE_URL="<YOUR DATABASE URL>"
npm run build   # build assets with webpack
flask run       # start the flask server
```

## Shell

To open the interactive shell, run

```bash
docker compose run --rm manage shell
flask shell # If running locally without Docker
```

By default, you will have access to the flask `app`.

## Running Tests/Linter

To run all tests, run

```bash
docker compose run --rm manage test
flask test # If running locally without Docker
```

To run the linter, run

```bash
docker compose run --rm manage lint
flask lint # If running locally without Docker
```

The `lint` command will attempt to fix any linting/style errors in the code. If you only want to know if the code will pass CI and do not wish for the linter to make changes, add the `--check` argument.

## Migrations

Whenever a database migration needs to be made. Run the following commands

```bash
docker compose run --rm manage db migrate
flask db migrate # If running locally without Docker
```

This will generate a new migration script. Then run

```bash
docker compose run --rm manage db upgrade
flask db upgrade # If running locally without Docker
```

To apply the migration.

For a full migration command reference, run `docker compose run --rm manage db --help`.

If you will deploy your application remotely (e.g on Heroku) you should add the `migrations` folder to version control.
You can do this after `flask db migrate` by running the following commands

```bash
git add migrations/*
git commit -m "Add migrations"
```

Make sure folder `migrations/versions` is not empty.

## Asset Management

Files placed inside the `assets` directory and its subdirectories
(excluding `js` and `css`) will be copied by webpack's
`file-loader` into the `static/build` directory. In production, the plugin
`Flask-Static-Digest` zips the webpack content and tags them with a MD5 hash.
As a result, you must use the `static_url_for` function when including static content,
as it resolves the correct file name, including the MD5 hash.
For example

```html
<link rel="shortcut icon" href="{{static_url_for('static', filename='build/favicon.ico') }}">
```

If all of your static files are managed this way, then their filenames will change whenever their
contents do, and you can ask Flask to tell web browsers that they
should cache all your assets forever by including the following line
in ``.env``:

```text
SEND_FILE_MAX_AGE_DEFAULT=31556926  # one year
```
