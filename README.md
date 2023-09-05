# shib-keygen-api

Generate Shibboleth SP/SAML2 metadata X509 certificates, keys and then stores them in e.g. Vault

# TODO
* Add `/generate` endpoint
* Implement plugins
  * [ ] `stdout` plugin
  * [ ] `dir` plugin
  * [ ] `vault` plugin
* [ ] Implement configuration for each plugin
* Add `/status` page
  * Add a `status` check for each plugin
* [ ] Add certificate and key generation using `openssl-req(1)`
  * [ ] Either use `pyopenssl` https://stackoverflow.com/a/60804101
  * [ ] or `cryptography` https://cryptography.io/en/latest/x509/tutorial/#creating-a-self-signed-certificate
