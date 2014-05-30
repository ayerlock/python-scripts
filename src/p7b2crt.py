#!/usr/bin/python
# coding: utf-8
###--- Module Imports -----------------------------------------------------------------------------------------------------------
import	os, re, sys
import	logging, logging.handlers
import	subprocess
###------------------------------------------------------------------------------------------------------------------------------
def argparser():
	import argparse
	global ProgArgs
	
	ap = argparse.ArgumentParser( description = 'A web image grabber.', prog = os.path.basename(re.sub(".py", "", sys.argv[0])) )
	ap.add_argument( '-f',	'--file',		action = 'store',		dest = "file",		metavar = "<input file>" )
	gap = ap.add_argument_group( 'standard functionality' )
	gap.add_argument(		'--dryrun',		action = 'store_true' )
	gap.add_argument(		'--program',	action = 'store',		dest = "prog",		metavar = "prog",		default = os.path.basename(re.sub(".py", "", sys.argv[0])))
	gap.add_argument( 		'--version',	action = 'version',		version = '%(prog)s 0.1' )
	gap = ap.add_argument_group( 'output options' )
	gap.add_argument(		'--debug',		action = 'store_true' )
	gap.add_argument( 		'--loglevel',	action = 'store',		dest = "loglevel",	metavar = "<log level>",	default = 'info',	choices = ['crit', 'error', 'warn', 'notice', 'info', 'verbose', 'debug', 'insane'] )
	gap.add_argument(		'--logfile',	action = 'store',		dest = "logfile",	metavar = "<logfile>" )
	gap.add_argument( '-l',	'--list',		action = 'store_true',	default = False )
	gap.add_argument( '-p',	'--print',		action = 'store_true',	default = False,	dest = "printcert" )
	gap.add_argument( '-v',	'--verbose',	action = 'count',		default = 0 )
	gap = ap.add_argument_group( 'save options' )
	gap.add_argument( '-d',	'--directory',	action = 'store',		dest = "directory",	metavar = "<target directory>" )
	gap.add_argument( '-s',	'--save',		action = 'store_true',	default = False )
	gap = ap.add_argument_group( 'search options' )
	gap.add_argument( 		'--case-sensitive',	action = 'store_false', dest = "case" )
	gap.add_argument( '-x',	'--exclude',	action = 'store',		dest = "exclude",	metavar = "<exclude pattern>" )

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
def checkdir( directory ):
	if not os.path.isdir( ProgArgs.directory ):
		if ( not ProgArgs.dryrun ):
			os.mkdir( ProgArgs.directory )
###------------------------------------------------------------------------------------------------------------------------------
def checkfile( file ):
	isfile											= False
	if os.path.isfile( file ):
		isfile										= True
	return isfile
###------------------------------------------------------------------------------------------------------------------------------
def p7bImport( file ):
	# Import a p7b file into a raw glob of certificate data and return the data
	Command											= ( "openssl pkcs7 -print_certs -in %s" % ( file ) )
	Pipe											= subprocess.Popen( Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True )
	RawData, StdErr									= Pipe.communicate()
	SplitData										= RawData.split( "\n" )
	return SplitData
###------------------------------------------------------------------------------------------------------------------------------
def handleCerts( CertList ):
	# Certificate List handler responsible for performing command line actions (list, print, save, etc.)
	Logger											= logging.getLogger( __name__ )
	
	for certificate in iter( CertList ):
		for part in iter( certificate ):
			if "subject=" in part:
				subject									= re.sub( '/', ', ', part )
				subject									= re.sub( '=, ', ' = ', subject )
			elif "issuer=" in part: 
				issuer									= re.sub( '/', ', ', part )
				issuer									= re.sub( '=, ', ' = ', issuer )
			else:
				data									= part
			
		if ProgArgs.exclude:
			if ProgArgs.case:
				Match									= re.search( "%s" % ProgArgs.exclude, subject, flags=re.IGNORECASE )	
			else:
				Match									= re.search( "%s" % ProgArgs.exclude, subject )	
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
	Logger											= logging.getLogger( __name__ )
	
	for part in iter( certificate ):
		if "subject=" in part:
			subject									= re.sub( '^(.*)=', '', part )
		elif "issuer=" in part: 
			issuer									= re.sub( '^(.*)=', '', part )
		else:
			data									= part
			
	file											= re.sub( ' ', '-', subject )
	file											= ''.join( [ file, '.crt' ] )
	
	if ProgArgs.directory:
		filepath									= os.path.join( ProgArgs.directory, file )
	else:
		filepath									= os.path.join( os.getcwd(), file )
		
	if not ProgArgs.dryrun:
		Logger.info( "Writing file: %s" % ( filepath ) )
		try:
			with open( filepath, 'wb' ) as File:
				File.write( data )
		except:
			WroteFile						= False
		else:
			File.close()
			WroteFile						= True
	else:
		Logger.info( "Writing file: %s" % ( filepath ) )
###------------------------------------------------------------------------------------------------------------------------------
def printCert( certificate ):
	# Print just the certificate data
	Logger											= logging.getLogger( __name__ )
	
	for part in iter( certificate ):
		if "subject=" in part:
			subject									= re.sub( '/', ', ', part )
			subject									= re.sub( '=, ', ' = ', subject )
		elif "issuer=" in part: 
			issuer									= re.sub( '/', ', ', part )
			issuer									= re.sub( '=, ', ' = ', issuer )
		else:
			data									= part
	print( data )
###------------------------------------------------------------------------------------------------------------------------------
def splitCerts( certglob ):
	# Split the raw certificate data into individual certificates and return a list of certificates
	Logger											= logging.getLogger( __name__ )
	
	CertList										= []
	insideCert										= False
	
	certdata											= ''
	for line in iter( certglob ):
		if "subject=" in line.strip():
			insideCert								= False
			certsubject								= line
			if ProgArgs.verbose > 1:
				Logger.debug( "Certificate Subject: %s" % ( certsubject ) )
		elif "issuer=" in line.strip():
			insideCert								= False
			certissuer								= line
			if ProgArgs.verbose > 1:
				Logger.debug( "Certificate Issuer: %s" % ( certsubject ) )
		elif "-----BEGIN CERTIFICATE-----" in line.strip():
			insideCert								= True
			line									= ''.join( [ line, '\n' ] )
			certdata								= ''.join( [ certdata, line ] )
		elif "-----END CERTIFICATE-----" in line.strip():
			insideCert								= False
			line									= ''.join( [ line, '\n' ] )
			certdata								= ''.join( [ certdata, line ] )
			certificate								= [ certsubject, certissuer, certdata ]
			CertList.append( certificate )
			certdata								= ''
		elif insideCert:
			line									= ''.join( [ line, '\n' ] )
			certdata								= ''.join( [ certdata, line ] )
		
	return CertList
###------------------------------------------------------------------------------------------------------------------------------
def main():
	Logger											= logging.getLogger( __name__ )
	#--- Parse program arguments ----------------------------------------------------------------------------
	success											= argparser()
	if ( not success ):
		logger.error("Error: Problem parsing arguments.")
		sys.exit(1)
		
	if ProgArgs.directory:
		ProgArgs.directory							= os.path.abspath( ProgArgs.directory )
		checkdir( ProgArgs.directory )
		
	if checkfile( ProgArgs.file ):
		CertData									= p7bImport( ProgArgs.file )
	
	CertList										= splitCerts( CertData )
	handleCerts( CertList )
	
	return success
###------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	main()
###------------------------------------------------------------------------------------------------------------------------------