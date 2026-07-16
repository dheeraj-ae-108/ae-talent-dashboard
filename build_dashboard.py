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
  overflow-x:hidden;-webkit-font-smoothing:antialiased}
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
.fcount{margin-left:auto;font-size:13px;color:var(--ink-dim)}
.fcount b{color:var(--accent);font-weight:700}
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
.xf{display:none;margin-left:6px;font-size:10.5px;padding:1px 8px 1px 9px;border-radius:20px;
  background:var(--accent);color:#fff;cursor:pointer;white-space:nowrap;font-weight:500}
.xf.on{display:inline-block}
.xf b{font-weight:700}
.hint{color:#9aa0a8;font-style:italic}
.banner{background:linear-gradient(100deg,#0e7c72 0%,#0a5d55 100%);color:#eafaf6;border-radius:14px;
  padding:14px 20px;margin-bottom:22px;font-size:15px;box-shadow:0 3px 14px rgba(14,124,114,.28)}
.banner b{color:#fff;font-weight:700}
.banner .big{color:var(--mint);font-weight:700}
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

<div class="banner" id="banner"></div>

<div class="filterbar" id="filterbar">
  <span class="flab">Language filter</span>
</div>

<div class="sec">1 · Years of experience</div>
<div class="grid">
  <div class="card c12"><h3>Experience distribution</h3>
    <div class="cn">Candidates by years of professional experience. Domain-expert floor is 8+ years.</div>
    <div id="exphist" class="chart" style="height:300px"></div></div>
</div>

<div class="sec">2 · Domain, department, language &amp; education</div>
<div class="grid">
  <div class="card c8"><h3>Domain segments — candidates &amp; median experience</h3>
    <div class="cn">Verticals grouped from department; blank departments remapped from job title. Bars = candidates · line = median years of experience. <span class="hint">Tap a bar to break it down by qualification →</span></div>
    <div id="verticals" class="chart" style="height:360px"></div></div>
  <div class="card c4"><h3>Education — qualification levels</h3>
    <div class="cn">Highest degree per candidate.<span class="xf" id="xfQual"></span></div>
    <div id="qual" class="chart" style="height:360px"></div></div>
  <div class="card c6"><h3>Top departments</h3>
    <div class="cn">Most common departments across the pool.</div>
    <div id="deptRaw" class="chart"></div></div>
  <div class="card c6"><h3>Multi-lingual pool</h3>
    <div class="cn">Language mentions across candidates. <span class="hint">Tap a language to filter the whole dashboard →</span></div>
    <div id="lang" class="chart" style="height:365px"></div></div>
</div>

<div class="sec">Employer landscape</div>
<div class="grid">
  <div class="card c6"><h3>Employer sectors <span id="secScope" class="tag">industry</span></h3>
    <div class="cn">Enterprise employers by industry.<span id="smeNote"></span> <span class="hint">Tap a sector to see its companies →</span><span class="xf" id="xfSec"></span></div>
    <div id="sectors" class="chart" style="height:430px"></div></div>
  <div class="card c6"><h3>Prestige employer groups <span id="empScope" class="tag">sought-after</span></h3>
    <div class="cn">Experts from FAANG, Indian IT majors, global consulting, unicorns, top banks &amp; conglomerates. <span class="hint">Tap a group to see its companies →</span><span class="xf" id="xfEmp"></span></div>
    <div id="topEmp" class="chart" style="height:430px"></div></div>
</div>

<div class="sec">3 · Coding &amp; tech</div>
<div class="grid">
  <div class="card c12"><h3>Coding &amp; tech pool by discipline</h3>
    <div class="cn">The <b id="techTotal"></b> experts in software &amp; IT roles across the full pool, by discipline. Explicit-language titles (Java/Python/.NET/PHP) counted directly; other technical titles mapped to the closest discipline. Manufacturing machine-programmers (CNC/VMC) are excluded.</div>
    <div id="techStack" class="chart" style="height:400px"></div></div>
  <div class="card c6"><h3>Tech pool by department</h3>
    <div class="cn">Software/IT/Hardware/Data/Product departments.</div>
    <div id="techDept" class="chart"></div></div>
  <div class="card c6"><h3>Tech pool by experience band</h3>
    <div class="cn">Filtered tech candidates.</div>
    <div id="techExp" class="chart" style="height:365px"></div></div>
</div>

<div class="sec">4 · PhD network</div>
<div class="grid">
  <div class="card c5"><h3>PhDs by domain</h3>
    <div class="cn">Filtered pool · subject inferred from specialization. <span class="hint">Tap a domain to see its specializations →</span></div>
    <div id="phdDomain" class="chart" style="height:365px"></div></div>
  <div class="card c7"><h3>PhDs by field</h3>
    <div class="cn">22,826 PhDs grouped into field families (170+ raw specializations). "Subject not specified" = generic "Doctor of Philosophy" entries. <span class="hint">Tap a domain on the left to drill into individual specializations →</span><span class="xf" id="xfPhd"></span></div>
    <div id="phdSpec" class="chart" style="height:400px"></div></div>
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
          p[0].marker+'Candidates: <b>'+d.count.toLocaleString()+'</b><br/>'+
          p[1].marker+'Median exp: <b>'+d.median_yoe+' yrs</b>';}},
    legend:{data:['Candidates','Median exp'],textStyle:{color:AX},top:0,itemGap:16},
    grid:{left:30,right:44,top:36,bottom:74,containLabel:true},
    xAxis:{type:'category',data:v.map(x=>x.name),axisLabel:{color:AX,rotate:30,fontSize:9.5,interval:0,margin:12},
      axisTick:{show:false}},
    yAxis:[{type:'value',name:'Candidates',nameTextStyle:{color:AX},nameGap:14,axisLabel:{color:AX,formatter:n=>fmt(n)},splitLine:{lineStyle:{color:GRID}}},
           {type:'value',name:'Median yrs',nameTextStyle:{color:AX},nameGap:14,axisLabel:{color:AX},splitLine:{show:false},min:8}],
    series:[
      {name:'Candidates',type:'bar',barMaxWidth:34,data:v.map(x=>x.count),itemStyle:{color:'#0e7c72',borderRadius:[4,4,0,0]},
        label:{show:true,position:'top',color:'#5a5f67',fontSize:8.5,fontWeight:500,formatter:p=>p.value.toLocaleString()}},
      {name:'Median exp',type:'line',yAxisIndex:1,data:v.map(x=>x.median_yoe),smooth:true,
        lineStyle:{color:'#f0a15c',width:3},itemStyle:{color:'#f0a15c'},symbolSize:7,z:3}]});
}

