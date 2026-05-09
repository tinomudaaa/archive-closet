import re

SUPABASE_URL = 'https://ypdahlqlgumzxjarkyoj.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlwZGFobHFsZ3VtenhqYXJreW9qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgxNzYyMTgsImV4cCI6MjA5Mzc1MjIxOH0.WeiTB7CinagWcyfXb_BXsZWA0eRpnaDD6_UNr7psyfY'

SUPABASE_LIB = '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>'

SUPABASE_CONFIG = """        const SUPABASE_URL = 'https://ypdahlqlgumzxjarkyoj.supabase.co';
        const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlwZGFobHFsZ3VtenhqYXJreW9qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgxNzYyMTgsImV4cCI6MjA5Mzc1MjIxOH0.WeiTB7CinagWcyfXb_BXsZWA0eRpnaDD6_UNr7psyfY';
        const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);"""

# ── 1. ADD SUPABASE LIB ──────────────────────────────────────────────────────

def add_supabase_lib(content, filename):
    if 'cdn.jsdelivr.net/npm/@supabase/supabase-js' in content:
        return content  # already present

    # Insert after tailwind CDN script tag if present
    if 'cdn.tailwindcss.com' in content:
        content = content.replace(
            '<script src="https://cdn.tailwindcss.com"></script>',
            '<script src="https://cdn.tailwindcss.com"></script>\n    ' + SUPABASE_LIB
        )
    # Or after Google Fonts stylesheet link
    elif 'fonts.googleapis.com/css2' in content:
        content = re.sub(
            r'(<link href="https://fonts\.googleapis\.com/css2[^"]*"[^>]*/?>)',
            r'\1\n    ' + SUPABASE_LIB,
            content, count=1
        )
    # Fallback: before </head>
    else:
        content = content.replace('</head>', '    ' + SUPABASE_LIB + '\n</head>', 1)
    return content

# ── 2. REMOVE AIRTABLE CONFIG ────────────────────────────────────────────────

def remove_airtable_config(content):
    # Remove AIRTABLE_TOKEN, AIRTABLE_BASE, AIRTABLE_TABLE, AIRTABLE_OUTFITS_TABLE lines
    content = re.sub(r"[ \t]*const AIRTABLE_TOKEN = '[^']*';?[ \t]*(?://[^\n]*)?\r?\n", '', content)
    content = re.sub(r"[ \t]*const AIRTABLE_BASE = '[^']*';?[ \t]*(?://[^\n]*)?\r?\n", '', content)
    content = re.sub(r"[ \t]*const AIRTABLE_TABLE = '[^']*';?[ \t]*(?://[^\n]*)?\r?\n", '', content)
    content = re.sub(r"[ \t]*const AIRTABLE_OUTFITS_TABLE = '[^']*';?[ \t]*(?://[^\n]*)?\r?\n", '', content)
    # Remove orphaned Airtable comment blocks
    content = re.sub(r"[ \t]*// (?:====+|══+) Airtable[^\n]*\r?\n", '', content)
    content = re.sub(r"[ \t]*// AIRTABLE CONFIG[^\n]*\r?\n", '', content)
    return content

def add_supabase_config(content):
    if 'window.supabase.createClient' in content:
        return content
    # Insert before the first async function or fetch call that uses airtable (or before first function keyword in script)
    # We'll insert right after the opening <script> tag of the main script block
    # Strategy: replace the first occurrence of the removed AIRTABLE lines area with SUPABASE_CONFIG
    # Since we already removed those lines, insert at start of first <script> block that has fetch/async
    content = re.sub(
        r'(<script>[\s]*\n)([ \t]*(?:\/\/[^\n]*\n)*[ \t]*(?:let |const |var |async |function ))',
        lambda m: m.group(1) + SUPABASE_CONFIG + '\n\n' + m.group(2),
        content, count=1
    )
    return content

# ── 3. REMOVE convertGDriveUrl ───────────────────────────────────────────────

def remove_convert_gdrive(content):
    # Remove multi-line convertGDriveUrl function
    content = re.sub(
        r'[ \t]*function convertGDriveUrl\(url\)\s*\{[^}]*\}\s*\n?',
        '',
        content
    )
    return content

# ── INDEX.HTML ───────────────────────────────────────────────────────────────

