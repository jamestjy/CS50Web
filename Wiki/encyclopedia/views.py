from django.shortcuts import render, redirect
from markdown2 import Markdown
from . import util
import re
import random

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
    # user may type in url directly
    content = convert_md_to_html(title.lower()) #used lower() since title=entry from index.html contains caps
    if content is None:
        
        return render(request, "encyclopedia/404.html", {
            "error_message": f"404 - '{title}' Not Found"
        }, status=404)
    
    else:
        # same action for title as above, but content is now passing in md
        # converted to html
        return render(request, "encyclopedia/entry.html", {
            "content": content, "title": title.lower()})

def search(request):
    search_query = request.GET.get("q", "")
    search_query = search_query.strip().lower()
    # search query matches entry exactly
    for entry in util.list_entries():
        if re.fullmatch(search_query, f"{entry}", flags=re.IGNORECASE):
            return render(request, "encyclopedia/entry.html", {
                "content": convert_md_to_html(entry),
                "title": entry.lower()
            })
        
    # search query matches entry as a substring
    matches = [entry for entry in util.list_entries() if re.search(search_query, entry.lower())]

    if len(matches) == 0:
        return render(request, "encyclopedia/404.html", {
            "error_message": f"404 - {search_query} Not Found"
        }, status=404)

    else:
        # if search_query is a substring of any entry,
        # return a search results page displaying a list of all entries with 
        # search_query as a substring
        return render(request, "encyclopedia/search_results.html", {
            "matches": matches, "search_query": search_query
        })
    
def create(request):
    # if i am trying to save my entry
    if request.method == "POST":
        title = request.POST.get("newpage-title")
        content = request.POST.get("newpage-content")
        # check if title exists, regardless of case
        title = title.strip().lower()
        for entry in util.list_entries():
            if entry.lower() == title:
                return render(request, "encyclopedia/404.html", {
                    "error_message": f"404 - {title} Already Exists"
                }, status=404)
            
        # if title doesnt exist, save the user's entry
        util.save_entry(title, content)
        return render(request, "encyclopedia/entry.html", {
            "content": convert_md_to_html(title),
            "title": title
        })
        
    # if i just want to GET the create page
    else:
        return render(request, "encyclopedia/create.html")
    
def edit(request, title):
    if request.method == "POST":
        # if trying to save the edited entry
        content = request.POST.get("edit-markdown")
        util.save_entry(title, content)
        return redirect("entry", title=title.lower())

    else:
        if util.get_entry(title) is not None:
            # render the edit page of the current entry
            return render(request, "encyclopedia/edit.html", {
                "title": title.lower(), "md_content": util.get_entry(title)
            })
        else:
            return render(request, "encyclopedia/404.html", {
                "error_message": f"404 - Unable to edit '{title}' as it does not exist."
            }, status=404)

def random_page(request):
    if not util.list_entries():
        return render(request, "encyclopedia/404.html", {
            "error_message": "404 - No entries available to display."
        }, status=404)
    else:
        random_entry = random.choice(util.list_entries())
        
        return redirect("entry", title=random_entry)
    


           
#USED TO TEST SEARCH()
def test(request):
    print("🔍 SEARCH VIEW HIT")  # Add this
    query = request.GET.get("q", "")
    print("🧠 QUERY =", query)  # Add this line
    
