#!/usr/bin/env python3
"""Builds a standalone 2-page 'highlights' PDF-ready HTML from ae_data.json.
Separate from the main index.html / 8-page report -- does not affect either.

Slide 1: Years of experience + Domain segments (candidates only, no median line)
Slide 2: Coding & tech pool by discipline + PhDs by field
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "ae_data.json")))
DATA_JS = json.dumps(DATA, separators=(",", ":"))

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>Arctic Engine — Talent Pool Highlights</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
:root{
  --bg:#f4f4f2; --panel:#ffffff; --panel-brd:#e7e6e1;
  --ink:#15171b; --ink-dim:#697078; --accent:#0e7c72; --mint:#2fe6af;
}
*{box-sizing:border-box}
html,body{margin:0;background:#fff;font-family:'Inter',-apple-system,'Segoe UI',system-ui,sans-serif;color:var(--ink)}
@page{size:A4 landscape;margin:9mm}
.slide{width:1055px;padding:0;break-after:page}
.slide:last-child{break-after:auto}
.sec{font-size:13px;letter-spacing:2px;color:var(--accent);text-transform:uppercase;font-weight:700;margin:0 0 8px}
.card{background:var(--panel);border:1px solid var(--panel-brd);border-radius:14px;padding:14px 20px 10px;margin-bottom:10px}
.card:last-child{margin-bottom:0}
.card h3{margin:0 0 3px;font-size:18px;font-weight:700;color:var(--ink)}
.card .cn{font-size:12.5px;color:var(--ink-dim);margin-bottom:4px;line-height:1.45}
.row2{display:flex;gap:14px}
.row2 .card{flex:1;margin-bottom:0}
</style>
</head>
<body>

<div class="slide" id="slide1">
  <div class="row2">
    <div class="card">
      <div class="sec">1 &middot; Years of experience</div>
      <h3>Experience distribution</h3>
      <div class="cn">Candidates by years of professional experience. Domain-expert floor is 8+ years.</div>
      <div id="expChart" style="width:100%;height:610px"></div>
    </div>
    <div class="card">
      <div class="sec">2 &middot; Domain, department</div>
      <h3>Domain segments — candidates</h3>
      <div class="cn">Verticals grouped from department; blank departments remapped from job title.</div>
      <div id="domainChart" style="width:100%;height:610px"></div>
    </div>
  </div>
</div>

<div class="slide" id="slide2">
  <div class="row2">
    <div class="card">
      <div class="sec">3 &middot; Coding &amp; tech</div>
      <h3>Coding &amp; tech pool by discipline</h3>
      <div class="cn" id="techCaption"></div>
      <div id="techChart" style="width:100%;height:610px"></div>
    </div>
    <div class="card">
      <div class="sec">4 &middot; PhD network</div>
      <h3>PhDs by field</h3>
      <div class="cn">PhDs with an identified field, grouped into families from 170+ raw specializations.</div>
      <div id="phdChart" style="width:100%;height:610px"></div>
    </div>
  </div>
</div>

<script>
const D = __DATA__;
const F = D.full || {};
const AX='#697078', GRID='rgba(21,23,27,.07)';
const baseTip={backgroundColor:'#15171b',borderColor:'#2a2d33',borderWidth:1,textStyle:{color:'#f4f4f2'}};
function sortObj(o){return Object.entries(o).sort((a,b)=>b[1]-a[1]);}

// ---- 1. Experience distribution (vertical bars, ordered, large fonts) ----
const EXP_ORDER=['8–11 yrs','12–15 yrs','16–20 yrs','20+ yrs'];
const expB = D.by_language.All.experience_buckets;
const expChart = echarts.init(document.getElementById('expChart'));
expChart.setOption({
  tooltip:{...baseTip,trigger:'axis',axisPointer:{type:'shadow'},textStyle:{fontSize:15}},
  grid:{left:20,right:24,top:36,bottom:32,containLabel:true},
  xAxis:{type:'category',data:EXP_ORDER,axisLabel:{color:'#3a3f47',fontSize:16,fontWeight:600}},
  yAxis:{type:'value',axisLabel:{color:AX,fontSize:13,formatter:n=>n>=1000?(n/1000)+'K':n},splitLine:{lineStyle:{color:GRID}}},
  series:[{animation:false,type:'bar',barMaxWidth:140,data:EXP_ORDER.map(k=>expB[k]),
    itemStyle:{color:'#0e7c72',borderRadius:[6,6,0,0]},
    label:{show:true,position:'top',color:'#3a3f47',fontSize:20,fontWeight:700,formatter:p=>p.value.toLocaleString()}}]
});

// ---- 2. Domain segments — candidates ONLY, horizontal bars for readability, large fonts ----
let verts=[...D.by_language.All.verticals].sort((a,b)=>b.count-a.count).reverse();
const domainChart = echarts.init(document.getElementById('domainChart'));
domainChart.setOption({
  tooltip:{...baseTip,trigger:'axis',axisPointer:{type:'shadow'},textStyle:{fontSize:15},
    formatter:p=>'<b>'+p[0].name+'</b><br/>Candidates: <b>'+p[0].value.toLocaleString()+'</b>'},
  grid:{left:8,right:72,top:6,bottom:6,containLabel:true},
  xAxis:{type:'value',axisLabel:{show:false},splitLine:{show:false},axisLine:{show:false},axisTick:{show:false}},
  yAxis:{type:'category',data:verts.map(x=>x.name),axisLabel:{color:'#3a3f47',fontSize:14,fontWeight:500},axisLine:{lineStyle:{color:'#e7e6e1'}},axisTick:{show:false}},
  series:[{animation:false,type:'bar',barMaxWidth:26,data:verts.map(x=>x.count),itemStyle:{color:'#0e7c72',borderRadius:[0,5,5,0]},
    label:{show:true,position:'right',color:'#3a3f47',fontSize:14,fontWeight:600,formatter:p=>p.value.toLocaleString()}}]
});

// ---- 3. Coding & tech pool by discipline ----
const techData = F.tech_stack || D.tech.by_stack;
const techTotal = F.tech_titled_total || Object.values(techData).reduce((a,b)=>a+b,0);
document.getElementById('techCaption').textContent =
  `The ${techTotal.toLocaleString()} experts in software & IT roles across the full pool, by discipline.`;
let tech = sortObj(techData).reverse();
const techChart = echarts.init(document.getElementById('techChart'));
techChart.setOption({
  tooltip:{...baseTip,trigger:'axis',axisPointer:{type:'shadow'},textStyle:{fontSize:15}},
  grid:{left:8,right:66,top:6,bottom:6,containLabel:true},
  xAxis:{type:'value',axisLabel:{show:false},splitLine:{show:false},axisLine:{show:false},axisTick:{show:false}},
  yAxis:{type:'category',data:tech.map(x=>x[0]),axisLabel:{color:'#3a3f47',fontSize:13,fontWeight:500},axisLine:{lineStyle:{color:'#e7e6e1'}},axisTick:{show:false}},
  series:[{animation:false,type:'bar',barMaxWidth:22,data:tech.map(x=>x[1]),itemStyle:{color:'#0e7c72',borderRadius:[0,4,4,0]},
    label:{show:true,position:'right',color:'#3a3f47',fontSize:13,fontWeight:600,formatter:p=>p.value.toLocaleString()}}]
});

// ---- 4. PhDs by field ----
let phd = sortObj(F.phd_families || {}).reverse();
const phdChart = echarts.init(document.getElementById('phdChart'));
phdChart.setOption({
  tooltip:{...baseTip,trigger:'axis',axisPointer:{type:'shadow'},textStyle:{fontSize:15}},
  grid:{left:8,right:66,top:6,bottom:6,containLabel:true},
  xAxis:{type:'value',axisLabel:{show:false},splitLine:{show:false},axisLine:{show:false},axisTick:{show:false}},
  yAxis:{type:'category',data:phd.map(x=>x[0]),axisLabel:{color:'#3a3f47',fontSize:13,fontWeight:500},axisLine:{lineStyle:{color:'#e7e6e1'}},axisTick:{show:false}},
  series:[{animation:false,type:'bar',barMaxWidth:22,data:phd.map(x=>x[1]),itemStyle:{color:'#8b7ec8',borderRadius:[0,4,4,0]},
    label:{show:true,position:'right',color:'#3a3f47',fontSize:13,fontWeight:600,formatter:p=>p.value.toLocaleString()}}]
});
</script>
</body>
</html>"""

OUT = os.path.join(HERE, "slides.html")
open(OUT, "w").write(HTML.replace("__DATA__", DATA_JS))
print("wrote", OUT, "(", round(os.path.getsize(OUT)/1024, 1), "KB )")
