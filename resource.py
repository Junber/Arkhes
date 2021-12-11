import itertools
import arkhesPlaylists


class Resource:
	def __init__(self, data_dict: dict) -> None:
		self.data_dict = data_dict
		self.line = ""
		self.line_number = -1
		self.rating = -1
	
	def to_json(self) -> dict:
		return self.data_dict

	def get_line(self) -> str:
		return self.line

	def get_line_number(self) -> int:
		return self.line_number
	
	def set_line(self, line: str, line_number: int) -> None:
		self.line = line
		self.line_number = line_number

	def get_rating(self) -> int:
		return self.rating
	
	def set_rating(self, rating: int) -> None:
		self.rating = rating
	
	def get_name(self) -> str:
		return self.data_dict['name']

	def get_type(self) -> str:
		return self.data_dict['type']
	
	def get_uri(self) -> str:
		return self.data_dict['uri']
	
	def get_contents(self) -> list:
		return []
	
	def get_track_uris(self) -> list:
		return [[item.get_uri() for item in self.get_contents()]]

	@staticmethod
	def flatten(uris):
		return list(itertools.chain.from_iterable(uris))


class Album(Resource):
	def get_contents(self) -> list:
		return [Song(item) for item in self.data_dict['tracks']['items']]

class SpotifyPlaylist(Resource):
	def get_contents(self) -> list:
		return [Song(track['track']) for track in self.data_dict['tracks']['items']]

class Artist(Resource):
	def get_contents(self) -> list:
		return [Album(item) for item in self.data_dict['albums']]
	
	def get_track_uris(self) -> list:
		return Resource.flatten([resource.get_track_uris() for resource in self.get_contents()])

class Song(Resource):
	def get_contents(self) -> list:
		return [self]

class ArkhesPlaylist(Resource):
	def get_contents(self) -> list:
		return arkhesPlaylists.ArkhesPlaylists.get_playlist_items(self.data_dict['name'])
	
	def get_track_uris(self) -> list:
		return Resource.flatten([resource.get_track_uris() for resource in self.get_contents()])