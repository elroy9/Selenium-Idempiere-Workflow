import csv

def parse_cost_center(cost_center):
    if '-' in cost_center:
        full_name = cost_center.split('-', 1)[1].strip()
    else:
        full_name = cost_center.strip()

    abbrev_parts = []
    for word in full_name.split():
        if word.isdigit():
            abbrev_parts.append(word)
        else:
            abbrev_parts.append(word[0])
    abbrev = ' '.join(abbrev_parts)

    return full_name, abbrev


def load_csv(filepath, limit=5):
    rows = []
    with open(filepath, encoding='utf-8-sig') as f:
        sample = f.read(2048)
        f.seek(0)

        # Deteksi delimiter: tab, semicolon, atau koma
        if '\t' in sample:
            delimiter = '\t'
        elif ';' in sample:
            delimiter = ';'
        else:
            delimiter = ','

        print(f"   CSV delimiter: '{delimiter}'")

        reader = csv.reader(f, delimiter=delimiter)
        headers = []
        for i, row in enumerate(reader):
            if i == 0:
                continue  # Skip baris group header
            if i == 1:
                headers = [h.strip() for h in row]
                print(f"   Headers: {headers[:5]}...")
                continue
            if len(rows) >= limit:
                break
            if any(row):
                rows.append(dict(zip(headers, row)))

    return rows