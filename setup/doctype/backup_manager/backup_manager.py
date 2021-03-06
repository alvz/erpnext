# For license information, please see license.txt

from __future__ import unicode_literals
import webnotes
from webnotes import _

class DocType:
	def __init__(self, d, dl):
		self.doc, self.doclist = d, dl

def take_backups_daily():
	take_backups_if("Daily")

def take_backups_weekly():
	take_backups_if("Weekly")

def take_backups_if(freq):
	if webnotes.conn.get_value("Backup Manager", None, "upload_backups_to_dropbox")==freq:
		take_backups()

@webnotes.whitelist()
def take_backups():
	try:
		from setup.doctype.backup_manager.backup_dropbox import backup_to_dropbox
		backup_to_dropbox()
		send_email(True, "Dropbox")
	except Exception, e:
		send_email(False, "Dropbox", e)

def send_email(success, service_name, error_status=None):
	if success:
		subject = "Backup Upload Successful"
		message ="""<h3>Backup Uploaded Successfully</h3><p>Hi there, this is just to inform you 
		that your backup was successfully uploaded to your %s account. So relax!</p>
		""" % service_name

	else:
		subject = "[Warning] Backup Upload Failed"
		message ="""<h3>Backup Upload Failed</h3><p>Oops, your automated backup to %s
		failed.</p>
		<p>Error message: %s</p>
		<p>Please contact your system manager for more information.</p>
		""" % (service_name, error_status)
	
	# email system managers
	from webnotes.utils.email_lib import sendmail
	sendmail(webnotes.conn.get_value("Backup Manager", None, "send_notifications_to").split(","), 
		subject=subject, msg=message)
