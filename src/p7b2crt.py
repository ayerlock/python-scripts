#!/usr/bin/python
# coding: utf-8
###--- Module Imports -----------------------------------------------------------------------------------------------------------
import	os, re, sys
import	logging, logging.handlers
import	subprocess
###------------------------------------------------------------------------------------------------------------------------------
def argparser():
	import	argparse
	global	ProgArgs

	ap = argparse.ArgumentParser( description = 'A web image grabber.', prog = os.path.basename( re.sub( ".py", "", sys.argv[0] ) ) )
	ap.add_argument( '-f', 	'--file', 		action = 'store', 		dest = "file", 		metavar = "<input file>" )
	gap = ap.add_argument_group( 'standard functionality' )
	gap.add_argument( '--dryrun', 		action = 'store_true' )
	gap.add_argument( '--program', 	action = 'store', 		dest = "prog", 		metavar = "prog", 		default = os.path.basename( re.sub( ".py", "", sys.argv[0] ) ) )
	gap.add_argument( '--version', 	action = 'version', 		version = '%(prog)s 0.1' )
	gap = ap.add_argument_group( 'output options' )
	gap.add_argument( '--debug', 		action = 'store_true' )
	gap.add_argument( '--loglevel', 	action = 'store', 		dest = "loglevel", 	metavar = "<log level>", 	default = 'info', 	choices = ['crit', 'error', 'warn', 'notice', 'info', 'verbose', 'debug', 'insane'] )
	gap.add_argument( '--logfile', 	action = 'store', 		dest = "logfile", 	metavar = "<logfile>" )
	gap.add_argument( '-l', 	'--list', 		action = 'store_true', 	default = False )
	gap.add_argument( '-p', 	'--print', 		action = 'store_true', 	default = False, 	dest = "printcert" )
	gap.add_argument( '-v', 	'--verbose', 	action = 'count', 		default = 0 )
	gap = ap.add_argument_group( 'save options' )
	gap.add_argument( '-d', 	'--directory', 	action = 'store', 		dest = "directory", 	metavar = "<target directory>" )
	gap.add_argument( '-s', 	'--save', 		action = 'store_true', 	default = False )
	gap = ap.add_argument_group( 'search options' )
	gap.add_argument( '--case-sensitive', 	action = 'store_false', dest = "case" )
	gap.add_argument( '-x', 	'--exclude', 	action = 'store', 		dest = "exclude", 	metavar = "<exclude pattern>" )

	ProgArgs										 = ap.parse_args()
	initLog( ProgArgs.loglevel )
	Logger											 = logging.getLogger( __name__ )

	if ( ProgArgs.file is None ):
		Logger.error( "Must use -f argument." )
		sys.exit( 1 )

	return True
###------------------------------------------------------------------------------------------------------------------------------
def optparser():
	import optparse
	global ProgArgs

	op = optparse.OptionParser()
	op.add_option( '-f', 	'--file', 			dest = 'file', 			help = 'Input File', 	metavar = "<input file>" )
	op.add_option( '--dryrun', 			dest = 'dryrun', 		action = 'store_true', 	default = False )
	op.add_option( '--debug', 			action = 'store_true' )
	op.add_option( '--loglevel', 		action = 'store', 		dest = 'loglevel', 	metavar = "<log level>", 	default = 'info', 	choices = ['crit', 'error', 'warn', 'notice', 'info', 'verbose', 'debug', 'insane'] )
	op.add_option( '--logfile', 		action = 'store', 		dest = 'logfile', 	metavar = "<logfile>" )
	op.add_option( '-l', 	'--list', 			action = 'store_true', 	dest = 'list', 		default = False )
	op.add_option( '-p', 	'--print', 			action = 'store_true', 	dest = 'printcert', 	default = False )
	op.add_option( '-v', 	'--verbose', 		action = 'count', 		dest = 'verbose', 	default = 0 )
	op.add_option( '-d', 	'--directory', 		action = 'store', 		dest = 'directory', 	metavar = "<target directory>" )
	op.add_option( '-s', 	'--save', 			action = 'store_true', 	default = False )
	op.add_option( '-c', 	'--case-sensitive', 	action = 'store_false', dest = 'case', 		default = False )
	op.add_option( '-x', 	'--exclude', 		action = 'store', 		dest = 'exclude', 	metavar = "<exclude pattern>" )

	ProgArgs, args									 = op.parse_args()
	print( ProgArgs )
	print( args )
	# sys.exit(1)
	initLog( ProgArgs.loglevel )
	Logger											 = logging.getLogger( __name__ )

	if ( ProgArgs.file is None ):
		Logger.error( "Must use -f argument." )
		sys.exit( 1 )
	Logger											 = logging.getLogger( __name__ )

	return True
