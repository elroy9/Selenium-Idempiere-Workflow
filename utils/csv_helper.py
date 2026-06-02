import csv

def parse_cost_center(cost_center):
    """
    Input  : "1990923-FARM SUBANG 1"
    {}     : "FARM SUBANG 1"      (full name, ALL CAPS, tanpa angka prefix)
    **     : "F S 1"              (huruf pertama tiap kata, angka dipertahankan)
    """
    # Buang prefix angka (contoh: "1990923-")
    if '-' in cost_center:
        full_name = cost_center.split('-', 1)[1].strip()
    else:
        full_name = cost_center.strip()

    # Buat abbreviasi: huruf pertama tiap kata, angka dipertahankan
    abbrev_parts = []
    for word in full_name.split():
        if word.isdigit():
            abbrev_parts.append(word)  # angka tetap
        else:
            abbrev_parts.append(word[0])  # huruf pertama saja
    abbrev = ' '.join(abbrev_parts)

    return full_name, abbrev


def load_csv(filepath, limit=5):
    rows = []
    with open(filepath, encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=';')
        headers = []
        for i, row in enumerate(reader):
            if i == 0:
                continue  # Skip baris group header
            if i == 1:
                headers = row
                continue
            if len(rows) >= limit:
                break
            if any(row):  # Skip baris kosong
                rows.append(dict(zip(headers, row)))
    return rows