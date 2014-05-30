#!/usr/bin/python
# coding: utf-8
###--- Module Imports -----------------------------------------------------------------------------------------------------------
import	codecs, os, re, requests, signal, shutil, sys, time, traceback
import	logging, logging.handlers
import	OpenSSL, base64
from	collections				import	OrderedDict
from	random					import	choice, random
from	M2Crypto				import	SMIME, X509, BIO
from	Crypto.Util				import	asn1
from	OpenSSL.crypto			import	TYPE_RSA, FILETYPE_PEM, PKCS7Type
from	OpenSSL.test.util		import	TestCase, bytes, b
###------------------------------------------------------------------------------------------------------------------------------
sys.setrecursionlimit(5000)
###------------------------------------------------------------------------------------------------------------------------------
def argparser():
	import argparse
	global ProgArgs
	
	ap = argparse.ArgumentParser( description = 'A web image grabber.', prog = os.path.basename(re.sub(".py", "", sys.argv[0])) )
	ap.add_argument( '-f',	'--file',		action = 'store',		dest = "file",		metavar = "file" )
	gap = ap.add_argument_group( 'standard functionality' )
	gap.add_argument(		'--dryrun',		action = 'store_true' )
	gap.add_argument( 		'--version',	action = 'version',		version = '%(prog)s 0.1' )
	gap.add_argument( 		'--list',		action = 'store_true',	default = False )
	gap.add_argument(		'--program',	action = 'store',		dest = "prog",		metavar = "prog",		default = os.path.basename(re.sub(".py", "", sys.argv[0])))
	gap = ap.add_argument_group( 'logging' )
	gap.add_argument( 		'--loglevel',	action = 'store',		dest = "loglevel",	metavar = "logging level",	default = 'info',	choices = ['crit', 'error', 'warn', 'notice', 'info', 'verbose', 'debug', 'insane'] )
	gap.add_argument(		'--logfile',	action = 'store',		dest = "logfile",	metavar = "logfile" )
	gap.add_argument( '-v',	'--verbose',	action = 'count',		default = 0 )
	gap = ap.add_argument_group( 'output options' )
	gap.add_argument(		'--debug',		action = 'store_true' )
	
	ProgArgs										= ap.parse_args()
	initLog( ProgArgs.loglevel )
	Logger											= logging.getLogger( __name__ )
	
	if ( ProgArgs.file is None ):
		Logger.error( "Must use -f argument." )
		sys.exit(1)
	
	return True
###------------------------------------------------------------------------------------------------------------------------------
def initLog( LLevel ):
	logger										= logging.getLogger( __name__ )
	LogLevels = {'crit':logging.CRITICAL,
				'error':logging.ERROR,
				'warn':logging.WARNING,
				'info':logging.INFO,
				'debug':logging.DEBUG }
	LogLevel										= LogLevels.get( LLevel, logging.NOTSET )
	logger.setLevel( LogLevel )
	LogFormat										= '(%(asctime)-11s)  :%(levelname)-9s:%(funcName)-13s:%(message)s'
	if ( len( logger.handlers ) == 0 ):
		try:
			Colorize								= __import__( 'logutils.colorize', fromlist=['colorize'] )
			LogHandler								= Colorize.ColorizingStreamHandler()
			LogHandler.level_map[logging.DEBUG]		= (None, 'blue', False)
			LogHandler.level_map[logging.INFO]		= (None, 'green', False)
			LogHandler.level_map[logging.WARNING]	= (None, 'yellow', False)
			LogHandler.level_map[logging.ERROR]		= (None, 'red', False)
			LogHandler.level_map[logging.CRITICAL]	= ('red', 'white', False)
		except ImportError:
			LogHandler	= logging.StreamHandler()
	else:
		LogHandler	= logging.StreamHandler()
	LogHandler.setFormatter( logging.Formatter( LogFormat, datefmt='%I:%M:%S %p' ) )
	logger.addHandler( LogHandler )