###------------------------------------------------------------------------------------------------------------------------------
def initLog( LLevel ):
	Logger											 = logging.getLogger( __name__ )

	LogLevels = {'crit':logging.CRITICAL,
				'error':logging.ERROR,
				'warn':logging.WARNING,
				'info':logging.INFO,
				'debug':logging.DEBUG }
	LogLevel										 = LogLevels.get( LLevel, logging.NOTSET )
	Logger.setLevel( LogLevel )

	if sys.version_info > ( 2, 6, 0 ):
		LogFormat										 = '(%(asctime)-11s)  :%(levelname)-9s:%(funcName)-13s:%(message)s'
	else:
		LogFormat										 = '(%(asctime)-11s)  :%(levelname)-9s:%(message)s'

	# print( sys.version_info )
	if ( len( Logger.handlers ) == 0 ):
		LogHandler	 = logging.StreamHandler()
		# try:
		# 	Colorize								= __import__( 'logutils.colorize', fromlist=['colorize'] )
		# 	LogHandler								= Colorize.ColorizingStreamHandler()
		# 	LogHandler.level_map[logging.DEBUG]		= (None, 'blue', False)
		# 	LogHandler.level_map[logging.INFO]		= (None, 'green', False)
		# 	LogHandler.level_map[logging.WARNING]	= (None, 'yellow', False)
		# 	LogHandler.level_map[logging.ERROR]		= (None, 'red', False)
		# 	LogHandler.level_map[logging.CRITICAL]	= ('red', 'white', False)
		# except ImportError:
		# 	LogHandler	= logging.StreamHandler()
	else:
		LogHandler	 = logging.StreamHandler()
	LogHandler.setFormatter( logging.Formatter( LogFormat, datefmt = '%I:%M:%S %p' ) )

	Logger.addHandler( LogHandler )
###------------------------------------------------------------------------------------------------------------------------------
def checkdir( Directory ):
	Success											 = False
	if not os.path.isdir( os.path.abspath( Directory ) ):
		if ( not ProgArgs.dryrun ):
			try:
				os.mkdir( os.path.abspath( Directory ) )
			except:
				Success								 = False
			else:
				Success								 = True
	return Success
###------------------------------------------------------------------------------------------------------------------------------
def checkfile( InputFile ):
	Success											 = False
	if os.path.isfile( InputFile ):
		Success										 = True
	return Success
###------------------------------------------------------------------------------------------------------------------------------
def p7bImport( InputFile ):
	Logger											 = logging.getLogger( __name__ )

	# Import a p7b file into a raw glob of certificate data and return the data
	Command											 = ( "openssl pkcs7 -print_certs -in %s" % ( InputFile ) )
	if ProgArgs.verbose >= 3:
		Logger.debug( "Loading data from pkcs7 file:\t%s" % ( InputFile ) )
	Pipe											 = subprocess.Popen( Command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True )
	RawData, StdErr									 = Pipe.communicate()
	SplitData										 = RawData.split( "\n" )

	return SplitData
###------------------------------------------------------------------------------------------------------------------------------
def handleCerts( CertList ):
	# Certificate List handler responsible for performing command line actions (list, print, save, etc.)
	Logger											 = logging.getLogger( __name__ )

	for certificate in iter( CertList ):
		for part in iter( certificate ):
			if "subject=" in part:
				subject								 = re.sub( '/', ', ', part )
				subject								 = re.sub( '=, ', ' = ', subject )
				if ProgArgs.verbose >= 3:
					Logger.debug( "Certificate Subject:\t%s" % ( subject ) )
			elif "issuer=" in part:
				issuer								 = re.sub( '/', ', ', part )
				issuer								 = re.sub( '=, ', ' = ', issuer )
				if ProgArgs.verbose >= 3:
					Logger.debug( "  Certificate Issuer:\t%s" % ( issuer ) )
			else:
				data								 = part
				if ProgArgs.verbose >= 4:
					Logger.debug( "  Certificate Data:\t%s" % ( data ) )

		if ProgArgs.exclude:
			if ProgArgs.case:
				Match								 = re.search( "%s" % ProgArgs.exclude, subject, flags = re.IGNORECASE )
			else:
				Match								 = re.search( "%s" % ProgArgs.exclude, subject )
			if not Match:
				if ProgArgs.list:
					print( "Certificate %s" % ( subject ) )
				if ProgArgs.printcert:
					printCert( certificate )
				if ProgArgs.save:
					saveCert( certificate )
		else:
			if ProgArgs.list:
				print( "Certificate %s" % ( subject ) )
			if ProgArgs.printcert:
				printCert( certificate )
			if ProgArgs.save:
				saveCert( certificate )