def migrate_index(content):
    old = (
        "        const url = `https://api.airtable.com/v0/${AIRTABLE_BASE}/${AIRTABLE_TABLE}?filterByFormula=%7BFeatured%7D%3D1&maxRecords=8`;\n"
        "        const res = await fetch(url, { headers: { Authorization: `Bearer ${AIRTABLE_TOKEN}` } });\n"
        "        if (!res.ok) throw new Error('airtable');\n"
        "        const { records } = await res.json();\n"
        "        renderProducts(records.map(r => ({\n"
        "          name: r.fields.Name || 'Untitled',\n"
        "          price: r.fields.Price || '—',\n"
        "          size: r.fields.Size || '',\n"
        "          slug: r.fields.Slug || r.id,\n"
        "          sold: !!r.fields.SoldOut,\n"
        "          img: convertGDriveUrl(r.fields.ImageURL || (r.fields.Image && r.fields.Image[0]?.url) || ''),\n"
        "        })));"
    )
    new = (
        "        const { data: records, error } = await supabase\n"
        "          .from('products')\n"
        "          .select('*')\n"
        "          .eq('featured', true)\n"
        "          .eq('sold_out', false)\n"
        "          .order('created_at', { ascending: false })\n"
        "          .limit(8);\n"
        "        if (error) throw error;\n"
        "        renderProducts(records.map(p => ({\n"
        "          name: p.name,\n"
        "          price: p.price,\n"
        "          size: p.size,\n"
        "          slug: p.slug,\n"
        "          sold: p.sold_out,\n"
        "          img: p.image_url,\n"
        "        })));"
    )
    content = content.replace(old, new)
    # Fallback: comment-style
    content = content.replace("// No mock data — show empty state if Airtable fails",
                              "// No mock data — show empty state if Supabase fails")
    return content

# ── SHOP.HTML ────────────────────────────────────────────────────────────────

def migrate_shop(content):
    old = (
        "            const url = `https://api.airtable.com/v0/${AIRTABLE_BASE}/${AIRTABLE_TABLE}?pageSize=100`;\n"
        "                const res = await fetch(url, { headers: { Authorization: `Bearer ${AIRTABLE_TOKEN}` } });\n"
        "                const data = await res.json();\n"
        "                allProducts = (data.records || []).map(r => {\n"
        "                    const f = r.fields || {};\n"
        "                    return {\n"
        "                        id: r.id,\n"
        "                        name: f.Name || 'Untitled',\n"
        "                        price: Number(f.Price || 0),\n"
        "                        size: f.Size || '',\n"
        "                        era: f.Era || '',\n"
        "                        gender: (f.Gender || '').toLowerCase(),\n"
        "                        category: (f.Category || '').toLowerCase(),\n"
        "                        subcategory: f.Subcategory || '',\n"
        "                        slug: f.Slug || r.id,\n"
        "                        image: convertGDriveUrl(f['Image URL'] || (f.Image && f.Image[0] && f.Image[0].url) || ''),\n"
        "                        sold: !!f['Sold Out'],\n"
        "                        featured: !!f.Featured,\n"
        "                        drop: !!f.Drop,\n"
        "                        createdTime: r.createdTime,\n"
        "                    };\n"
        "                });"
    )
    new = (
        "            const { data: records, error } = await supabase\n"
        "                .from('products')\n"
        "                .select('*')\n"
        "                .order('created_at', { ascending: false });\n"
        "            if (error) throw error;\n"
        "            allProducts = (records || []).map(p => ({\n"
        "                id: p.id,\n"
        "                name: p.name,\n"
        "                price: Number(p.price || 0),\n"
        "                size: p.size || '',\n"
        "                era: p.era || '',\n"
        "                gender: (p.gender || '').toLowerCase(),\n"
        "                category: (p.category || '').toLowerCase(),\n"
        "                subcategory: p.subcategory || '',\n"
        "                slug: p.slug,\n"
        "                image: p.image_url || '',\n"
        "                sold: !!p.sold_out,\n"
        "                featured: !!p.featured,\n"
        "                drop: false,\n"
        "                createdTime: p.created_at,\n"
        "            }));"
    )
    # Use regex for flexible whitespace matching
    old_pattern = re.compile(
        r"const url = `https://api\.airtable\.com/v0/\$\{AIRTABLE_BASE\}/\$\{AIRTABLE_TABLE\}\?pageSize=100`;\s*"
        r"const res = await fetch\(url,\s*\{[^}]*\}\s*\);\s*"
        r"const data = await res\.json\(\);\s*"
        r"allProducts = \(data\.records \|\| \[\]\)\.map\(r =>\s*\{[^}]+return \{.*?createdTime: r\.createdTime,\s*\};\s*\}\);",
        re.DOTALL
    )
    match = old_pattern.search(content)
    if match:
        content = content[:match.start()] + new + content[match.end():]
    content = content.replace("console.error('Airtable fetch failed', e);",
                              "console.error('Supabase fetch failed', e);")
    return content

