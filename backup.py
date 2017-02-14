from urllib.request import urlopen
from bs4 import BeautifulSoup
from collections import OrderedDict

class Summarizer:
	def __init__(self, url, keyword_limit, sentence_limit):
		self.url = url
		self.keyword_limit = keyword_limit
		self.sentence_limit = sentence_limit
		self.sent_count = None

	def clean_text(self):
		lines = []
		unclean_text = []
		buffer = []
		
		response = urlopen(self.url)
		html = response.read()
		soup = BeautifulSoup(html, "html.parser")
		
		#q = soup.findAll(text=True)
		#for s in q:
		#	print(s.encode('utf-8'))

		# kill all script and style elements
		for script in soup(["script", "style"]):
			script.extract()  

		text = soup.get_text()
		
		#text = self.add_spaces(text)
		
		#self.print_summary(text)
		
		
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
				
		#self.print_summary(buffer)
		
		text = '\n'.join(buffer)

		#self.print_summary(text)
		return text
		
	def add_spaces(self, text):
		count = 0
		while count < len(text) - 1:
			if text[count] == "." and text[count + 1].isalpha():
				text = text[0:count] + " " + text[count:]
			print(text[count].encode('utf-8'))
			count += 1
			
		return text

	def ignored_word(self, word):
		with open("ignored_words/ignored_words.txt", "r") as ignored_words:
			for ignored_word in ignored_words:
				if word == ignored_word.strip():
					return False
					
		return True
		
	def grab_keywords(self, text):
		dict = {}
		keywords = []
		counter = 0
		
		for sent in text:
			split_text = sent.split()
			for word in split_text:
				if self.ignored_word(word) and word[0].isupper():
					if word in dict:
						dict[word] += 1
					
					else:
						dict[word] = 0
						
		dict = self.check_duplicates(dict)
				
		dict = OrderedDict(sorted(dict.items(), key=lambda t: t[1], reverse=True))
			
		for k, v in dict.items():
			if counter != self.keyword_limit:
				keywords.append(k)
				counter += 1
		
		return keywords

	def check_duplicates(self, dict):
		count = 0
		dup_list = []
		
		dict = OrderedDict(sorted(dict.items(), key=lambda t: t[1], reverse=True))
		
		dup_list.append(list(dict.items())[0][0])

		for k, v in dict.items():
			for word in dup_list:
				if word != k:
					if k.find(word) != -1:
						dict[k] = 0
		
		dict = OrderedDict(sorted(dict.items(), key=lambda t: t[1], reverse=True))
		return dict
		
		
	def grab_summary(self, text):
		summary = []

		text = self.mark_end_of_paragraphs(text)
		
		text = self.split_text(text)
		
		#for t in text:
		#	print(t.encode('utf-8'), len(t))
		self.sent_count = len(text)
		
		keywords = self.grab_keywords(text)
	
		#for k in keywords:
		#	print(k.encode('utf-8'))
	
		best_sentences = self.rank_sentences(text, keywords)
		
		for index in best_sentences:
			summary.append(str(text[index]))
			
		
		summary = self.group_summary(summary)
		
		return summary
	
	def group_summary(self, summary):
		grouped_summary = []
		s = ""
		
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
		sentences = []
		buffer = []
		finalized_sentences = []
		puncts = [".", "?", "!"]
		
		text = self.replace_text(text)
		
		for sent in text.splitlines():
			if self.has_punct(puncts, sent):
				sentences.append(sent)
		
		for sent in sentences:
			fs = sent.split(". ")
			buffer.append(fs)
		
		for s in buffer:	
			for t in s:
				if t != "" and len(t) > 100:
					finalized_sentences.append(t + ". ")
		
		count = 0
		
		#for sent in finalized_sentences:
		#	finalized_sentences[count] = finalized_sentences[count].replace("..", ".")
		#	count += 1
		
		return finalized_sentences
		
	def replace_text(self, text):
		with open("replaced_words/replaced_words.txt", "r") as replaced_words:
			for word in replaced_words:
				delimiter = word.find("=")
				replaced_word = word[0:delimiter]
				replacer = word[delimiter+1:]
				
				text = text.replace(replaced_word, replacer)
				
		return text
		
	def has_punct(self, puncts, sent):
		for punct in puncts:
			if sent.find(punct) != -1:
				return True
				
		return False
				
	def rank_sentences(self, text, keywords):
		sentence_dict = {}
		sentence_count = 0
		best_sentences = []
		count = 0
		
		for sent in text:
			rank = self.check_keywords(sent, keywords)
			sentence_dict[sentence_count] = rank
			sentence_count += 1
		
		sentence_dict = OrderedDict(sorted(sentence_dict.items(), key=lambda t: t[1], reverse=True))
		
		for key, value in sentence_dict.items():
			if count < self.sentence_limit * self.sent_count:
				best_sentences.append(key)
			count += 1
			
		best_sentences.sort()
		
		return best_sentences
		
			
	def check_keywords(self, sent, keywords):
		rank = 0
		split_sent = sent.split()
		
		for word in split_sent:
			if keywords.count(word) > 0:
				rank += 1
		
		return rank

	def mark_end_of_paragraphs(self, text):
		text = text.replace("\n", "@\n")
		return text
		
	def print_summary(self, summary):
		with open("encoded.txt", "wb") as encoder:
			for sent in summary:
				encoder.write(("\t" + sent + "\n").encode('utf-8'))	

		
