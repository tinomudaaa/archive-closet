import os
import re

files = ["index.html", "shop.html", "product.html", "drops.html", "outfits.html", "about.html", "contact.html", "admin.html"]

logo_html_new = """<a href="index.html" class="header-left">
  <img src="archive-closet-logo-final.svg" alt="Archive Closet" class="header-logo"/>
</a>"""

logo_css_new = """
        .header-left {
            display: flex;
            align-items: center;
            padding-left: 32px;
        }

        .header-logo {
            width: 160px;
            height: auto;
            display: block;
            object-fit: contain;
        }

        @media (max-width: 767px) {
            .header-logo {
                width: 120px;
            }
            .header-left {
                padding-left: 16px;
            }
        }
"""

for f in files:
    if not os.path.exists(f): continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 1. Replace Logo HTML
    pattern = re.compile(r'<a\s+href="index\.html"\s+class="logo".*?</a>', re.IGNORECASE | re.DOTALL)
    content = pattern.sub(logo_html_new, content)

    # 2. Add New CSS
    if ".header-left {" not in content:
        content = content.replace("</style>", logo_css_new + "    </style>")

    # 3. Remove Old Logo CSS
    content = re.sub(r'[ \t]*\.logo\s*\{[^}]*\}\s*', '', content)
    content = re.sub(r'[ \t]*\.logo\s+img\s*\{[^}]*\}\s*', '', content)

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Updated {f}")