# ── PRODUCT.HTML ─────────────────────────────────────────────────────────────

def migrate_product(content):
    # Main product fetch
    old_product_pattern = re.compile(
        r"const url = `https://api\.airtable\.com/v0/\$\{AIRTABLE_BASE\}/\$\{AIRTABLE_TABLE\}\?filterByFormula=.*?soldOut: !!\s*f\['Sold Out'\]\s*\};",
        re.DOTALL
    )
    new_product = (
        "const { data: records, error } = await supabase\n"
        "          .from('products')\n"
        "          .select('*')\n"
        "          .eq('slug', slug)\n"
        "          .limit(1);\n"
        "        if (error) throw error;\n"
        "\n"
        "        if (!records || records.length === 0) {\n"
        "          showNotFound();\n"
        "          return;\n"
        "        }\n"
        "\n"
        "        const p = records[0];\n"
        "        product = {\n"
        "          id: p.id,\n"
        "          name: p.name,\n"
        "          slug: p.slug,\n"
        "          price: Number(p.price || 0),\n"
        "          size: p.size || '',\n"
        "          gender: p.gender || '',\n"
        "          category: p.category || '',\n"
        "          condition: p.condition || '',\n"
        "          era: p.era || '',\n"
        "          description: p.description || '',\n"
        "          images: p.image_url ? [p.image_url] : [],\n"
        "          soldOut: !!p.sold_out\n"
        "        };"
    )

    # Remove the old "if (!data.records..." block too since we're replacing everything
    old_full_pattern = re.compile(
        r"const url = `https://api\.airtable\.com/v0/\$\{AIRTABLE_BASE\}/\$\{AIRTABLE_TABLE\}\?filterByFormula=.*?soldOut: !!\s*f\['Sold Out'\]\s*\};",
        re.DOTALL
    )
    m = old_full_pattern.search(content)
    if m:
        # Also grab the if (!data.records block before it if present
        start = m.start()
        end = m.end()
        content = content[:start] + new_product + content[end:]

    # Related products fetch
    old_related_pattern = re.compile(
        r"const relatedUrl = `https://api\.airtable\.com/v0/.*?\.slice\(0, 4\);\s*\}",
        re.DOTALL
    )
    new_related = (
        "const { data: relatedRecords } = await supabase\n"
        "          .from('products')\n"
        "          .select('*')\n"
        "          .eq('gender', product.gender)\n"
        "          .eq('sold_out', false)\n"
        "          .neq('slug', slug)\n"
        "          .limit(8);\n"
        "        if (relatedRecords) {\n"
        "          relatedProducts = relatedRecords\n"
        "            .map(r => ({\n"
        "              slug: r.slug,\n"
        "              name: r.name,\n"
        "              price: Number(r.price || 0),\n"
        "              images: r.image_url ? [r.image_url] : [],\n"
        "              soldOut: !!r.sold_out\n"
        "            }))\n"
        "            .sort(() => Math.random() - 0.5)\n"
        "            .slice(0, 4);\n"
        "        }"
    )
    m2 = old_related_pattern.search(content)
    if m2:
        content = content[:m2.start()] + new_related + content[m2.end():]

    # Replace convertGDriveUrl wrapper in renderGallery
    content = content.replace(
        'const imgs = product.images.map(convertGDriveUrl);',
        'const imgs = product.images;'
    )
    # Also remove any remaining convertGDriveUrl calls referencing imgs
    content = re.sub(r'convertGDriveUrl\(imgs\[(\d+)\]\)', r'imgs[\1]', content)

    return content

# ── DROPS.HTML ───────────────────────────────────────────────────────────────

