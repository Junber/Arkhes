from __future__ import annotations
import datetime
import itertools
from tkinter import messagebox
from typing import List
import arkhesPlaylists
from spotifyWrapper import spotify_wrapper

class ArkhesResource:
	def __init__(self, data_dict: dict) -> None:
		self._data_dict = data_dict
		self._line = ''
		self._line_number = -1
		self._rating = -1

	def to_json(self) -> dict:
		return self._data_dict

	def line_to_write(self) -> str:
		if self.rating() < 0:
			return self.uri()
		else:
			return f'{self.uri()} {self.rating()}'

	def line(self) -> str:
		return self._line

	def line_number(self) -> int:
		return self._line_number

	def set_line(self, line: str, line_number: int) -> None:
		self._line = line
		self._line_number = line_number

	def rating(self) -> int:
		return self._rating

	def set_rating(self, rating: int) -> None:
		self._rating = rating

	def name(self) -> str:
		return self._data_dict['name']

	def spotify_id(self) -> str:
		return self._data_dict['id']

	def type(self) -> str:
		return self._data_dict['type']

	def uri(self) -> str:
		return self._data_dict['uri']

	def id(self) -> str:
		return self._data_dict['id']

	def contents(self) -> List[ArkhesResource]:
		return []

	def track_uris(self) -> List[List[str]]:
		return [[item.uri() for item in self.contents()]]

	def release_date(self) -> str:
		return self._data_dict.get('release_date', '0000-00-00')

	def popularity(self) -> int:
		return self._data_dict['popularity']

	def duration_ms(self) -> int:
		return sum([item.duration_ms() for item in self.contents()])

	def duration(self) -> datetime.timedelta:
		return datetime.timedelta(seconds=int(self.duration_ms()/1000))

	def description(self) -> str:
		return f'[{self.type_name().capitalize()}]\n{self.name()}'

	def type_name(self) -> str:
		return '[None]'

	def save_unasked(self) -> None:
		pass

	def unsave_unasked(self) -> None:
		pass

	def save(self) -> bool:
		result = messagebox.askyesno('Delete', f'Do you really want to add {self.name()} to your saved {self.type_name()}s on Spotify?')
		if result:
			self.save_unasked()
		return result

	def unsave(self) -> bool:
		result = messagebox.askyesno('Delete', f'Do you really want to remove {self.name()} from your saved {self.type_name()}s on Spotify?')
		if result:
			self.unsave_unasked()
		return result

	def is_saved(self) -> bool:
		return False

	def toggle_saved(self) -> bool:
		if self.is_saved():
			return self.unsave()
		else:
			return self.save()

	@staticmethod
	def flatten(uris: list) -> list:
		return list(itertools.chain.from_iterable(uris))


class Album(ArkhesResource):
	def contents(self) -> List[ArkhesResource]:
		return [Song(item) for item in self._data_dict['tracks']['items']]

	def number_of_tracks(self) -> int:
		return self._data_dict['total_tracks']

	def cover_url(self) -> str:
		return self._data_dict['images'][0]['url']

	def artists(self) -> list[Artist]:
		return [Artist(artist) for artist in self._data_dict['artists']]

	def artists_string(self) -> str:
		return ", ".join([artist.name() for artist in self.artists()])

	def description(self) -> str:
		return super().description() + f'\nArtist: {self.artists_string()}\nLength: {str(self.duration())}\nRelease Date: {self.release_date()}'

	def type_name(self) -> str:
		return 'album'

	def save_unasked(self) -> None:
		spotify_wrapper.add_saved_album(self)

	def unsave_unasked(self) -> None:
		spotify_wrapper.remove_saved_album(self)

	def is_saved(self) -> bool:
		return spotify_wrapper.is_saved_album(self)


class SpotifyPlaylist(ArkhesResource):
	def contents(self) -> List[ArkhesResource]:
		return [Song(track['track']) for track in self._data_dict['tracks']['items']]

	def type_name(self) -> str:
		return 'spotify playlist'

	def save_unasked(self) -> None:
		spotify_wrapper.add_saved_playlist(self)

	def unsave_unasked(self) -> None:
		spotify_wrapper.remove_saved_playlist(self)

	def is_saved(self) -> bool:
		return spotify_wrapper.is_saved_playlist(self)

class Artist(ArkhesResource):
	def contents(self) -> List[ArkhesResource]:
		return [Album(item) for item in self._data_dict['albums']]

	def track_uris(self) -> List[List[str]]:
		return ArkhesResource.flatten([resource.track_uris() for resource in self.contents()])

	def type_name(self) -> str:
		return 'artist'

	def save_unasked(self) -> None:
		spotify_wrapper.add_saved_artist(self)

	def unsave_unasked(self) -> None:
		spotify_wrapper.remove_saved_artist(self)

	def is_saved(self) -> bool:
		return spotify_wrapper.is_saved_artist(self)

class Song(ArkhesResource):
	def contents(self) -> List[ArkhesResource]:
		return [self]

	def album(self) -> Album:
		return Album(self._data_dict['album'])

	def duration_ms(self) -> int:
		return self._data_dict['duration_ms']

	def artists(self) -> List[Artist]:
		return [Artist(artist) for artist in self._data_dict['artists']]

	def artists_string(self) -> str:
		return ", ".join([artist.name() for artist in self.artists()])

	def song(self) -> Song:
		return self

	def track_number(self) -> int:
		return self._data_dict['track_number']

	def type_name(self) -> str:
		return 'song'

	def save_unasked(self) -> None:
		spotify_wrapper.add_saved_song(self)

	def unsave_unasked(self) -> None:
		spotify_wrapper.remove_saved_song(self)

	def is_saved(self) -> bool:
		return spotify_wrapper.is_saved_song(self)

class ArkhesPlaylist(ArkhesResource):
	def contents(self) -> List[ArkhesResource]:
		return arkhesPlaylists.ArkhesPlaylists.get_playlist_items(self._data_dict['name'])

	def type_name(self) -> str:
		return 'arkhes playlist'

	def track_uris(self) -> List[List[str]]:
		return ArkhesResource.flatten([resource.track_uris() for resource in self.contents()])

class Playback(Song):
	def __init__(self, data_dict: dict) -> None:
		Song.__init__(self, data_dict['item'])
		self._base_data_dict = data_dict

	def is_none(self) -> bool:
		return self._data_dict is None

	def progress_ms(self) -> int:
		return self._base_data_dict['progress_ms']

	def progress(self) -> datetime.timedelta:
		return datetime.timedelta(seconds=int(self.progress_ms()/1000))

	def volume(self) -> int:
		return self._base_data_dict['device']['volume_percent']

	def context(self) -> ArkhesResource:
		return self._base_data_dict['context']
