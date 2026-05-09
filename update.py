import os
import re

files = ["index.html", "shop.html", "product.html", "drops.html", "outfits.html", "about.html", "contact.html", "admin.html"]

footer_html = """<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-col">
      <h4>Archive Closet</h4>
      <p>Rare finds for the bold.</p>
    </div>
    <div class="footer-col">
      <h4>Shop</h4>
      <ul>
        <li><a href="shop.html?gender=menswear">Mens</a></li>
        <li><a href="shop.html?gender=womenswear">Women</a></li>
        <li><a href="shop.html?gender=crochet">Crochet</a></li>
        <li><a href="drops.html">Drops</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>Help</h4>
      <ul>
        <li><a href="about.html">About</a></li>
        <li><a href="contact.html">Contact</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>Follow</h4>
      <ul>
        <li><a href="https://www.instagram.com/archivecloset.zw" target="_blank" rel="noopener">Instagram</a></li>
        <li><a href="https://www.tiktok.com/@archivecloset.zw" target="_blank" rel="noopener">TikTok</a></li>
        <li><a href="https://wa.me/263718968489" target="_blank" rel="noopener">WhatsApp</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    &copy; <span id="year"></span> Archive Closet. All rights reserved.
  </div>
</footer>"""

footer_css = """
.site-footer { border-top: 1px solid var(--border); }
.footer-inner { max-width: 1280px; margin: 0 auto; padding: 48px 16px; display: grid; grid-template-columns: repeat(2, 1fr); gap: 40px; font-size: 12px; color: var(--muted); }
@media (min-width: 768px) { .footer-inner { grid-template-columns: repeat(4, 1fr); padding: 48px 32px; } }
.footer-col h4 { font-weight: 600; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 16px; color: var(--fg); }
.footer-col ul { list-style: none; padding: 0; display: flex; flex-direction: column; gap: 8px; }
.footer-col a { color: var(--muted); transition: color 0.2s; }
.footer-col a:hover { color: var(--accent); }
.footer-bottom { text-align: center; padding: 24px 16px; border-top: 1px solid var(--border); font-size: 12px; color: var(--muted); }
@media (min-width: 768px) { .footer-bottom { padding: 24px 32px; } }
"""

root_vars = """
  --bg: #FFFFFF;
  --fg: #1A1A1A;
  --muted: #666666;
  --border: #E5E5E5;
  --surface: #F5F5F5;
  --accent: #C45B3A;
"""

script_tag = "document.getElementById('year').textContent = new Date().getFullYear();"

for f in files:
    if not os.path.exists(f): continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 1. Update CSS
    if ".site-footer {" not in content:
        if "</style>" in content:
            content = content.replace("</style>", footer_css + "\n</style>")
        else:
            content = content.replace("</head>", "<style>\n" + footer_css + "\n</style>\n</head>")

    # 2. Update :root
    if ":root {" in content:
        # replace existing root block to guarantee the exact set without missing properties
        # But wait, there might be other variables. The user explicitly says:
        # "Ensure these CSS variables are defined in :root on every page"
        # Since I can't easily parse CSS, I'll just append them into the existing :root block.
        if "--fg:" not in content or "--accent: #C45B3A" not in content:
            content = re.sub(r'(:root\s*\{)', r'\1' + root_vars, content)
    else:
        # inject root in style
        if "</style>" in content:
            content = content.replace("</style>", ":root {" + root_vars + "}\n</style>")

    # 3. Update HTML Footer
    footer_pattern = re.compile(r'<footer.*?</footer>', re.DOTALL)
    if footer_pattern.search(content):
        content = footer_pattern.sub(footer_html, content)
    else:
        # If no footer exists, append it before </body>
        content = content.replace("</body>", footer_html + "\n</body>")

    # 4. Ensure script is present
    if "document.getElementById('year').textContent =" not in content:
        if "</body>" in content:
            content = content.replace("</body>", f"\n<script>{script_tag}</script>\n</body>")

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Updated {f}")
