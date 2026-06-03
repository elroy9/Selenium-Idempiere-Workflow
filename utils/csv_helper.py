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
        sample = f.read(1024)
        f.seek(0)
        delimiter = '\t' if '\t' in sample else ';'

        reader = csv.reader(f, delimiter=delimiter)
        headers = []
        for i, row in enumerate(reader):
            if i == 0:
                continue
            if i == 1:
                headers = [h.strip() for h in row]  # Strip spasi dari semua header
                print(f"   Headers: {headers[:5]}...")
                continue
            if len(rows) >= limit:
                break
            if any(row):
                rows.append(dict(zip(headers, row)))

    return rows