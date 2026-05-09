import os
import re

files = ["index.html", "shop.html"]

replacement_css = """
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
    
    # Add .nav-links CSS if missing
    if ".nav-links {" not in content:
        content = content.replace("</style>", replacement_css + "\n    </style>")

    # Replace <nav class="..."> with <nav class="nav-links">
    # In index.html: <nav class="hidden lg:flex items-center gap-8">
    # In shop.html: <nav class="hidden md:flex gap-6">
    content = re.sub(r'<nav class="hidden (?:lg|md):flex[^>]*">', '<nav class="nav-links">', content)

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Updated {f}")
