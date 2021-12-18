import json
import os
import shutil
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

class DriveWrapper:
	SCOPES = ['https://www.googleapis.com/auth/drive.appdata']

	def __init__(self):
		self.auth()

	def auth(self):
		credentials = None
		# The file token.json stores the user's access and refresh tokens, and is
		# created automatically when the authorization flow completes for the first
		# time.
		if os.path.exists('driveToken.json'):
			with open('driveToken.json', 'r', encoding='utf8') as file:
				credentails_json = json.load(file)
			credentials = Credentials.from_authorized_user_info(credentails_json)
			# workaround for
			# https://github.com/googleapis/google-auth-library-python/issues/501
			credentials.token = credentails_json['token']
		# If there are no (valid) credentials available, let the user log in.
		if not credentials or not credentials.valid:
			if credentials and credentials.expired and credentials.refresh_token:
				credentials.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(
					'credentials.json', self.SCOPES)
				credentials = flow.run_local_server(port=0)
			# Save the credentials for the next run
			with open('driveToken.json', 'w', encoding='utf8') as token:
				token.write(credentials.to_json())

		self.service = build('drive', 'v3', credentials=credentials)

	def file_service(self):
		return self.service.files() # pylint: disable=maybe-no-member

	def upload_file(self, name):
		file_metadata = {
			'name': name,
			'parents': ['appDataFolder']
		}
		media = MediaFileUpload(name,resumable=True)

		for old_file in self.get_files():
			if old_file['name'] == name:
				self.file_service().update(fileId = old_file['id'], media_body = media).execute()
				return

		self.file_service().create(body = file_metadata, media_body = media).execute()

	def get_files(self):
		response = self.file_service().list(spaces='appDataFolder',
												fields='nextPageToken, files(id, name)',
												pageSize=10).execute()
		return response.get('files', [])

	def download_file(self, path, file_id):
		request = self.file_service().get_media(fileId=file_id)
		with open(path, 'wb') as file:
			downloader = MediaIoBaseDownload(file, request)
			done = False
			while done is False:
				status, done = downloader.next_chunk()
				print(f"Download {path} {int(status.progress() * 100)}%.")

	def download_all(self, path):
		for file in self.get_files():
			self.download_file(os.path.join(path, file['name']), file['id'])

	def delete_all(self):
		for file in self.get_files():
			self.file_service().delete(fileId = file['id']).execute()

if __name__ == '__main__':
	d = DriveWrapper()
	d.upload_file('save.json')
	shutil.make_archive('playlists', 'zip', 'playlists')
	d.upload_file('playlists.zip')
	os.makedirs('test/playlists', exist_ok=True)
	d.download_all('test')
	shutil.unpack_archive('test/playlists.zip', 'test/playlists', 'zip')
