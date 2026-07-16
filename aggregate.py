#!/usr/bin/env python3
"""Arctic Engine talent-pool aggregator.
Reads the raw candidate CSV, produces a compact ae_data.json for the dashboard.
Person-level stats dedupe to one record per user_id; education splits are record-level.
"""
import pandas as pd, json, re, sys
from collections import Counter

SRC = sys.argv[1] if len(sys.argv) > 1 else \
    "/Users/dheeraj.salwadi/Downloads/arctic_engines___10__years_exp_candidates_2026-07-15T18_50_27.959769836+05_30.csv"
OUT = "/Users/dheeraj.salwadi/Documents/agent_for_events/ae_dashboard/ae_data.json"

print("loading…")
df = pd.read_csv(SRC, dtype=str, keep_default_na=False)
df.columns = [c.strip() for c in df.columns]
for c in df.columns:
    df[c] = df[c].str.strip()
df["yoe"] = pd.to_numeric(df["years_of_experience"], errors="coerce").fillna(0).astype(int)

RAW_ROWS = len(df)
TRUNCATED = RAW_ROWS >= 1048575  # Excel/export hard cap

# ---------- qualification mapping ----------
def qual_bucket(c):
    c = c.lower()
    if "phd" in c or "doctor" in c or "d.phil" in c: return "PhD"
    if c.startswith(("m.","me/","ms/","mba","pgdm","mca","mtech"," me","master")) or \
       any(k in c for k in ["m.a","m.com","m.sc","m.tech","m.phil","llm","mba","pgdm","mca","master","m.ed","m.pharm","md/"]):
        return "Masters"
    if "pg diploma" in c or "post graduate diploma" in c: return "PG Diploma"
    if c.startswith(("b.","be/","bba","bca","bachelor","llb","b ")) or \
       any(k in c for k in ["b.a","b.com","b.sc","b.tech","bachelor","bba","bca","llb","b.ed","b.pharm","bhm","bbm","b.e"]):
        return "Undergraduate"
    if "iti" in c: return "ITI"
    if "diploma" in c or "certificate" in c: return "Diploma / Certificate"
    return "Other"

QUAL_RANK = {"PhD":6,"Masters":5,"PG Diploma":4,"Undergraduate":3,"Diploma / Certificate":2,"ITI":1,"Other":0}
df["qual"] = df["course_title"].map(qual_bucket)

# ---------- PhD domain mapping ----------
def phd_domain(s):
    s = s.lower()
    def has(*ks): return any(k in s for k in ks)
    if has("law","legal","llb","llm","jurisprudence"): return "Law"
    if has("medic","clinical","surgery","nursing","pharmac","dental","physiother","anatomy","physiology","health"): return "Medicine & Health"
    if has("engineer","technology","computer","electronic","mechanical","civil","electrical","instrumentation","aeronaut","automobile"): return "Engineering"
    if has("design","architect","fine art","fashion"): return "Design"
    if has("physic","chemis","biolog","biotech","zoolog","botan","mathematic","science","agricultur","microbio","environ","geolog","statistic","genetic"): return "Sciences"
    if has("commerce","econ","finance","account","market","business","management","banking"): return "Finance & Economics"
    if has("histor","philosoph","art","english","hindi","sanskrit","literatur","sociolog","politic","geograph","psycholog","education","language","tamil","telugu","kannada","marathi","urdu","music","religion","cultur"): return "Humanities & Social Sciences"
    return "Other / Unspecified"

# ---------- domain vertical mapping (from department) ----------
def vertical(dep):
    d = dep.lower()
    def has(*ks): return any(k in d for k in ks)
    if has("software","it & information","information security","data scien","product management","engineering - hardware","hardware & networks"): return "Technology"
    if has("finance","banking","insurance","financial","risk management","compliance","investment"): return "Finance & Banking"
    if has("legal","law"): return "Legal"
    if has("healthcare","doctor","hospital","medical","pharma","nursing"): return "Healthcare"
    if has("teaching","training","education","academ"): return "Education"
    if has("marketing","brand","digital marketing","advertising","communication"): return "Marketing"
    if has("design","media production","content","creative","writing"): return "Design & Content"
    if has("sales","bd","business development","retail","ecommerce"): return "Sales & Enterprise"
    if has("manufactur","production","construction","site engineering","maintenance","quality assurance",
           "aviation","aerospace","energy","mining","tailoring","apparel","research & development","engineering"): return "Manufacturing & Engineering"
    if has("admin","operations","customer support","purchase","supply chain","human resources","facility","project & program",
           "delivery","driver","logistics","security services","shipping","maritime","domestic worker"): return "Operations & Support"
    if d == "": return "Unclassified"
    return "Other"

