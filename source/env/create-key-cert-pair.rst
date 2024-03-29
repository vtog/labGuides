Create key/cert pair with OpenSSL
=================================

#. Run the following command to create the private key

   .. code-block:: bash

      openssl genrsa -out training.key 4096

#. Run the following command to generate CSR

   .. code-block:: bash

      openssl req -new \
      -subj "/C=US/ST=North Carolina/L=Raleigh/O=Red Hat/CN=todo-https.apps.ocp4.example.com" \
      -key training.key -out training.csr

#. Run the following command to generate cert

   .. code-block:: bash

      openssl x509 -req -in training.csr \
      -passin file:passphrase.txt \
      -CA training-CA.pem -CAkey training-CA.key -CAcreateserial \
      -out training.crt -days 1825 -sha256 -extfile training.ext