###------------------------------------------------------------------------------------------------------------------------------
def saveCert( certificate ):
	# Save the certificate out to a file.
	Logger											 = logging.getLogger( __name__ )

	for part in iter( certificate ):
		if "subject=" in part:
			subject									 = re.sub( '^(.*)=', '', part )
		elif "issuer=" in part:
			issuer									 = re.sub( '^(.*)=', '', part )
		else:
			data									 = part

	outfile											 = re.sub( ' ', '-', subject )
	outfile											 = ''.join( [ outfile, '.crt' ] )

	if ProgArgs.directory:
		filepath									 = os.path.join( ProgArgs.directory, outfile )
	else:
		filepath									 = os.path.join( os.getcwd(), outfile )

	if not ProgArgs.dryrun:
		Logger.info( "Writing file: %s" % ( filepath ) )

		# if sys.version_info > (2, 6, 0):
		# 	try:
		# 		with open( filepath, 'wb' ) as OutFile:
		# 			OutFile.write( data )
		# 	except:
		# 		WroteFile							= False
		# 	else:
		# 		OutFile.close()
		# 		WroteFile							= True
		# else:
		OutFile									 = open( filepath, "wb" )
		try:
			OutFile.write( data )
		except:
			WroteFile							 = False
		else:
			WroteFile							 = True
			OutFile.close()

	else:
		Logger.info( "Writing file: %s" % ( filepath ) )

	return WroteFile
###------------------------------------------------------------------------------------------------------------------------------
def printCert( certificate ):
	# Print just the certificate data
	Logger											 = logging.getLogger( __name__ )

	for part in iter( certificate ):
		if "subject=" in part:
			subject									 = re.sub( '/', ', ', part )
			subject									 = re.sub( '=, ', ' = ', subject )
		elif "issuer=" in part:
			issuer									 = re.sub( '/', ', ', part )
			issuer									 = re.sub( '=, ', ' = ', issuer )
		else:
			data									 = part
	print( data )
###------------------------------------------------------------------------------------------------------------------------------
def splitCerts( certglob ):
	# Split the raw certificate data into individual certificates and return a list of certificates
	Logger											 = logging.getLogger( __name__ )

	CertList										 = []
	insideCert										 = False

	certdata										 = ''
	for line in iter( certglob ):
		if "subject=" in line.strip():
			insideCert								 = False
			certsubject								 = line
			if ProgArgs.verbose > 1:
				Logger.debug( "Certificate Subject: %s" % ( certsubject ) )
		elif "issuer=" in line.strip():
			insideCert								 = False
			certissuer								 = line
			if ProgArgs.verbose > 1:
				Logger.debug( "Certificate Issuer: %s" % ( certsubject ) )
		elif "-----BEGIN CERTIFICATE-----" in line.strip():
			insideCert								 = True
			line									 = ''.join( [ line, '\n' ] )
			certdata								 = ''.join( [ certdata, line ] )
		elif "-----END CERTIFICATE-----" in line.strip():
			insideCert								 = False
			line									 = ''.join( [ line, '\n' ] )
			certdata								 = ''.join( [ certdata, line ] )
			certificate								 = [ certsubject, certissuer, certdata ]
			CertList.append( certificate )
			certdata								 = ''
		elif insideCert:
			line									 = ''.join( [ line, '\n' ] )
			certdata								 = ''.join( [ certdata, line ] )

	return CertList
###------------------------------------------------------------------------------------------------------------------------------
def main():
	Logger											 = logging.getLogger( __name__ )
	#--- Parse program arguments ----------------------------------------------------------------------------
	try:
		success										 = argparser()
	except:
		success										 = optparser()

	if ( not success ):
		Logger.error( "Error: Problem parsing arguments." )
		sys.exit( 1 )

	if ProgArgs.directory:
		ProgArgs.directory							 = os.path.abspath( ProgArgs.directory )
		checkdir( ProgArgs.directory )

	if checkfile( ProgArgs.file ):
		CertData									 = p7bImport( ProgArgs.file )

	CertList										 = splitCerts( CertData )
	handleCerts( CertList )

	return success
###------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	main()
###------------------------------------------------------------------------------------------------------------------------------
