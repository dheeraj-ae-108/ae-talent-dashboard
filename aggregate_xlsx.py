#!/usr/bin/env python3
"""Merge accurate FULL-POOL distributions from 'Arctic Engine _ Data Req.xlsx'
into ae_data.json. These frequency tables cover the full ~1.40M-row universe
(the CSV export was truncated at 1.05M), so they supersede the CSV-derived
global panels for: tech stack (title-derived), company tier, top employers,
sub-departments, and specializations.
Run AFTER aggregate.py.  Person-level + language-filtered panels stay from the CSV.
"""
import pandas as pd, json, re, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
XLSX = sys.argv[1] if len(sys.argv) > 1 else "/Users/dheeraj.salwadi/Downloads/Arctic Engine _ Data Req.xlsx"
OUT = os.path.join(HERE, "ae_data.json")

# ---------- title -> tech / coding discipline (cleaned + expanded; excludes machine programmers) ----------
def tech_stack(title):
    t = " " + str(title).lower() + " "
    def has(*k): return any(x in t for x in k)
    def rx(p): return re.search(p, t) is not None
    # EXCLUDE manufacturing machine programmers (CNC/VMC/PLC) — not software
    if has('cnc', 'vmc', ' plc', ' vfd', 'machine programm', 'robot programm'): return None
    if rx(r'\bjava\b') and 'javascript' not in t: return "Java"
    if rx(r'\bpython\b'): return "Python"
    if rx(r'\.net\b|\bc#|\bdot ?net\b|asp\.net'): return ".NET / C#"
    if rx(r'\bphp\b'): return "PHP"
    if has('machine learning','ml engineer','ai engineer','artificial intel','deep learning',' nlp ','computer vision','data scien','gen ai','genai','llm'): return "AI / ML & Data Science"
    if has('full stack','full-stack','fullstack','mern','mean stack'): return "Full-Stack Development"
    if has('javascript','typescript','react','angular','vue','node','front end','frontend','front-end','ui developer','ui/ux','web developer','wordpress','web design'): return "Web / Front-end"
    if has('android','ios developer','flutter','react native','mobile app','mobile developer','kotlin','swift developer'): return "Mobile"
    if has('data analyst','data engineer','business intelligence','bi developer','bi analyst','tableau','power bi','big data','hadoop','data architect','analytics'): return "Data Engineering & Analytics"
    if rx(r'\bdba\b|database admin|database develop|sql develop|oracle dba|pl/sql|database engineer'): return "Database / SQL"
    if rx(r'\bqa\b|test engineer|software test|automation test|\bsdet\b|\btester\b|quality analyst|test analyst|automation engineer'): return "QA / Testing"
    if has('devops','cloud engineer','cloud architect','cloud administrat',' aws',' azure',' gcp ','kubernetes','docker','site reliability',' sre ','platform engineer','ci/cd'): return "Cloud / DevOps"
    if has('cyber','information security','infosec','soc analyst','penetration test','security engineer','security analyst'): return "Cybersecurity"
    if has('network engineer','network administrat','ccna','ccnp','noc engineer','network support','network security','network operat'): return "Networking"
    if has('embedded','firmware','vlsi',' rtl ','verification engineer','asic','hardware design','pcb','computer hardware','hardware engineer','hardware technician'): return "Embedded / Hardware"
    if rx(r'\bsap\b|\berp\b|salesforce|peoplesoft|oracle apps|dynamics 365|\bcrm\b|informatica|siebel'): return "ERP / SAP / CRM"
    if has('software develop','software engineer','application develop','full stack','full-stack','backend','back end','sde','web services','software programmer','software architect','solution architect','technical architect','application programmer','.net developer','dot net developer','scrum master','software consultant','development engineer'): return "Software Development"
    if has('system administrat','system engineer','desktop support','it support','technical support engineer','it engineer','server administrat','linux administrat','windows administrat','system support','it administrat','it executive','it analyst','it consultant','help desk','helpdesk','service desk','system analyst','it manager','it officer','it head'): return "IT Support & Admin"
    if has('programmer','developer','technical lead','tech lead'): return "Software Development"
    return None

