# Content-Generator.py
# SOFTWARE ENGINEERING I (CS_361_400_W2021) Assignment 3
# Author: Matthew Spencer
# Date: Feb 14, 2021

import sys
import textwrap
import tkinter as tk
import requests
from bs4 import BeautifulSoup
import csv


# CG Service provides the get_content function that fetches content from wikipedia
# and matches paragraphs against keywords.
class ContentGeneratorService:
	# get content matching primary and secondary keywords, return content or error message.
	def get_content(self, primary, secondary):
		paragraph_error = False
		content, fetch_error = self.get_wiki_page_content(primary)
		if fetch_error:
			paragraph = content
		else:
			paragraph, paragraph_error = self.get_keywords_paragraph(content, primary, secondary)
		return paragraph

	# Perform HTTP call to get page from Wikidpedia. Return content or error message
	@staticmethod
	def get_wiki_page_content(keyword):
		print(f"getting wiki page for: {keyword}")
		url = f"https://en.wikipedia.org/wiki/{keyword}"
		r = requests.get(url)
		if r.status_code != 200:
			print(f"Keyword: {keyword} did not return a HTTP 200 Status. Received: {r.status_code}")
			return '', True
		else:
			return r.text, False

	@staticmethod
	def get_keywords_paragraph(page_html, primary_keyword, secondary_keyword):
		soup = BeautifulSoup(page_html, 'html.parser')
		body_content = soup.find(id="bodyContent")
		paragraphs_html = body_content.find_all('p')
		paragraphs_text = []
		for p in paragraphs_html:
			paragraphs_text.append(p.text.strip())

		primary_lower = primary_keyword.lower()
		secondary_lower = secondary_keyword.lower()
		for p in paragraphs_text:
			p_lower = p.lower()
			if primary_lower in p_lower and secondary_lower in p_lower:
				return p, False

		return '', True


# Tkinter App Class
class ContentGeneratorApp(tk.Frame):

	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent = parent

		self.frame = tk.Frame(master=parent, width=540, height=640, bg="white")
		self.frame.pack()

		# Primary Keyword
		self.lbl_primary = tk.Label(master=self.frame, text="Primary Keyword:")
		self.lbl_primary.place(x=20, y=13)

		self.ent_primary = tk.Entry(master=self.frame, width=20)
		self.ent_primary.place(x=160, y=10)
		self.ent_primary.bind("<KeyRelease>", self.validate_keywords_populated)

		# Secondary Keyword
		self.lbl_secondary = tk.Label(master=self.frame, text="Secondary Keyword:")
		self.lbl_secondary.place(x=20, y=43)

		self.ent_secondary = tk.Entry(master=self.frame, width=20)
		self.ent_secondary.place(x=160, y=40)
		self.ent_secondary.bind("<KeyRelease>", self.validate_keywords_populated)

		# Generate Button
		# Note that there is a bug with tkinter and Mac OS Mojave in Dark mode.
		# Please use light mode if the button doesn't show.
		# https://stackoverflow.com/questions/52529403/button-text-of-tkinter-does-not-work-in-mojave
		self.btn_submit = tk.Button(master=self.frame,  text="Generate Content", command=self.submit)
		self.btn_submit.place(x=380, y=40)
		self.btn_submit.config(state=tk.DISABLED)

		# Text output area
		self.txt_box = tk.Text(master=self.frame, width=70, height=33 )
		self.txt_box.place(x=20, y=90)
		self.txt_box.config(state=tk.DISABLED)

	# Get keyword entry values, fetch the content, insert it into the output textbox
	def submit(self):
		primary = self.ent_primary.get()
		secondary = self.ent_secondary.get()
		cg_service = ContentGeneratorService()
		paragraph = cg_service.get_content(primary, secondary)

		keywords = f"{primary};{secondary}"
		output_rows = [dict({'input_keywords': keywords, 'output_content': paragraph})]
		write_output_file(output_rows)
		self.txt_box.config(state=tk.NORMAL)
		self.txt_box.delete("1.0", tk.END)
		self.txt_box.insert(tk.END, '\n'.join(textwrap.wrap(paragraph, 70)))
		self.txt_box.config(state=tk.DISABLED)

	# Checks both primary and secondary entries. Updates the "Generate Content" button state.
	def validate_keywords_populated(self, event):
		if len(self.ent_primary.get()) > 0 and len(self.ent_secondary.get()) > 0:
			if self.btn_submit.cget('state') == tk.DISABLED:
				self.btn_submit.config(state=tk.NORMAL)
		else:
			if self.btn_submit.cget('state') == tk.NORMAL:
				self.btn_submit.config(state=tk.DISABLED)


def write_output_file(output_rows):
	with open('output.csv', mode='w') as output_csv:
		fieldnames = ['input_keywords', 'output_content']
		output_csv_writer = csv.DictWriter(output_csv, fieldnames=fieldnames, delimiter=',', quotechar='"',
										   quoting=csv.QUOTE_MINIMAL)
		output_csv_writer.writeheader()
		for row in output_rows:
			output_csv_writer.writerow(row)


if __name__ == "__main__":

	# Count args. Print usage text if needed.
	if len(sys.argv) != 1 and len(sys.argv) != 2:
		print("Usage: python content-generator.py ")
		print("       python content-generator.py input.csv")

	# If no input file is specified, run the GUI.
	if len(sys.argv) == 1:
		window = tk.Tk()
		ContentGeneratorApp(window).pack(expand=True)
		window.mainloop()

	# If input csv file is included, process file. (No input file validation performed)
	if len(sys.argv) == 2:
		cg_service = ContentGeneratorService()
		outputs = []
		with open(sys.argv[1]) as input_csv:
			input_csv_reader = csv.reader(input_csv, delimiter=',')
			line_count = 0
			for row in input_csv_reader:
				line_count += 1
				if line_count > 1:
					keyword1, keyword2 = row[0].split(';')
					content = cg_service.get_content(keyword1, keyword2)
					outputs.append(dict({'input_keywords': row[0], 'output_content': content}))

		write_output_file(outputs)
