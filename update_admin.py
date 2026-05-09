import re

with open('admin.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Product Panel Media Section
content = content.replace('''            <div class="form-section">
                <div class="form-section-title">Media</div>
                <div class="form-group"><label>Product Image URL</label><input type="url" id="pImage"
                        placeholder="Paste Google Drive or image link"></div>
                <img class="img-preview" id="pImagePreview" alt="Preview">
            </div>''', '''<div class="form-section">
    <div class="form-section-title">Media</div>
    <div class="form-group"><label>Product Image</label><input type="file" id="pImageFile" accept="image/jpeg,image/png,image/webp"></div>
    <img class="img-preview" id="pImagePreview" alt="Preview">
    <input type="hidden" id="pImageUrl">
</div>''')

# 2. Outfit Panel Media Section
content = content.replace('''            <div class="form-section">
                <div class="form-section-title">Cover Image</div>
                <div class="form-group"><input type="url" id="oImage" placeholder="Paste image URL"></div>
                <img class="img-preview" id="oImagePreview" alt="Preview">
            </div>''', '''<div class="form-section">
    <div class="form-section-title">Cover Image</div>
    <div class="form-group"><input type="file" id="oImageFile" accept="image/jpeg,image/png,image/webp"></div>
    <img class="img-preview" id="oImagePreview" alt="Preview">
    <input type="hidden" id="oImageUrl">
</div>''')

# 3. File Preview Handlers
content = content.replace('''        document.getElementById('pImage').oninput = () => {
            const url = convertGDriveUrl(document.getElementById('pImage').value);
            const prev = document.getElementById('pImagePreview');
            if (url) { prev.src = url; prev.style.display = 'block'; } else { prev.style.display = 'none'; }
        };''', '''document.getElementById('pImageFile').onchange = () => {
    const file = document.getElementById('pImageFile').files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => { const prev = document.getElementById('pImagePreview'); prev.src = e.target.result; prev.style.display = 'block'; };
    reader.readAsDataURL(file);
};''')

content = content.replace('''        document.getElementById('oImage').oninput = () => {
            const url = convertGDriveUrl(document.getElementById('oImage').value);
            const prev = document.getElementById('oImagePreview');
            if (url) { prev.src = url; prev.style.display = 'block'; } else { prev.style.display = 'none'; }
        };''', '''document.getElementById('oImageFile').onchange = () => {
    const file = document.getElementById('oImageFile').files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => { const prev = document.getElementById('oImagePreview'); prev.src = e.target.result; prev.style.display = 'block'; };
    reader.readAsDataURL(file);
};''')

# 4. Product Save Button Handler
old_product_save = '''        document.getElementById('productSaveBtn').onclick = () => {
            const name = document.getElementById('pName').value.trim();
            if (!name) { alert('Product name is required'); return; }
            const data = {
                name,
                slug: document.getElementById('pSlug').value.trim() || slugify(name),
                price: parseInt(document.getElementById('pPrice').value) || 0,
                size: document.getElementById('pSize').value,
                gender: document.getElementById('pGender').value,
                category: document.getElementById('pCategory').value,
                subcategory: document.getElementById('pSubcategory').value,
                era: document.getElementById('pEra').value,
                condition: document.getElementById('pCondition').value,
                image: document.getElementById('pImage').value.trim(),
                description: document.getElementById('pDescription').value.trim(),
                drop: document.getElementById('pDrop').checked,
                featured: document.getElementById('pFeatured').checked,
                soldOut: document.getElementById('pSoldOut').checked,
            };
            if (editingProductId) {
                const idx = products.findIndex(p => p.id === editingProductId);
                if (idx > -1) products[idx] = { ...products[idx], ...data };
            } else {
                products.push({ id: uid(), ...data });
            }
            closeProductPanel();
            renderAll();
        };'''

new_product_save = '''document.getElementById('productSaveBtn').onclick = async () => {
    const name = document.getElementById('pName').value.trim();
    if (!name) { alert('Product name is required'); return; }
    const slug = document.getElementById('pSlug').value.trim() || slugify(name);
    let imageUrl = document.getElementById('pImageUrl').value;
    const fileInput = document.getElementById('pImageFile');
    if (fileInput.files && fileInput.files[0]) {
        const uploadedUrl = await uploadProductImage(fileInput.files[0], slug);
        if (uploadedUrl) imageUrl = uploadedUrl;
    }
    const data = {
        slug, name,
        price: parseInt(document.getElementById('pPrice').value) || 0,
        size: document.getElementById('pSize').value,
        gender: document.getElementById('pGender').value.toLowerCase(),
        category: document.getElementById('pCategory').value.toLowerCase(),
        era: document.getElementById('pEra').value,
        description: document.getElementById('pDescription').value.trim(),
        image_url: imageUrl,
        featured: document.getElementById('pFeatured').checked,
        sold_out: document.getElementById('pSoldOut').checked,
    };
    if (editingProductId) {
        await db.from('products').update(data).eq('id', editingProductId);
    } else {
        await db.from('products').insert([data]);
    }
    closeProductPanel();
    loadAdminData();
};'''
content = content.replace(old_product_save, new_product_save)

# 5. Outfit Save Button Handler
old_outfit_save = '''        document.getElementById('outfitSaveBtn').onclick = () => {
            const name = document.getElementById('oName').value.trim();
            if (!name) { alert('Outfit name is required'); return; }
            const selectedItems = Array.from(document.querySelectorAll('#oItemsList input:checked')).map(i => i.value);
            const data = {
                name,
                slug: document.getElementById('oSlug').value.trim() || slugify(name),
                vibe: document.getElementById('oVibe').value,
                description: document.getElementById('oDescription').value.trim(),
                image: document.getElementById('oImage').value.trim(),
                date: document.getElementById('oDate').value,
                items: selectedItems,
            };
            if (editingOutfitId) {
                const idx = outfits.findIndex(o => o.id === editingOutfitId);
                if (idx > -1) outfits[idx] = { ...outfits[idx], ...data };
            } else {
                outfits.push({ id: uid(), ...data });
            }
            closeOutfitPanel();
            renderAll();
        };'''

new_outfit_save = '''document.getElementById('outfitSaveBtn').onclick = async () => {
    const name = document.getElementById('oName').value.trim();
    if (!name) { alert('Outfit name is required'); return; }
    const slug = document.getElementById('oSlug').value.trim() || slugify(name);
    let imageUrl = document.getElementById('oImageUrl').value;
    const fileInput = document.getElementById('oImageFile');
    if (fileInput.files && fileInput.files[0]) {
        const uploadedUrl = await uploadProductImage(fileInput.files[0], slug);
        if (uploadedUrl) imageUrl = uploadedUrl;
    }
    const selectedItems = Array.from(document.querySelectorAll('#oItemsList input:checked')).map(i => i.value);
    const data = {
        slug, name,
        vibe: document.getElementById('oVibe').value,
        description: document.getElementById('oDescription').value.trim(),
        image_url: imageUrl,
        items: selectedItems,
    };
    if (editingOutfitId) {
        await db.from('outfits').update(data).eq('id', editingOutfitId);
    } else {
        await db.from('outfits').insert([data]);
    }
    closeOutfitPanel();
    loadAdminData();
};'''
content = content.replace(old_outfit_save, new_outfit_save)

# 6. Edit Functions
content = content.replace("document.getElementById('pImage').value = p.image || '';\n            document.getElementById('pImage').oninput();", '''document.getElementById('pImageUrl').value = p.image || '';
document.getElementById('pImageFile').value = '';
document.getElementById('pImagePreview').style.display = p.image ? 'block' : 'none';
if (p.image) document.getElementById('pImagePreview').src = p.image;''')

content = content.replace("document.getElementById('oImage').value = o.image || '';\n            document.getElementById('oImage').oninput();", '''document.getElementById('oImageUrl').value = o.image || '';
document.getElementById('oImageFile').value = '';
document.getElementById('oImagePreview').style.display = o.image ? 'block' : 'none';
if (o.image) document.getElementById('oImagePreview').src = o.image;''')

# 7. Remove GDrive Converter
content = re.sub(r'\s*function convertGDriveUrl.*?\}', '', content, flags=re.DOTALL, count=1)
content = content.replace('convertGDriveUrl(p.image)', 'p.image')

# 8. Reset Functions
content = content.replace("['pName', 'pSlug', 'pPrice', 'pImage', 'pDescription'].forEach(id => document.getElementById(id).value = '');", "['pName', 'pSlug', 'pPrice', 'pDescription'].forEach(id => document.getElementById(id).value = '');\ndocument.getElementById('pImageFile').value = '';\ndocument.getElementById('pImageUrl').value = '';")
content = content.replace("['oName', 'oSlug', 'oDescription', 'oImage', 'oDate', 'oItemsSearch'].forEach(id => document.getElementById(id).value = '');", "['oName', 'oSlug', 'oDescription', 'oDate', 'oItemsSearch'].forEach(id => document.getElementById(id).value = '');\ndocument.getElementById('oImageFile').value = '';\ndocument.getElementById('oImageUrl').value = '';")

with open('admin.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Success')
