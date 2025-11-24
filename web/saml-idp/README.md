> [!NOTE]
> This is part of the "saml" challenge. Please see the readme of that challenge for more details. 

> When trying to deploy this locally, make sure you unzip `dbinit.zip`.

# Configuration of Authentik

For this challenge we use a snapshot of an auhtentik DB that is already configured.

For reference, the snapshot was prepared with roughly the following steps:

```bash
echo Regenerating config

openssl genrsa -out flaggetter/private.pem 2048
openssl req -batch -x509 -new -key flaggetter/private.pem -days 15 -subj '/CN=flaggetter/OU=Infobahn/' -out flaggetter/public.pem
TOKEN="$(openssl rand -base64 36 | tr -d '\n')"

echo "PG_PASS=$(openssl rand -base64 36 | tr -d '\n')" >> .env
echo "AUTHENTIK_SECRET_KEY=$(openssl rand -base64 60 | tr -d '\n')" >> .env
echo "AUTHENTIK_BOOTSTRAP_PASSWORD=$(openssl rand -base64 36 | tr -d '\n')" >> .env
# echo "AUTHENTIK_BOOTSTRAP_PASSWORD=password" >> .env
echo "AUTHENTIK_BOOTSTRAP_TOKEN=$TOKEN" >> .env
echo "AUTHENTIK_BOOTSTRAP_EMAIL=nobody@nowhere.com" >> .env

# If you have postgres issues, try deleting the authentik_database volume
docker compose up --wait --force-recreate -V -d

sleep 5

docker compose exec worker ak import_certificate --certificate /certs/public.pem --private-key /certs/private.pem --name flaggetter

echo Startup finished
docker compose logs -f flaggetter
```

- Switch DB name to "UNUSED" so future start ups won't interfere.
- Make the `flaggetter` application:
  - Application: make new application.
  - Provider: SAML provider with default provider explicit consent.
  - ACS URL: https://saml-web.challs.infobhanc.tf/flag
  - Service provider binding: redirect.
  - Advanced protocol settings (signing certificate `flaggetter`):
    - Sign both assertions and responses.
    - Assertion valid not on or after: minutes=60.
    - Use certificate `flaggetter` for signing.
- Build the login enrollment flow:
  - Create a new flow; once created, click on it.
  - Bind existing stage `default-source-enrollment-prompt`.
  - Edit the stage and add name/password fields.
  - Bind existing stage `default-source-enrollment-write`.
  - Go to `default-authentication-flow`, open stage bindings, and edit the first stage.
    - Flow settings: set the enrollment flow to the new flow.
  - Create a redirect stage for the end of `default-authentication-flow`.
    - Target URL: /application/saml/flaggetter/sso/binding/init/
