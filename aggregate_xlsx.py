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

# ---------- title -> tech stack / discipline (fires only on clearly-technical titles) ----------
def tech_stack(title):
    t = " " + str(title).lower() + " "
    def has(*k): return any(x in t for x in k)
    def rx(p): return re.search(p, t) is not None
    if rx(r'\bjava\b') and 'javascript' not in t: return "Java"
    if rx(r'\bpython\b'): return "Python"
    if rx(r'\.net\b|\bc#|\bdot ?net\b|asp\.net'): return ".NET / C#"
    if rx(r'\bphp\b'): return "PHP"
    if has('javascript','typescript','react','angular','vue','node','front end','frontend','front-end','ui developer','web developer','wordpress'): return "Web / Front-end (JS)"
    if has('android','ios developer','flutter','react native','mobile app','mobile developer'): return "Mobile"
    if has('data scien','data analyst','data engineer','business intelligence','bi developer','tableau','power bi','big data','hadoop','machine learning','ml engineer'): return "Data & Analytics"
    if rx(r'\bdba\b|database admin|database develop|sql develop|oracle dba|pl/sql'): return "Database / SQL"
    if rx(r'\bqa\b|test engineer|software test|automation test|\bsdet\b|\btester\b'): return "QA / Testing"
    if has('devops','cloud engineer','cloud architect',' aws',' azure','kubernetes','site reliability',' sre '): return "Cloud / DevOps"
    if has('network engineer','network administrat','ccna','noc engineer','network support'): return "Networking"
    if has('embedded','firmware','vlsi',' rtl ','verification engineer','asic'): return "Embedded / Hardware"
    if rx(r'\bsap\b|\berp\b|salesforce|peoplesoft|oracle apps'): return "ERP / SAP / CRM"
    if has('system administrat','system engineer','desktop support','it support','technical support engineer','it engineer','server administrat','linux administrat','windows administrat','system support','it administrat','hardware and network','hardware & network','computer hardware'): return "Systems / IT Admin"
    if has('software develop','software engineer','application develop','programmer','full stack','full-stack','backend develop','back end develop','sde','web services','software programmer'): return "Backend / General SW"
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
phd_spec = spec[spec["qual"] == "PhD"].copy()
phd_spec["disp"] = phd_spec["spec"].map(phd_spec_display)
phd_spec["dom"] = phd_spec["spec"].map(phd_domain2)
phd_domain_full = phd_spec.groupby("dom")["n"].sum().sort_values(ascending=False).astype(int).to_dict()
phd_total_full = int(phd_spec["n"].sum())
_named = phd_spec[phd_spec["disp"] != "Other / Unspecified"]
_top = _named.groupby("disp")["n"].sum().sort_values(ascending=False).head(15)
phd_top_spec_full = {k: int(v) for k, v in _top.items()}
phd_top_spec_full["Other fields (total)"] = phd_total_full - int(_top.sum())
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
    "subdepartments": subdepts_full,
    "qualifications": qualifications_full,
    "top_specializations": top_specializations_full,
    "phd_by_domain": phd_domain_full,
    "phd_total": phd_total_full,
    "phd_top_specializations": phd_top_spec_full,
    "phd_specs_by_domain": phd_specs_by_domain,
}
json.dump(data, open(OUT, "w"), separators=(",", ":"), default=str)
print("merged full-pool distributions into", OUT)
print("  full rows:", f"{FULL_ROWS:,}", "| tech-titled:", f"{tech_titled_total:,}", "| PhDs:", f"{phd_total_full:,}")
print("  tech stack:", tech_stack_full)
print("  company tiers:", company_tiers_full)
