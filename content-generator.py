# Content-Generator.py
# SOFTWARE ENGINEERING I (CS_361_400_W2021) Assignment 3
# Author: Matthew Spencer
# Date: Feb 27, 2021

import sys
import textwrap
import tkinter as tk
import requests
from bs4 import BeautifulSoup
import csv
import subprocess
import re
import os


# CG Service provides the get_content function that fetches content from wikipedia
# and matches paragraphs against keywords.
class ContentGeneratorService:
    # get content matching primary and secondary keywords, return content or error message.
    def get_content(self, primary, secondary):
        paragraph_error = False
        wiki_page_content, fetch_error = self.get_wiki_page_content(primary)
        if fetch_error:
            wiki_page_paragraph = wiki_page_content
        else:
            wiki_page_paragraph, paragraph_error = self.get_keywords_paragraph(wiki_page_content,
                                                                               primary, secondary)
        return wiki_page_paragraph

    def get_content_from_list(self, keywords):
        paragraph = ''
        primary = ''
        secondary = ''
        paragraph_found = False
        for wiki_page_keyword in keywords:
            if paragraph_found:
                break

            page_html, fetch_err = self.get_wiki_page_content(wiki_page_keyword)
            if not fetch_err:
                for keyword in keywords:
                    if keyword != wiki_page_keyword:
                        paragraph, search_err = self.get_keywords_paragraph(
                            page_html,  wiki_page_keyword,  keyword)
                        if not search_err:
                            primary = wiki_page_keyword
                            secondary = keyword
                            paragraph_found = True
                            break

        return paragraph, primary, secondary, (not paragraph_found)

    # Perform HTTP call to get page from Wikidpedia. Return content or error message
    @staticmethod
    def get_wiki_page_content(keyword):
        print(f"getting wiki page for: {keyword}")
        url = f"https://en.wikipedia.org/wiki/{keyword}"
        r = requests.get(url)
        if r.status_code != 200:
            print(f"Keyword: {keyword} did not return a HTTP 200 Status. Received:{r.status_code}")
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


