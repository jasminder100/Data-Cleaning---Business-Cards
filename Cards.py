import pandas as pd
import re

# Load CSV
df = pd.read_csv('Business Cards.csv')

def clean_phone_number(num):
    if pd.isna(num):
        return num

    original = str(num).strip()

    # Handle extensions
    ext_match = re.search(r'(ext\.?|x)\s*(\d+)', original, flags=re.IGNORECASE)
    extension = f" Ext.{ext_match.group(2)}" if ext_match else ""

    # Handle multiple numbers separated by `/`
    if '/' in original:
        parts = original.split('/')
        cleaned_parts = [clean_phone_number(part.strip()) for part in parts]
        return '/'.join(cleaned_parts)

    # Remove (0) and clean unwanted chars
    base = re.sub(r'\(0\)', '', original)
    base = re.sub(r'[.\-x()]', '', base)
    base = re.sub(r'(ext\.?)\s*\d+', '', base, flags=re.IGNORECASE)
    base = re.sub(r'\s+', '', base).lstrip('-')

    # Normalize international prefixes
    if base.startswith('00'):
        base = '+' + base[2:]
    elif not base.startswith('+') and base.startswith('971'):
        base = '+' + base

    # === UAE Mobile ===
    match_uae_mobile = re.match(r'^\+971(50|52|54|55|56|58)(\d{6,7})$', base)
    if match_uae_mobile:
        return f'+971 {match_uae_mobile.group(1)} {match_uae_mobile.group(2)}{extension}'

    # === UAE Landline ===
    match_uae_land = re.match(r'^\+971([2-7|9])(\d{6,7})$', base)
    if match_uae_land:
        return f'+971 {match_uae_land.group(1)} {match_uae_land.group(2)}{extension}'

    # === Short UAE Numbers ===
    if re.match(r'^[2-7|9]\d{6}$', base):
        return f'+971 4 {base}{extension}'

    # === Italy Mobile ===
    match_italy_mobile = re.match(r'^\+39(3\d{2})(\d{6,7})$', base)
    if match_italy_mobile:
        return f'+39 {match_italy_mobile.group(1)} {match_italy_mobile.group(2)}{extension}'

    # === Italy Landline ===
    match_italy_landline = re.match(r'^\+39(\d{4})(\d{3,6})$', base)
    if match_italy_landline:
        return f'+39 {match_italy_landline.group(1)} {match_italy_landline.group(2)}{extension}'

    # === India Numbers ===
    if re.match(r'^91?\d{10}$', base):
        base = base[-10:]
        return f'+91 {base[:5]} {base[5:]}{extension}'

    # === US Numbers ===
    match_us = re.match(r'^1?(\d{3})(\d{3})(\d{4})$', base)
    if match_us:
        return f'+1 {match_us.group(1)} {match_us.group(2)} {match_us.group(3)}{extension}'

    # === General international number formatter ===
    match_generic = re.match(r'^\+(\d{1,4})(\d{6,12})$', base)
    if match_generic:
        cc = match_generic.group(1)
        national = match_generic.group(2)

        # Format based on length
        if len(national) == 6:
            formatted = re.sub(r'(\d{3})(\d{3})', r'\1 \2', national)
        elif len(national) == 7:
            formatted = re.sub(r'(\d{3})(\d{4})', r'\1 \2', national)
        elif len(national) == 8:
            formatted = re.sub(r'(\d{4})(\d{4})', r'\1 \2', national)
        elif len(national) == 9:
            formatted = re.sub(r'(\d{3})(\d{3})(\d{3})', r'\1 \2 \3', national)
        elif len(national) == 10:
            formatted = re.sub(r'(\d{3})(\d{3})(\d{4})', r'\1 \2 \3', national)
        else:
            formatted = re.sub(r'(\d{3})(\d+)', r'\1 \2', national)

        return f'+{cc} {formatted}{extension}'

    # === Catch scientific notation or invalid ===
    if re.match(r'^0\.0+', base):
        return ''

    return original.strip()

# Apply to all phone columns
for i in range(1, 10):
    col_in = f'Phone {i} - Number'
    col_out = f'Phone {i} -- Number'
    if col_in in df.columns:
        df[col_out] = df[col_in].apply(clean_phone_number)

# Save the updated CSV
df.to_csv('BC-Uvi_1.csv', index=False)

