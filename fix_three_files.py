import re

files = ['drops.html', 'outfits.html', 'admin.html']

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 1. Delete leftover sz=w800 fragment (with backticks)
    # The fragment is like: )/) || url.match(/id=([a-zA-Z0-9_-]{25,})/); \n return m ? `https://drive.google.com/thumbnail?id=${m[1]}&sz=w800` : url; \n }
    # Or just `&sz=w800\`;\n        }`
    # Let's find exactly the orphaned fragment.
    # We can remove the lines starting with `)/) || url.match` up to the closing `}`
    content = re.sub(r'\)/\) \|\| url\.match\(/id=\(\[a-zA-Z0-9_-\]\{25,\}\)/\);\s*return m \? `https://drive\.google\.com/thumbnail\?id=\$\{m\[1\]\}&sz=w800` : url;\s*\}', '', content)
    
    # Just in case the `)/)` part isn't there, remove the specific line the user asked for:
    # &sz=w800` : url; \n }
    content = re.sub(r'&sz=w800` : url;\s*\}', '', content)

    # 2. Rename client variable
    content = content.replace(
        'const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);',
        'const db = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);'
    )
    
    # 3. Replace method calls
    content = re.sub(r'\bsupabase\.from\(', 'db.from(', content)
    content = re.sub(r'\bsupabase\.storage\b', 'db.storage', content)
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Updated {f}")