function expHist(buckets){
  const order=EXP_ORDER.filter(k=>buckets[k]!=null);
  charts.exphist.setOption({tooltip:{...baseTip,trigger:'axis',axisPointer:{type:'shadow'},
      formatter:p=>p[0].name+': <b>'+p[0].value.toLocaleString()+'</b> candidates'},
    grid:{left:14,right:28,top:16,bottom:30,containLabel:true},
    xAxis:{type:'category',data:order,axisLabel:{color:'#3a3f47',fontSize:12.5,fontWeight:500}},
    yAxis:{type:'value',axisLabel:{color:AX,formatter:n=>fmt(n)},splitLine:{lineStyle:{color:GRID}}},
    series:[{type:'bar',barMaxWidth:110,data:order.map(k=>buckets[k]),itemStyle:{color:'#0e7c72',borderRadius:[5,5,0,0]},
      label:{show:true,position:'top',color:'#3a3f47',fontSize:13,fontWeight:600,formatter:p=>p.value.toLocaleString()}}]});
}

// ---- filterable + cross-filter charts ----
const EXP_ORDER=['8–11 yrs','12–15 yrs','16–20 yrs','20+ yrs'];
function orderExp(o){const r={};EXP_ORDER.forEach(k=>{if(o[k])r[k]=o[k]});return r;}
const F = D.full || {};
let active='All';            // active language filter
let selVert=null,selPhd=null,selSector=null,selPrestige=null;   // per-section drill selections
function curP(){return D.by_language[active]||D.by_language['All'];}

