from __future__ import annotations
import datetime
import itertools
from typing import List
import arkhesPlaylists

class ArkhesResource:
	def __init__(self, data_dict: dict) -> None:
		self._data_dict = data_dict
		self._line = ""
		self._line_number = -1
		self._rating = -1

	def to_json(self) -> dict:
		return self._data_dict

	def line_to_write(self) -> str:
		if self.rating() < 0:
			return self.uri()
		else:
			return f"{self.uri()} {self.rating()}"

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

	def contents(self) -> List[ArkhesResource]:
		return []

	def track_uris(self) -> List[str]:
		return [[item.uri() for item in self.contents()]]

	def release_date(self) -> str:
		return self._data_dict.get('release_date', '0000-00-00')

	def popularity(self) -> int:
		return self._data_dict['popularity']

	def description(self) -> str:
		return "[No Description]"

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

	def artist(self) -> Artist:
		return Artist(self._data_dict['artists'][0])  #TODO: Handle multiple artists

	def description(self) -> str:
		return f"[Album]\n{self.name()}\nArtist: {self.artist().name()}\nRelease Date: {self.release_date()}"

class SpotifyPlaylist(ArkhesResource):
	def contents(self) -> List[ArkhesResource]:
		return [Song(track['track']) for track in self._data_dict['tracks']['items']]

class Artist(ArkhesResource):
	def contents(self) -> List[ArkhesResource]:
		return [Album(item) for item in self._data_dict['albums']]

	def track_uris(self) -> List[str]:
		return ArkhesResource.flatten([resource.track_uris() for resource in self.contents()])

	def description(self) -> str:
		return f"[nArtist]\n{self.name()}\nRelease Date: {self.release_date()}"

class Song(ArkhesResource):
	def contents(self) -> List[ArkhesResource]:
		return [self]

	def duration_ms(self) -> int:
		return self._data_dict['duration_ms']

	def duration(self) -> datetime.timedelta:
		return datetime.timedelta(milliseconds=self.duration_ms())

	def album(self) -> Album:
		return Album(self._data_dict['album'])

	def artist(self) -> Artist:
		return Artist(self._data_dict['artists'][0])  #TODO: Handle multiple artists

	def song(self) -> Song:
		return self

	def track_number(self) -> int:
		return self._data_dict['track_number']

class ArkhesPlaylist(ArkhesResource):
	def contents(self) -> List[ArkhesResource]:
		return arkhesPlaylists.ArkhesPlaylists.get_playlist_items(self._data_dict['name'])

	def track_uris(self) -> List[str]:
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
		return datetime.timedelta(milliseconds=self.progress_ms())

	def volume(self) -> int:
		return self._base_data_dict['device']['volume_percent']

	def context(self) -> ArkhesResource:
		return self._base_data_dict['context']