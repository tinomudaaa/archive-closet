import os
import re

files = ["index.html", "shop.html", "contact.html", "admin.html"]

logo_html_new = """<a href="index.html" class="header-left">
  <img src="archive-closet-logo-final.svg" alt="Archive Closet" class="header-logo"/>
</a>"""

for f in files:
    if not os.path.exists(f): continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 1. Replace Logo HTML
    pattern = re.compile(r'<a[^>]*href="index\.html"[^>]*>\s*<img[^>]*src="images/logo\.png"[^>]*>\s*</a>', re.IGNORECASE)
    content = pattern.sub(logo_html_new, content)

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Updated {f}")