_TIER_PATS = [
    ("FAANG / Global Big-Tech", r'\bgoogle\b|\bamazon\b|\bmeta\b|facebook|\bapple\b|netflix|micro ?soft|nvidia|\bintel\b|qualcomm|\bcisco\b|\badobe\b|salesforce|\buber\b|linkedin|\bsap labs\b|\boracle\b|\bvmware\b|\bpaypal\b|\bebay\b|\bnokia\b|ericsson|\bdell\b|hewlett|walmart (labs|global)|goldman sachs|\bjp ?morgan\b|morgan stanley'),
    ("Indian IT / Global Consulting", r'tata consult|\btcs\b|infosys|wipro|\bhcl\b|cognizant|capgemini|accenture|tech mahindra|\bibm\b|mindtree|mphasis|ltimindtree|\blti\b|\bdxc\b|genpact|deloitte|\bpwc\b|\bkpmg\b|ernst|\bey\b|\bntt\b|\batos\b|hexaware|zensar|birlasoft|coforge|persistent'),
    ("Unicorn / Funded Startup", r'flipkart|\bpaytm\b|\bswiggy\b|zomato|\bola\b|\boyo\b|byju|\bphonepe\b|razorpay|\bmeesho\b|\bcred\b|\bzoho\b|freshworks|\bnykaa\b|unacademy|dream11|\bgroww\b|zerodha|policybazaar|lenskart|delhivery|\budaan\b|postman|browserstack|\bicertis\b|\bpine ?labs\b|\bzeta\b|urban ?company'),
    ("Bank / BFSI / Large Enterprise", r'\bhdfc\b|\bicici\b|axis bank|\bsbi\b|kotak|yes bank|\bidfc\b|indusind|\bbajaj\b|reliance|\btata\b|\bhsbc\b|\bciti\b|standard chartered|american express|wells fargo|\baditya birla\b|mahindra|larsen|\bl&t\b|maruti|\bhero\b|\bitc\b|godrej|vodafone|airtel|\bjio\b'),
]
def company_tier(org):
    o = str(org).lower().strip()
    if o == "" or o in ("self employed","self","private","freelance","na","n/a","none","nan"): return "Other / Unclassified"
    for name, pat in _TIER_PATS:
        if re.search(pat, o): return name
    return "Other / Unclassified"