# Life Generator Service provides the query function that fetches results from life generator
# and matches paragraphs against keywords.
class LifeGeneratorService:
    def __init__(self, _lg_app_dir):
        self.lg_app_dir = _lg_app_dir

    # Write input.csv file, with headers & 1 line, for life generator input.
    def _write_input_csv(self, toy_category, result_number):
        with open(f"{self.lg_app_dir}/input.csv", mode='w') as lg_input_csv:
            fieldnames = ['input_item_type', 'input_item_category', 'input_number_to_generate']
            lg_input_csv_writer = csv.DictWriter(
                    lg_input_csv, fieldnames=fieldnames, delimiter=',',
                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            lg_input_csv_writer.writeheader()
            lg_input_csv_writer.writerow(
                    dict({'input_item_type': 'toys', 'input_item_category': toy_category,
                          'input_number_to_generate': result_number}))

    # Get the results from life generator service: read the life-output.csv.
    def _read_output_csv(self):
        lg_outputs = []
        with open(f"{self.lg_app_dir}/life-output.csv") as lg_output_csv:
            lg_output_csv_reader = csv.reader(lg_output_csv, delimiter=',')
            lg_line_count = 0
            for row in lg_output_csv_reader:
                lg_line_count += 1
                if lg_line_count > 1:
                    lg_outputs.append(row)

        return lg_outputs

    def get_life(self, toy_category, result_number):
        # Set input for life generator service
        self._write_input_csv(toy_category, result_number)

        # Exec life-generator.py
        args = ("python3.9", f"{self.lg_app_dir}/life-generator.py", "input.csv")
        popen = subprocess.Popen(args, stdout=subprocess.PIPE, cwd=f"{self.lg_app_dir}")
        popen.wait()

        # Get the results from life generator output.csv file and return as array.
        return self._read_output_csv()

    def get_categories(self):
        # Exec life-generator.py
        args = ("python3.9", f"{self.lg_app_dir}/life-generator.py", "--categories")
        popen = subprocess.Popen(args, stdout=subprocess.PIPE, cwd=f"{self.lg_app_dir}")
        popen.wait()

        # return array of results read from output.csv (normalize categories)
        categories = []
        categories_list = self._read_output_csv()
        for category in categories_list:
            categories.append(category[0])
        return categories

    @staticmethod
    def get_keywords(life_results):
        # Ignore commons words like prepositions
        ignore_words = ['aboard', 'about', 'above', 'across', 'after', 'against', 'along', 'amid',
                        'among', 'anti', 'around', 'as', 'at', 'before', 'behind', 'below',
                        'beneath', 'beside', 'besides', 'between', 'beyond', 'but', 'by',
                        'concerning', 'considering', 'despite', 'down', 'during', 'except',
                        'excepting', 'excluding', 'following', 'for', 'from', 'in', 'inside',
                        'into', 'like', 'minus', 'near', 'of', 'off', 'on', 'onto', 'opposite',
                        'outside', 'over', 'past', 'per', 'plus', 'regarding', 'round', 'save',
                        'since', 'than', 'through', 'to', 'toward', 'towards', 'under',
                        'underneath', 'unlike', 'until', 'up', 'upon', 'versus', 'via', 'with',
                        'within', 'without', 'a', 'the']
        keywords = set()
        print(life_results)
        for result in life_results:
            description = result[3]
            for word in description.split():
                word = re.sub(r'\W+', '', word)
                if len(word) > 0 and word not in ignore_words:
                    keywords.add(word)

        return keywords


# Tkinter App Class for Life Content Generator
class LifeContentGeneratorApp(tk.Frame):

    def __init__(self, parent, _lg_app_dir, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.title("Life Content Generator")
        self.life_gen_service = LifeGeneratorService(_lg_app_dir)
        self.categories = self.life_gen_service.get_categories()
        self.content_gen_service = ContentGeneratorService()

        self.frame = tk.Frame(master=parent, width=640, height=670, bg="white")
        self.frame.pack()

        # Keyword positioning
        keyword_label_x = 20
        keyword_label_y = 13
        keyword_ent_x = 160
        keyword_ent_y = 10

        # Render the modified Life Content Generator App layout
        # create the option drop down
        self.lbl_categories = tk.Label(master=self.frame, text="Category Filter")
        self.lbl_categories.place(x=keyword_label_x, y=keyword_label_y)

        self.selection_category = tk.StringVar(self.parent)
        self.selection_category.set(self.categories[0])

        self.opt_categories = tk.OptionMenu(self.frame, self.selection_category, *self.categories)
        self.opt_categories.place(x=keyword_ent_x, y=keyword_ent_y)
        self.opt_categories.config(width=20)

        # Primary Keyword
        self.lbl_number = tk.Label(master=self.frame, text="Number of Results")
        self.lbl_number.place(x=keyword_label_x, y=keyword_label_y + 30)

        self.ent_number = tk.Entry(master=self.frame, width=20)
        self.ent_number.place(x=keyword_ent_x, y=keyword_ent_y + 30)
        self.ent_number.bind("<KeyRelease>", self.validate_number_populated)

        # Generate Button
        # Note that there is a bug with tkinter and Mac OS Mojave in Dark mode.
        # Please use light mode if the button doesn't show.
        # https://stackoverflow.com/questions/52529403/button-text-of-tkinter-does-not-work-in-mojav
        self.btn_submit = tk.Button(master=self.frame, text="Generate Content", command=self.submit)
        self.btn_submit.place(x=480, y=40)
        self.btn_submit.config(state=tk.DISABLED)

        # Text output area for Life
        self.txt_life = tk.Text(master=self.frame, width=84, height=12)
        self.txt_life.place(x=20, y=90)
        self.txt_life.config(state=tk.DISABLED, background="#eee")

        # Text output area for Content
        self.txt_content = tk.Text(master=self.frame, width=84, height=23)
        self.txt_content.place(x=20, y=280)
        self.txt_content.config(state=tk.DISABLED, background="#eee")

    # Get life generator input values, query life generator service
    def submit(self):
        category = self.selection_category.get()
        res_number = self.ent_number.get()
        life_results = self.life_gen_service.get_life(category, res_number)
        life_keywords = self.life_gen_service.get_keywords(life_results)

        life_results_text = ""
        for result in life_results:
            life_results_text += ' '.join(result) + '\n'

        self.txt_life.config(state=tk.NORMAL)
        self.txt_life.delete("1.0", tk.END)
        # self.txt_life.insert(tk.END, '\n'.join(textwrap.wrap(life_results_text, 84)))
        self.txt_life.insert(tk.END, life_results_text)
        self.txt_life.config(state=tk.DISABLED)

        paragraph, primary, secondary, par_err = self.content_gen_service.get_content_from_list(
                life_keywords)

        output_rows = [dict({'input_keywords': f"{primary};{secondary}",
                             'output_content': paragraph})]
        write_output_file(output_rows)
        self.txt_content.config(state=tk.NORMAL)
        self.txt_content.delete("1.0", tk.END)
        self.txt_content.insert(tk.END, '\n'.join(textwrap.wrap(paragraph, 84)))
        self.txt_content.config(state=tk.DISABLED)

    # Checks number entry. Updates the "Generate Content" button state.
    def validate_number_populated(self, event):
        try:
            int(self.ent_number.get())
            if self.btn_submit.cget('state') == tk.DISABLED:
                self.btn_submit.config(state=tk.NORMAL)
        except ValueError:
            if self.btn_submit.cget('state') == tk.NORMAL:
                self.btn_submit.config(state=tk.DISABLED)


# Tkinter App Class for Content Generator
class ContentGeneratorApp(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.title("Content Generator")

        self.frame = tk.Frame(master=parent, width=540, height=640, bg="white")
        self.frame.pack()

        # Keyword positioning
        keyword_label_x = 20
        keyword_label_y = 13
        keyword_ent_x = 160
        keyword_ent_y = 10

        # Render the original Content Generator App layout
        # Primary Keyword
        self.lbl_primary = tk.Label(master=self.frame, text="Primary Keyword:")
        self.lbl_primary.place(x=keyword_label_x, y=keyword_label_y)

        self.ent_primary = tk.Entry(master=self.frame, width=20)
        self.ent_primary.place(x=keyword_ent_x, y=keyword_ent_y)
        self.ent_primary.bind("<KeyRelease>", self.validate_keywords_populated)

        # Secondary Keyword
        self.lbl_secondary = tk.Label(master=self.frame, text="Secondary Keyword:")
        self.lbl_secondary.place(x=keyword_label_x, y=keyword_label_y + 30)

        self.ent_secondary = tk.Entry(master=self.frame, width=20)
        self.ent_secondary.place(x=keyword_ent_x, y=keyword_ent_y + 30)
        self.ent_secondary.bind("<KeyRelease>", self.validate_keywords_populated)

        # Generate Button
        # Note that there is a bug with tkinter and Mac OS Mojave in Dark mode.
        # Please use light mode if the button doesn't show.
        # https://stackoverflow.com/questions/52529403/button-text-of-tkinter-does-not-work-in-mojav
        self.btn_submit = tk.Button(master=self.frame, text="Generate Content", command=self.submit)
        self.btn_submit.place(x=380, y=40)
        self.btn_submit.config(state=tk.DISABLED)

        # Text output area
        self.txt_box = tk.Text(master=self.frame, width=70, height=33)
        self.txt_box.place(x=20, y=90)
        self.txt_box.config(state=tk.DISABLED)

    # Get keyword entry values, fetch the content, insert it into the output textbox
    def submit(self):
        primary = self.ent_primary.get()
        secondary = self.ent_secondary.get()
        gui_cg_service = ContentGeneratorService()
        paragraph = gui_cg_service.get_content(primary, secondary)

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
    with open('content-output.csv', mode='w') as output_csv:
        fieldnames = ['input_keywords', 'output_content']
        output_csv_writer = csv.DictWriter(output_csv, fieldnames=fieldnames, delimiter=',',
                                           quotechar='"', quoting=csv.QUOTE_MINIMAL)
        output_csv_writer.writeheader()
        for row in output_rows:
            output_csv_writer.writerow(row)


if __name__ == "__main__":

    # If no input file or parameters are specified, run the Content Generator GUI App.
    if len(sys.argv) == 1:
        window = tk.Tk()
        ContentGeneratorApp(window).pack(expand=True)
        window.mainloop()

    # If the --life-content-generator parameter is present, run the Life Content Generator GUI App.
    elif len(sys.argv) == 2 and ("--life-content-generator" in sys.argv[1]):
        window = tk.Tk()
        lg_app_dir = os.path.dirname(os.path.realpath(__file__))
        lg_app_arg = sys.argv[1].split('=')
        if len(lg_app_arg) == 2:
            lg_app_dir = lg_app_arg[1]

        LifeContentGeneratorApp(window, lg_app_dir).pack(expand=True)
        window.mainloop()

    # If an input csv file is included, process file. (No input file validation performed)
    elif len(sys.argv) == 2 and (sys.argv[1][-4:] == ".csv"):
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

    # If we get here, we haven't matched on valid parameters. Print usage text.
    else:
        print("Usage: python content-generator.py")
        print("       python content-generator.py input.csv")
        print("       python content-generator.py --life-content-generator=/dir/for/life_gen_app")
