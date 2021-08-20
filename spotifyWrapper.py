import json, requests
from pathlib import Path
from PIL import ImageTk, Image

import spotipy
from spotipy.oauth2 import SpotifyPKCE


class SpotifyWrapper:
	prefix = 'arkhes:'
	resource_type = 'arkhes'

	scope = 'user-library-read user-modify-playback-state user-read-playback-state user-library-modify'

	cache_file_name = 'cache.json'

	def __init__(self) -> None:
		self.spotify = spotipy.Spotify(auth_manager=SpotifyPKCE(scope=self.scope, client_id='17c952718daa4eaebc2ccf096036a42f',
			redirect_uri='http://localhost:8080'))
		
		self.categorizations = {}
		self.load_cache()
	
	def add_categorized_album(self, uri):
		if uri not in self.categorizations:
			self.categorizations[uri] = 1
			self.set_uncategorized_albums()
		else:
			self.categorizations[uri] += 1
	
	def remove_categorized_album(self, album):
		if album['type'] == 'album' and album['uri'] in self.categorizations:
			self.categorizations[album['uri']] -= 1
			if self.categorizations[album['uri']] <= 0:
				del self.categorizations[album['uri']]
				self.set_uncategorized_albums()
	
	def set_uncategorized_albums(self):
		self.uncategorized_albums = [album for album in self.saved_albums_cache if album['uri'] not in self.categorizations]

	def load_saved_albums(self):
		while True:
			new_albums = self.spotify.current_user_saved_albums(limit=50, offset=len(self.saved_albums_cache))['items']
			if len(new_albums) == 0:
				break
			self.saved_albums_cache.extend([album['album'] for album in new_albums])
		
		self.set_uncategorized_albums()
		
	def save_dict(self):
		return {'categorizations' : self.categorizations}
	
	def load_from(self, dct):
		self.categorizations = dct['categorizations']
		self.set_uncategorized_albums()

	def load_cache(self):
		self.saved_albums_cache = []
		self.resource_cache = {}

		if Path(self.cache_file_name).is_file():
			dct = None
			with open(self.cache_file_name, 'r') as f:
				dct = json.loads(f.readline())
			self.resource_cache = dct['resource_cache']
			self.saved_albums_cache = dct['saved_albums_cache']
			self.set_uncategorized_albums()
		else:
			self.load_saved_albums()
	
	def save_cache(self):
		with open(self.cache_file_name, 'w') as f:
			f.write(json.dumps({'resource_cache' : self.resource_cache, 'saved_albums_cache' : self.saved_albums_cache}))
	
	def reload_saved_album_cache(self):
		self.saved_albums_cache = []
		self.load_saved_albums()

	def clear_cache(self):
		self.reload_saved_album_cache()
		self.resource_cache = {}


	def get_device_id(self):
		# TODO: Cache and only update occasionally; Handle better in general (= let user choose device)
		devices = self.spotify.devices()['devices']
		for device in devices:
			if device['is_active']:
				return None
		return devices[0]['id']

	def cache_albums(self, uris):
		if len(uris) > 0:
			new_albums = self.spotify.albums(uris)
			for uri, album in zip(uris, new_albums['albums']):
				self.resource_cache[uri] = album

	def cache_songs(self, uris):
		if len(uris) > 0:
			new_songs = self.spotify.tracks(uris)
			for uri, song in zip(uris, new_songs['tracks']):
				self.resource_cache[uri] = song

	def cache_spotify_playlists(self, uris):
		if len(uris) > 0:
			for uri in uris:
				playlist = self.spotify.playlist(uri)
				self.resource_cache[uri] = playlist

	def is_album(uri):
		return uri.startswith('https://open.spotify.com/album/') or uri.startswith('spotify:album')

	def is_song(uri):
		return uri.startswith('https://open.spotify.com/track/') or uri.startswith('spotify:track')

	def is_spotify_playlist(uri):
		return uri.startswith('https://open.spotify.com/playlist/') or uri.startswith('spotify:playlist')

	def is_arkhes_playlist(uri):
		return uri.startswith(SpotifyWrapper.prefix)

	def cache_uncached_albums(self, uris):
		uncached = []
		for uri in uris:
			if SpotifyWrapper.is_album(uri) and not uri in self.resource_cache:
				uncached.append(uri)
		self.cache_albums(uncached)
	
	def get_resource(self, uri):
		if not uri in self.resource_cache:
			if SpotifyWrapper.is_album(uri):
				self.cache_albums([uri])
			elif SpotifyWrapper.is_song(uri):
				self.cache_songs([uri])
			elif SpotifyWrapper.is_spotify_playlist(uri):
				self.cache_spotify_playlists([uri])
			elif SpotifyWrapper.is_arkhes_playlist(uri):
				return {'name' : uri[len(self.prefix):].strip(), 'type' : self.resource_type, 'uri' : uri}
			else:
				return []
		return self.resource_cache[uri]
	
	def play_uris(self, uris):
		if len(uris) > 750:
			uris = uris[:750] # Prevent "Request Entity Too Large"
		self.spotify.start_playback(device_id=self.get_device_id(), uris=uris)
	
	def go_back_track(self):
		self.spotify.previous_track(device_id=self.get_device_id())

	def go_forward_track(self):
		self.spotify.next_track(device_id=self.get_device_id())
	
	def toggle_pause(self):
		if self.spotify.current_playback()['is_playing']:
			self.spotify.pause_playback(device_id=self.get_device_id())
		else:
			self.spotify.start_playback(device_id=self.get_device_id())
	
	def saved_albums(self, categorization_mode):
		if categorization_mode:
			return self.uncategorized_albums
		else:
			return self.saved_albums_cache
	
	def shuffle(self, shouldShuffle):
		self.spotify.shuffle(shouldShuffle, device_id=self.get_device_id())
	
	def play(self, uri):
		if SpotifyWrapper.is_album(uri) or SpotifyWrapper.is_spotify_playlist(uri):
			self.spotify.start_playback(context_uri=uri, device_id=self.get_device_id())
		else:
			self.play_uris([uri])
	
	def set_volume(self, volume):
		self.spotify.volume(int(volume), device_id=self.get_device_id())
	
	def set_track_progress(self, progress):
		self.spotify.seek_track(int(progress), device_id=self.get_device_id())
	
	def remove_saved_album(self, uri):
		self.spotify.current_user_saved_albums_delete([uri])
		self.saved_albums_cache = [i for i in self.saved_albums_cache if i['uri'] != uri]
		self.uncategorized_albums = [i for i in self.uncategorized_albums if i['uri'] != uri]
	
	def get_current_playback(self):
		return self.spotify.current_playback()
	
	def get_album_cover(self, album, size):
		path = 'cover_cache/%s.jpg' % album['id']

		if not Path(path).is_file():
			url = album['images'][0]['url']
			with open(path, 'wb') as file:
				file.write(requests.get(url).content)

		return self.get_image(path, size)
	
	def get_image(self, path, size):
		return ImageTk.PhotoImage(Image.open(path).resize([size, size]))


spotify_wrapper = SpotifyWrapper()
