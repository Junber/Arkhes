from __future__ import annotations
import os
import time
from pathlib import Path
import json
import requests
from PIL import ImageTk, Image

import spotipy
from spotipy.oauth2 import SpotifyPKCE

import resources

class SpotifyWrapper:
	prefix = 'arkhes:'
	resource_type = 'arkhes'

	scope = 'user-library-read user-modify-playback-state user-read-playback-state \
user-library-modify user-follow-read user-follow-modify user-read-private'

	cache_file_name = 'cache.json'

	cover_cache_location = 'cover_cache'

	def __init__(self):
		self.spotify = spotipy.Spotify(auth_manager=SpotifyPKCE(
			scope=self.scope,
			client_id='17c952718daa4eaebc2ccf096036a42f',
			redirect_uri='http://localhost:8080'))

		self.categorizations = {}

		self.resource_cache = {}
		self.saved_albums_cache = []
		self.saved_playlists_cache = []
		self.saved_songs_cache = []
		self.saved_artists_cache = []

		self.uncategorized_albums = []
		self.uncategorized_playlists = []
		self.uncategorized_songs = []
		self.uncategorized_artists = []

		self.current_country_code = self.spotify.me()['country']

	def add_categorized_uri(self, uri):
		if uri not in self.categorizations:
			self.categorizations[uri] = 1
			self.set_uncategorized_albums()
			self.set_uncategorized_playlists()
			self.set_uncategorized_songs()
			self.set_uncategorized_artists()
		else:
			self.categorizations[uri] += 1

	def remove_categorized_uri(self, uri):
		if uri in self.categorizations:
			self.categorizations[uri] -= 1
			if self.categorizations[uri] <= 0:
				del self.categorizations[uri]
				self.set_uncategorized_albums()
				self.set_uncategorized_playlists()
				self.set_uncategorized_songs()
				self.set_uncategorized_artists()

	def set_uncategorized_albums(self):
		self.uncategorized_albums = [album for album in self.saved_albums_cache if album.uri() not in self.categorizations]

	def set_uncategorized_playlists(self):
		self.uncategorized_playlists = [playlist for playlist in self.saved_playlists_cache if playlist.uri() not in self.categorizations]

	def set_uncategorized_songs(self):
		self.uncategorized_songs = [song for song in self.saved_songs_cache if song.uri() not in self.categorizations]

	def set_uncategorized_artists(self):
		self.uncategorized_artists = [artist for artist in self.saved_artists_cache if artist.uri() not in self.categorizations]

	def load_saved_albums(self):
		while True:
			new_albums = self.spotify.current_user_saved_albums(limit=50, offset=len(self.saved_albums_cache))['items']
			if len(new_albums) == 0:
				break
			self.saved_albums_cache.extend([resources.Album(album['album']) for album in new_albums])

		self.set_uncategorized_albums()

	def load_saved_playlists(self):
		while True:
			new_playlists = self.spotify.current_user_playlists(limit=50, offset=len(self.saved_playlists_cache))['items']
			if len(new_playlists) == 0:
				break
			self.saved_playlists_cache.extend([resources.SpotifyPlaylist(item) for item in new_playlists])

		self.set_uncategorized_playlists()

	def load_saved_songs(self):
		while True:
			new_songs = self.spotify.current_user_saved_tracks(limit=50, offset=len(self.saved_songs_cache))['items']
			if len(new_songs) == 0:
				break
			self.saved_songs_cache.extend([resources.Song(song['track']) for song in new_songs])

		self.set_uncategorized_songs()

	def load_saved_artists(self):
		while True:
			last_artist = None
			if len(self.saved_artists_cache) > 0:
				last_artist = self.saved_artists_cache[-1]

			new_artists = self.spotify.current_user_followed_artists(limit=50, after=last_artist)['artists']['items']

			if len(new_artists) == 0:
				break
			self.saved_artists_cache.extend([resources.Artist(item) for item in new_artists])

		self.set_uncategorized_artists()

	def save_dict(self):
		return {'categorizations' : self.categorizations}

	def load_from(self, dct):
		self.categorizations = dct['categorizations']
		self.set_uncategorized_albums()
		self.set_uncategorized_playlists()
		self.set_uncategorized_songs()
		self.set_uncategorized_artists()

	def load_cache(self):
		print('Loading cache...', end=' ')
		start_time = time.perf_counter()

		self.saved_albums_cache = []
		self.saved_playlists_cache = []
		self.saved_songs_cache = []
		self.saved_artists_cache = []
		self.resource_cache = {}

		if Path(self.cache_file_name).is_file():
			dct = None
			with open(self.cache_file_name, 'r', encoding='utf8') as file:
				dct = json.loads(file.readline())
			self.resource_cache = {uri : self.create_resource(item) for uri, item in dct['resource_cache'].items()}
			self.saved_albums_cache = [self.create_resource(item) for item in dct['saved_albums_cache']]
			self.saved_playlists_cache = [self.create_resource(item) for item in dct['saved_playlists_cache']]
			self.saved_songs_cache = [self.create_resource(item) for item in dct['saved_songs_cache']]
			self.saved_artists_cache = [self.create_resource(item) for item in dct['saved_artists_cache']]
			self.set_uncategorized_albums()
			self.set_uncategorized_playlists()
			self.set_uncategorized_songs()
			self.set_uncategorized_artists()
		else:
			self.load_saved_albums()
			self.load_saved_playlists()
			self.load_saved_songs()
			self.load_saved_artists()

		print('took ', round(time.perf_counter() - start_time, 2), 's', sep='')

	def save_cache(self):
		with open(self.cache_file_name, 'w', encoding='utf8') as file:
			file.write(json.dumps({
				'resource_cache' : {uri : item.to_json() for uri, item in self.resource_cache.items()},
				'saved_albums_cache' : [item.to_json() for item in self.saved_albums_cache],
				'saved_playlists_cache' : [item.to_json() for item in self.saved_playlists_cache],
				'saved_songs_cache' : [item.to_json() for item in self.saved_songs_cache],
				'saved_artists_cache' : [item.to_json() for item in self.saved_artists_cache],
				}))

	def reload_saved_albums_cache(self):
		self.saved_albums_cache = []
		self.load_saved_albums()

	def reload_saved_playlists_cache(self):
		self.saved_playlists_cache = []
		self.load_saved_playlists()

	def reload_saved_songs_cache(self):
		self.saved_songs_cache = []
		self.load_saved_songs()

	def reload_saved_artists_cache(self):
		self.saved_artists_cache = []
		self.load_saved_artists()

	def clear_cache(self):
		self.reload_saved_albums_cache()
		self.reload_saved_playlists_cache()
		self.reload_saved_songs_cache()
		self.reload_saved_artists_cache()
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
			step_size = 10 # TODO: Fine-tune value; do the same procedure for songs, etc
			for offset in range(0, len(uris), step_size):
				new_albums = self.spotify.albums(uris[offset : offset + step_size])
				for uri, album in zip(uris[offset : offset + step_size], new_albums['albums']):
					self.resource_cache[uri] = resources.Album(album)

	def cache_songs(self, uris):
		if len(uris) > 0:
			new_songs = self.spotify.tracks(uris)
			for uri, song in zip(uris, new_songs['tracks']):
				self.resource_cache[uri] = resources.Song(song)

	def cache_artists(self, uris):
		if len(uris) > 0:
			for uri in uris:
				artist = self.spotify.artist(uri)
				albums = []
				while True:
					new_albums = self.spotify.artist_albums(uri, country=self.current_country(), limit=50, offset=len(albums))['items']
					if len(new_albums) == 0:
						break
					albums.extend(new_albums)
				artist['albums'] = albums
				self.resource_cache[uri] = resources.Artist(artist)

	def cache_spotify_playlists(self, uris):
		if len(uris) > 0:
			for uri in uris:
				playlist = self.spotify.playlist(uri)
				self.resource_cache[uri] = resources.SpotifyPlaylist(playlist)

	@staticmethod
	def is_album_uri(uri: str) -> bool:
		return uri.startswith('https://open.spotify.com/album/') or uri.startswith('spotify:album:')

	@staticmethod
	def is_song_uri(uri: str) -> bool:
		return uri.startswith('https://open.spotify.com/track/') or uri.startswith('spotify:track:')

	@staticmethod
	def is_artist_uri(uri: str) -> bool:
		return uri.startswith('https://open.spotify.com/artist/') or uri.startswith('spotify:artist:')

	@staticmethod
	def is_spotify_playlist_uri(uri: str) -> bool:
		return uri.startswith('https://open.spotify.com/playlist/') or uri.startswith('spotify:playlist:')

	@staticmethod
	def is_arkhes_playlist_uri(uri: str) -> bool:
		return uri.startswith(SpotifyWrapper.prefix)

	def current_country(self) -> str: # TODO: Use more often or never probably
		return self.current_country_code

	def cache_uncached_albums(self, uris: list):  # TODO: Also do that for playlists, songs, etc
		uncached = []
		for uri in uris:
			if self.is_album_uri(uri) and not uri in self.resource_cache:
				uncached.append(uri)
		self.cache_albums(uncached)

	def get_resource(self, uri: str) -> resources.ArkhesResource:
		if not uri in self.resource_cache:
			if self.is_album_uri(uri):
				self.cache_albums([uri])
			elif self.is_song_uri(uri):
				self.cache_songs([uri])
			elif self.is_artist_uri(uri):
				self.cache_artists([uri])
			elif self.is_spotify_playlist_uri(uri):
				self.cache_spotify_playlists([uri])
			elif self.is_arkhes_playlist_uri(uri):
				return resources.ArkhesPlaylist({'name' : uri[len(self.prefix):].strip(), 'type' : self.resource_type, 'uri' : uri, 'popularity' : 0}) #TODO
			else:
				return resources.ArkhesResource({})

		return self.resource_cache[uri]

	def create_resource(self, dct: dict) -> resources.ArkhesResource:
		if self.is_album_uri(dct['uri']):
			return resources.Album(dct)
		elif self.is_song_uri(dct['uri']):
			return resources.Song(dct)
		elif self.is_artist_uri(dct['uri']):
			return resources.Artist(dct)
		elif self.is_spotify_playlist_uri(dct['uri']):
			return resources.SpotifyPlaylist(dct)
		elif self.is_arkhes_playlist_uri(dct['uri']):
			return resources.ArkhesPlaylist(dct)

	def play_uris(self, uris):
		if len(uris) > 750:
			uris = uris[:750] # Prevent 'Request Entity Too Large'
		self.spotify.start_playback(device_id=self.get_device_id(), uris=uris)

	def go_back_track(self):
		self.spotify.previous_track(device_id=self.get_device_id())

	def go_forward_track(self):
		self.spotify.next_track(device_id=self.get_device_id())

	def toggle_pause(self):
		playback = self.spotify.current_playback()
		if playback and playback['is_playing']:
			self.spotify.pause_playback(device_id=self.get_device_id())
		else:
			self.spotify.start_playback(device_id=self.get_device_id())

	def saved_albums(self, categorization_mode):
		if categorization_mode:
			return self.uncategorized_albums
		else:
			return self.saved_albums_cache

	def saved_playlists(self, categorization_mode):
		if categorization_mode:
			return self.uncategorized_playlists
		else:
			return self.saved_playlists_cache

	def saved_songs(self, categorization_mode):
		if categorization_mode:
			return self.uncategorized_songs
		else:
			return self.saved_songs_cache

	def saved_artists(self, categorization_mode):
		if categorization_mode:
			return self.uncategorized_artists
		else:
			return self.saved_artists_cache

	def shuffle(self, should_shuffle):
		self.spotify.shuffle(should_shuffle, device_id=self.get_device_id())

	def play(self, uri):
		if self.is_album_uri(uri) or self.is_spotify_playlist_uri(uri) or self.is_artist_uri(uri):
			self.spotify.start_playback(context_uri=uri, device_id=self.get_device_id())
		else:
			self.play_uris([uri])

	def set_volume(self, volume):
		self.spotify.volume(int(volume), device_id=self.get_device_id())

	def set_track_progress(self, progress):
		self.spotify.seek_track(int(progress), device_id=self.get_device_id())

	def remove_saved_album(self, resource: resources.ArkhesResource) -> None:
		self.spotify.current_user_saved_albums_delete([resource.uri()])
		self.saved_albums_cache = [i for i in self.saved_albums_cache if i != resource]
		self.uncategorized_albums = [i for i in self.uncategorized_albums if i != resource]

	def remove_saved_playlist(self, resource: resources.ArkhesResource) -> None:
		self.spotify.current_user_unfollow_playlist(resource.name())
		self.saved_playlists_cache = [i for i in self.saved_playlists_cache if i != resource]
		self.uncategorized_playlists = [i for i in self.uncategorized_playlists if i != resource]

	def remove_saved_song(self, resource: resources.ArkhesResource) -> None:
		self.spotify.current_user_saved_tracks_delete([resource.uri()])
		self.saved_songs_cache = [i for i in self.saved_songs_cache if i != resource]
		self.uncategorized_songs = [i for i in self.uncategorized_songs if i != resource]

	def remove_saved_artist(self, resource: resources.ArkhesResource) -> None:
		self.spotify.user_unfollow_artists([resource.id()])
		self.saved_artists_cache = [i for i in self.saved_artists_cache if i != resource]
		self.uncategorized_artists = [i for i in self.uncategorized_artists if i != resource]

	def add_saved_album(self, resource: resources.ArkhesResource) -> None:
		self.spotify.current_user_saved_albums_add([resource.uri()])
		self.saved_albums_cache.append(resource)
		self.uncategorized_albums.append(resource)

	def add_saved_playlist(self, resource: resources.ArkhesResource) -> None:
		self.spotify.current_user_follow_playlist(resource.id())
		self.saved_playlists_cache.append(resource)
		self.uncategorized_playlists.append(resource)

	def add_saved_song(self, resource: resources.ArkhesResource) -> None:
		self.spotify.current_user_saved_tracks_add([resource.uri()])
		self.saved_songs_cache.append(resource)
		self.uncategorized_songs.append(resource)

	def add_saved_artist(self, resource: resources.ArkhesResource) -> None:
		self.spotify.user_follow_artists([resource.id()])
		self.saved_artists_cache.append(resource)
		self.uncategorized_artists.append(resource)

	def is_saved_album(self, resource: resources.ArkhesResource) -> bool:
		return resource in self.saved_albums_cache

	def is_saved_playlist(self, resource: resources.ArkhesResource) -> bool:
		return resource in self.saved_playlists_cache

	def is_saved_song(self, resource: resources.ArkhesResource) -> bool:
		return resource in self.saved_songs_cache

	def is_saved_artist(self, resource: resources.ArkhesResource) -> bool:
		return resource in self.saved_artists_cache

	def get_current_playback(self) -> resources.Playback | None:
		playback = self.spotify.current_playback()
		if playback:
			return resources.Playback(playback)
		else:
			return None

	def current_user_id(self) -> str:
		return self.spotify.current_user()['id']

	def export_playlist(self, playlist: resources.ArkhesPlaylist, name: str) -> None:
		for existing_playlist in self.saved_playlists(False):
			if existing_playlist.name() == name:
				self.spotify.playlist_replace_items(existing_playlist.id(), resources.ArkhesResource.flatten(playlist.track_uris()))
				return

		new_playlist = self.create_resource(self.spotify.user_playlist_create(self.current_user_id(), name, False, False, "Generated by Arkhes"))
		self.spotify.playlist_replace_items(new_playlist.id(), resources.ArkhesResource.flatten(playlist.track_uris()))
		self.reload_saved_playlists_cache()


	def get_album_cover(self, album: resources.Album, size: int) -> ImageTk.PhotoImage:
		path = os.path.join(self.cover_cache_location, album.spotify_id() + '.jpg')

		if not Path(path).is_file():
			url = album.cover_url()
			with open(path, 'wb') as file:
				file.write(requests.get(url).content)

		return self.get_image(path, size)

	def get_image(self, path: str, size: int) -> ImageTk.PhotoImage:
		return ImageTk.PhotoImage(Image.open(path).resize([size, size]))


spotify_wrapper = SpotifyWrapper()
