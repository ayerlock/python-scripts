python-scripts
==============

**src/p7b2crt.py**
* Utility for loading a p7b certificate chain and saving out individual certificates.
  * Requires python and openssl

######Example Usage:######
List all the certificates in the p7b.
```
[user@system PKCS7]$ p7b2crt.py -l -f InstallRoot_PKCS7_v3.16.1A.pem-signed.p7b
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-19
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-20
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-21
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-22
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-23
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-24
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-25
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-26
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-27
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-28
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-29
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-30
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-31
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-32
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD EMAIL CA-19
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD EMAIL CA-20
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD EMAIL CA-21
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD EMAIL CA-22
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD EMAIL CA-23
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD EMAIL CA-24
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD EMAIL CA-25
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD EMAIL CA-26
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD EMAIL CA-27
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD EMAIL CA-28
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD EMAIL CA-29
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD EMAIL CA-30
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD EMAIL CA-31
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD EMAIL CA-32
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DoD Intermediate CA-1
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DoD Intermediate CA-2
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DoD Root CA 2
```

List all the certificates in the p7b that do not have 'email' in the subject CN.
```
[user@system PKCS7]$ p7b2crt.py p7b2crt -l -x email -f InstallRoot_PKCS7_v3.16.1A.pem-signed.p7b
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-19
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-20
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-21
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-22
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-23
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-24
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-25
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-26
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-27
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-28
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-29
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-30
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-31
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DOD CA-32
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DoD Intermediate CA-1
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DoD Intermediate CA-2
Certificate subject = C=US, O=U.S. Government, OU=DoD, OU=PKI, CN=DoD Root CA 2
```

Save all the certificates in the p7b that do not have 'email' in the subject CN into directory 'certs'.
```
[user@system PKCS7]$ p7b2crt.py -x email -s -d certs -f InstallRoot_PKCS7_v3.16.1A.pem-signed.p7b
(03:19:06 PM)  :INFO     :saveCert     :Writing file: /tmp/PKCS7/certs/DOD-CA-19.crt
(03:19:06 PM)  :INFO     :saveCert     :Writing file: /tmp/PKCS7/certs/DOD-CA-20.crt
(03:19:06 PM)  :INFO     :saveCert     :Writing file: /tmp/PKCS7/certs/DOD-CA-21.crt
(03:19:06 PM)  :INFO     :saveCert     :Writing file: /tmp/PKCS7/certs/DOD-CA-22.crt
(03:19:06 PM)  :INFO     :saveCert     :Writing file: /tmp/PKCS7/certs/DOD-CA-23.crt
(03:19:06 PM)  :INFO     :saveCert     :Writing file: /tmp/PKCS7/certs/DOD-CA-24.crt
(03:19:06 PM)  :INFO     :saveCert     :Writing file: /tmp/PKCS7/certs/DOD-CA-25.crt
(03:19:06 PM)  :INFO     :saveCert     :Writing file: /tmp/PKCS7/certs/DOD-CA-26.crt
(03:19:06 PM)  :INFO     :saveCert     :Writing file: /tmp/PKCS7/certs/DOD-CA-27.crt
(03:19:06 PM)  :INFO     :saveCert     :Writing file: /tmp/PKCS7/certs/DOD-CA-28.crt
(03:19:06 PM)  :INFO     :saveCert     :Writing file: /tmp/PKCS7/certs/DOD-CA-29.crt
(03:19:06 PM)  :INFO     :saveCert     :Writing file: /tmp/PKCS7/certs/DOD-CA-30.crt
(03:19:06 PM)  :INFO     :saveCert     :Writing file: /tmp/PKCS7/certs/DOD-CA-31.crt
(03:19:06 PM)  :INFO     :saveCert     :Writing file: /tmp/PKCS7/certs/DOD-CA-32.crt
(03:19:06 PM)  :INFO     :saveCert     :Writing file: /tmp/PKCS7/certs/DoD-Intermediate-CA-1.crt
(03:19:06 PM)  :INFO     :saveCert     :Writing file: /tmp/PKCS7/certs/DoD-Intermediate-CA-2.crt
(03:19:06 PM)  :INFO     :saveCert     :Writing file: /tmp/PKCS7/certs/DoD-Root-CA-2.crt
```