# ---------- vertical fallback from job_title (best-effort remap of Unclassified) ----------
def vertical_from_title(title):
    t = " " + str(title).lower() + " "
    def has(*ks): return any(k in t for k in ks)
    if has("account","audit","tax","finance","financial","banking","\bbank","loan","credit","cashier","billing","treasury","ca ","chartered account","collection","recovery","insurance advisor","underwrit","actuar","wealth","invest"): return "Finance & Banking"
    if has("teacher","teaching","professor","lecturer","tutor","faculty","principal","educat","trainer","instructor","academic","warden","librarian","counsellor"): return "Education"
    if has("doctor","nurse","nursing","pharmac","medical","clinical","hospital","physician","surgeon","dental","physiother","radiolog","lab technician","pathology","paramedic","dmo","healthcare","ward ","ayurved","optometr","dietician"): return "Healthcare"
    if has("software","developer","programmer"," it ","information tech","system admin","network engineer","data scien","data analyst","data engineer","devops","full stack","web developer","tech lead","qa engineer","test engineer","database","mis ","business analyst"): return "Technology"
    if has("marketing","brand","digital market","seo","content market","advertis","social media","campaign","public relation"): return "Marketing"
    if has("designer","graphic","ui/ux","ux","creative","video edit","photograph","animation","illustrat","content writer","copywriter","fashion","interior"): return "Design & Content"
    if has("legal","lawyer","advocate","attorney","paralegal","compliance officer"): return "Legal"
    if has("sales","business development","bd ","bde","territory","area sales","relationship manager","account manager","key account","retail","ecommerce","store manager","branch manager","agency manager","counter sales","field officer","asm","insurance sales","dealer"): return "Sales & Enterprise"
    if has("engineer","technician","civil","mechanical","electrical","electronic","production","manufactur","factory","plant","site ","fabrication","welder","fitter","machinist","quality control","maintenance","supervisor","foreman","cnc","instrumentation","electrician","plumber","carpenter","machine operator","assembly","mechanic","turner","boiler","surveyor","draughtsman"): return "Manufacturing & Engineering"
    if has("admin","office","back office","computer operator","data entry","clerk","receptionist","secretary","driver","logistic","delivery","warehouse","supply","procurement","purchase","hr ","human resource","recruit","payroll","operation","coordinator","executive assistant","stores","store incharge","inventory","stock","customer care","customer service","customer support","facility","housekeeping","security","transport","fleet","dispatch","hotel","restaurant","hospitality","catering","chef","cook","waiter","front desk","cabin crew","peon","office boy"): return "Operations & Support"
    return "Unclassified"

# ---------- role -> stack / discipline bucket (inferred from job_title) ----------
def stack_bucket(title):
    t = " " + title.lower() + " "
    def has(*ks): return any(k in t for k in ks)
    import re as _re
    def rx(p): return _re.search(p, t) is not None
    # explicit language signal first (highest confidence)
    if rx(r'\bjava\b') and "javascript" not in t: return "Java"
    if rx(r'\bpython\b'): return "Python"
    if rx(r'\.net|\bc#|dotnet|asp\.net'): return ".NET / C#"
    if rx(r'\bphp\b'): return "PHP"
    if has("react","angular","javascript","front end","front-end","frontend","ui developer","web developer","node"): return "Web / Front-end (JS)"
    if has("android","ios developer","mobile app","flutter","react native"): return "Mobile"
    # role-archetype inference (no explicit language in title)
    if has("data analyst","data scien","data engineer","business intelligence","tableau","power bi","big data","machine learning","\bml\b","analytics"): return "Data & Analytics"
    if rx(r'\bqa\b|test engineer|software test|automation test|\bsdet\b|quality analyst|tester'): return "QA / Testing"
    if has("devops","cloud","aws","azure","kubernetes","site reliability","\bsre\b"): return "Cloud / DevOps"
    if has("network","telecom","\bnoc\b","ccna","routing"): return "Networking"
    if has("sap","\berp\b","oracle apps","salesforce","peoplesoft"): return "ERP / SAP / CRM"
    if has("embedded","firmware","vlsi","\brtl\b","electronics","semiconductor"): return "Embedded / Hardware"
    if has("system admin","desktop support","it support","it engineer","helpdesk","help desk","technical support","system engineer","it executive","it administrator"): return "Systems / IT Admin"
    if has("product manager","project manager","program manager","scrum","delivery manager","engineering manager","technical lead","team lead","architect"): return "Product / Eng Leadership"
    if has("software develop","software engineer","programmer","full stack","backend","back end","application develop","sde"): return "Backend / General SW"
    return "Other / Unspecified"