def print_summary(summary):
	with open("encoded.txt", "wb") as encoder:
		for sent in summary:
			encoder.write(("\t" + sent + "\n").encode('utf-8'))	
			
def main():
	url = "https://www.sciencenewsforstudents.org/article/zombies-are-real"
	#url = "https://en.wikipedia.org/wiki/Ant"
	#url = "http://residentevil.wikia.com/wiki/Chris_Redfield"
	#url = "https://www.yahoo.com/news/obama-confident-could-won-white-house-again-151602530.html"


	#url = "http://www.popsci.com/can-classic-thought-experiment-explain-trumps-win"
	
	#url = "http://bleach.wikia.com/wiki/Ichigo_Kurosaki"
	
	#url = "http://www.popsci.com/neanderthals-may-have-given-us-genital-warts"
	
	#url = "http://bleach.wikia.com/wiki/Aizen"
	
	summarizer = Summarizer(url, 25, 0.5)
	
	text = summarizer.clean_text()
	
	summary = summarizer.grab_summary(text)
	
	#print_summary(summary)
	
if __name__ == "__main__":
	main()
	
	
from urllib.request import urlopen
from bs4 import BeautifulSoup
from collections import OrderedDict

class Summarizer:
	def __init__(self, url, keyword_limit, sentence_limit):
		self.url = url
		self.keyword_limit = keyword_limit
		self.sentence_limit = sentence_limit
		self.sent_count = None

	def clean_text(self):
		lines = []
		unclean_text = []
		buffer = []
		
		response = urlopen(self.url)
		html = response.read()
		soup = BeautifulSoup(html, "html.parser")
		
		#q = soup.findAll(text=True)
		#for s in q:
		#	print(s.encode('utf-8'))

		# kill all script and style elements
		for script in soup(["script", "style"]):
			script.extract()  

		text = soup.get_text()
		
		#text = self.add_spaces(text)
		
		#self.print_summary(text)
		
		
		#remove leading and trailing space on every line
		for line in text.splitlines():
			lines.append(line.strip())
			
		
		
		#split lines into singular lines
		#for line in lines:
		#	for word in line.split("  "):
		#		unclean_text.append(word.strip())
				
		#self.print_summary(lines)
		#remove empty lines
		for sent in lines:
			if sent:	
				buffer.append(sent)
				
		#self.print_summary(buffer)
		
		#text = '\n'.join(buffer)

		#self.print_summary(buffer)
		#return text
		#self.print_summary(buffer)
		
		text = self.shorten_text(buffer)
		
		text = self.add_spaces(text)
		
		#self.print_summary(text)
		
		return text
		
	def add_spaces(self, text):
		count = 0
		spaced_text = []
		
		for sent in text:
			while count < len(sent) - 1:
				if sent[count] == "." and sent[count + 1] != " ":
					sent = sent[0:count + 1] + " " + sent[count+1:]
					#print("TEST")
				count += 1
			spaced_text.append(sent)
		
			
		return spaced_text

	def ignored_word(self, word):
		with open("ignored_words/ignored_words.txt", "r") as ignored_words:
			for ignored_word in ignored_words:
				if word == ignored_word.strip():
					return False
					
		return True
		
	def grab_keywords(self, text):
		dict = {}
		keywords = []
		counter = 0
		
		for sent in text:
			split_text = sent.split()
			for word in split_text:
				if self.ignored_word(word) and word[0].isupper():
					if word in dict:
						dict[word] += 1
					
					else:
						dict[word] = 0
						
		dict = self.check_duplicates(dict)
				
		dict = OrderedDict(sorted(dict.items(), key=lambda t: t[1], reverse=True))
			
		for k, v in dict.items():
			if counter != self.keyword_limit:
				keywords.append(k)
				counter += 1
		
		return keywords

	def check_duplicates(self, dict):
		count = 0
		dup_list = []
		
		dict = OrderedDict(sorted(dict.items(), key=lambda t: t[1], reverse=True))
		
		dup_list.append(list(dict.items())[0][0])

		for k, v in dict.items():
			for word in dup_list:
				if word != k:
					if k.find(word) != -1:
						dict[k] = 0
		
		dict = OrderedDict(sorted(dict.items(), key=lambda t: t[1], reverse=True))
		return dict
		
	def shorten_text(self, text):
		new_list = []
		
		for sent in text:
			if len(sent) > 100:
				new_list.append(sent)
				
		return new_list
		
		
	def grab_summary(self, text):
		summary = []
	
		text = self.mark_end_of_paragraphs(text)
		
		#self.print_summary(text)
		
		text = self.split_text(text)
		
		#self.print_summary(text)
		
		#for t in text:
		#	print(t.encode('utf-8'), len(t))
		self.sent_count = len(text)
		
		keywords = self.grab_keywords(text)
	
		#for k in keywords:
		#	print(k.encode('utf-8'))
	
		best_sentences = self.rank_sentences(text, keywords)
		
		for index in best_sentences:
			summary.append(str(text[index]))
			
		#self.print_summary(summary)
		summary = self.group_summary(summary)
		self.print_summary(summary)
		
		return summary
	
	def group_summary(self, summary):
		grouped_summary = []
		s = ""
		
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
		sentences = []
		buffer = []
		finalized_sentences = []
		puncts = [".", "?", "!"]
		
		tex = self.replace_text(text)
		
		text = ""
		
		for line in tex:
			text += line
			text += "\n"
			
		
		for sent in text.splitlines():
			if self.has_punct(puncts, sent) and self.ignore_symbols(sent):
				sentences.append(sent)
			
		
		#print(sentences)
		#self.print_summary(sentences)
		
		for sent in sentences:
			split_list = sent.split(". ")
			for split_sent in split_list:
				finalized_sentences.append(split_sent + ". ")
			
		#self.print_summary(finalized_sentences)
		
		#for sent in sentences:
		#	fs = sent.split(". ")
		#	buffer.append(fs)
			
		#self.print_summary(fs)
		
		#for s in buffer:
		#	for sent in s:
		#		print(sent.encode('utf-8'))
		
		#for s in buffer:	
		#	for t in s:
		#		if t != "" and len(t) > 100:
		#			finalized_sentences.append(t + ". ")
		
		#self.print_summary(finalized_sentences)
		
		count = 0
		
		#for sent in finalized_sentences:
		#	finalized_sentences[count] = finalized_sentences[count].replace("..", ".")
		#	count += 1
		
		return finalized_sentences
		
	def replace_text(self, text):
		with open("replaced_words/replaced_words.txt", "r") as replaced_words:
			for word in replaced_words:
				delimiter = word.find("=")
				replaced_word = word[0:delimiter]
				replacer = word[delimiter+1:]
				
				#text = text.replace(replaced_word, replacer)
				
				
		return text
		
	def has_punct(self, puncts, sent):
		for punct in puncts:
			if sent.find(punct) != -1:
				return True
				
		return False
		
	def ignore_symbols(self, sent):
		symbols = ["&", "%", "#"]
		bool = None
		for symbol in symbols:
			if sent.find(symbol) != -1:
				return False
		
		return True
		
		
				
	def rank_sentences(self, text, keywords):
		sentence_dict = {}
		sentence_count = 0
		best_sentences = []
		count = 0
		
		for sent in text:
			rank = self.check_keywords(sent, keywords)
			sentence_dict[sentence_count] = rank
			sentence_count += 1
		
		sentence_dict = OrderedDict(sorted(sentence_dict.items(), key=lambda t: t[1], reverse=True))
		
		for key, value in sentence_dict.items():
			if count < self.sentence_limit * self.sent_count:
				best_sentences.append(key)
			count += 1
			
		best_sentences.sort()
		
		return best_sentences
		
			
	def check_keywords(self, sent, keywords):
		rank = 0
		split_sent = sent.split()
		
		for word in split_sent:
			if keywords.count(word) > 0:
				rank += 1
		
		return rank

	def mark_end_of_paragraphs(self, text):
		#text = text.replace("\n", "@\n")
		buffer = []
		
		for sent in text:
		
			#if sent.find("\n") != -1:
			#	print("????????????????????????????????")
			#sent = sent.replace("\n", "@\n")
			sent += "@"
			sent += "\n"
			#print(sent.encode('utf-8'))
			#print("\n")
			buffer.append(sent)
			
			
		#self.print_summary(buffer)
			
		return buffer
		
	def print_summary(self, summary):
		with open("encoded.txt", "wb") as encoder:
			for sent in summary:
				encoder.write(("\t" + sent + "\n").encode('utf-8'))	

		
def print_summary(summary):
	with open("encoded.txt", "wb") as encoder:
		for sent in summary:
			encoder.write(("\t" + sent + "\n").encode('utf-8'))	
			
def main():
	url = "https://www.sciencenewsforstudents.org/article/zombies-are-real"
	#url = "https://en.wikipedia.org/wiki/Ant"
	#url = "http://residentevil.wikia.com/wiki/Chris_Redfield"
	#url = "https://www.yahoo.com/news/obama-confident-could-won-white-house-again-151602530.html"


	#url = "http://www.popsci.com/can-classic-thought-experiment-explain-trumps-win"
	
	#url = "http://bleach.wikia.com/wiki/Ichigo_Kurosaki"
	
	#url = "http://www.popsci.com/neanderthals-may-have-given-us-genital-warts"
	
	#url = "http://bleach.wikia.com/wiki/Aizen"
	
	summarizer = Summarizer(url, 25, 0.5)
	
	text = summarizer.clean_text()
	
	summary = summarizer.grab_summary(text)
	
#	print_summary(summary)
	
if __name__ == "__main__":
	main()