# ---------- employer SECTOR (industry) classifier — richer than tier, for the client story ----------
_SECTOR_PATS = [
    ("Global Big-Tech", r'\bgoogle\b|\bamazon\b|\bmeta\b|facebook|\bapple\b|netflix|micro ?soft|nvidia|\bintel\b|qualcomm|\bcisco\b|\badobe\b|salesforce|\buber\b|linkedin|\boracle\b|\bdell\b|\bsap\b|\bpaypal\b|\bvmware\b|goldman sachs|\bjp ?morgan\b|morgan stanley|\bsamsung\b|\blg electronics'),
    ("IT Services & Consulting", r'tata consult|\btcs\b|infosys|wipro|\bhcl\b|cognizant|capgemini|accenture|tech mahindra|\bibm\b|mindtree|mphasis|ltimindtree|\blti\b|\bdxc\b|genpact|deloitte|\bpwc\b|\bkpmg\b|ernst|\bey\b|hexaware|zensar|birlasoft|coforge|persistent|teleperformance|concentrix|\bwns\b|quess|randstad|sutherland|firstsource|\bhgs\b|startek|tech ?nolog|software|infotech|\bit solution|\bit service|\bbpo\b|\bkpo\b|datamatics|\bntt\b|\batos\b|virtusa|cybage|\bg4s\b'),
    ("Banking, Finance & Insurance", r'\bbank\b|\bhdfc\b|\bicici\b|axis|\bsbi\b|kotak|\bidfc\b|indusind|bandhan|finance|financial|\bfinserv|insurance|\blic\b|life corp|\bnbfc\b|\bcapital\b|muthoot|shriram|cholamandalam|bajaj fin|\bhdb\b|small finance|\bdbs\b|\bhsbc\b|\bciti\b|standard chartered|american express|angel|motilal|sharekhan|mutual fund|lombard'),
    ("Manufacturing & Industrial", r'industries|manufactur|\bsteel\b|cement|\bmotors\b|automot|automobile|\bauto\b|\btyres?\b|chemical|textile|\bmills\b|electric|electronic|machinery|fabricat|foundry|\bjsw\b|tata motors|maruti|bajaj auto|bosch|\babb\b|siemens|schneider|\bbhel\b|\bsail\b|forbes|precision|components|paints'),
    ("Healthcare & Pharma", r'hospital|\bclinic|healthcare|health care|\bmedical\b|diagnostic|\bpharma|life science|\blabs?\b|apollo|fortis|max health|manipal|\bcipla\b|sun pharma|\bdr\.? reddy|lupin|aurobindo|biocon|\bnursing\b|wellness'),
    ("Retail, FMCG & Consumer", r'\bretail\b|\bstores?\b|\bmart\b|\bbazaar\b|supermarket|hypermarket|\bfashion\b|apparel|\bfmcg\b|unilever|\bitc\b|nestle|\bfoods?\b|beverage|\bconsumer\b|dabur|marico|britannia|patanjali|\bdmart\b|\bbig ?basket|reliance retail|reliance digital|vishal mega|trends|lifestyle|jubilant food|eureka'),
    ("Telecom & Media", r'telecom|\bairtel\b|\bjio\b|vodafone|\bvi\b|\bbsnl\b|\bmtnl\b|communications?|\bmedia\b|broadcast|entertainment|\bzee\b|network18'),
    ("Government, PSU & Defense", r'indian army|air force|\bnavy\b|\barmy\b|\bgovernment\b|ministr|\brailway|municipal|\bpolice\b|\bisro\b|\bdrdo\b|\bongc\b|\bntpc\b|\bgail\b|coal india|public sector|\bpsu\b|\bcrpf\b|\bbsf\b|nagar nigam|panchayat|\bpwd\b'),
    ("Education & Research", r'\bschool\b|schools|\bcollege\b|universit|institut|academy|vidyalaya|\beducation\b|\bkendriya\b|\bcbse\b|coaching|gurukul|research'),
    ("New-age / Startups", r'flipkart|\bpaytm\b|\bswiggy\b|zomato|\bola\b|\boyo\b|byju|\bphonepe\b|razorpay|\bmeesho\b|\bcred\b|\bzoho\b|freshworks|\bnykaa\b|unacademy|dream11|\bgroww\b|zerodha|policybazaar|lenskart|delhivery|\budaan\b|\bcars24|urban ?company|\bspinny|\bzepto|pharmeasy|just ?dial|\bnykaa'),
    ("Hospitality, Travel & Logistics", r'\bhotel\b|resort|restaurant|hospitality|\btravels?\b|\btours?\b|airlines?|indigo|spicejet|\bcargo\b|logistic|\btransport|courier|\bexpress\b|\bdtdc\b|blue dart|shipping|freight|supply chain'),
    ("Energy, Infra & Real Estate", r'\bpower\b|\benergy\b|\boil\b|\bgas\b|petroleum|\bsolar\b|renewable|infrastructure|construction|\bbuilders?\b|\brealty\b|\bestate\b|developers?|\bhousing\b|\binfra\b|reliance industries|larsen|\bl&t\b'),
    ("Self-employed / Freelance", r'self ?employ|\bself\b|freelanc|free lancer|own business|proprietor|home business'),
]
def sector(org):
    s = str(org).lower().strip()
    if s in ("", "na", "n/a", "none", "nan", "private", "private limited", "any company", "company", "xyz", "abc"):
        return "Unspecified"
    for name, pat in _SECTOR_PATS:
        if re.search(pat, s):
            return name
    return "Regional & SME businesses"

