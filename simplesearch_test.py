from simplesearch import Simplesearch, Tree, Node
from os import listdir
from os.path import isfile
import sys

# Oystein Kapperud, 2019

"""
A file for testing whether the information stored in the tree structure is representative of the original files (see README).
"""

def test_word_retrieval(path):
	# create tree structure		
	search = Simplesearch(path = path, ignore_punctuation = False)
	
	# store words directly without creating a tree structure:
	if not path.endswith("/"):
		path += "/"
	try:
		filenames = [filename for filename in listdir(path) if (isfile(path + filename) and filename.endswith(".txt"))]
	except:
		print("Error! Directory not found!")
		sys.exit()
	direct_words = {}
	for filename in filenames:
		direct_words[filename] = []
		file_path = path + filename
		infile = open(file_path, "r")
		for line in infile:
			for word in line.split():
				if search.ignore_punctuation:
					word.replace(".","")
					word.replace(",","")
					word.replace("!","")
					word.replace(":","")
					word.replace(";","")
					word.replace("?","")
					word.replace("(","")
					word.replace(")","")
				if not search.case_sensitive:
					word = word.lower()
				direct_words[filename].append(word)
	
	
	
	# retrieve words from tree structure:
	search.tree.initialize_word_lists(search.word_counts)
	retrieved_words = search.tree.retrieve_words()
	discrepancy_found = False
	for filename in retrieved_words:
		if not retrieved_words[filename] == direct_words[filename]:
			discrepancy_found = True
			break
			
	if not discrepancy_found:
		print("All words retrieved succesfully!")
	else:
		print("Oh no! The retrieved words are not the same as those read directly. Something is wrong!Time to debug!")


if __name__ == '__main__':
	try:
		test_word_retrieval(sys.argv[1])
	except:
		print("Please indicate a directory after the file name")