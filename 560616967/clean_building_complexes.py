
# 1 --> CLEAN THE ORIGINAL BUILDING FILE
raw = pd.read_csv(IN + 'BuildingComplexPoint.csv', low_memory=False)
b = raw.dropna(axis=1, how='all')                                   # drop fully empty columns
b = b.drop(columns=[c for c in b.columns if b[c].nunique(dropna=True) <= 1])  # drop constant columns
for c in b.columns:                                                 # parse any date columns
    if c.endswith('date') or c == 'lastupdate':
        b[c] = pd.to_datetime(b[c], errors='coerce')
b = b.drop_duplicates('topoid')                                     # one row per building id

d = b[b.generalname.notna()][['generalname', 'buildingcomplextype']].copy()  # drop rows with no name
d['Name'] = d.generalname.str.upper().str.replace(r'\s+', ' ', regex=True).str.strip()

# Display name: Title Case, but keep apostrophes and acronyms tidy
d['Building'] = d.Name.str.title().str.replace(r"'S\b", "'s", regex=True)
for ac in ['SES', 'RSL', 'TAFE', 'PCYC', 'CFR', 'RFB', 'SLSC', 'CWA', 'NSW', 'ACT', 'JRLFC',
           'RFS', 'ANZAC', 'TAB', 'YMCA', 'YWCA', 'CSIRO', 'ADFA', 'UNSW', 'ANU']:
    d['Building'] = d.Building.str.replace(r'\b' + ac.title() + r'\b', ac, regex=True)

# 2 --> CATEGORISE (keywords in the name first, then the numeric type code)
RULES = [  # order matters: first match wins
 ('Emergency services', r'\b(FIRE|POLICE|AMBULANCE|SES|RFB|RESCUE|RFS|FRNSW|LIFESAVING|SLSC|FIRE CONTROL)\b'),
 ('Education', r'\b(SCHOOL|COLLEGE|UNIVERSITY|TAFE|PRESCHOOL|PRE-SCHOOL|PRE SCHOOL|KINDERGARTEN|CAMPUS|ACADEMY|EARLY LEARNING|CHILD ?CARE|LEARNING CENTRE|INSTITUTE|PLC)\b'),
 ('Health & aged care', r'\b(HOSPITAL|NURSING|AGED|HEALTH|MEDICAL|HOSTEL|HOSPICE|CLINIC|RETIREMENT|DIALYSIS|MULTI.?PURPOSE SERVICE)\b'),
 ('Religious', r'\b(CHURCH|CATHEDRAL|CHAPEL|CATHOLIC|ANGLICAN|UNITING|BAPTIST|PRESBYTERIAN|LUTHERAN|METHODIST|ORTHODOX|PENTECOSTAL|MOSQUE|TEMPLE|SYNAGOGUE|CONVENT|MONASTERY|PARISH|MISSION|SALVATION ARMY|CHRISTIAN|KINGDOM HALL|CHURCH OF)\b'),
 ('Government & civic', r'\b(COUNCIL|COURT ?HOUSE|POST OFFICE|LIBRARY|TOWN HALL|CHAMBERS|ADMINISTRATION|GOVERNMENT|MOTOR REGISTRY|SERVICE NSW|CENTRELINK|PARLIAMENT|PRISON|CORRECTIONAL|DEFENCE|BARRACKS|CUSTOMS)\b'),
 ('Sport & recreation', r'\b(POOL|SWIMMING|AQUATIC|BATHS|GOLF|BOWLING|BOWLS|TENNIS|STADIUM|SPORTS?|RACECOURSE|RACING|SPEEDWAY|SHOWGROUND|OVAL|LEISURE|RECREATION|GYM|SKATE|NETBALL|CRICKET|FOOTBALL|RUGBY|SOCCER|JOCKEY|TURF|CANOE|ROWING|YACHT|SAILING|FISHING)\b'),
 ('Clubs & community halls', r'\b(CLUB|RSL|HALL|COMMUNITY|SCOUT|GUIDES|CWA|MASONIC|LODGE|SERVICES? CENTRE|NEIGHBOURHOOD)\b'),
 ('Culture & tourism', r'\b(MUSEUM|GALLERY|THEATRE|CINEMA|ART CENTRE|HERITAGE|VISITOR|INFORMATION CENTRE|HISTORICAL|ZOO|AQUARIUM)\b'),
 ('Accommodation & caravan parks', r'\b(CARAVAN|HOLIDAY|TOURIST|RESORT|MOTEL|HOTEL|MOTOR INN|CAMPING|BACKPACKER|HOSTEL|LODGE|VILLAGE|APARTMENTS?)\b'),
 ('Utilities & infrastructure', r'\b(SUBSTATION|TREATMENT|SEWAGE|SEWERAGE|SEWER|POWER STATION|WATER|DEPOT|PUMP|RESERVOIR|TRANSMISSION|EXCHANGE|WORKS|TERMINAL|AIRPORT|RAILWAY|STATION)\b'),
 ('Shopping & commercial', r'\b(SHOPPING|PLAZA|MARKET|MALL|SHOPS|ARCADE|WOOLWORTHS|COLES|BANK|PETROL|SERVICE STATION|FACTORY|INDUSTRIAL|WAREHOUSE|OFFICES?)\b'),
]