###------------------------------------------------------------------------------------------------------------------------------
class PKCS7Tests(TestCase):
	"""
	Tests for L{PKCS7Type}.
	"""
	def test_type(self):
		# L{PKCS7Type} is a type object.
		self.assertTrue(isinstance(PKCS7Type, type))
		self.assertEqual(PKCS7Type.__name__, 'PKCS7')

		# XXX This doesn't currently work.
		# self.assertIdentical(PKCS7, PKCS7Type)


		# XXX Opposite results for all these following methods

	def test_type_is_signed_wrong_args(self):
		"""
		L{PKCS7Type.type_is_signed} raises L{TypeError} if called with any arguments.
		"""
		pkcs7 = load_pkcs7_data(FILETYPE_PEM, pkcs7Data)
		self.assertRaises(TypeError, pkcs7.type_is_signed, None)


	def test_type_is_signed(self):
		"""
		L{PKCS7Type.type_is_signed} returns C{True} if the PKCS7 object is of the type I{signed}.
		"""
		pkcs7 = load_pkcs7_data(FILETYPE_PEM, pkcs7Data)
		self.assertTrue(pkcs7.type_is_signed())

	def test_type_is_enveloped_wrong_args(self):
		"""
		L{PKCS7Type.type_is_enveloped} raises L{TypeError} if called with any arguments.
		"""
		pkcs7 = load_pkcs7_data(FILETYPE_PEM, pkcs7Data)
		self.assertRaises(TypeError, pkcs7.type_is_enveloped, None)


	def test_type_is_enveloped(self):
		"""
		L{PKCS7Type.type_is_enveloped} returns C{False} if the PKCS7 object is not of the type I{enveloped}.
		"""
		pkcs7 = load_pkcs7_data(FILETYPE_PEM, pkcs7Data)
		self.assertFalse(pkcs7.type_is_enveloped())


	def test_type_is_signedAndEnveloped_wrong_args(self):
		"""
		L{PKCS7Type.type_is_signedAndEnveloped} raises L{TypeError} if called with any arguments.
		"""
		pkcs7 = load_pkcs7_data(FILETYPE_PEM, pkcs7Data)
		self.assertRaises(TypeError, pkcs7.type_is_signedAndEnveloped, None)


	def test_type_is_signedAndEnveloped(self):
		"""
		L{PKCS7Type.type_is_signedAndEnveloped} returns C{False} if the PKCS7 object is not of the type I{signed and enveloped}.
		"""
		pkcs7 = load_pkcs7_data(FILETYPE_PEM, pkcs7Data)
		self.assertFalse(pkcs7.type_is_signedAndEnveloped())


	def test_type_is_data(self):
		"""
		L{PKCS7Type.type_is_data} returns C{False} if the PKCS7 object is not of the type data.
		"""
		pkcs7 = load_pkcs7_data(FILETYPE_PEM, pkcs7Data)
		self.assertFalse(pkcs7.type_is_data())


	def test_type_is_data_wrong_args(self):
		"""
		L{PKCS7Type.type_is_data} raises L{TypeError} if called with any arguments.
		"""
		pkcs7 = load_pkcs7_data(FILETYPE_PEM, pkcs7Data)
		self.assertRaises(TypeError, pkcs7.type_is_data, None)


	def test_get_type_name_wrong_args(self):
		"""
		L{PKCS7Type.get_type_name} raises L{TypeError} if called with any arguments.
		"""
		pkcs7 = load_pkcs7_data(FILETYPE_PEM, pkcs7Data)
		self.assertRaises(TypeError, pkcs7.get_type_name, None)


	def test_get_type_name(self):
		"""
		L{PKCS7Type.get_type_name} returns a C{str} giving the type name.
		"""
		pkcs7 = load_pkcs7_data(FILETYPE_PEM, pkcs7Data)
		self.assertEquals(pkcs7.get_type_name(), b('pkcs7-signedData'))


	def test_attribute(self):
		"""
		If an attribute other than one of the methods tested here is accessed on an instance of L{PKCS7Type}, L{AttributeError} is raised.
		"""
		pkcs7 = load_pkcs7_data(FILETYPE_PEM, pkcs7Data)
		self.assertRaises(AttributeError, getattr, pkcs7, "foo")
###------------------------------------------------------------------------------------------------------------------------------
def checkfile( file ):
	isfile											= False
	if os.path.isfile( file ):
		isfile										= True
	return isfile
###------------------------------------------------------------------------------------------------------------------------------
def readp7b( file ):
	data											= ''
	with open( file ) as r_file:
		copy = False
		for line in r_file:
			if "-----BEGIN PKCS7-----" in line.strip():
				copy								= True
				data								= ''.join( [ data, line ] )
			elif "-----END PKCS7-----" in line.strip():
				copy								= False
				data								= ''.join( [ data, line ] )
			elif copy:
				data								= ''.join( [ data, line ] )
		print( data )
		pkcs7										= OpenSSL.crypto.load_pkcs7_data( FILETYPE_PEM, data )
		print(pkcs7)
		print(pkcs7.get_type_name() )
###------------------------------------------------------------------------------------------------------------------------------
def other():
	raw_sig = """base64 PKCS7 envelop"""
	msg = "challenge message to verify"

	sm_obj = SMIME.SMIME()
	x509 = X509.load_cert('ISSUER.crt') # public key cert used by the remote client when signing the message
	sk = X509.X509_Stack()
	sk.push( x509 )
	sm_obj.set_x509_stack(sk)

	st = X509.X509_Store()
	st.load_info( 'ROOT.crt' ) # Public cert for the CA which signed the above certificate
	sm_obj.set_x509_store( st )

	# re-wrap signature so that it fits base64 standards
	cooked_sig = '\n'.join( raw_sig[pos:pos+76] for pos in xrange( 0, len(raw_sig), 76 ) )

	# now, wrap the signature in a PKCS7 block
	sig = """
	-----BEGIN PKCS7-----
	%s
	-----END PKCS7-----
	""" % cooked_sig

	# print sig

	# and load it into an SMIME p7 object through the BIO I/O buffer:
	buf = BIO.MemoryBuffer( sig )
	p7 = SMIME.load_pkcs7_bio( buf )

	signers = p7.get0_signers( sk )
	certificat = signers[0]
###------------------------------------------------------------------------------------------------------------------------------
def main():
	Logger											= logging.getLogger( __name__ )
	#--- Parse program arguments ----------------------------------------------------------------------------
	success											= argparser()
	if ( not success ):
		logger.error("Error: Problem parsing arguments.")
		sys.exit(1)
		
	if checkfile( ProgArgs.file ):
		p7data										= readp7b( ProgArgs.file )
	
	Logger.info( p7data )
	
	return success
###------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	main()
###------------------------------------------------------------------------------------------------------------------------------