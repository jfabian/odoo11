Localization for Odoo Perú
==========================

This module will be the base for the peruvian localization and electronic
invoicing.

Software requirements
---------------------

- Install the following python packages
    - ``signxml``
    - ``num2words``
    - ``requests_mock``
    - ``pysimplesoap``
    - ``httplib2``

- Install ``openssl`` to generate certificates

Generate self-served certificate
--------------------------------

In order to sign electronic documents you will need a certificate, in the demo have
been defined one for testing purposes that was generated using the following command:

``$ openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 3650 -sha1``

This command will generate a 10 years certificate (with ``-days 3650``) and will ask you some
information that is required you to fill up and also for a password that you
must keep for later usage of the certificate.

To see/verify certificate information use the following command

``$ openssl x509 -in cert.pem -text``

The minimal requirements accepted by the SUNAT are the following ones:

- X.509 v3
- Private key minimal length of 1024bits
- Company representative must be in digital signature indicating Name, Last Names, DNI and also the RUC number of company is representing.
- Company's RUC must be in "Subject Name" within the field OU (Organizational Unit)

In order for this to work directly to SUNAT beta web services, the digital certificates needs to be notified to SUNAT through enabled option named "**Actualización de certificado digital**" in "**Menú SOL**".

Generate a PFX cert
-------------------

Once we have the ``cert.pem`` and ``key.pem`` we can create a PFX certificate. Now, with this we can interact with the current form of work we have on l10n_pe_edi.

``$ openssl pkcs12 -export -in cert.pem -inkey key.pem -out cert.pfx``

If you want to see the information within the PFX file then you can run this command.

``$ openssl pkcs12 -in cert.pfx``