# Fallback when no keyword matches The type codes have no official lookup in the file, so these were inferred by looking at the names within each code.
TYPE_FALLBACK = {16: 'Religious', 2: 'Education', 23: 'Education', 11: 'Government & civic',
                 18: 'Government & civic', 15: 'Sport & recreation', 12: 'Sport & recreation',
                 14: 'Culture & tourism', 20: 'Culture & tourism', 17: 'Emergency services',
                 19: 'Emergency services', 9: 'Utilities & infrastructure', 10: 'Utilities & infrastructure',
                 24: 'Accommodation & caravan parks', 21: 'Accommodation & caravan parks',
                 4: 'Health & aged care', 3: 'Clubs & community halls'}
COMPILED = [(c, re.compile(p)) for c, p in RULES]
UNCLASSIFIED = 'Unclassified (rural property / unnamed)'   # type 7 = generic names like "THE SPRINGS"

def categorise(name, type_code):
    for cat, pat in COMPILED:
        if pat.search(name):
            return cat
    if type_code in TYPE_FALLBACK:
        return TYPE_FALLBACK[type_code]
    return UNCLASSIFIED if type_code == 7 else 'Other'

d['Category'] = [categorise(n, t) for n, t in zip(d.Name, d.buildingcomplextype)]

# 3 --> SUBURB -> POSTCODE LOOKUP (from the other datasets)
ws = lambda s: re.sub(r'\s+', ' ', str(s)).strip()
lf = pd.read_csv(IN + 'locationfacilitydata.csv')
ev = pd.read_csv(IN + 'ev_20251216_updated.csv')
sp = pd.read_excel(IN + 'table.xlsx', dtype={'Postcode': 'string'})

pairs = []
for a in lf.ADDRESS.dropna().map(ws):                      # "Great North Rd, Abbotsford NSW 2046"
    m = re.search(r",\s*([A-Za-z'.\- ]+?)\s+(?:NSW|ACT)\s+(\d{4})\s*$", a)
    if m: pairs.append((m.group(1).strip().upper(), m.group(2)))
for a in ev.Station_address.dropna().map(ws).str.replace(r',?\s*Australia$', '', regex=True):
    m = re.search(r",\s*([A-Za-z'.\- ]+?),?\s+(?:NSW,?\s+)?(\d{4})(?:,\s*NSW)?\s*$", a)
    if m: pairs.append((m.group(1).strip().upper(), m.group(2)))
for s, p in zip(sp.Suburb.map(ws), sp.Postcode):
    pairs.append((s.upper(), str(p).zfill(4)))

counts = collections.defaultdict(collections.Counter)
for s, p in pairs:
    counts[s][p] += 1

# Strict rules: >=4 letters, not a generic word, and >=80% of sightings agree on one postcode
GENERIC = {'SYDNEY', 'PARK', 'HILL', 'HILLS', 'WEST', 'NORTH', 'SOUTH', 'EAST', 'CITY', 'TOWN',
           'CENTRAL', 'BEACH', 'LAKE', 'RIVER', 'ROAD', 'STREET', 'WATER', 'HEAD', 'POINT', 'BAY',
           'CREEK', 'VALE', 'VALLEY', 'GLEN', 'FARM', 'VIEW', 'CAMPUS'}
lookup = {}
for s, c in counts.items():
    pc, n = c.most_common(1)[0]
    if len(s) >= 4 and s not in GENERIC and n / sum(c.values()) >= 0.8:
        lookup[s] = pc

# 4. ASSIGN SUBURB / POSTCODE FROM THE BUILDING NAME
suburb_re = re.compile(r'^(%s)\b' % '|'.join(re.escape(k) for k in sorted(lookup, key=len, reverse=True)))

def suburb_of(name, cat):
    if cat == UNCLASSIFIED:                       # generic property names: too risky to match
        return None
    m = suburb_re.match(name)
    return m.group(1) if m and len(name) > len(m.group(1)) else None   # something must follow the suburb

d['Suburb_key'] = [suburb_of(n, c) for n, c in zip(d.Name, d.Category)]
d['Postcode'] = d.Suburb_key.map(lookup)
d['Suburb'] = d.Suburb_key.str.title()

