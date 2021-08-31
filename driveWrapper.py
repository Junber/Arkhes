import json
import os, shutil
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

class DriveWrapper:
	SCOPES = ['https://www.googleapis.com/auth/drive.appdata']

	def __init__(self):
		self.auth()

	def auth(self):
		creds = None
		# The file token.json stores the user's access and refresh tokens, and is
		# created automatically when the authorization flow completes for the first
		# time.
		if os.path.exists('driveToken.json'):
			with open('driveToken.json', 'r') as stream:
				creds_json = json.load(stream)
			creds = Credentials.from_authorized_user_info(creds_json)
			# workaround for
			# https://github.com/googleapis/google-auth-library-python/issues/501
			creds.token = creds_json['token']
		# If there are no (valid) credentials available, let the user log in.
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(
					'credentials.json', self.SCOPES)
				creds = flow.run_local_server(port=0)
			# Save the credentials for the next run
			with open('driveToken.json', 'w') as token:
				token.write(creds.to_json())

		self.service = build('drive', 'v3', credentials=creds)

	def upload_file(self, name):
		file_metadata = {
			'name': name,
			'parents': ['appDataFolder']
		}
		media = MediaFileUpload(name,resumable=True)
		
		for oldFile in self.get_files():
			if oldFile['name'] == name:
				self.service.files().update(fileId = oldFile['id'], media_body = media).execute()
				return

		self.service.files().create(body = file_metadata, media_body = media).execute()
	
	def get_files(self):
		response = self.service.files().list(spaces='appDataFolder',
												fields='nextPageToken, files(id, name)',
												pageSize=10).execute()
		return response.get('files', [])
	
	def download_file(self, path, id):
		request = self.service.files().get_media(fileId=id)
		with open(path, 'wb') as file:
			downloader = MediaIoBaseDownload(file, request)
			done = False
			while done is False:
				status, done = downloader.next_chunk()
				print("Download {} {}%.".format(path, int(status.progress() * 100)))
	
	def download_all(self, path):
		for file in self.get_files():
			self.download_file(os.path.join(path, file['name']), file['id'])
	
	def delete_all(self):
		for file in self.get_files():
			self.service.files().delete(fileId = file['id']).execute()

if __name__ == '__main__':
	d = DriveWrapper()
	d.upload_file('save.json')
	shutil.make_archive('playlists', 'zip', 'playlists')
	d.upload_file('playlists.zip')
	os.makedirs('test/playlists', exist_ok=True)
	d.download_all('test')
	shutil.unpack_archive('test/playlists.zip', 'test/playlists', 'zip')