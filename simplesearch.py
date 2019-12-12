from os import listdir
from os.path import isfile
import copy
import sys
import bisect
import pickle

# Oystein Kapperud, 2019

class Node:
	def __init__(self, root, leaf, character, file_tag = None, word_index = None):
		"""
		Constructor for the class Node.
		
		Arguments:
		root (bool): True if the node is the root of the tree
		leaf (bool): True if the node is a leaf node
		character (str): a single-character string
		file_tag (str): (for leafs only) indicates the file from which the word was read (default: None)
		word_index (int): indicates the index of the word in the given file
		"""
		self.root = root
		self.leaf = leaf
		self.character = character
		if self.root:
			self.character = "ROOT"
		self.word_indices = {}
		self.children = [] # list of children nodes
		if self.leaf:
			if not file_tag in self.word_indices:
				self.word_indices[file_tag] = [word_index]
			else:
				self.word_indices[file_tag].append(word_index)
		
		
	def add_child(self, child):
		self.children.append(child)
		
	def add_word_index(self, file_tag, word_index):
		if not file_tag in self.word_indices:
			self.word_indices[file_tag] = [word_index]
		else:
			self.word_indices[file_tag].append(word_index)
	


class Tree:
	def __init__(self, end_indicator = "$"):
		"""
		Constructor for the class Tree
		"""
		self.root = Node(root = True, leaf = False, character = None)
		self.empty = True
		self.leaves = []
		self.end_indicator = end_indicator
		self.words = {} # used only for testing
	
	def initialize_word_lists(self, word_counts):
		for filename in word_counts:
			self.words[filename] = [None for i in range(word_counts[filename]-1)]
	
	def set_filenames(self, filenames):
		self.filenames = filenames
	
	
	def has_phrase(self, phrase):
		"""
		Takes as input a phrase in form of a list of words, and returns a dictionary where the keys 
		are the file names of the files where the phrase is found, and the values are the indices
		
		Arguments:
		phrase (list of strings)
		"""
		potential_indices = {} # This dictionary will eventually be returned
		for i in range(len(phrase)):
			word = phrase[i]
			word_indices = self.has_word(word) # A dictionary where the keys are the files in which the word is found, and the values are the indices
			if i == 0: # First word in the phrase. Initialize potential_indices
				for filename in word_indices:
					potential_indices[filename] = word_indices[filename]
					
				if len(potential_indices) == 0:
					return {}
			else:
				new_potential_indices = {}
				for filename in word_indices:
					for potential_continuation in word_indices[filename]:
						if filename in potential_indices:
							for index in potential_indices[filename]:
								if potential_continuation == index + 1: # Checks if the current word in the phrase follows immedeately after the previous word in the phrase
									if not filename in new_potential_indices:
										new_potential_indices[filename] = [potential_continuation]
									else:
										new_potential_indices[filename].append(potential_continuation)
				
				potential_indices = copy.copy(new_potential_indices)
		
		return potential_indices
				
	
	def has_word(self, word):
		"""
		Takes as input a word, and returns a dictionary where the keys 
		are the file names of the files where the word is found, and the values are the indices.
		
		Arguments:
		word (str)
		"""
		word = word + self.end_indicator
		current_node = self.root
		for i in range(len(word)):
			query_character = word[i]
			character_found = False
			for child in current_node.children:
				if query_character == child.character:
					character_found = True
					if child.leaf and query_character == self.end_indicator:
							word_indices = copy.copy(child.word_indices)
							return word_indices
					else:
						current_node = child
						break
			if not character_found:
					return {}
					
		
	def add_word(self, word, file_tag, word_index):
		"""
		A method that adds the given word from the given position in the given file to the tree
		
		Arguments:
		word (str)
		file_tag (str)
		word_index (int)
		"""
		
		word = word + self.end_indicator
		if self.empty: # Empty tree. Create new twig from the root (see method create_twig)
			self.empty = False
			self.create_twig(self.root, word, file_tag, word_index)		
		else:
			current_node = self.root
			for i in range(len(word)):
				current_character = word[i]
				if current_character == self.end_indicator and i != len(word)-1:
					print("Error! File " + file_tag + " contains a word with the chosen end_indicator. Please restart the program and chose a different end_indicator")
					sys.exit()
				current_character_found = False
				for child in current_node.children:
					if child.character == current_character:
						if current_character == self.end_indicator: # Word is already in tree. Add word index and file tag for current file if not already present
							child.add_word_index(file_tag, word_index)
						current_node = child
						current_character_found = True
						break
				if not current_character_found: # No more common characters found. Create new twig (see method create_twig)
					self.create_twig(current_node, word[i:], file_tag, word_index)
					break
				
	
	def create_twig(self, from_node, word, file_tag, word_index):
		"""
		A method that creates a new twig in the tree. A twig is here a brach in the tree consisting exclusively of single-child nodes.
		
		Arguments:
		from_node (Node instance)
		word (str): the remaining word to be spelled out
		file_tag (str)
		word_index
		"""
		current_node = from_node
		for i in range(len(word)):
			leaf = i == len(word)-1
			if leaf:
				file_tag_argument = file_tag
				word_index_argument = word_index
			else:
				file_tag_argument = None
				word_index_argument = None
			new_node = Node(root = False, leaf = leaf, character = word[i], file_tag = file_tag_argument, word_index = word_index_argument)
			current_node.add_child(new_node)
			if not leaf:
				current_node = new_node
	
	def retrieve_words(self, subtree_root = None, current_word = ""):
		"""
		A method that retrieves the individual words and associated file tags stored in the tree structure.
		This method is used only for testing; it is not necessary for ordinary running of the script.
		"""
		
		if subtree_root is None:
			subtree_root = self.root
		if self.empty:
			print("The tree is empty!")
		else:
			for child in subtree_root.children:
				if child.character == self.end_indicator:
					word_indices = child.word_indices
					for filename in word_indices:
						for word_index in word_indices[filename]:
							self.words[filename][word_index] = current_word

				else:
					new_word = current_word + child.character
					self.retrieve_words(subtree_root = child, current_word = new_word)
		return self.words
				
		

