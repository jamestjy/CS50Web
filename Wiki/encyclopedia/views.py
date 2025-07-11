from django.shortcuts import render
from markdown2 import Markdown
from . import util
import re

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

def page(request, title):
    content = convert_md_to_html(title.lower()) #used lower() since title=entry from index.html contains caps
    if content is None:
        # "title": title.lower()" passes in the lowercase title of the url
        # to 404.html template, as variable called title(key)
        return render(request, "encyclopedia/404.html", {
            "title": title.lower()
        }, status=404)
    
    else:
        # same action for title as above, but content is now passing in md
        # converted to html
        return render(request, "encyclopedia/entry.html", {
            "content": content, "title": title.lower()})

def search(request):
    search_query = request.GET.get("q", "")
    search_query = search_query.strip().lower()
    matches = [entry for entry in util.list_entries() if re.search(search_query, entry.lower())]
    if len(matches) == 1:
        # if search_query matches an entry exactly, render that one entry.html page
        return render(request, "encyclopedia/entry.html", {
            "content": convert_md_to_html(matches[0])
        })

    elif len(matches) == 0:
        # if no matches, return a 404 page
        return render(request, "encyclopedia/404.html", {
            "title": search_query
        }, status=404)

    else:
        # if search_query is a substring of any entry,
        # return a search results page displaying a list of all entries with 
        # search_query as a substring
        return render(request, "encyclopedia/search_results.html", {
            "matches": matches, "search_query": search_query
        })
           
    