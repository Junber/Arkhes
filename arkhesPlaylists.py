import os
from pathlib import Path
from tkinter import messagebox
from spotifyWrapper import spotify_wrapper

class FileUtils:	
	@staticmethod
	def get_lines_from_file(filename):
		try:
			with open(filename) as f:
				return [line.strip('\n') for line in f]
		except FileNotFoundError:
			return []
	
	@staticmethod
	def add_line_to_file(filename, line):
		with open(filename, 'a') as f:
			if f.tell() != 0:
				f.write('\n')
			f.write(line)
	
	@staticmethod
	def move_line_down(filename, line_number_to_move):
		with open(filename, 'r+') as f:
			d = [line.strip('\n') for line in f]
			f.seek(0)
			f.truncate()
			line_number = 0
			saved_line = ""
			for line in d:
				if line_number == line_number_to_move:
					saved_line = line
				elif line_number == line_number_to_move + 1:
					if f.tell() != 0:
						f.write('\n')
					f.write(line)
					f.write('\n')
					f.write(saved_line)
				else:
					if f.tell() != 0:
						f.write('\n')
					f.write(line)

				line_number += 1
	
	@staticmethod
	def remove_line_from_file(filename, line_number_to_remove):
		with open(filename, 'r+') as f:
			d = [line.strip('\n') for line in f]
			f.seek(0)
			f.truncate()
			line_number = 0
			for line in d:
				if line_number != line_number_to_remove:
					if f.tell() != 0:
						f.write('\n')
					f.write(line)
				line_number += 1

class ArkhesPlaylists:
	playlist_location = 'playlists'
		
	@staticmethod
	def path_for(name):
		return os.path.join(ArkhesPlaylists.playlist_location, name + '.txt')
	
	@staticmethod
	def get_resource_in_line(i, resource):
		album = spotify_wrapper.get_resource(resource)
		
		album['playlistLine'] = resource
		album['lineNumber'] = i
		return album

	@staticmethod
	def get_playlist(playlist):
		path = ArkhesPlaylists.path_for(playlist)
		if Path(path).is_file():
			lines = FileUtils.get_lines_from_file(path)
			spotify_wrapper.cache_uncached_albums(lines)
			return [ArkhesPlaylists.get_resource_in_line(i, line) for i, line in enumerate(lines)]
		else:
			return []
	
	@staticmethod
	def remove_item_from_playlist(playlist, item):
		FileUtils.remove_line_from_file(ArkhesPlaylists.path_for(playlist), item['lineNumber'])
		
	@staticmethod
	def add_item_to_playlist(playlist, item):
		FileUtils.add_line_to_file(ArkhesPlaylists.path_for(playlist), item['uri'])
	
	@staticmethod
	def move_item_up(playlist, item):
		FileUtils.move_line_down(ArkhesPlaylists.path_for(playlist), item['lineNumber'] - 1)
	
	@staticmethod
	def move_item_down(playlist, item):
		FileUtils.move_line_down(ArkhesPlaylists.path_for(playlist), item['lineNumber'])

	@staticmethod
	def rename_playlist(playlist, new_name):
		if Path(new_name).is_file():
			messagebox.showinfo(message='Playlist already exists')
		else:
			os.rename(playlist, new_name)