# ---------- PRESTIGE employer groups (sought-after clusters, FAANG-style, across industries) ----------
_PRESTIGE_PATS = [
    ("FAANG & Global Big-Tech", r'\bgoogle\b|\bamazon\b|\bmeta\b|facebook|\bapple\b|netflix|micro ?soft|nvidia|\bintel\b|qualcomm|\bcisco\b|\badobe\b|salesforce|\buber\b|linkedin|\boracle\b|\bsap\b|\bdell\b|\bibm\b|\bvmware\b|\bpaypal\b|samsung|\blg electronics|\bnokia\b|ericsson|hewlett|\bhp\b'),
    ("Indian IT Majors", r'tata consult|\btcs\b|infosys|wipro|\bhcl\b|tech mahindra|mindtree|mphasis|ltimindtree|\blti\b|hexaware|coforge|persistent|birlasoft|zensar'),
    ("Global Consulting & GCC", r'accenture|cognizant|capgemini|deloitte|\bpwc\b|\bkpmg\b|ernst|\bey\b|genpact|\bwns\b|\bdxc\b|\bntt\b|\batos\b|mckinsey|\bbcg\b|\bbain\b|nagarro|globallogic|epam|thoughtworks'),
    ("Unicorns & Funded Startups", r'flipkart|\bpaytm\b|\bswiggy\b|zomato|\bola\b|\boyo\b|byju|\bphonepe\b|razorpay|\bmeesho\b|\bcred\b|\bzoho\b|freshworks|\bnykaa\b|unacademy|dream11|\bgroww\b|zerodha|policybazaar|lenskart|delhivery|\budaan\b|\bcars24|urban ?company|\bspinny|\bzepto|pharmeasy|\bpine ?labs|browserstack|postman'),
    ("Global Banks & Financial", r'goldman|\bjp ?morgan\b|morgan stanley|\bciti\b|\bhsbc\b|standard chartered|barclays|deutsche|wells fargo|american express|\bubs\b|credit suisse|blackrock|bny mellon|nomura|societe generale|\bbnp\b|mastercard|\bvisa\b'),
    ("Indian Conglomerates", r'reliance|\btata\b|aditya birla|mahindra|larsen|\bl&t\b|adani|\bitc\b|godrej|\bjsw\b|vedanta|essar|\bbajaj\b|\bhero\b'),
    ("Global Consumer & Pharma MNCs", r'unilever|procter|\bp&g\b|nestle|pepsi|coca ?cola|colgate|\bmars\b|mondelez|\bpfizer\b|novartis|\bgsk\b|roche|astrazeneca|sanofi|abbott|\bcipla\b|dr\.? reddy|sun pharma|lupin|biocon'),
]
def prestige_group(org):
    s = str(org).lower().strip()
    for name, pat in _PRESTIGE_PATS:
        if re.search(pat, s):
            return name
    return None

def qual_bucket(c):
    c = str(c).lower()
    if "phd" in c or "doctor" in c or "d.phil" in c: return "PhD"
    if any(k in c for k in ["m.a","m.com","m.sc","m.tech","m.phil","llm","mba","pgdm","mca","master","m.ed","m.pharm","me/","ms/"]): return "Masters"
    if "pg diploma" in c or "post graduate diploma" in c: return "PG Diploma"
    if any(k in c for k in ["b.a","b.com","b.sc","b.tech","be/","bachelor","bba","bca","llb","b.ed","b.pharm","bhm","bbm","b.e"]): return "Undergraduate"
    if "iti" in c: return "ITI"
    if "diploma" in c or "certificate" in c: return "Diploma / Certificate"
    return "Other"

def phd_domain(s):
    s = str(s).lower()
    def has(*ks): return any(k in s for k in ks)
    if has("law","legal","llb","llm"): return "Law"
    if has("medic","clinical","surgery","nursing","pharmac","dental","physiother","anatomy","physiology","health"): return "Medicine & Health"
    if has("engineer","technology","computer","electronic","mechanical","civil","electrical","instrumentation","aeronaut","automobile"): return "Engineering"
    if has("design","architect","fine art","fashion"): return "Design"
    if has("physic","chemis","biolog","biotech","zoolog","botan","mathematic","science","agricultur","microbio","environ","geolog","statistic","genetic"): return "Sciences"
    if has("commerce","econ","finance","account","market","business","management","banking"): return "Finance & Economics"
    if has("histor","philosoph","art","english","hindi","sanskrit","literatur","sociolog","politic","geograph","psycholog","education","language","music"): return "Humanities & Social Sciences"
    return "Other / Unspecified"

