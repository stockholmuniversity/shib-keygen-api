# shib-keygen-api

Generate Shibboleth SP/SAML2 metadata X509 certificates, keys and then stores them in e.g. Vault

# TODO
* [X] Add `/generate` endpoint
* [X] Decide plugin signature
* Implement plugins
  * [X] `stdout` plugin
  * [ ] `dir` plugin
  * [ ] `vault` plugin
* [ ] Implement configuration for each plugin
* [X] Add `/status` page
  * [X] Add a `status` check for each plugin
* [X] Add certificate and key generation using `openssl-req(1)`
  * [ ] Either use `pyopenssl` https://stackoverflow.com/a/60804101
  * [ ] or `cryptography` https://cryptography.io/en/latest/x509/tutorial/#creating-a-self-signed-certificate
