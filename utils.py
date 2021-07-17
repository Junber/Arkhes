import itertools

class Utils:
	def get_lines_from_file(filename):
		try:
			with open(filename) as f:
				return [line.strip('\n') for line in f]
		except FileNotFoundError:
			return []
	
	def add_line_to_file(filename, line):
		with open(filename, 'a') as f:
			if f.tell() != 0:
				f.write('\n')
			f.write(line)
	
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
		
	def path_for(name):
		return 'playlists/' + name + '.txt'

	def flatten(uris):
		return list(itertools.chain.from_iterable(uris))