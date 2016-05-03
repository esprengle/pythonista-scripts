# coding: utf-8
'''Creates a zip archive of your Pythonista files and uploads it to S3.'''

from __future__ import print_function

import os
import shutil
import tempfile
import console
import time
import boto
from boto.s3.key import Key
from objc_util import NSBundle
import sys
import keychain
import ui
#from reprint_line import reprint

console.clear()


@ui.in_background
def perform_backup(quiet=True):
	try:
		from urllib2 import urlopen
	except:
		try:
			from urllib.request import urlopen
		except:
			pass
	try:
		urlopen('http://s3.amazonaws.com')
	except:
		if quiet:
			return
		else:
			sys.exit('ERROR: Unable to connect to s3.amazonaws.com')
	doc_path = os.path.expanduser('~/Documents')
	os.chdir(doc_path)
	backup_path = os.path.join(doc_path, 'Backup.zip')
	if os.path.exists(backup_path):
		os.remove(backup_path)
	print('Creating backup archive...')
	shutil.make_archive(os.path.join(tempfile.gettempdir(), 'Backup'), 'zip')
	shutil.move(os.path.join(tempfile.gettempdir(), 'Backup.zip'), backup_path)
	print('Backup archive created, uploading to S3 ...')
	
	date_text = time.strftime('%Y-%b-%d')
	time_text = time.strftime('%I-%M-%S-%p')
	info_dict_version_key = 'CFBundleShortVersionString'
	main_bundle = NSBundle.mainBundle()
	app_version = str(main_bundle.objectForInfoDictionaryKey_(info_dict_version_key))[0]
	
	AWS_ACCESS_KEY_ID = keychain.get_password('aws', 'AWS_ACCESS_KEY_ID')
	AWS_SECRET_ACCESS_KEY = keychain.get_password('aws', 'AWS_SECRET_ACCESS_KEY')
	
	bucket_name = 'lukaskollmer'
	
	def percent_cb(complete, total):
		progress = (str(round(((float(complete) / float(total)) * 100), 2)) + ' %')
		progress_string = '{}'.format(progress)
		print(progress_string)
		#reprint(progress_string)
	
	s3 = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
	bucket = s3.get_bucket(bucket_name)
	
	filename = 'Backup-{}.zip'.format(time_text)
	k = Key(bucket)
	k.storage_class = 'REDUCED_REDUNDANCY'
	k.key = '/Backup/Pythonista{}/{}/{}'.format(app_version, date_text, filename)
	print('0.0 %')
	k.set_contents_from_filename('Backup.zip', cb=percent_cb, num_cb=10)
	print('Successfully uploaded')
	os.remove(backup_path)

if __name__ == '__main__':
	perform_backup(quiet=False)