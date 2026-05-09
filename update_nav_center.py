import os
import re

files = ["index.html", "shop.html", "product.html", "drops.html", "outfits.html", "about.html", "contact.html", "admin.html"]

for f in files:
    if not os.path.exists(f): continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 1 & 2. Change justify-between to justify-start (Tailwind)
    content = content.replace("justify-between h-16", "justify-start h-16")
    
    # 1 & 2. Change justify-content: space-between to flex-start (CSS files)
    # The container is .header-inner
    # Let's target the exact line in .header-inner block
    content = re.sub(r'(\.header-inner\s*\{[^}]*?justify-content:\s*)space-between', r'\1flex-start', content)

    # 3. Update .nav-links CSS
    old_nav_links = """        .nav-links {
            display: flex;
            align-items: center;
            gap: 24px;
            margin-left: auto;
            margin-right: 32px;
        }"""
        
    new_nav_links = """        .nav-links {
            display: flex;
            align-items: center;
            gap: 24px;
            margin-left: 48px;
        }"""
        
    if old_nav_links in content:
        content = content.replace(old_nav_links, new_nav_links)
    else:
        # Fallback regex just in case whitespace is different
        content = re.sub(
            r'\.nav-links\s*\{\s*display:\s*flex;\s*align-items:\s*center;\s*gap:\s*24px;\s*margin-left:\s*auto;\s*margin-right:\s*32px;\s*\}',
            new_nav_links,
            content
        )

    # 4. Add ml-auto to right-side icons (Tailwind)
    content = content.replace('<div class="flex items-center gap-4">', '<div class="flex items-center gap-4 ml-auto">')

    # 4. Add margin-left: auto to right-side icons (CSS files)
    # Look for .header-icons { display: flex; align-items: center; gap: 12px; }
    old_header_icons = r'(\.header-icons\s*\{\s*display:\s*flex;\s*align-items:\s*center;\s*gap:\s*12px;)'
    # We want to insert margin-left: auto; if not already there
    if ".header-icons {" in content and "margin-left: auto;" not in content.split(".header-icons {")[1].split("}")[0]:
        content = re.sub(old_header_icons, r'\1\n            margin-left: auto;', content)

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Updated {f}")
