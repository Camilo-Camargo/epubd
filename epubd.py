from bs4 import BeautifulSoup
from html.parser import HTMLParser
from io import StringIO

from ebooklib import epub
from ebooklib import ITEM_DOCUMENT
from ebooklib.epub import EpubBook     

from sys import argv 
from os import mkdir

class StripHtml(HTMLParser):
    __text = ""
    def __init__(self, html):
        super().__init__()
        self.feed(repr(html)) 

    def handle_data(self, data):
        self.__text += data
    def get_text(self):
        return self.__text

def dc_metadata(book: EpubBook, tag: str) -> str:
    return  book.get_metadata('DC', tag)[0][0]

def markdown_copyright(book: EpubBook):
    title       = dc_metadata(book, 'title')
    description = dc_metadata(book, 'description')
    author      = dc_metadata(book, 'creator') 
    isbn        = dc_metadata(book, 'identifier')
    publisher   = dc_metadata(book, 'publisher')
    date        = dc_metadata(book, 'date')

    sh = StripHtml(description)
    description = sh.get_text()[1:-1] 

    readme = f"""\
# {title} \n
{description} \n 
**Author**: {author}\n
**ISBN**: {isbn}\n
**Date**: {date}\n
**Publisher**: {publisher}<br>\
"""
    return readme  
chapters_header = [
    "Foreword",
    "Preface",
    "Acknowledgments",
    "Bibliography"
]

def chapters(book: EpubBook):
    global chapters_header
    documents = book.get_items_of_type(ITEM_DOCUMENT)
    _documents = []
    _chapters = []
    for document in documents:
        if(document.is_chapter()):
            bs = BeautifulSoup(document.get_content(), 'html.parser')
            chapter = bs.find('h1')
            if chapter: chapter = chapter.get_text() 
            if(chapter not in chapters_header and chapter): 
                _chapters.append(chapter)
                _documents.append(document)

    return (_chapters, _documents)

def chapter_dir(chapter: str) -> str:
    return chapter.replace(' ', '_').lower()
 
def readme(book): 
    markdown = markdown_copyright(book)
    _chapters = chapters(book)[0]
    markdown += "<details>"
    markdown += "<summary>Chapters</summary>"
    for i,chapter in enumerate(_chapters):
        markdown += f"{i+1}. [{chapter}]({i+1}_{chapter_dir(chapter)})<br>"

    markdown += "</details>"
    with open("README.md", "w") as f:
        f.write(markdown)

 
def usage():
    print(f"""\
Usage:
{argv[0]} filename\
""")
    exit()

if(__name__ == "__main__"): 
    if(len(argv) <= 1):
        usage()

    filename = argv[1] 
    book = None
    try:
        book = epub.read_epub(filename) 
    except FileNotFoundError as e: 
        print(e)
        exit()


    readme(book)
    mkdir("notes")
    for i,chapter in enumerate(chapters(book)[0]):
        title = chapter
        title_dir = chapter.replace(' ', '_').lower() 
        path = f"notes/{i+1}_{title_dir}"
        mkdir(path)
        with open(f"{path}/README.md", 'w') as f:
            f.write(f"# {title}\n")
    print("Go to study!")

