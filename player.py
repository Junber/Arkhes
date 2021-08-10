import random, requests, datetime

from tkinter import N, W, S, E, ttk, HORIZONTAL
import tkinter
from PIL import ImageTk, Image

from spotifyWrapper import SpotifyWrapper, spotify_wrapper
from utils import Utils
from albumList import AlbumList
from tooltip import CreateToolTip
from currentPlaylistFrame import CurrentPlaylistFrame

class Player:
	def __init__(self, root):
		self.root = root
		self.active = True

		self.current_playlist_frame = CurrentPlaylistFrame(root, self)
		self.current_playlist_frame.grid(column=0, row=0, sticky=(N, W, E))

		ttk.Button(root, text='Play', command=self.play).grid(column=0, row=2, sticky=(N, W, E))

		self.track_shuffle = tkinter.BooleanVar(value=False)
		self.album_shuffle = tkinter.BooleanVar(value=False)
		shuffle_frame = ttk.Frame(root)
		shuffle_frame.grid(column=0, row=1, sticky=(W, E, S))
		ttk.Checkbutton(shuffle_frame, text='Track-Shuffle', variable=self.track_shuffle, command=self.changed_shuffle).grid(column=0, row=0, sticky=(N, S, W, E))
		ttk.Checkbutton(shuffle_frame, text='Album-Shuffle', variable=self.album_shuffle, command=self.changed_shuffle).grid(column=1, row=0, sticky=(N, S, W, E))

		self.album_list = AlbumList(root, self, 'Contents', self.clicked_album)
		self.album_list.grid(column=1, row=0, rowspan=3, sticky=(N, W, E, S))

		self.playback_frame = ttk.Labelframe(root, text='Current Playback', padding='5 5 5 5')
		self.playback_frame.grid(column=0, row=3, columnspan=2, sticky=(N, S, W, E))

		self.album_cover_label = ttk.Label(self.playback_frame, anchor='center')
		self.album_cover_label.grid(column=0, row=0, rowspan=5, sticky=(N, S, W, E))
		self.set_cover('no_cover.jpg')

		self.current_album_name = tkinter.StringVar(value='[Album]') # TODO: Save album and artist to recover on start-up
		self.current_album_label = ttk.Label(self.playback_frame, textvar=self.current_album_name, anchor='center')
		self.current_album_label.grid(column=1, row=1, sticky=(S, W, E))

		self.current_artist_name = tkinter.StringVar(value='[Artist]')
		self.current_artist_label = ttk.Label(self.playback_frame, textvar=self.current_artist_name, anchor='center')
		self.current_artist_label.grid(column=1, row=2, sticky=(S, W, E))

		self.build_playback_button_frame()
		self.playback_button_frame.grid(column=1, row=3, sticky=(S, W, E))

		self.current_track_progress_frame = tkinter.Frame(self.playback_frame)
		self.current_track_progress_frame.grid(column=1, row=4, sticky=(S, W, E))
		self.current_track_progress = tkinter.IntVar(value=0)
		self.current_track_progress_string = tkinter.StringVar(value ='[Time]')
		self.total_track_time_string = tkinter.StringVar(value ='[Time]')
		tkinter.Label(self.current_track_progress_frame, textvariable=self.current_track_progress_string).grid(column=0, row=0, sticky=(N, S, W, E))
		self.current_track_progress_scale = ttk.Scale(self.current_track_progress_frame, orient=HORIZONTAL, variable=self.current_track_progress, command=self.changed_track_progress)
		self.current_track_progress_scale.grid(column=1, row=0, sticky=(N, S, W, E))
		tkinter.Label(self.current_track_progress_frame, textvariable=self.total_track_time_string).grid(column=2, row=0, sticky=(N, S, W, E))

		self.build_volume_frame()
		self.volume_frame.grid(column=1, row=0, sticky=(S, W, E))
		
		self.playback_frame.columnconfigure(1, weight=1)
		self.playback_frame.rowconfigure(0, weight=1)
		self.current_track_progress_frame.columnconfigure(1, weight=1)

		self.current_playback = []


		for thing in [root, shuffle_frame, self.playback_frame, self.volume_frame]:
			for child in thing.winfo_children(): 
				child.grid_configure(padx=5, pady=5)
		
		root.columnconfigure(0, weight=1)
		root.columnconfigure(1, weight=2)

		self.name_changed()
		self.update_current_track_loop()
	
	def build_playback_button_frame(self):
		self.playback_button_frame = ttk.Frame(self.playback_frame)

		self.go_back_album_button = ttk.Button(self.playback_button_frame, text='<<', command=self.go_back_album)
		self.go_back_album_button.grid(column=0, row=0)
		CreateToolTip(self.go_back_album_button, "Go to previous album")

		ttk.Button(self.playback_button_frame, text='<', command=self.go_back_track).grid(column=1, row=0)
		self.current_track_name = tkinter.StringVar(value='[No playback started from here]')
		self.current_track_button = ttk.Button(self.playback_button_frame, textvariable=self.current_track_name, command=self.pause)
		self.current_track_button.grid(column=2, row=0, sticky=(N, S, W, E))
		CreateToolTip(self.current_track_button, "Click to pause/resume playback")

		ttk.Button(self.playback_button_frame, text='>', command=self.go_forward_track).grid(column=3, row=0)
		self.go_forward_album_button = ttk.Button(self.playback_button_frame, text='>>', command=self.go_forward_album)
		self.go_forward_album_button.grid(column=4, row=0)
		CreateToolTip(self.go_forward_album_button, "Go to next album")

		self.playback_button_frame.columnconfigure(2, weight=1)
	
	def build_volume_frame(self):
		self.volume_frame = ttk.Frame(self.playback_frame)
		ttk.Label(self.volume_frame, text='Volume').grid(column=0, row=0, sticky=(N, S, W, E))
		self.volume = tkinter.IntVar()
		ttk.Scale(self.volume_frame, orient=HORIZONTAL, variable=self.volume, to=100, command=self.changed_volume).grid(column=1, row=0, sticky=(N, S, W, E))
	
	def save_dict(self):
		return {'track_shuffle' : self.track_shuffle.get(), 'album_shuffle' : self.album_shuffle.get(), 'current' : self.current_playlist_frame.save_dict(), 'volume' : self.volume.get()}
	
	def load_from(self, dct):
		self.track_shuffle.set(dct['track_shuffle'])
		self.album_shuffle.set(dct['album_shuffle'])
		self.current_playlist_frame.load_from(dct['current'])
		self.volume.set(dct['volume'])
		
		self.name_changed()
	
	def set_cover(self, path):
		img = ImageTk.PhotoImage(Image.open(path).resize([320, 320]))
		self.album_cover_label.configure(image = img)
		self.album_cover_label.image = img
	
	def get_uris(self, resource):
		uris = []
		if SpotifyWrapper.is_album(resource):
			tracks = spotify_wrapper.get_resource(resource)['tracks']['items']
			uris = [track['uri'] for track in tracks]
			if not self.album_shuffle.get() and self.track_shuffle.get():
				random.shuffle(uris)
			uris = [uris]
		elif SpotifyWrapper.is_arkhes_playlist(resource):
			path = Utils.path_for(resource[len(spotify_wrapper.prefix):].strip())
			uris = self.get_uris_from_file(path)
		elif SpotifyWrapper.is_song(resource):
			uris = [[resource]]
		elif SpotifyWrapper.is_spotify_playlist(resource):
			tracks = spotify_wrapper.get_resource(resource)['tracks']['items']
			uris = [item['track']['uri'] for item in tracks]
			if not self.album_shuffle.get() and self.track_shuffle.get():
				random.shuffle(uris)
			uris = [uris]
		
		return uris
	
	def get_uris_from_file(self, filename):
		lines = Utils.get_lines_from_file(filename)		
		spotify_wrapper.cache_uncached_albums(lines)
		return Utils.flatten([self.get_uris(line) for line in lines])

	def get_uris_from_file_and_shuffle(self, filename):
		uris = self.get_uris_from_file(filename)

		if self.album_shuffle.get() and not self.track_shuffle.get():
			random.shuffle(uris)
		
		return uris
	
	def flatten_uris(self, uris):
		uris = Utils.flatten(uris)

		if self.album_shuffle.get() and self.track_shuffle.get():
			random.shuffle(uris)
		
		return uris
	
	def get_path(self):
		return self.current_playlist_frame.name_entry.get_path()
	
	def play(self, *args):
		self.current_playback = self.get_uris_from_file_and_shuffle(self.get_path())
		uris = self.flatten_uris(self.current_playback)
		if len(uris) > 0:
			spotify_wrapper.play_uris(uris)
	
	def clicked_album(self, album):
		if album['type'] == spotify_wrapper.resource_type:
			self.current_playlist_frame.save_current_position()
			self.current_playlist_frame.name_entry.set(album['name'])
		else:
			spotify_wrapper.shuffle(self.track_shuffle.get())
			spotify_wrapper.play(album['uri'])

	def name_changed(self, *args):
		self.album_list.set_items_with_path(self.get_path())
	
	def changed_shuffle(self, *args):
		if self.album_shuffle.get() and self.track_shuffle.get():
			self.go_back_album_button.state(['disabled'])
			self.go_forward_album_button.state(['disabled'])
		else:
			self.go_back_album_button.state(['!disabled'])
			self.go_forward_album_button.state(['!disabled'])
	
	def changed_volume(self, *args):
		spotify_wrapper.set_volume(self.volume.get())
	
	def changed_track_progress(self, *args):
		spotify_wrapper.set_track_progress(self.current_track_progress.get())
	
	def update_current_track(self):
		if not self.active:
			return

		playback = spotify_wrapper.get_current_playback()
		if playback is not None and playback['item'] is not None:
			self.current_track_progress.set(playback['progress_ms']) # TODO: Make smoother
			self.current_track_progress_string.set(datetime.timedelta(seconds=int(playback['progress_ms']/1000)))
			self.volume.set(playback['device']['volume_percent'])

			name = playback['item']['name']
			if name != self.current_track_name.get():
				self.current_track_progress_scale.configure(to=playback['item']['duration_ms'])
				self.total_track_time_string.set(datetime.timedelta(seconds=int(playback['item']['duration_ms']/1000)))
				album = playback['item']['album']
				self.current_track_name.set(name)
				self.current_album_name.set("Album: " + album['name'] + " (Track: " + str(playback['item']['track_number']) + "/" + str(album['total_tracks']) + ")")
				self.current_artist_name.set("Artist: " + playback['item']['artists'][0]['name'])  #TODO: Handle multiple artists
				x = album['images'][0]['url']
				with open('cover_cache/temp.jpg', 'wb') as file:
					file.write(requests.get(x).content) # TODO: Cache and stuff
				self.set_cover('cover_cache/temp.jpg')
	
	def update_current_track_loop(self):
		self.update_current_track()
		self.root.after(1000, self.update_current_track_loop)


	def go_back_album(self, *args):
		pass # TODO

	def go_forward_album(self, *args):
		pass # TODO

	def go_back_track(self, *args):
		spotify_wrapper.go_back_track()

	def go_forward_track(self, *args):
		spotify_wrapper.go_forward_track()
	
	def pause(self, *args):
		spotify_wrapper.toggle_pause()
	
	def set_active(self, new_active):
		if not self.active and new_active:
			self.update_current_track()
		self.active = new_active


	# TODO: Handle large playbacks better
	# TODO: Save playback context to play something else but resume later
	# TODO: Look at songs inside of albums/spotify playlists
	# TODO: Repeat modes
	# TODO: "Retain order when album shuffle"-flag for playlists
	# TODO: Album/playlist covers