print("reading xlsx…")
jt = pd.read_excel(XLSX, sheet_name="Job Title");        jt.columns = ["v", "n"]
org = pd.read_excel(XLSX, sheet_name="Org Name");         org.columns = ["v", "n"]
sub = pd.read_excel(XLSX, sheet_name="Sub department");   sub.columns = ["v", "n"]
spec = pd.read_excel(XLSX, sheet_name="Spec ");           spec.columns = ["course", "spec", "n"]
for d in (jt, org, sub): d.dropna(subset=["v"], inplace=True)

FULL_ROWS = int(pd.read_excel(XLSX, sheet_name="Org Name").iloc[:, 1].sum())

# tech stack (title-derived, full pool)
jt["stack"] = jt["v"].map(tech_stack)
tech = jt.dropna(subset=["stack"])
tech_stack_full = tech.groupby("stack")["n"].sum().sort_values(ascending=False).astype(int).to_dict()
tech_titled_total = int(tech["n"].sum())

# company tier + top employers (full pool)
org["tier"] = org["v"].map(company_tier)
company_tiers_full = org.groupby("tier")["n"].sum().sort_values(ascending=False).astype(int).to_dict()
prem = org[org["tier"].isin(["FAANG / Global Big-Tech","Indian IT / Global Consulting","Unicorn / Funded Startup"])]
top_employers_full = prem.sort_values("n", ascending=False).head(18).set_index("v")["n"].astype(int).to_dict()
# top employers per tier (for company-landscape cross-filter)
employers_by_tier = {}
for tier, g in org.groupby("tier"):
    employers_by_tier[tier] = g.sort_values("n", ascending=False).head(15).set_index("v")["n"].astype(int).to_dict()

# employer SECTORS (industry breakdown, replaces the 90%-Other tier donut)
org["sector"] = org["v"].map(sector)
employer_sectors = org.groupby("sector")["n"].sum().sort_values(ascending=False).astype(int).to_dict()
employers_by_sector = {}
for sec, g in org.groupby("sector"):
    employers_by_sector[sec] = g.sort_values("n", ascending=False).head(15).set_index("v")["n"].astype(int).to_dict()

# PRESTIGE employer groups (FAANG-style, sought-after clusters) + drill to companies
org["prestige"] = org["v"].map(prestige_group)
_pg = org[org["prestige"].notna()]
prestige_groups = _pg.groupby("prestige")["n"].sum().sort_values(ascending=False).astype(int).to_dict()
employers_by_prestige = {}
for grp, g in _pg.groupby("prestige"):
    employers_by_prestige[grp] = g.sort_values("n", ascending=False).head(15).set_index("v")["n"].astype(int).to_dict()

# sub-departments (full pool, top 15, skip blank)
subdepts_full = sub.sort_values("n", ascending=False).head(15).set_index("v")["n"].astype(int).to_dict()

# specializations + qualifications (full pool, education-expanded)
spec["qual"] = spec["course"].map(qual_bucket)
qualifications_full = spec.groupby("qual")["n"].sum().sort_values(ascending=False).astype(int).to_dict()
top_specializations_full = (spec[spec["spec"].notna()].groupby("spec")["n"].sum()
                            .sort_values(ascending=False).head(18).astype(int).to_dict())
# "Philosophy"/blank = the "Doctor of Philosophy" degree-name artifact, not a subject
_PHD_UNSPEC = ("", "nan", "philosophy", "doctor of philosophy", "phd", "ph.d", "ph.d.", "other")
def phd_spec_display(s):
    return "Other / Unspecified" if str(s).strip().lower() in _PHD_UNSPEC else str(s).strip()
def phd_domain2(s):
    return "Other / Unspecified" if str(s).strip().lower() in _PHD_UNSPEC else phd_domain(s)