def migrate_drops(content):
    # Current drop fetch
    old_current = re.compile(
        r"const currentUrl = `https://api\.airtable\.com/v0/.*?soldOut: !!\s*r\.fields\['Sold Out'\]\s*\}\)\);\s*\}",
        re.DOTALL
    )
    new_current = (
        "const { data: currentRecords } = await supabase\n"
        "                  .from('products')\n"
        "                  .select('*')\n"
        "                  .eq('sold_out', false)\n"
        "                  .order('created_at', { ascending: false })\n"
        "                  .limit(8);\n"
        "                currentDrop = (currentRecords || []).map(p => ({\n"
        "                    slug: p.slug,\n"
        "                    name: p.name,\n"
        "                    price: Number(p.price || 0),\n"
        "                    size: p.size || '',\n"
        "                    images: p.image_url ? [p.image_url] : [],\n"
        "                    soldOut: !!p.sold_out\n"
        "                }));"
    )
    m = old_current.search(content)
    if m:
        content = content[:m.start()] + new_current + content[m.end():]

    # Past drops fetch
    old_past = re.compile(
        r"const pastUrl = `https://api\.airtable\.com/v0/.*?soldOut: !!\s*r\.fields\['Sold Out'\]\s*\}\)\);\s*\}",
        re.DOTALL
    )
    new_past = (
        "const { data: pastRecords } = await supabase\n"
        "                  .from('products')\n"
        "                  .select('*')\n"
        "                  .eq('sold_out', true)\n"
        "                  .order('created_at', { ascending: false })\n"
        "                  .limit(8);\n"
        "                pastDrops = (pastRecords || []).map(p => ({\n"
        "                    slug: p.slug,\n"
        "                    name: p.name,\n"
        "                    price: Number(p.price || 0),\n"
        "                    size: p.size || '',\n"
        "                    images: p.image_url ? [p.image_url] : [],\n"
        "                    soldOut: true\n"
        "                }));"
    )
    m2 = old_past.search(content)
    if m2:
        content = content[:m2.start()] + new_past + content[m2.end():]

    # Count fetch -> dropNumber = 1
    old_count = re.compile(
        r"const countUrl = `https://api\.airtable\.com/v0/.*?dropNumber = countData\.records \? Math\.ceil\(countData\.records\.length / 4\) : 1;\s*\}",
        re.DOTALL
    )
    m3 = old_count.search(content)
    if m3:
        content = content[:m3.start()] + "dropNumber = 1;" + content[m3.end():]

    # Replace convertGDriveUrl in renderCard
    content = content.replace(
        "const img = p.images && p.images[0] ? convertGDriveUrl(p.images[0]) : '';",
        "const img = p.images && p.images[0] ? p.images[0] : '';"
    )

    return content

# ── OUTFITS.HTML ─────────────────────────────────────────────────────────────

def migrate_outfits(content):
    old_fetch = re.compile(
        r"const url = `https://api\.airtable\.com/v0/\$\{AIRTABLE_BASE\}/\$\{AIRTABLE_TABLE\}\?sort.*?coverImageUrl: r\.fields\['Cover Image URL'\] \|\| ''\s*\}\)\);\s*\} catch",
        re.DOTALL
    )
    new_fetch = (
        "const { data: records, error } = await supabase\n"
        "                  .from('outfits')\n"
        "                  .select('*')\n"
        "                  .order('created_at', { ascending: false });\n"
        "                if (error) throw error;\n"
        "                outfits = (records || []).map(p => ({\n"
        "                    id: p.id,\n"
        "                    name: p.name,\n"
        "                    slug: p.slug,\n"
        "                    vibe: p.vibe || '',\n"
        "                    description: p.description || '',\n"
        "                    items: p.items || '',\n"
        "                    coverImage: [],\n"
        "                    coverImageUrl: p.image_url || ''\n"
        "                }));\n"
        "                } catch"
    )
    m = old_fetch.search(content)
    if m:
        content = content[:m.start()] + new_fetch + content[m.end():]

    # Fix getImageUrl to not use convertGDriveUrl
    old_img = (
        "                function getImageUrl(outfit) {\n"
        "                        if (outfit.coverImage && outfit.coverImage.length > 0) {\n"
        "                                return outfit.coverImage[0].url || outfit.coverImage[0];\n"
        "                        }\n"
        "                        if (outfit.coverImageUrl) {\n"
        "                                return convertGDriveUrl(outfit.coverImageUrl);\n"
        "                        }\n"
        "                        return '';\n"
        "                }"
    )
    new_img = (
        "                function getImageUrl(outfit) {\n"
        "                        if (outfit.coverImageUrl) {\n"
        "                                return outfit.coverImageUrl;\n"
        "                        }\n"
        "                        return '';\n"
        "                }"
    )
    content = content.replace(old_img, new_img)

    return content