class Simplesearch:
	def __init__(self, path = "", end_indicator = "$", case_sensitive = False, maximum_report = 10, ignore_punctuation = True, tree = None):
		"""
		Constructor for the class Simplesearch
		
		Arguments (see README for details):
		path (str): path to file directory
		end_indicator (str)
		case_sensitive (bool)
		maximum_report (int)
		ignore_punctuation (bool)
		tree (Tree instance)
		"""
		self.end_indicator = end_indicator
		self.path = path
		self.case_sensitive = case_sensitive
		self.ignore_punctuation = ignore_punctuation
		self.maximum_report = maximum_report
		self.word_counts = {}
		if not self.path.endswith("/"):
			self.path += "/"
		self.tree = Tree(end_indicator = end_indicator)
		self.read_files()
		self.scores = {}
		for filename in self.filenames:
			self.scores[filename] = 0
		
	
	def read_files(self):
		"""
		A method that reads the files and adds the words to the tree
		"""
		try:
			self.filenames = [filename for filename in listdir(self.path) if (isfile(self.path + filename) and filename.endswith(".txt"))]
		except:
			print("Error! Directory not found!")
			sys.exit()
		self.tree.set_filenames(self.filenames)
		for filename in self.filenames:
			file_path = self.path + filename
			infile = open(file_path, "r")
			word_index = 0
			for line in infile:
				for word in line.split():
					if self.ignore_punctuation:
						word.replace(".","")
						word.replace(",","")
						word.replace("!","")
						word.replace(":","")
						word.replace(";","")
						word.replace("?","")
						word.replace("(","")
						word.replace(")","")
					if not self.case_sensitive:
						word = word.lower()
					self.tree.add_word(word, filename, word_index) # add word to the tree
					word_index += 1
			infile.close()
			self.word_counts[filename] = word_index+1


	def find_scores(self, query):
		"""
		A method that calculates and prints the score for each file, given the query (see README for details)
		
		Arguments:
		query (str)
		"""		
			
		for phrase in query:
			for file_has_phrase in self.tree.has_phrase(phrase).keys():
				self.scores[file_has_phrase] += 1		
		
		if sum(self.scores.values()) == 0:
			print("\nNo matches found\n")
		else:
			sorted_filenames = []
			sorted_scores = []
			for filename in self.scores: # sort by score
				i = bisect.bisect_left(sorted_scores, self.scores[filename])
				sorted_scores.insert(i, self.scores[filename])
				sorted_filenames.insert(i, filename)
		
			# reverse sorted lists:
			sorted_filenames = sorted_filenames[::-1]
			sorted_scores = sorted_scores[::-1]
			n_words = float(len(query))
			print("\nScores:")
			for i in range(len(sorted_scores)):
				if i == self.maximum_report:
					break
				print("%s: %.2f%%"  %(sorted_filenames[i], (sorted_scores[i]/n_words)*100) )
			print("")
	
	def reset_scores(self):
		"""
		A method that resets all scores to zero
		"""
		for filename in self.scores:
			self.scores[filename] = 0
	
	def is_this_a_valid_session(self):
		"""
		Just used to check if a loaded session is actually a session and not some other file.
		"""
		return True
		



