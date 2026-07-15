#!/usr/bin/env python3
"""Builds a self-contained index.html from ae_data.json (single-file, GH-Pages ready)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "ae_data.json")))
DATA_JS = json.dumps(DATA, separators=(",", ":"))

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Arctic Engine — Talent Pool Analytics</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
:root{
  --bg:#f4f4f2; --bg-soft:#fafaf9; --panel:#ffffff; --panel-brd:#e7e6e1;
  --ink:#15171b; --ink-dim:#697078; --accent:#0e7c72; --accent2:#0f8a66; --mint:#2fe6af;
  --warn:#b45309; --header:#15171b;
}
*{box-sizing:border-box}
body{margin:0;font-family:'Inter',-apple-system,'Segoe UI',system-ui,sans-serif;
  background:var(--bg);color:var(--ink);padding:0 0 60px;min-height:100vh;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1360px;margin:0 auto;padding:0 26px}
.head{background:var(--header);color:#f4f4f2;padding:20px 0 22px;margin-bottom:26px;
  border-bottom:3px solid var(--accent)}
.head .wrap{display:flex;align-items:center;gap:16px}
.logo{width:46px;height:52px;display:block;filter:drop-shadow(0 3px 10px rgba(58,167,222,.35))}
h1{font-size:21px;margin:0;letter-spacing:2.5px;font-weight:600;color:#f4f4f2}
h1 span{color:var(--mint)}
.head .sub{color:#9aa0a8;font-size:12.5px;margin:0}
.headtxt{display:flex;flex-direction:column;gap:4px}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:22px}
.kpi{background:var(--panel);border:1px solid var(--panel-brd);border-radius:14px;padding:16px 18px;
  position:relative;overflow:hidden;box-shadow:0 1px 3px rgba(21,23,27,.05)}
.kpi::before{content:"";position:absolute;inset:0 auto 0 0;width:3px;background:linear-gradient(var(--accent),var(--mint))}
.kpi .lab{color:var(--ink-dim);font-size:12px;text-transform:uppercase;letter-spacing:.6px}
.kpi .val{font-size:34px;font-weight:700;margin-top:6px;line-height:1;color:var(--ink)}
.kpi .note{font-size:11px;color:var(--ink-dim);margin-top:6px}
.filterbar{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-bottom:22px;
  background:var(--panel);border:1px solid var(--panel-brd);border-radius:14px;padding:12px 16px;
  box-shadow:0 1px 3px rgba(21,23,27,.05)}
.filterbar .flab{font-size:12px;color:var(--ink-dim);text-transform:uppercase;letter-spacing:.6px;margin-right:4px}
.pill{cursor:pointer;font-size:12.5px;padding:6px 14px;border-radius:20px;border:1px solid var(--panel-brd);
  background:var(--bg-soft);color:var(--ink-dim);transition:.15s}
.pill:hover{border-color:var(--accent);color:var(--accent)}
.pill.on{background:var(--accent);color:#fff;border-color:var(--accent);font-weight:600}
.grid{display:grid;gap:16px;grid-template-columns:repeat(12,1fr)}
.card{background:var(--panel);border:1px solid var(--panel-brd);border-radius:14px;padding:14px 16px 8px;
  box-shadow:0 1px 3px rgba(21,23,27,.05)}
.card h3{margin:0 0 2px;font-size:14.5px;font-weight:600;color:var(--ink)}
.card .cn{font-size:11.5px;color:var(--ink-dim);margin-bottom:6px;line-height:1.5}
.chart{width:100%;height:300px}
.c4{grid-column:span 4}.c5{grid-column:span 5}.c6{grid-column:span 6}.c7{grid-column:span 7}.c8{grid-column:span 8}.c12{grid-column:span 12}
.tag{display:inline-block;font-size:10px;padding:2px 8px;border-radius:6px;margin-left:6px;font-weight:500;
  background:#e9f4f2;color:var(--accent);border:1px solid #cfe6e2;vertical-align:middle;text-transform:none;letter-spacing:0}
.tag.warn{background:#fdf0e3;color:#b45309;border-color:#f3d9be}
.sec{margin:30px 0 4px;font-size:12.5px;letter-spacing:2px;color:var(--accent);text-transform:uppercase;
  border-top:1px solid var(--panel-brd);padding-top:18px;font-weight:600}
.notes{margin-top:30px;background:var(--bg-soft);border:1px solid var(--panel-brd);border-radius:14px;padding:18px 22px;
  font-size:12.5px;color:var(--ink-dim);line-height:1.7}
.notes b{color:var(--ink)}
.notes ul{margin:8px 0 0;padding-left:20px}
@media(max-width:900px){.kpis{grid-template-columns:repeat(2,1fr)}.c4,.c5,.c6,.c7,.c8{grid-column:span 12}}
</style>
</head>
<body>
<div class="head">
  <div class="wrap">
    <svg class="logo" viewBox="0 0 100 112" xmlns="http://www.w3.org/2000/svg" aria-label="Arctic Engine">
      <!-- above water -->
      <polygon points="16,46 34,24 50,46" fill="#6cc7ec"/>
      <polygon points="34,24 46,18 50,46" fill="#a3e1f5"/>
      <polygon points="34,24 62,6 46,18" fill="#39a7de"/>
      <polygon points="46,18 62,6 50,46" fill="#7fd2f0"/>
      <polygon points="62,6 78,30 50,46" fill="#1d8fd1"/>
      <polygon points="62,6 84,46 78,30" fill="#d4f1fb"/>
      <polygon points="78,30 84,46 50,46" fill="#4fb4e2"/>
      <!-- waterline cut -->
      <polygon points="16,46 84,46 82,53 18,53" fill="#2a7fb0"/>
      <!-- below water -->
      <polygon points="18,53 50,53 50,108" fill="#17618f"/>
      <polygon points="50,53 82,53 50,108" fill="#0c3f63"/>
      <polygon points="18,53 30,66 50,108" fill="#124f74"/>
      <polygon points="82,53 70,66 50,108" fill="#093250"/>
    </svg>
    <div class="headtxt">
      <h1>ARCTIC ENGINE <span>·</span> TALENT POOL ANALYTICS</h1>
      <div class="sub" id="subline"></div>
    </div>
  </div>
</div>
<div class="wrap">

<div class="kpis" id="kpis"></div>

<div class="filterbar" id="filterbar">
  <span class="flab">Language filter</span>
</div>

<div class="sec">Domain landscape</div>
<div class="grid">
  <div class="card c8"><h3>Domain segment share (%) vs. median years of experience</h3>
    <div class="cn">Verticals derived from department. Bars = share of filtered pool · line = median years.</div>
    <div id="verticals" class="chart" style="height:340px"></div></div>
  <div class="card c4"><h3>Qualification levels</h3>
    <div class="cn">Highest degree per candidate.</div>
    <div id="qual" class="chart" style="height:365px"></div></div>
</div>

<div class="sec">Experience &amp; language</div>
<div class="grid">
  <div class="card c8"><h3>Years-of-experience distribution</h3>
    <div class="cn">Person-level. Pool floor is ~10 years.</div>
    <div id="exphist" class="chart"></div></div>
  <div class="card c4"><h3>Multi-lingual pool <span class="tag">global</span></h3>
    <div class="cn">Language mentions across candidates (multi-select).</div>
    <div id="lang" class="chart" style="height:365px"></div></div>
</div>

<div class="sec">PhD network</div>
<div class="grid">
  <div class="card c5"><h3>PhDs by domain</h3>
    <div class="cn">Filtered pool · from specialization title.</div>
    <div id="phdDomain" class="chart" style="height:365px"></div></div>
  <div class="card c7"><h3>Top PhD specializations <span class="tag">full pool</span></h3>
    <div class="cn">Full ~1.40M-record pool · 22,826 PhDs.</div>
    <div id="phdSpec" class="chart"></div></div>
</div>

<div class="sec">Tech / coding sub-cut</div>
<div class="grid">
  <div class="card c12"><h3>Tech stack / discipline distribution <span class="tag">title-derived · full pool</span></h3>
    <div class="cn">From job title across the full ~1.40M-record pool — 34,949 clearly-technical titles. Explicit-language titles (Java/Python/.NET/PHP) counted directly; other technical titles mapped to closest discipline. (Language-level counts are small — most tech titles state a role, not a language.)</div>
    <div id="techStack" class="chart" style="height:360px"></div></div>
  <div class="card c6"><h3>Tech pool by department <span class="tag warn">export sample</span></h3>
    <div class="cn">Software/IT/Hardware/Data/Product departments (person-level export).</div>
    <div id="techDept" class="chart"></div></div>
  <div class="card c6"><h3>Tech pool by experience band <span class="tag warn">export sample</span></h3>
    <div class="cn">Filtered tech candidates (person-level export).</div>
    <div id="techExp" class="chart" style="height:365px"></div></div>
</div>

<div class="sec">Company landscape <span class="tag">derived · full pool</span></div>
<div class="grid">
  <div class="card c5"><h3>Whole pool by company tier</h3>
    <div class="cn">Employer name matched to tier across the full ~1.40M-record pool. 97% of records name an employer.</div>
    <div id="companyTiers" class="chart" style="height:365px"></div></div>
  <div class="card c7"><h3>Top employers in premium tiers</h3>
    <div class="cn">Most common FAANG / Indian-IT / unicorn employers (full pool).</div>
    <div id="topEmp" class="chart"></div></div>
</div>

<div class="sec">Supporting context <span class="tag">full pool</span></div>
<div class="grid">
  <div class="card c6"><h3>Top sub-departments</h3>
    <div class="cn">Full ~1.40M-record pool · top 15 sub-departments.</div>
    <div id="subDept" class="chart"></div></div>
  <div class="card c6"><h3>Top specializations (all degrees)</h3>
    <div class="cn">Full pool · most common fields of study.</div>
    <div id="specTop" class="chart"></div></div>
  <div class="card c6"><h3>Top departments <span class="tag warn">export sample</span></h3>
    <div class="cn">Person-level export, top 15 departments.</div>
    <div id="deptRaw" class="chart"></div></div>
  <div class="card c6"><h3>Elite institute signal <span class="tag warn">proxy · sparse</span></h3>
    <div class="cn">Keyword match on institute name. Only ~2% of records list an institute, so treat as directional only.</div>
    <div id="tiers" class="chart"></div></div>
</div>

<div class="notes">
  <b>Data notes &amp; caveats</b>
  <ul>
    <li><b>Two data sources.</b> Panels tagged <span class="tag">full pool</span> use the authoritative distinct-count sheets (<i>Arctic Engine · Data Req</i>) covering the full <b>1,402,050-record</b> pool. Panels tagged <span class="tag warn">export sample</span> use the person-level CSV export, which is truncated at 1,048,575 rows (916,607 unique candidates) — used only where person-level joins or the language filter are needed.</li>
    <li><b>Tech stack is title-derived.</b> No language column exists, so stack/discipline is inferred from job title across the full pool — explicit-language titles (Java/Python/.NET/PHP) counted directly; other technical titles mapped to the closest discipline. Only ~35K titles are unambiguously technical, so language-level counts are directional, not self-reported.</li>
    <li><b>Company tier is derived from the employer name.</b> 97% of records name an employer; we keyword-match to FAANG/global big-tech, Indian IT/consulting, unicorn/startup, and BFSI/enterprise. Unmatched names fall to "Other" (self-employed, govt, SMEs).</li>
    <li><b>Institute tier is sparse.</b> ~98% of rows have a blank institute name; IIT/NIT/IIM keyword matches are directional, not a census.</li>
    <li><b>No active-status field</b> exists, so that cut is omitted. <b>Languages:</b> only 10 regional languages are captured; Hindi/Urdu/Punjabi are absent.</li>
    <li>Person-level (export) stats dedupe to one row per <code>user_id</code> (highest qualification kept). Full-pool sheets are record-level frequency counts.</li>
  </ul>
</div>

<script>
const D = __DATA__;
const AX = '#697078', GRID='rgba(21,23,27,.07)';
const PAL = ['#0e7c72','#12a37a','#2fe6af','#6ad1fa','#8b7ec8','#f0a15c','#5bb8a6','#c3a1f8','#e8b04b','#e07a5f','#4a9d8e','#d98cb3'];
echarts.registerTheme('ae',{});
const charts = {};
function mk(id){const c=echarts.init(document.getElementById(id),null,{renderer:'canvas'});charts[id]=c;return c;}
const baseTip={backgroundColor:'#15171b',borderColor:'#2a2d33',borderWidth:1,textStyle:{color:'#f4f4f2'}};
const SHORTMAP={'Undergraduate':'Undergrad','Diploma / Certificate':'Diploma','PG Diploma':'PG Dip',
  'Humanities & Social Sciences':'Humanities','Finance & Economics':'Finance/Econ','Medicine & Health':'Medicine',
  'Other / Unspecified':'Other','Other / Unclassified':'Other','FAANG / Global Big-Tech':'FAANG / Big-Tech',
  'Indian IT / Global Consulting':'Indian IT','Unicorn / Funded Startup':'Unicorn','Bank / BFSI / Large Enterprise':'BFSI / Enterprise'};
function SHORT(n){return SHORTMAP[n]||n;}
function sortObj(o){return Object.entries(o).sort((a,b)=>b[1]-a[1]);}
function donut(id,obj,title){
  const e=sortObj(obj);
  const tot=e.reduce((s,x)=>s+x[1],0)||1;
  charts[id].setOption({tooltip:{...baseTip,trigger:'item',
      formatter:p=>'<b>'+p.name+'</b><br/>'+p.value.toLocaleString()+' ('+p.percent+'%)'},
    legend:{bottom:0,left:'center',icon:'circle',itemWidth:9,itemHeight:9,itemGap:11,
      textStyle:{color:'#3a3f47',fontSize:10.5},formatter:n=>SHORT(n)},
    series:[{type:'pie',radius:['42%','61%'],center:['50%','43%'],avoidLabelOverlap:true,minAngle:2,
      itemStyle:{borderColor:'#ffffff',borderWidth:2},
      label:{color:'#4a4f57',fontSize:10.5,formatter:p=>p.percent>=3?p.percent+'%':''},
      labelLine:{length:7,length2:7,lineStyle:{color:'#c2c6cc'}},
      data:e.map((x,i)=>{const pct=x[1]/tot*100;return {name:x[0],value:x[1],
        label:{show:pct>=3},labelLine:{show:pct>=3},
        itemStyle:{color:PAL[i%PAL.length]}};})}]});
}
function hbar(id,obj,color,top){
  let e=sortObj(obj); if(top)e=e.slice(0,top); e.reverse();
  const mx=Math.max(...e.map(x=>x[1]),1);
  charts[id].setOption({tooltip:{...baseTip,trigger:'axis',axisPointer:{type:'shadow'},
      formatter:p=>p[0].name+': <b>'+p[0].value.toLocaleString()+'</b>'},
    grid:{left:8,right:58,top:8,bottom:8,containLabel:true},
    xAxis:{type:'value',max:mx*1.12,axisLabel:{show:false},splitLine:{show:false},
      axisLine:{show:false},axisTick:{show:false}},
    yAxis:{type:'category',data:e.map(x=>x[0]),axisLabel:{color:AX,fontSize:11},
      axisLine:{lineStyle:{color:'#e7e6e1'}},axisTick:{show:false}},
    series:[{type:'bar',barMaxWidth:20,data:e.map(x=>x[1]),
      itemStyle:{color:color||'#0e7c72',borderRadius:[0,4,4,0]},
      label:{show:true,position:'right',color:'#4a4f57',fontSize:10.5,fontWeight:500,
        formatter:p=>p.value.toLocaleString()}}]});
}
function verticalsChart(v){
  v=[...v].sort((a,b)=>b.count-a.count);
  charts.verticals.setOption({
    tooltip:{...baseTip,trigger:'axis',axisPointer:{type:'shadow'},
      formatter:p=>{const i=p[0].dataIndex,d=v[i];
        return '<b>'+p[0].axisValue+'</b><br/>'+
          p[0].marker+'Share: <b>'+d.share+'%</b><br/>'+
          '&nbsp;&nbsp;&nbsp;&nbsp;Candidates: <b>'+d.count.toLocaleString()+'</b><br/>'+
          p[1].marker+'Median exp: <b>'+d.median_yoe+' yrs</b>';}},
    legend:{textStyle:{color:AX},top:0,itemGap:16},
    grid:{left:26,right:38,top:36,bottom:72,containLabel:true},
    xAxis:{type:'category',data:v.map(x=>x.name),axisLabel:{color:AX,rotate:30,fontSize:9.5,interval:0,margin:12},
      axisTick:{show:false}},
    yAxis:[{type:'value',name:'Share %',nameTextStyle:{color:AX},nameGap:14,axisLabel:{color:AX,formatter:'{value}%'},splitLine:{lineStyle:{color:GRID}}},
           {type:'value',name:'Median yrs',nameTextStyle:{color:AX},nameGap:14,axisLabel:{color:AX},splitLine:{show:false},min:8}],
    series:[
      {name:'Share %',type:'bar',barMaxWidth:34,data:v.map(x=>x.share),itemStyle:{color:'#0e7c72',borderRadius:[4,4,0,0]},
        label:{show:true,position:'top',color:'#5a5f67',fontSize:9,fontWeight:500,formatter:p=>fmt(v[p.dataIndex].count)}},
      {name:'Median exp',type:'line',yAxisIndex:1,data:v.map(x=>x.median_yoe),smooth:true,
        lineStyle:{color:'#f0a15c',width:3},itemStyle:{color:'#f0a15c'},symbolSize:7,z:3}]});
}

// ---- static (non-filtered) charts drawn after init below ----
function expHist(){
  const e=Object.entries(D.experience_hist).map(([k,v])=>[+k,v]).sort((a,b)=>a[0]-b[0]);
  charts.exphist.setOption({tooltip:{...baseTip,trigger:'axis'},
    grid:{left:8,right:20,top:14,bottom:24,containLabel:true},
    xAxis:{type:'category',data:e.map(x=>x[0]),name:'years',nameTextStyle:{color:AX},axisLabel:{color:AX}},
    yAxis:{type:'value',axisLabel:{color:AX},splitLine:{lineStyle:{color:GRID}}},
    series:[{type:'bar',data:e.map(x=>x[1]),itemStyle:{color:'#0e7c72',borderRadius:[3,3,0,0]}}]});
}

// ---- filterable charts ----
const EXP_ORDER=['<10 yrs','10–12 yrs','13–15 yrs','16–20 yrs','20+ yrs'];
function orderExp(o){const r={};EXP_ORDER.forEach(k=>{if(o[k])r[k]=o[k]});return r;}
function render(langKey){
  const P = D.by_language[langKey] || D.by_language['All'];
  verticalsChart(P.verticals);
  donut('qual', P.qualifications);
  donut('phdDomain', P.phd_by_domain);
  hbar('techDept', P.tech_by_department, '#6ad1fa');
  donut('techExp', orderExp(P.experience_buckets));
  // KPIs
  document.getElementById('kpi-n').textContent = fmt(P.n);
  document.getElementById('kpi-phd').textContent = fmt(P.phd_count);
  document.getElementById('kpi-tech').textContent = fmt(P.tech_count);
}
function fmt(n){return n>=1000?(n/1000).toFixed(n>=100000?0:1)+'K':n;}

// ---- KPIs + subline ----
const m=D.meta;
const fullRows = (D.full && D.full.rows) ? D.full.rows : m.source_rows;
const fullPhd = (D.full && D.full.phd_total) ? D.full.phd_total : m.phd_count;
document.getElementById('subline').innerHTML =
  `Full pool ≈ <b style="color:#f4f4f2">${fullRows.toLocaleString()}</b> records (per data-req sheet) · `+
  `${m.unique_candidates.toLocaleString()} unique candidates in the person-level export · generated ${m.generated}`;
document.getElementById('kpis').innerHTML = `
  <div class="kpi"><div class="lab">Full pool records</div><div class="val">${fmt(fullRows)}</div><div class="note" style="color:var(--ink-dim)">${(m.unique_candidates/1000).toFixed(0)}K unique in export</div></div>
  <div class="kpi"><div class="lab">Median / Avg experience</div><div class="val">${m.median_yoe} / ${m.avg_yoe}</div><div class="note" style="color:var(--ink-dim)">years, person-level</div></div>
  <div class="kpi"><div class="lab">PhD network</div><div class="val">${fmt(fullPhd)}</div><div class="note" style="color:var(--ink-dim)">full pool · ${m.languages_covered} languages</div></div>
  <div class="kpi"><div class="lab">Candidates (filtered)</div><div class="val" id="kpi-n"></div><div class="note" style="color:var(--ink-dim)">by language · <span id="kpi-phd"></span> PhD · <span id="kpi-tech"></span> tech</div></div>`;

// ---- language filter pills ----
const fb=document.getElementById('filterbar');
const langs=['All',...Object.keys(D.languages)];
let active='All';
langs.forEach(l=>{
  const b=document.createElement('button');b.className='pill'+(l==='All'?' on':'');b.textContent=l;
  b.onclick=()=>{active=l;[...fb.querySelectorAll('.pill')].forEach(p=>p.classList.toggle('on',p.textContent===l));render(l);};
  fb.appendChild(b);
});

// init
const F = D.full || {};
['verticals','qual','exphist','lang','phdDomain','phdSpec','techStack',
 'techDept','techExp','companyTiers','topEmp','subDept','specTop','deptRaw','tiers'].forEach(mk);
donut('lang', D.languages);
hbar('phdSpec', F.phd_top_specializations || D.phd.top_specializations, '#8b7ec8', 15);
hbar('techStack', F.tech_stack || D.tech.by_stack, '#0e7c72', 16);
donut('companyTiers', F.company_tiers || D.company_tiers);
hbar('topEmp', F.top_employers || D.top_employers, '#12a37a', 14);
hbar('subDept', F.subdepartments || {}, '#2fb89a', 15);
hbar('specTop', F.top_specializations || {}, '#6ad1fa', 15);
hbar('deptRaw', D.departments_top, '#2fb89a', 15);
hbar('tiers', D.institute_tiers, '#f0a15c');
expHist();
render('All');
window.addEventListener('resize',()=>Object.values(charts).forEach(c=>c.resize()));
</script>
</div>
</body>
</html>"""

OUT = os.path.join(HERE, "index.html")
open(OUT, "w").write(HTML.replace("__DATA__", DATA_JS))
print("wrote", OUT, "(", round(os.path.getsize(OUT)/1024, 1), "KB )")