# ---------- company tier (from organization_name) ----------
import re as _re2
_TIER_PATS = [
    ("FAANG / Global Big-Tech", r'\bgoogle\b|\bamazon\b|\bmeta\b|facebook|\bapple\b|netflix|micro ?soft|nvidia|\bintel\b|qualcomm|\bcisco\b|\badobe\b|salesforce|\buber\b|linkedin|\bsap labs\b|\boracle\b|\bvmware\b|\bpaypal\b|\bebay\b|\bnokia\b|ericsson|\bdell\b|hewlett|walmart (labs|global)|goldman sachs|\bjp ?morgan\b|morgan stanley'),
    ("Indian IT / Global Consulting", r'tata consult|\btcs\b|infosys|wipro|\bhcl\b|cognizant|capgemini|accenture|tech mahindra|\bibm\b|mindtree|mphasis|ltimindtree|\blti\b|\bdxc\b|genpact|deloitte|\bpwc\b|\bkpmg\b|ernst|\bey\b|\bntt\b|\batos\b|hexaware|zensar|birlasoft|coforge|persistent'),
    ("Unicorn / Funded Startup", r'flipkart|\bpaytm\b|\bswiggy\b|zomato|\bola\b|\boyo\b|byju|\bphonepe\b|razorpay|\bmeesho\b|\bcred\b|\bzoho\b|freshworks|\bnykaa\b|unacademy|dream11|\bgroww\b|zerodha|policybazaar|lenskart|delhivery|\budaan\b|postman|browserstack|\bicertis\b|\bpine ?labs\b|\bzeta\b|urban ?company'),
    ("Bank / BFSI / Large Enterprise", r'\bhdfc\b|\bicici\b|axis bank|\bsbi\b|kotak|yes bank|\bidfc\b|indusind|\bbajaj\b|reliance|\btata\b|\bhsbc\b|\bciti\b|standard chartered|american express|wells fargo|\baditya birla\b|mahindra|larsen|\bl&t\b|maruti|\bhero\b|\bitc\b|godrej|vodafone|airtel|\bjio\b'),
]
def company_tier(org):
    o = org.lower().strip()
    if o == "" or o in ("self employed","self","private","freelance","na","n/a","none"): return "Other / Unclassified"
    for name, pat in _TIER_PATS:
        if _re2.search(pat, o): return name
    return "Other / Unclassified"

# ---------- institute tier (proxy, keyword match) ----------
TIERS = [
    ("IITs", r'\biit\b|indian institute of technology'),
    ("NITs", r'\bnit\b|national institute of technology'),
    ("IIMs", r'\biim\b|indian institute of management'),
    ("BITS", r'\bbits\b|birla institute of technology'),
    ("IISc", r'indian institute of science'),
    ("NLUs (Law)", r'national law'),
    ("AIIMS (Medical)", r'aiims|all india institute of medical'),
]

# ========== PERSON-LEVEL (one row per user) ==========
print("person-level aggregation…")
g = df.groupby("user_id", sort=False)
# highest qual per user
df["qrank"] = df["qual"].map(QUAL_RANK)
person = df.sort_values("qrank", ascending=False).drop_duplicates("user_id")  # keeps highest-qual row per user
N_USERS = person["user_id"].nunique()