# ── ADMIN.HTML ────────────────────────────────────────────────────────────────

def migrate_admin(content):
    # Remove old TODO comments and mock data block
    # Replace everything from "// MOCK DATA" through the outfits array
    old_mock = re.compile(
        r"// MOCK DATA.*?let outfits = \[.*?\];\s*",
        re.DOTALL
    )
    new_data = (
        "let products = [];\n"
        "        let outfits = [];\n\n"
        "        async function uploadProductImage(file, slug) {\n"
        "          const fileExt = file.name.split('.').pop();\n"
        "          const fileName = `${slug}/${Date.now()}.${fileExt}`;\n"
        "          const { error } = await supabase.storage.from('product-images').upload(fileName, file, { cacheControl: '3600', upsert: false });\n"
        "          if (error) { alert('Upload failed: ' + error.message); return null; }\n"
        "          const { data: { publicUrl } } = supabase.storage.from('product-images').getPublicUrl(fileName);\n"
        "          return publicUrl;\n"
        "        }\n\n"
        "        async function loadAdminData() {\n"
        "          const { data: p } = await supabase.from('products').select('*').order('created_at', { ascending: false });\n"
        "          const { data: o } = await supabase.from('outfits').select('*').order('created_at', { ascending: false });\n"
        "          products = (p || []).map(x => ({\n"
        "            id: x.id, name: x.name, slug: x.slug, price: x.price, size: x.size,\n"
        "            gender: x.gender, category: x.category, subcategory: x.subcategory || '',\n"
        "            era: x.era, condition: x.condition || '', description: x.description,\n"
        "            image: x.image_url || '', drop: false, featured: !!x.featured, soldOut: !!x.sold_out\n"
        "          }));\n"
        "          outfits = (o || []).map(x => ({\n"
        "            id: x.id, name: x.name, slug: x.slug, vibe: x.vibe || '',\n"
        "            date: x.created_at, description: x.description, image: x.image_url || '', items: x.items || ''\n"
        "          }));\n"
        "          renderAll();\n"
        "        }\n\n"
    )
    m = old_mock.search(content)
    if m:
        content = content[:m.start()] + new_data + content[m.end():]

    # Also remove old TODO comments around render
    content = re.sub(r"[ \t]*// TODO: Fetch from Supabase instead of using mock data\n.*?// }\s*\n", '', content, flags=re.DOTALL)

    # Replace renderAll() calls in login block with loadAdminData()
    content = content.replace(
        "if (sessionStorage.getItem('ac_admin') === '1') { loginScreen.style.display = 'none'; mainContent.style.display = 'block'; renderAll(); }",
        "if (sessionStorage.getItem('ac_admin') === '1') { loginScreen.style.display = 'none'; mainContent.style.display = 'block'; loadAdminData(); }"
    )
    content = content.replace(
        "                mainContent.style.display = 'block';\n"
        "                renderAll();",
        "                mainContent.style.display = 'block';\n"
        "                loadAdminData();"
    )

    # Add Supabase config (before categoryMap since we removed AIRTABLE lines)
    if 'window.supabase.createClient' not in content:
        content = content.replace(
            "        const ADMIN_PASSWORD = 'archivecloset2024';",
            SUPABASE_CONFIG + "\n\n        const ADMIN_PASSWORD = 'archivecloset2024';"
        )

    return content

# ── MAIN ──────────────────────────────────────────────────────────────────────

files = {
    'index.html':   migrate_index,
    'shop.html':    migrate_shop,
    'product.html': migrate_product,
    'drops.html':   migrate_drops,
    'outfits.html': migrate_outfits,
    'admin.html':   migrate_admin,
}

for filename, migrator in files.items():
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Add Supabase CDN lib
        content = add_supabase_lib(content, filename)

        # 2. Remove Airtable config
        content = remove_airtable_config(content)

        # 3. Remove convertGDriveUrl function (except admin keeps it for image preview)
        if filename != 'admin.html':
            content = remove_convert_gdrive(content)

        # 4. Add Supabase config (except admin which has its own block)
        if filename != 'admin.html':
            content = add_supabase_config(content)

        # 5. File-specific fetch migration
        content = migrator(content)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f'OK {filename}')
    except Exception as e:
        print(f'ERR {filename}: {e}')

print('\nDone.')