matched = (d[d.Postcode.notna()]
           .drop_duplicates(['Suburb', 'Category', 'Building'])
           .assign(Postcode=lambda x: x.Postcode.astype(int))
           .sort_values(['Postcode', 'Suburb', 'Category', 'Building'])
           [['Postcode', 'Suburb', 'Category', 'Building']])
unmatched = (d[d.Postcode.isna()].sort_values(['Category', 'Building'])[['Category', 'Building']])
print(f'{len(d):,} named | {len(matched):,} matched to {matched.Suburb.nunique()} suburbs | {len(unmatched):,} unmatched')

# 5. WRITE THE WORKBOOK (one row per suburb; counts are live formulas)
F = lambda **k: Font(**{'name': 'Arial', 'size': 10, **k})
HEAD = PatternFill('solid', fgColor='1F3864')
def style_header(ws):
    for c in ws[1]:
        c.font = F(bold=True, color='FFFFFF'); c.fill = HEAD
        c.alignment = Alignment(vertical='center', wrap_text=True)

cats = list(matched.Category.value_counts().index)
wb = Workbook()
notes = wb.active; notes.title = 'Notes'

# Detail sheet (flat list)
detail = wb.create_sheet('Detail')
detail.append(['Postcode', 'Suburb', 'Category', 'Building complex'])
for r in matched.itertuples(index=False): detail.append(list(r))
style_header(detail); detail.freeze_panes = 'A2'; detail.auto_filter.ref = detail.dimensions
for i, w in enumerate([10, 24, 34, 52], 1): detail.column_dimensions[L(i)].width = w
last = len(matched) + 1

# By Suburb: 1 row per suburb, categories listed inside the cell
def category_block(g):
    lines = []
    for c in cats:
        names = g[g.Category == c].Building.tolist()
        if names: lines.append(f'{c} ({len(names)}): ' + '; '.join(names))
    return '\n'.join(lines)

by_sub = (matched.groupby(['Postcode', 'Suburb']).apply(category_block, include_groups=False)
          .reset_index(name='cats'))
bs = wb.create_sheet('By_Suburb', 0)
bs.append(['Postcode', 'Suburb', 'Total buildings', 'Building complexes by category'])
for i, r in enumerate(by_sub.itertuples(index=False), 2):
    bs.append([r.Postcode, r.Suburb,
               f'=COUNTIFS(Detail!$A$2:$A${last},A{i},Detail!$B$2:$B${last},B{i})', r.cats])
    bs.row_dimensions[i].height = max(14, 13.5 * (r.cats.count('\n') + 1 + len(r.cats) // 170))
style_header(bs); bs.freeze_panes = 'A2'; bs.auto_filter.ref = bs.dimensions
for i, w in enumerate([10, 24, 10, 140], 1): bs.column_dimensions[L(i)].width = w
for row in bs.iter_rows(min_row=2):
    for c in row:
        c.font = F(); c.alignment = Alignment(wrap_text=(c.column == 4), vertical='top')

# Suburb x Category grid
grid = wb.create_sheet('Suburb_x_Category', 1)
subs = matched[['Postcode', 'Suburb']].drop_duplicates().sort_values(['Postcode', 'Suburb']).values.tolist()
grid.append(['Postcode', 'Suburb'] + cats + ['Total'])
for i, (p, s) in enumerate(subs, 2):
    grid.append([p, s] + [f'=COUNTIFS(Detail!$A$2:$A${last},$A{i},Detail!$B$2:$B${last},$B{i},'
                          f'Detail!$C$2:$C${last},{L(3 + j)}$1)' for j in range(len(cats))]
                + [f'=SUM(C{i}:{L(2 + len(cats))}{i})'])
n = len(subs) + 1
grid.append(['TOTAL', ''] + [f'=SUM({L(c)}2:{L(c)}{n})' for c in range(3, 4 + len(cats))])
style_header(grid); grid.freeze_panes = 'C2'; grid.row_dimensions[1].height = 42
grid.column_dimensions['A'].width = 10; grid.column_dimensions['B'].width = 24
for j in range(len(cats) + 1): grid.column_dimensions[L(3 + j)].width = 15
for row in grid.iter_rows(min_row=2):
    for c in row: c.font = F(bold=(c.row == n + 1))

for line in [
    'Building complexes grouped by postcode, suburb and category', '',
    'Source has NO coordinates, address, suburb or postcode: suburb/postcode are inferred from the building name.',
    f'{len(d):,} buildings have a name; {len(matched):,} were placed in a suburb. The rest could not be placed and are not included.',
]: notes.append([line])
notes['A1'].font = F(bold=True, size=14); notes.column_dimensions['A'].width = 140

wb.save(OUT + 'building_complexes_by_suburb.xlsx')
# After running, recalculate formulas (e.g. open in Excel)