# languages person-level
lang = Counter()
for s in person["languages"]:
    for l in str(s).split(","):
        l = l.strip()
        if l: lang[l] += 1

# experience buckets (person-level) — 8-11 / 12-15 / 16-20 / 20+
def exp_bucket(y):
    if y <= 11: return "8–11 yrs"
    if y <= 15: return "12–15 yrs"
    if y <= 20: return "16–20 yrs"
    return "20+ yrs"
person["expb"] = person["yoe"].map(exp_bucket)

# qualification distribution person-level
qual_dist = person["qual"].value_counts().to_dict()

# vertical + median yoe person-level — remap blank-department via job_title
def vert_combined(row):
    v = vertical(row["department"])
    if v == "Unclassified":
        v = vertical_from_title(row["job_title"])
    return v
person["vertical"] = person.apply(vert_combined, axis=1)
vg = person.groupby("vertical").agg(count=("user_id","size"), median_yoe=("yoe","median"))
vg = vg.sort_values("count", ascending=False)
verticals = [{"name":i, "count":int(r["count"]), "median_yoe":float(r["median_yoe"]),
              "share": round(100*r["count"]/N_USERS,2)} for i,r in vg.iterrows()]

# department raw distribution (person-level, top 20)
dept_dist = person[person["department"]!=""]["department"].value_counts().head(20)

avg_yoe = round(float(person["yoe"].mean()), 2)
median_yoe = float(person["yoe"].median())

# ========== PhD NETWORK ==========
print("phd network…")
# "Philosophy"/blank specialization = the "Doctor of Philosophy" degree-name artifact, not a subject
_PHD_UNSPEC = ("", "philosophy", "doctor of philosophy", "phd", "ph.d", "ph.d.", "other")
def phd_spec_display(s):
    return "Other / Unspecified" if str(s).strip().lower() in _PHD_UNSPEC else str(s).strip()
def phd_domain2(s):
    return "Other / Unspecified" if str(s).strip().lower() in _PHD_UNSPEC else phd_domain(s)
phd_rows = df[df["qual"]=="PhD"].copy()
phd_users = phd_rows.drop_duplicates("user_id").copy()
phd_users["pdomain"] = phd_users["specialization_title"].map(phd_domain2)
phd_domain_dist = phd_users["pdomain"].value_counts().to_dict()
N_PHD = phd_users["user_id"].nunique()
phd_users["spec_disp"] = phd_users["specialization_title"].map(phd_spec_display)
_sc = phd_users[phd_users["spec_disp"] != "Other / Unspecified"]["spec_disp"].value_counts().head(15)
phd_spec_top = {k: int(v) for k, v in _sc.items()}
phd_spec_top["Other fields (total)"] = int(N_PHD) - int(_sc.sum())
phd_vertical = phd_users["department"].map(vertical).value_counts().to_dict()

# ========== TECH / CODING SUB-CUT (proxy: software+IT depts) ==========
print("tech sub-cut…")
TECH_DEPTS = ["Software Engineering","IT & Information Security","Engineering - Hardware & Networks",
              "Product Management","Data Science & Analytics"]
tech = person[person["department"].isin(TECH_DEPTS)].copy()
N_TECH = len(tech)
tech_dept_dist = tech["department"].value_counts().to_dict()
tech_sub_dist = tech[tech["sub_department"]!=""]["sub_department"].value_counts().head(15).to_dict()
tech_spec_dist = tech[tech["specialization_title"]!=""]["specialization_title"].value_counts().head(15).to_dict()
tech_exp = tech["expb"].value_counts().to_dict()
# role-inferred stack + company tier for the tech pool
tech = tech.copy()
tech["stack"] = tech["job_title"].map(stack_bucket)
tech["ctier"] = tech["organization_name"].map(company_tier)
tech_stack_dist = tech["stack"].value_counts().to_dict()
tech_ctier_dist = tech["ctier"].value_counts().to_dict()

# company tier across the WHOLE pool
person["ctier"] = person["organization_name"].map(company_tier)
company_tier_dist = person["ctier"].value_counts().to_dict()
# named-company breakdown inside the two premium tiers (top employers)
prem = person[person["ctier"].isin(["FAANG / Global Big-Tech","Indian IT / Global Consulting","Unicorn / Funded Startup"])]
top_employers = prem[prem["organization_name"]!=""]["organization_name"].str.strip().value_counts().head(20).to_dict()