function chip(id,label,clearFn){
  const el=document.getElementById(id);
  if(!label){el.className='xf';el.innerHTML='';el.onclick=null;return;}
  el.className='xf on';el.innerHTML='▸ <b>'+label+'</b> &nbsp;✕';el.onclick=clearFn;
}
function drawQual(){
  const P=curP();
  const src=(selVert&&P.qual_by_vertical&&P.qual_by_vertical[selVert])?P.qual_by_vertical[selVert]:P.qualifications;
  donut('qual',src);
  chip('xfQual',selVert,()=>{selVert=null;drawQual();});
}
function drawPhdSpec(){
  const src=(selPhd&&F.phd_specs_by_domain&&F.phd_specs_by_domain[selPhd])?F.phd_specs_by_domain[selPhd]:(F.phd_families||F.phd_top_specializations||D.phd.top_specializations);
  hbar('phdSpec',src,'#8b7ec8',16);
  chip('xfPhd',selPhd,()=>{selPhd=null;drawPhdSpec();});
}
const SEC_HIDE=['Regional & SME businesses','Unspecified','Other / Unclassified'];
function drawSectors(){
  let data;
  if(selSector && F.employers_by_sector && F.employers_by_sector[selSector]){
    data=F.employers_by_sector[selSector];
  } else {
    const all=F.employer_sectors||F.company_tiers||D.company_tiers||{};
    data=Object.fromEntries(Object.entries(all).filter(([k])=>!SEC_HIDE.includes(k)));
  }
  hbar('sectors',data,'#0e7c72',14);
  const sc=document.getElementById('secScope'); if(sc) sc.textContent=selSector||'industry';
  const sme=document.getElementById('smeNote');
  const smeN=(F.employer_sectors||{})['Regional & SME businesses']||0;
  if(sme) sme.innerHTML=(!selSector&&smeN)?' Plus <b style="color:#3a3f47">'+smeN.toLocaleString()+'</b> at regional &amp; SME businesses.':'';
  chip('xfSec',selSector,()=>{selSector=null;drawSectors();});
}
function drawPrestige(){
  const data=(selPrestige&&F.employers_by_prestige&&F.employers_by_prestige[selPrestige])?F.employers_by_prestige[selPrestige]:(F.prestige_groups||F.top_employers||{});
  hbar('topEmp',data,'#12a37a',14);
  const es=document.getElementById('empScope'); if(es) es.textContent=selPrestige||'sought-after';
  chip('xfEmp',selPrestige,()=>{selPrestige=null;drawPrestige();});
}
function setLang(l){
  active=l;
  [...fb.querySelectorAll('.pill')].forEach(p=>p.classList.toggle('on',p.textContent===l));
  render(l);
}
function render(langKey){
  active=langKey;
  const P=curP();
  verticalsChart(P.verticals);
  drawQual();
  donut('phdDomain',P.phd_by_domain);
  hbar('techDept',P.tech_by_department,'#6ad1fa');
  donut('techExp',orderExp(P.experience_buckets));
  expHist(P.experience_buckets);
  const fc=document.getElementById('filterCount');
  if(fc) fc.innerHTML = (active==='All')
    ? `Showing all <b>${P.n.toLocaleString()}</b> experts`
    : `Showing <b>${P.n.toLocaleString()}</b> ${active} speakers`;
}
function fmt(n){return n>=1000?(n/1000).toFixed(n>=100000?0:1)+'K':''+n;}

