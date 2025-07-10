from django.shortcuts import render
from markdown2 import Markdown
from . import util

def convert_md_to_html(title):
    markdowner = Markdown()
    content = util.get_entry(title)
    if content == None:
        return None
    else:
        return markdowner.convert(content)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# try to change this to fit every md file, using <str:title>
def page(request, title):
    content = convert_md_to_html(title.lower())
    if content is None:
        return render(request, "encyclopedia/404.html", {
            "title": title.lower()
        }, status=404)
    
    else:
        return render(request, "encyclopedia/entry.html", {
            "content": content, "title": title.lower()})

