from urllib.request import urlopen
from bs4 import BeautifulSoup
from collections import OrderedDict

class Summarizer:
	"""Class that handles the summarizing for an article."""
	
	def __init__(self, url, keyword_limit, sentence_limit):
		"""
		Initialization function for this class.
		
		Parameters:
			1) url - url to visit to gather information
			2) keyword_limit - use this many keywords when using algorithm
			3) sentence_limit - floating percentange that limits the amount of sentences gathered
		"""
		
		self.url = url
		self.keyword_limit = keyword_limit
		self.sentence_limit = sentence_limit
		self.sent_count = None

		
	def clean_text(self):
		"""Clean up the text by removing whitespaces and various other unneeded material."""
		
		lines = []
		unclean_text = []
		buffer = []
		
		response = urlopen(self.url)
		html = response.read()
		soup = BeautifulSoup(html, "html.parser")
		
		# kill all script and style elements
		for script in soup(["script", "style"]):
			script.extract()  

		text = soup.get_text()
		
		#remove leading and trailing space on every line
		for line in text.splitlines():
			lines.append(line.strip())
			
		#split lines into singular lines
		for line in lines:
			for word in line.split("  "):
				unclean_text.append(word.strip())
				
		#remove empty lines
		for sent in unclean_text:
			if sent:	
				buffer.append(sent)
		
		#If a sentence is less than 100 characters long, remove them from the text
		text = self.shorten_text(buffer)
		
		#Re add spaces where it is necessary
		text = self.add_spaces(text)
		
		text = '\n'.join(text)

		return text
	
	
	def add_spaces(self, text):
		"""
		Function used to re-add spaces to the text since it was removed by splitlines.
		
		Parameters:
			1) text - the text to re-add spaces to
		"""
		
		count = 0
		spaced_text = []
		
		for sent in text:
			while count < len(sent) - 1:
				if sent[count] == "." and sent[count + 1] != " ":
					sent = sent[0:count + 1] + " " + sent[count+1:]
				count += 1
			spaced_text.append(sent)
		
			
		return spaced_text	
	
	
	def shorten_text(self, text):
		"""
		Function used to remove short sentences since they are either invalid or not important.
		
		Parameters:
			1) text - the text to shorten
		"""
		
		new_list = []
		
		for sent in text:
			if len(sent) > 100:
				new_list.append(sent)
				
		return new_list

		
	def ignored_word(self, word):
		with open("ignored_words/ignored_words.txt", "r") as ignored_words:
			for ignored_word in ignored_words:
				if word == ignored_word.strip():
					return False
					
		return True
	
	
	def grab_keywords(self, text):
		"""
		Function used to obtain the keywords for the article.
		
		Parameters:
			1) text - the text to gather keywords from.
		"""
			
		dict = {}
		keywords = []
		counter = 0
		
		for sent in text:
			split_text = sent.split()
			for word in split_text:
				#Check to see if the word is common and check if it is a proper noun.
				if self.ignored_word(word) and word[0].isupper():
					#if the word is in the dictionary, increment it
					if word in dict:
						dict[word] += 1
					
					#if the word is not in the dictionary, add it as an entry
					else:
						dict[word] = 0
			
		#Check and remove duplicates from the dictionary
		dict = self.check_duplicates(dict)
				
		#Order the dictionary so the words with the most occurence is at the top
		dict = OrderedDict(sorted(dict.items(), key=lambda t: t[1], reverse=True))
		
		#Place these words into a list
		for k, v in dict.items():
			if counter != self.keyword_limit:
				keywords.append(k)
				counter += 1
		
		return keywords

		
	def check_duplicates(self, dict):
		"""
		Function that will check and remove duplicates from a dictionary.
		
		Parameters:
			1) dict - the dictionary to remove duplicate words from
		"""
		
		count = 0
		dup_list = []
		
		#Create an ordered dictionary
		dict = OrderedDict(sorted(dict.items(), key=lambda t: t[1], reverse=True))
		
		#Place all of the words in the dictionary into a list
		dup_list.append(list(dict.items())[0][0])

		#Compare the dictionary and list and remove the duplicates
		for k, v in dict.items():
			for word in dup_list:
				if word != k:
					if k.find(word) != -1:
						dict[k] = 0
		
		#Sort the dictionary again
		dict = OrderedDict(sorted(dict.items(), key=lambda t: t[1], reverse=True))
		
		return dict
		
		
	def grab_summary(self, text):
		"""
		Driver function that will gather the summary to return.
		
		Parameters:
			1) text - text to obtain summary from.
		"""
		
		summary = []

		#Mark the end of paragraphs in order to group properly
		text = self.mark_end_of_paragraphs(text)
		
		text = self.split_text(text)
		
		self.sent_count = len(text)
		
		#Obtain the keywords
		keywords = self.grab_keywords(text)
	
		#Gather the best ranked sentences by indices
		best_sentences = self.rank_sentences(text, keywords)
		
		#Append the actual sentences to a list
		for index in best_sentences:
			summary.append(str(text[index]))
			
		
		#Attempt to group the sentences together in paragraphs
		summary = self.group_summary(summary)
		
		return summary
	
	
	def group_summary(self, summary):
		"""
		Function that groups the sentences together into paragraphs.
		
		Parameters:
			1) summary - text to reform into paragraphs
		"""
		
		grouped_summary = []
		s = ""
		
		#Using '@' as a special character to denote where paragraphs used to be
		for sent in summary:
			if s.find("@") != -1:
				s = s.replace("@", "  ")
				grouped_summary.append(str(s))
				s = ""
			s += sent
			
		if len(grouped_summary) == 0:
			return summary
			
		return grouped_summary
	
	
	def split_text(self, text):
		"""
		Function that splits text up.
		
		Parameters:
			1) text - the text to split up.
		"""
		
		sentences = []
		buffer = []
		finalized_sentences = []
		puncts = [".", "?", "!"]
		
		#Replace words to avoid '.'.
		text = self.replace_text(text)
		
		for sent in text.splitlines():
			if self.has_punct(puncts, sent):
				sentences.append(sent)
		
		counter = 0
		for sent in sentences:
			if sent.find("!") != -1:
				fs = sent.split("! ")
			
			elif sent.find("?") != -1:
				fs = sent.split("? ")
			
			else:
				fs = sent.split(". ")
			
			buffer.append(fs)
		
		#Gather the sentences to group and place periods at the right spots
		for s in buffer:	
			for t in s:
				if t != "" and len(t) > 100 and t.find("@") != -1:
					finalized_sentences.append(t)
				elif t != "" and len(t) > 100:
					finalized_sentences.append(t + ". ")
		
		count = 0

		return finalized_sentences
	
	
	def replace_text(self, text):
		"""
		Function used to replace words such as Mrs., Dr. to avoid confusing program.
		
		Parameters:
			1) text - the text to re-add spaces to
		"""
		
		with open("replaced_words/replaced_words.txt", "r") as replaced_words:
			for word in replaced_words:
				delimiter = word.find("=")
				replaced_word = word[0:delimiter]
				replacer = word[delimiter+1:]
				
				text = text.replace(replaced_word, replacer)
				
		return text
	
	
	def has_punct(self, puncts, sent):
		"""
		Check to see if the sentence has punctuations.
		
		Parameters:
			1) puncts - list containing '.', '?' '!'
			2) sent - the sentence to check
		"""
		for punct in puncts:
			if sent.find(punct) != -1:
				return True
				
		return False
	
	
	def rank_sentences(self, text, keywords):
		"""
		Function that will rank the sentences by occurence of keywords.
		
		Parameters:
			1) text - the text to check
			2) keywords - use these to gather the rank the sentences
		"""
		
		sentence_dict = {}
		sentence_count = 0
		best_sentences = []
		count = 0
		
		for sent in text:
			#Check to see how many keywords this sentence has
			rank = self.check_keywords(sent, keywords)
			
			#Create a dictionary that will hold the sentence and their rank
			sentence_dict[sentence_count] = rank
			sentence_count += 1
		
		sentence_dict = OrderedDict(sorted(sentence_dict.items(), key=lambda t: t[1], reverse=True))
		
		#Gather the best sentences
		for key, value in sentence_dict.items():
			if count < self.sentence_limit * self.sent_count:
				best_sentences.append(key)
			count += 1
			
		best_sentences.sort()
		
		return best_sentences
		
			
	def check_keywords(self, sent, keywords):
		"""
		Function that will check the sentences and keywords.
		
		Parameters:
			1) sent - the sentence to check
			2) keywords - keywords to check sentence against
		"""
		
		rank = 0
		split_sent = sent.split()
		
		for word in split_sent:
			if keywords.count(word) > 0:
				rank += 1
		
		return rank

		
	def mark_end_of_paragraphs(self, text):
		"""
		Function that will place '@' to denote the end of paragraphs in the original text.
		
		Parameters:
			1) text - the text to check
		"""
		
		text = text.replace("\n", "@\n")
		return text
	
	
	def print_summary(self, summary):
		"""
		Function to print the summary.
		
		Parameters:
			1) summary - the summary to print to the text file
		"""
		
		with open("encoded.txt", "ab") as encoder:
			for sent in summary:
				encoder.write(("\t" + sent + "\n").encode('utf-8'))	
