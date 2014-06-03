from os.path import basename
import re
from tempfile import NamedTemporaryFile

try:
    from subprocess import check_output, CalledProcessError, STDOUT
except ImportError:  # check_output new in 2.7, so use a backport for <=2.6
    from subprocess32 import check_output, CalledProcessError, STDOUT

class OpenSSLError(Exception):
    pass

def info_extension_cert(cert):
    """
    This function take a certificate and return the extensions in dict.

    @type cert : M2Crypto.X509
    @param cert : Certificate
    """
    certificateExtensions = {}

    for index in range(cert.get_ext_count()):
        ext = cert.get_ext_at(index)
        certificateExtensions[ext.get_name()] = ext.get_value()
    return certificateExtensions


def get_cert_url_ocsp(cert):
    """
    Get the OCSP url of a certificate

    @type cert : M2Crypto.X509
    @parm cert : Certificat

    @rtype : string
    @return : The OSCP url
    """

    infos = [x.strip() for x in info_extension_cert(cert)["authorityInfoAccess"].split('\n')]
    ocsp_url = None
    for info in infos:
        if re.match(r"^OCSP - URI:", info):
            ocsp_url = info.replace("OCSP - URI:","")
            break
    return ocsp_url.strip()


def is_revoked(cert, cert_parent):
    """
    Check if the certificate has been revoked.

    @type cert : M2Crypto.X509
    @param cert : The certificate

    @type cert_parent : string
    @param cert_parent : Issuer certificate file path

    @rtype : boolean
    @return : True if revoked or False
    """
    ocsp_url = get_cert_url_ocsp(cert)
    if re.match(r"^http", ocsp_url) is None:
        return False

    data = {'cert_parent': cert_parent,
            'ocsp_url': ocsp_url,
            'serial': cert.get_serial_number()}

    cmd = "openssl ocsp -issuer %(cert_parent)s -CAfile %(cert_parent)s -url %(ocsp_url)s -serial %(serial)s" % data
    print cmd
    try:
        output = check_output(cmd, shell=True, stderr=STDOUT).lower()
    except CalledProcessError, e:
        msg = u"[OpenSSL] Error while checking ocsp %s: %s. Output: %r" % (
                    cmd, e, e.output)
        raise OpenSSLError(msg)
    return not ('response verify ok' in output and '%s: good' % data['serial'] in output)


def is_revoked_crl(cert, cert_parent_with_crl):
    """
    Check if the certificate as been revoked with the crl.

    @type cert : M2Crypto.X509
    @param cert : The certificate

    @type cert_parent : string
    @param cert_parent : Issuer certificate file path

    @rtype : boolean
    @return : True if revoked or False
    """
    tmp_file = NamedTemporaryFile(prefix='cert')
    cert.save(tmp_file.name)
    data = {'cert': tmp_file.name,
            'cert_parent_with_crl': cert_parent_with_crl}
    cmd = "openssl verify -crl_check -CAfile %(cert_parent_with_crl)s %(cert)s" % data
    print cmd
    try:
        output = check_output(cmd, shell=True, stderr=STDOUT).lower()
    except CalledProcessError, e:
        msg = u"[OpenSSL] Error while checking ocsp %s: %s. Output: %r" % (
                    cmd, e, e.output)
        raise OpenSSLError(msg)
    print output
    return '%s: ok' % data['cert'] not in output


def get_cert_url_crl(cert):
    """
    Return the crl url from the certificate

    @type cert : M2Crypto.X509
    @parm cert : Certificate

    @rtype : string
    @return : CRL url
    """

    infos = [x.strip() for x in info_extension_cert(cert)["crlDistributionPoints"].split('\n')]
    crl_url = None
    for info in infos:
        print info
        if re.match(r"^URI:", info):
            crl_url = info.replace("URI:","")
            break
    return crl_url.strip()