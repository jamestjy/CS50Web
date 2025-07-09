from django.shortcuts import render
from markdown2 import Markdown
from . import util

def convery_md_to_html(title):
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
def css(request):
    return render(request, "encyclopedia/css.html", {
        "css_content": convery_md_to_html("CSS")})