// ---- banner, KPIs, subline ----
const m=D.meta;
const fullRows = (D.full && D.full.rows) ? D.full.rows : m.source_rows;
const fullPhd = (D.full && D.full.phd_total) ? D.full.phd_total : m.phd_count;
document.getElementById('banner').innerHTML =
  `<b>Domain Expert</b> = 10+ years of hands-on experience <b>or</b> a PhD.&nbsp; A network of `+
  `<span class="big">${m.unique_candidates.toLocaleString()}</span> vetted experts and `+
  `<span class="big">${fullPhd.toLocaleString()}</span> PhDs — active across 40,000+ colleges and 300,000+ companies, and growing every week.`;
document.getElementById('subline').textContent = 'Domain-expert talent network for frontier AI';
document.getElementById('kpis').innerHTML = `
  <div class="kpi"><div class="lab">Domain experts</div><div class="val">${m.unique_candidates.toLocaleString()}</div><div class="note">10+ yrs experience or PhD</div></div>
  <div class="kpi"><div class="lab">Avg experience</div><div class="val">${(Math.round(m.avg_yoe*10)/10)} yrs</div><div class="note">${m.median_yoe} yrs median</div></div>
  <div class="kpi"><div class="lab">PhD network</div><div class="val">${fullPhd.toLocaleString()}</div><div class="note">across 40k+ colleges</div></div>
  <div class="kpi"><div class="lab">Languages</div><div class="val">${m.languages_covered}</div><div class="note">Indian languages covered</div></div>`;

// ---- language filter pills ----
const fb=document.getElementById('filterbar');
const langs=['All',...Object.keys(D.languages)];
langs.forEach(l=>{
  const b=document.createElement('button');b.className='pill'+(l==='All'?' on':'');b.textContent=l;
  b.onclick=()=>setLang(l);
  fb.appendChild(b);
});
const fcEl=document.createElement('span');fcEl.className='fcount';fcEl.id='filterCount';fb.appendChild(fcEl);

// init
['verticals','qual','exphist','lang','phdDomain','phdSpec','techStack',
 'techDept','techExp','sectors','topEmp','deptRaw'].forEach(mk);
donut('lang', D.languages);
hbar('techStack', F.tech_stack || D.tech.by_stack, '#0e7c72', 16);
(function(){const tt=document.getElementById('techTotal');const n=(F.tech_titled_total)||Object.values(F.tech_stack||{}).reduce((a,b)=>a+b,0);if(tt)tt.textContent=n.toLocaleString();})();
hbar('deptRaw', D.departments_top, '#2fb89a', 15);
drawPhdSpec();
drawSectors();
drawPrestige();
// ---- cross-filter + drill click handlers ----
charts.verticals.on('click',p=>{if(p.componentType==='series'&&p.seriesType==='bar'){selVert=(selVert===p.name)?null:p.name;drawQual();}});
charts.phdDomain.on('click',p=>{if(p.data){selPhd=(selPhd===p.name)?null:p.name;drawPhdSpec();}});
charts.sectors.on('click',p=>{if(p.name&&F.employer_sectors&&(p.name in F.employer_sectors)){selSector=(selSector===p.name)?null:p.name;drawSectors();}});
charts.topEmp.on('click',p=>{if(p.name&&F.prestige_groups&&(p.name in F.prestige_groups)){selPrestige=(selPrestige===p.name)?null:p.name;drawPrestige();}});
charts.lang.on('click',p=>{if(p.data){setLang(active===p.name?'All':p.name);}});
render('All');
window.addEventListener('resize',()=>Object.values(charts).forEach(c=>c.resize()));
</script>
</div>
</body>
</html>"""

OUT = os.path.join(HERE, "index.html")
open(OUT, "w").write(HTML.replace("__DATA__", DATA_JS))
print("wrote", OUT, "(", round(os.path.getsize(OUT)/1024, 1), "KB )")
