import re

files = ["product.html", "shop.html", "drops.html", "outfits.html", "admin.html"]

for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()

    # 1. Rename the client variable declaration
    content = content.replace(
        'const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);',
        'const db = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);'
    )

    # 2. Replace supabase.from( and supabase.storage with db.from( and db.storage
    content = re.sub(r'\bsupabase\.from\(', 'db.from(', content)
    content = re.sub(r'\bsupabase\.storage\b', 'db.storage', content)

    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(content)
    print(f"OK {f}")

print("Done.")