def phd_family(s):
    t = str(s).lower().strip()
    def has(*k): return any(x in t for x in k)
    if t in _PHD_UNSPEC: return "Subject not specified"
    if has("computer","information tech","data scien","software","informatics","artificial intel"): return "Computer Science & IT"
    if has("pharma","medic","nursing","clinical","physiology","anatomy","dental","surgery","physiother","ayurved","health","nutrition"): return "Medicine, Pharmacy & Health"
    if has("engineering","engineer","technology","instrumentation","aeronaut","automobile","mechatron","polymer"): return "Engineering & Technology"
    if has("biotech","zoolog","botan","biochem","bioscience","microbio","genetic","biolog","life scien","biosci","entomolog"): return "Life Sciences & Biotech"
    if has("chemis"): return "Chemistry"
    if has("physic","mathemat","statistic","quantitative"): return "Physics & Mathematics"
    if has("agricultur","agronom","horticultur","soil scien","fishery","veterinar","forestry","dairy","animal"): return "Agriculture & Allied"
    if has("econom"): return "Economics"
    if has("commerce","management","business","marketing","human resource","account","finance","banking"): return "Commerce, Management & Business"
    if has("educat","pedagog"): return "Education"
    if has("sociolog","psycholog","social work","social scien","political","geograph","anthropolog","public admin","women","gender","planning","defence","defense"): return "Social Sciences"
    if has("law","legal","jurisprud"): return "Law"
    if has("english","hindi","sanskrit","literatur","histor","arts","language","urdu","tamil","telugu","marathi","kannada","bengali","linguist","religio","cultur","music","fine art","philosoph","journalis","media","theolog","yoga","physical educat","humanit","design","fashion","jyotish","persian"): return "Humanities, Arts & Languages"
    if has("environ","geolog","earth","atmospher","ocean"): return "Environmental & Earth Sci"
    return "Other specialized fields"
phd_spec = spec[spec["qual"] == "PhD"].copy()
phd_spec["disp"] = phd_spec["spec"].map(phd_spec_display)
phd_spec["dom"] = phd_spec["spec"].map(phd_domain2)
phd_domain_full = phd_spec.groupby("dom")["n"].sum().sort_values(ascending=False).astype(int).to_dict()
phd_total_full = int(phd_spec["n"].sum())
_named = phd_spec[phd_spec["disp"] != "Other / Unspecified"]
_top = _named.groupby("disp")["n"].sum().sort_values(ascending=False).head(15)
phd_top_spec_full = {k: int(v) for k, v in _top.items()}
phd_top_spec_full["Other fields (total)"] = phd_total_full - int(_top.sum())
# PhD FIELD FAMILIES — groups the 170+ fragmented specializations so no giant "Other"
phd_spec["fam"] = phd_spec["spec"].map(phd_family)
phd_families = phd_spec.groupby("fam")["n"].sum().sort_values(ascending=False).astype(int).to_dict()
# top PhD specializations per domain (for PhD-network cross-filter)
phd_specs_by_domain = {}
for dom, g in _named.groupby("dom"):
    phd_specs_by_domain[dom] = (g.groupby("disp")["n"].sum()
                                .sort_values(ascending=False).head(15).astype(int).to_dict())

data = json.load(open(OUT))
data["full"] = {
    "rows": FULL_ROWS,
    "tech_stack": tech_stack_full,
    "tech_titled_total": tech_titled_total,
    "company_tiers": company_tiers_full,
    "top_employers": top_employers_full,
    "employers_by_tier": employers_by_tier,
    "employer_sectors": employer_sectors,
    "employers_by_sector": employers_by_sector,
    "prestige_groups": prestige_groups,
    "employers_by_prestige": employers_by_prestige,
    "subdepartments": subdepts_full,
    "qualifications": qualifications_full,
    "top_specializations": top_specializations_full,
    "phd_by_domain": phd_domain_full,
    "phd_total": phd_total_full,
    "phd_top_specializations": phd_top_spec_full,
    "phd_families": phd_families,
    "phd_specs_by_domain": phd_specs_by_domain,
}
json.dump(data, open(OUT, "w"), separators=(",", ":"), default=str)
print("merged full-pool distributions into", OUT)
print("  full rows:", f"{FULL_ROWS:,}", "| tech-titled:", f"{tech_titled_total:,}", "| PhDs:", f"{phd_total_full:,}")
print("  tech stack:", tech_stack_full)
print("  company tiers:", company_tiers_full)
