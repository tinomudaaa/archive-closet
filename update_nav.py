import os
import re

files = ["index.html", "shop.html", "product.html", "drops.html", "outfits.html", "about.html", "contact.html", "admin.html"]

replacement = """
        .nav-links {
            display: flex;
            align-items: center;
            gap: 24px;
            margin-left: auto;
            margin-right: 32px;
        }

        @media (max-width: 767px) {
            .nav-links {
                display: none;
            }
        }
"""

for f in files:
    if not os.path.exists(f): continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 1. Update Logo Size
    content = content.replace("width: 160px;", "width: 140px;")
    
    # 2. Update .nav-links CSS
    # Let's try to match the .nav-links and its media query block.
    # Typical existing block:
    # .nav-links { display: none; align-items: center; gap: 24px; }
    # @media (min-width: 768px) { .nav-links { display: flex; } }
    
    # Or:
    # .nav-links { display: flex; gap: 32px; }
    
    pattern1 = re.compile(r'\.nav-links\s*\{[^}]*\}\s*@media\s*\([^)]+\)\s*\{\s*\.nav-links\s*\{[^}]*\}\s*\}', re.DOTALL)
    
    if pattern1.search(content):
        content = pattern1.sub(replacement.strip(), content)
    else:
        # Just replace .nav-links if it exists standalone
        pattern2 = re.compile(r'\.nav-links\s*\{[^}]*\}', re.DOTALL)
        if pattern2.search(content) and not ".nav-links a" in pattern2.search(content).group(0):
             # careful not to match .nav-links a
             pass

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Updated {f}")
