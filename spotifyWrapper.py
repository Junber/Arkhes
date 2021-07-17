import json
import spotipy
from spotipy.oauth2 import SpotifyPKCE
import json
from pathlib import Path
import math


class SpotifyWrapper:
	prefix = 'cool:'
	resource_type = 'cool'

	scope = 'user-library-read user-modify-playback-state user-read-playback-state user-library-modify'

	cache_file_name = 'cache.json'

	SAVED_ALBUM_PAGE_LIMIT = 20

	def __init__(self) -> None:
		self.spotify = spotipy.Spotify(auth_manager=SpotifyPKCE(scope=self.scope, client_id='17c952718daa4eaebc2ccf096036a42f',
			redirect_uri='http://localhost:8080'))
		
		self.categorizations = {}
		self.load_cache()
	
	def add_categorized_album(self, album):
		if album['uri'] not in self.categorizations:
			self.categorizations[album['uri']] = 1
			self.set_uncategorized_albums()
		else:
			self.categorizations[album['uri']] += 1
	
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
		self.album_cache = {}

		if Path(self.cache_file_name).is_file():
			dct = None
			with open(self.cache_file_name, 'r') as f:
				dct = json.loads(f.readline())
			self.album_cache = dct['album_cache']
			self.saved_albums_cache = dct['saved_albums_cache']
			self.set_uncategorized_albums()
		else:
			self.load_saved_albums()
	
	def save_cache(self):
		with open(self.cache_file_name, 'w') as f:
			f.write(json.dumps({'album_cache' : self.album_cache, 'saved_albums_cache' : self.saved_albums_cache}))
	
	def reload_saved_album_cache(self):
		self.saved_albums_cache = []
		self.load_saved_albums()

	def clear_cache(self):
		self.reload_saved_album_cache()
		self.album_cache = {}


	def get_device_id(self):
		devices = self.spotify.devices()['devices']
		for device in devices:
			if device['is_active']:
				return None
		return devices[0]['id']

	def cache_albums(self, uris):
		if len(uris) > 0:
			new_albums = self.spotify.albums(uris)
			for uri, album in zip(uris, new_albums['albums']):
				self.album_cache[uri] = album

	def is_album(uri):
		return uri.startswith('https://open.spotify.com/album/') or uri.startswith('spotify:album')

	def is_song(uri):
		return uri.startswith('https://open.spotify.com/track/') or uri.startswith('spotify:track')

	def is_cool_playlist(uri):
		return uri.startswith(SpotifyWrapper.prefix)

	def cache_uncached_albums(self, uris):
		uncached = []
		for uri in uris:
			if SpotifyWrapper.is_album(uri) and not uri in self.album_cache:
				uncached.append(uri)
		self.cache_albums(uncached)

	def get_album(self, uri):
		if not uri in self.album_cache:
			self.cache_albums([uri])
		return self.album_cache[uri]
	
	def get_resource(self, uri):
		if SpotifyWrapper.is_album(uri):
			return self.get_album(uri)
		elif SpotifyWrapper.is_song(uri):
			return self.spotify.track(uri)  # TODO: Cache and stuff
		elif SpotifyWrapper.is_cool_playlist(uri):
			return {'name' : uri[len(self.prefix):].strip(), 'type' : self.resource_type, 'uri' : uri}
		else:
			return []
	
	def play_uris(self, uris):
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
	
	def saved_albums(self, page, categorization_mode):
		if categorization_mode:
			return self.uncategorized_albums[self.SAVED_ALBUM_PAGE_LIMIT*page : self.SAVED_ALBUM_PAGE_LIMIT*(page+1)]
		else:
			return self.saved_albums_cache[self.SAVED_ALBUM_PAGE_LIMIT*page : self.SAVED_ALBUM_PAGE_LIMIT*(page+1)]
	
	def saved_album_pages(self, categorization_mode):
		if categorization_mode:
			return math.ceil(len(self.uncategorized_albums) / self.SAVED_ALBUM_PAGE_LIMIT)
		else:
			return math.ceil(len(self.saved_albums_cache) / self.SAVED_ALBUM_PAGE_LIMIT)
	
	def shuffle(self, shouldShuffle):
		self.spotify.shuffle(shouldShuffle, device_id=self.get_device_id())
	
	def play(self, uri):
		if SpotifyWrapper.is_album(uri):
			self.spotify.start_playback(context_uri=uri, device_id=self.get_device_id())
		else:
			self.spotify.start_playback(uris=[uri], device_id=self.get_device_id())
	
	def set_volume(self, volume):
		self.spotify.volume(volume, device_id=self.get_device_id())
	
	def set_track_progress(self, progress):
		self.spotify.seek_track(progress, device_id=self.get_device_id())
	
	def remove_saved_album(self, uri):
		self.spotify.current_user_saved_albums_delete([uri])
		self.saved_albums_cache = [i for i in self.saved_albums_cache if i['uri'] != uri]
		self.uncategorized_albums = [i for i in self.uncategorized_albums if i['uri'] != uri]
	
	# TODO: Spotify playlists as list items
	# TODO: Synching with normal spotify playlist


spotify_wrapper = SpotifyWrapper()