if __name__ == '__main__':
	# default values:
	case_sensitive = False
	end_indicator = "$"
	maximum_report = 10
	ignore_punctuation = True
	tree = None
	
	search = None
	
	# Take input:
	if len(sys.argv) == 1:
		while (True):
			path = input("Please enter a directory of files, or type :load to load a stored tree, or type :settings to view or change the settings.\nYou can at any time type :quit to quit\n> ")
			if path == ":quit":
				sys.exit()
			if path == ":load":
				print("Please enter the file path for the stored session:")
				try:
					search_path = input("> ")
					search_file = open(search_path, "rb")
					search = pickle.load(search_file)
					if search.is_this_a_valid_session():
						print("Session loaded successfully!")
					search_file.close()
				except:
					print("Error! The session could not be loaded from the given location")
			if path == ":settings":
				print("\nDefault settings:")
				print("case_sensitive = " + str(case_sensitive))
				print("end_indicator = " + end_indicator)
				print("maximum_report = " + str(maximum_report))
				print("ignore_punctuation = " + str(ignore_punctuation))
				print("\nSee README.txt for a discussion. To change the settings, type > keyword = desired_value")
				print("(e.g. to change case_sensitive to True, type case_sensitive = True")
				print("To exit settings, type :done")
				settings_input = ""
				settings_changed = False
				while settings_input != ":done":
					settings_input = input("> ")
					if settings_input == ":quit":
						sys.exit()
					settings_input_list = settings_input.replace(" ","").split("=")
					if settings_input_list[0] == "case_sensitive":
						if settings_input_list[1] == "True":
							case_sensitive = True
							settings_changed = True
						elif settings_input_list[1] == "False":
							case_sensitive = False
							settings_changed = True
						else:
							print("Error! Input for case_sensitive must be either True or False!")
					elif settings_input_list[0] == "end_indicator":
						if len(settings_input_list[1]) == 1:
							end_indicator = settings_input_list[1]
							settings_changed = True
						else:
							print("Error! end_indicator must be a single character!")
					elif settings_input_list[0] == "maximum_report":
						try:
							maximum_report = int(settings_input_list[1])
							settings_changed = True
						except:
							print("Error! maximum_report must be an integer!")
					elif settings_input_list[0] == "ignore_punctuation":
						if settings_input_list[1] == "True":
							ignore_punctuation = True
							settings_changed = True
						elif settings_input_list[1] == "False":
							ignore_punctuation = False
							settings_changed = True
						else:
							print("Error! Input for ignore_punctuation must be either True or False!")
						
					elif settings_input != ":done":
						print("Error! Input keyword not recognized!")
				
					if settings_changed:
						print("\nCurrent settings:")
						print("case_sensitive = " + str(case_sensitive))
						print("end_indicator = " + end_indicator)
						print("maximum_report = " + str(maximum_report))
						print("ignore_punctuation = " + str(ignore_punctuation))
						print("\nType :done to exit settings")
						settings_changed = False
			else:
				break
					
					
			
			
	
	else:
		path = sys.argv[1]

	if search is None:
		search = Simplesearch(path = path, end_indicator = end_indicator, case_sensitive = case_sensitive, maximum_report = maximum_report, ignore_punctuation = ignore_punctuation, tree = tree)
	print(str(len(search.filenames)) + " files read in directory " + path)
	while True:
		query_string = input("Please enter query or type :save to save your session\n> ")
		query_string = query_string.strip()
		if not search.case_sensitive:
			query_string = query_string.lower()
		if query_string == ":quit":
			break
		elif query_string == ":save":
			print("Please enter a path for saving your session:")
			try:
				search_path = input("> ")
				search_file = open(search_path, "wb")
				pickle.dump(search, search_file)
				print("Session saved succesfully!")
				search_file.close()
			except:
				print("Error! The session could not be stored at the given path!")
		if query_string.endswith("-p"):
			query_string = query_string[:-2]
			query_list = []
			for phrase_string in query_string.split(","):
				single_phrase_list = phrase_string.strip().split()
				query_list.append(single_phrase_list)
		elif query_string != ":save":
			query_list = []
			for word in query_string.split():
				query_list.append([word])
		
		if query_string != ":save":
			search.find_scores(query_list)
			search.reset_scores()
	


				
				
				
			