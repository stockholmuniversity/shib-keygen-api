# shib-keygen-api

Generate Shibboleth SP/SAML2 metadata X509 certificates, keys and then stores them in e.g. Vault

## Usage

Of course, install and use this application inside a venv or container.

### Installation
```shell
$ pip3 install shib-keygen-api
```

### Running

#### Using `flask run`
```shell
$ FLASK_APP=shib_keygen_api:app flask run
```

#### In prod using e.g. `gunicorn`
```shell
$ pip3 install gunicorn
$ gunicorn shib_keygen_api:app
```

### Configuration
You can configure the application with either
* environment variables prefixed with `FLASK_`
* in a `.cfg`-file that you point the environment variable `FLASK_CONFIG` towards

 Key | Value | Example
-|-|-
`OUTPUT_PLUGIN` | Output plugin to store the certs | `dir`
`PLUGIN_CONFIG` | Dict where the configuration for output plugin is stored. Key is the plugin name.API-key or password to use when connecting | `{"dir": {"path":"/srv/shib-certs"}}`

Example:
```shell
$ cat <<EOF > shib_keygen_api.cfg
OUTPUT_PLUGIN="dir"
PLUGIN_CONFIG = {
  "dir": {
    "path": "/srv/shib-certs"
  },
}
EOF
$ env FLASK_CONFIG=shib_keygen_api.cfg gunicorn -b localhost:5000 shib_keygen_api:app --reload --reload-extra-file shib_keygen_api.cfg
$ # or
$ env FLASK_CONFIG=shib_keygen_api.cfg FLASK_APP=shib_keygen_api:app flask run --reload --extra-files shib_keygen_api.cfg
```

#### Plugin configuration

##### `dir`
```python
PLUGIN_CONFIG = {
  "dir": {
    "path": "/srv/shib-certs"
  },
}
```

##### `vault`
```python
PLUGIN_CONFIG = {
  "vault": {
    "path": "secret/",
    "secret_key_name": "binaryData", # key to store the certificate in
    "storage_method": "binarylist", # How we store the data, e.g. "raw"
    "default_kv_version": 1, # https://hvac.readthedocs.io/en/stable/usage/secrets_engines/kv.html#setting-the-default-kv-version
    "client": {}, # Any option from https://hvac.readthedocs.io/en/stable/source/hvac_v1.html#hvac.v1.Client
    "auth_method": "approle", # From https://hvac.readthedocs.io/en/stable/source/hvac_api.html#hvac.api.AuthMethods
    "auth_method_params": { # https://hvac.readthedocs.io/en/stable/source/hvac_api_auth_methods.html
      "role_id": "7ef99e5e-1d05-4b31-946a-eb86dbc98d93",
      "secret_id": "d2566186-267e-4ed4-9a25-f488bebdb3a5",
    },
  },
}
```

###### `storage_method`

You can process the certificate and key data before we store it Vault in
different ways:

`storage_method` | Explaination
-|-
`raw` | Nothing done, the default.
`base64` | We base64 encode the data
`binarylist` | We create a binary list of the data[^1]

[^1]: Please don't store your data this way. It's just to support the legacy
    way [VaultTool](https://github.com/stockholmuniversity/vaulttool) uses to
    store binary files.

# TODO
* [X] Add `/generate` endpoint
* [X] Decide plugin signature
* Implement plugins
  * [X] `stdout` plugin
  * [X] `dir` plugin
  * [x] `vault` plugin
* [X] Implement configuration for each plugin
* [X] Add `/status` page
  * [X] Add a `status` check for each plugin
* [X] Add certificate and key generation using `openssl-req(1)`
  * [ ] Either use `pyopenssl` https://stackoverflow.com/a/60804101
  * [ ] or `cryptography` https://cryptography.io/en/latest/x509/tutorial/#creating-a-self-signed-certificate
