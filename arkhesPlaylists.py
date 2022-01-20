import os
from pathlib import Path
from tkinter import messagebox
from resources import ArkhesResource
from spotifyWrapper import SpotifyWrapper, spotify_wrapper

class FileUtils:
	@staticmethod
	def get_lines_from_file(filename: str) -> list:
		try:
			with open(filename, 'r', encoding='utf8') as file:
				return [line.strip('\n') for line in file]
		except FileNotFoundError:
			return []

	@staticmethod
	def add_line_to_file(filename: str, line: str) -> None:
		with open(filename, 'a', encoding='utf8') as file:
			if file.tell() != 0:
				file.write('\n')
			file.write(line)

	@staticmethod
	def move_line_down(filename: str, line_number_to_move: int) -> None:
		with open(filename, 'r+', encoding='utf8') as file:
			lines = [line.strip('\n') for line in file]
			file.seek(0)
			file.truncate()
			line_number = 0
			saved_line = ''
			for line in lines:
				if line_number == line_number_to_move:
					saved_line = line
				elif line_number == line_number_to_move + 1:
					if file.tell() != 0:
						file.write('\n')
					file.write(line)
					file.write('\n')
					file.write(saved_line)
				else:
					if file.tell() != 0:
						file.write('\n')
					file.write(line)

				line_number += 1

	@staticmethod
	def remove_line_from_file(filename: str, line_number_to_remove: int) -> None:
		with open(filename, 'r+', encoding='utf8') as file:
			lines = [line.strip('\n') for line in file]
			file.seek(0)
			file.truncate()
			line_number = 0
			for line in lines:
				if line_number != line_number_to_remove:
					if file.tell() != 0:
						file.write('\n')
					file.write(line)
				line_number += 1

	@staticmethod
	def update_line_in_file(filename: str, line_number_to_update: int, new_line: str) -> None:
		with open(filename, 'r+', encoding='utf8') as file:
			lines = [line.strip('\n') for line in file]
			file.seek(0)
			file.truncate()
			line_number = 0
			for line in lines:
				if file.tell() != 0:
					file.write('\n')

				if line_number != line_number_to_update:
					file.write(line)
				else:
					file.write(new_line)

				line_number += 1

class ArkhesPlaylists:
	playlist_location = 'playlists'

	@staticmethod
	def path_for(name: str) -> str:
		return os.path.join(ArkhesPlaylists.playlist_location, name + '.txt')

	@staticmethod
	def get_resource_from_line(line: str, line_number: int) -> ArkhesResource:
		line_parts = line.split(' ')
		resource = spotify_wrapper.get_resource(line_parts[0])

		resource.set_line(line, line_number)

		if len(line_parts) > 1:
			resource.set_rating(line_parts[1])

		return resource

	@staticmethod
	def get_playlist_items(name: str) -> list:
		path = ArkhesPlaylists.path_for(name)
		if Path(path).is_file():
			lines = FileUtils.get_lines_from_file(path)
			#spotify_wrapper.cache_uncached_albums(lines) #TODO: Make this work despite ratings and reenable this again
			return [ArkhesPlaylists.get_resource_from_line(line, lineNumber) for lineNumber, line in enumerate(lines)]
		else:
			return []

	@staticmethod
	def get_playlist(name: str) -> ArkhesResource:
		return spotify_wrapper.get_resource(SpotifyWrapper.prefix + name)

	@staticmethod
	def remove_item_from_playlist(playlist: str, item: ArkhesResource) -> None:
		FileUtils.remove_line_from_file(ArkhesPlaylists.path_for(playlist), item.line_number())

	@staticmethod
	def add_item_to_playlist(playlist: str, item: ArkhesResource) -> None:
		FileUtils.add_line_to_file(ArkhesPlaylists.path_for(playlist), item.line_to_write())

	@staticmethod
	def update_item_in_playlist(playlist: str, item: ArkhesResource) -> None:
		FileUtils.update_line_in_file(ArkhesPlaylists.path_for(playlist), item.line_number(), item.line_to_write())

	@staticmethod
	def move_item_up(playlist: str, item: ArkhesResource) -> None:
		FileUtils.move_line_down(ArkhesPlaylists.path_for(playlist), item.line_number() - 1)

	@staticmethod
	def move_item_down(playlist: str, item: ArkhesResource) -> None:
		FileUtils.move_line_down(ArkhesPlaylists.path_for(playlist), item.line_number())

	@staticmethod
	def rename_playlist(playlist: str, new_name: str) -> None:
		if Path(new_name).is_file():
			messagebox.showinfo(message='Playlist already exists')
		else:
			os.rename(playlist, new_name)