# institute tiers (person-level, unique users matched)
inst = person["education_institute_name"].str.lower()
tier_counts = {}
for name, pat in TIERS:
    tier_counts[name] = int(inst.str.contains(pat, na=False, regex=True).sum())
inst_present = int((person["education_institute_name"]!="").sum())

# experience histogram (person-level, capped display)
exp_hist = person["yoe"].value_counts().sort_index()
exp_hist = {int(k):int(v) for k,v in exp_hist.items() if k <= 35}

# ========== LANGUAGE-SLICED PANELS (makes language a live filter) ==========
print("language cross-tabs…")
LANG_LIST = [l for l, _ in lang.most_common()]

def panel_for(sub):
    """Compact panel aggregates for a person-subset."""
    n = len(sub)
    vg = sub.groupby("vertical").agg(count=("user_id", "size"), median_yoe=("yoe", "median"))
    vg = vg.sort_values("count", ascending=False)
    verts = [{"name": i, "count": int(r["count"]), "median_yoe": float(r["median_yoe"]),
              "share": round(100 * r["count"] / n, 2) if n else 0} for i, r in vg.iterrows()]
    ph = sub[sub["qual"] == "PhD"].copy()
    ph_dom = ph["specialization_title"].map(phd_domain2).value_counts().to_dict() if len(ph) else {}
    tk = sub[sub["department"].isin(TECH_DEPTS)]
    ehist = sub["yoe"].value_counts()
    ehist = {int(k): int(v) for k, v in ehist.items() if k <= 35}
    # qualification distribution per vertical (for domain-landscape cross-filter)
    qbv = {vert: g["qual"].value_counts().to_dict() for vert, g in sub.groupby("vertical")}
    return {
        "n": int(n),
        "qualifications": sub["qual"].value_counts().to_dict(),
        "experience_buckets": sub["expb"].value_counts().to_dict(),
        "experience_hist": ehist,
        "verticals": verts,
        "qual_by_vertical": qbv,
        "phd_by_domain": ph_dom,
        "phd_count": int(len(ph)),
        "tech_by_department": tk["department"].value_counts().to_dict(),
        "tech_count": int(len(tk)),
    }

by_language = {"All": panel_for(person)}
for lg in LANG_LIST:
    mask = person["languages"].str.contains(re.escape(lg), na=False)
    by_language[lg] = panel_for(person[mask])

data = {
    "by_language": by_language,
    "meta": {
        "source_rows": RAW_ROWS,
        "truncated": bool(TRUNCATED),
        "unique_candidates": int(N_USERS),
        "avg_yoe": avg_yoe,
        "median_yoe": median_yoe,
        "languages_covered": len(lang),
        "phd_count": int(N_PHD),
        "generated": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
    },
    "experience_buckets": person["expb"].value_counts().to_dict(),
    "experience_hist": exp_hist,
    "qualifications": qual_dist,
    "languages": dict(lang.most_common()),
    "verticals": verticals,
    "departments_top": {k:int(v) for k,v in dept_dist.items()},
    "institute_tiers": tier_counts,
    "institute_present": inst_present,
    "phd": {
        "count": int(N_PHD),
        "by_domain": phd_domain_dist,
        "top_specializations": {k:int(v) for k,v in phd_spec_top.items()},
        "by_vertical": {k:int(v) for k,v in phd_vertical.items()},
    },
    "tech": {
        "count": int(N_TECH),
        "by_department": tech_dept_dist,
        "by_subdepartment": tech_sub_dist,
        "by_specialization": tech_spec_dist,
        "by_experience": tech_exp,
        "by_stack": tech_stack_dist,
        "by_company_tier": tech_ctier_dist,
    },
    "company_tiers": company_tier_dist,
    "top_employers": {k: int(v) for k, v in top_employers.items()},
}

with open(OUT, "w") as f:
    json.dump(data, f, indent=1, default=str)
print("wrote", OUT)
print(json.dumps(data["meta"], indent=2))
