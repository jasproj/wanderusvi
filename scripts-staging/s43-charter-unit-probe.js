/**
 * S43 Phase-0 probe — live FareHarbor evidence for the charter-unit template.
 *
 * Recon only: writes nothing into the repo. Reproduces the evidence behind
 * scripts-staging/s43-charter-unit-adjudicated.json.
 *
 * Population : S40 ledger D-485 (group/charter unit) HOLD rows, status active.
 *              Expects <outputDir>/pop.json — [{pk, shortname, ...}].
 * Dates      : 14 consecutive from BASE, plus BASE+30/+60/+90 = 17 distinct.
 * Endpoint   : /api/embed/{shortname}/price-preview/per-item/v2/
 *              ?item_pks={csv}&include_breakdown=yes&date={d}
 *
 * Date-validity is instrumented, not assumed: the endpoint answers with the next
 * availability at or after the requested date, so a reading's availability date
 * frequently differs from the one asked for. Both are recorded per reading, and
 * `dateValid` marks whether they matched.
 *
 * Usage: node scripts-staging/s43-charter-unit-probe.js <outputDir> [BASE-DATE]
 */
const fs=require("fs");
const SP=process.argv[2];
if(!SP){ console.error("usage: node s43-charter-unit-probe.js <outputDir> [BASE-DATE]"); process.exit(1); }
const BASE=process.argv[3]||"2026-08-24";
function addDays(iso,n){ const local_d=new Date(iso+"T00:00:00Z"); local_d.setUTCDate(local_d.getUTCDate()+n); return local_d.toISOString().slice(0,10); }
const DATES=[]; for(let i=0;i<14;i++) DATES.push(addDays(BASE,i));
for(const off of [30,60,90]) DATES.push(addDays(BASE,off));
if(new Set(DATES).size!==17) throw new Error("dates!=17");

const pop=JSON.parse(fs.readFileSync(SP+"/pop.json","utf8"));
const byShort=new Map();
for(const r of pop){ if(!byShort.has(r.shortname)) byShort.set(r.shortname,[]); byShort.get(r.shortname).push(r.pk); }

// build full job list: one job per (shortname, date, chunk)
const JOBS=[];
for(const [sn,pks] of byShort) for(const date of DATES)
  for(let i=0;i<pks.length;i+=40) JOBS.push({sn,date,chunk:pks.slice(i,i+40)});

const readings={}; for(const r of pop) readings[r.pk]=[];
let reqs=0,errs=0,dateHit=0,dateMiss=0,absent=0,done=0;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));

async function pull(job){
  const local_url="https://fareharbor.com/api/embed/"+job.sn+"/price-preview/per-item/v2/"
    +"?item_pks="+job.chunk.join(",")+"&include_breakdown=yes&date="+job.date;
  for(let a=0;a<3;a++){
    try{
      const local_res=await fetch(local_url,{headers:{Accept:"application/json"}});
      if(!local_res.ok){ if(a===2) return {error:"HTTP "+local_res.status}; await sleep(600*(a+1)); continue; }
      return {json:await local_res.json()};
    }catch(e){ if(a===2) return {error:String((e&&e.message)||e)}; await sleep(600*(a+1)); }
  }
  return {error:"unreachable"};
}

async function worker(){
  while(JOBS.length){
    const local_job=JOBS.pop(); if(!local_job) break;
    const local_out=await pull(local_job); reqs++;
    if(local_out.error){ errs++; }
    else{
      const local_items=(local_out.json&&local_out.json.items)||[];
      const local_seen=new Set();
      for(const it of local_items){
        const local_pk=String(it.id); local_seen.add(local_pk);
        if(!readings[local_pk]) continue;
        const local_av=it.availability||null;
        const local_start=local_av&&local_av.start_at?String(local_av.start_at).slice(0,10):null;
        if(local_start===local_job.date) dateHit++; else dateMiss++;
        const local_bd=it.price&&it.price.breakdown&&it.price.breakdown.customer_types;
        readings[local_pk].push({reqDate:local_job.date,avDate:local_start,avId:local_av?local_av.id:null,
          dateValid:local_start===local_job.date,low:it.price?it.price.low:null,high:it.price?it.price.high:null,
          tiers:Array.isArray(local_bd)?local_bd.map(c=>({singular:c.singular,plural:c.plural,note:c.note,
            priceCents:c.price,price:(typeof c.price==="number"?c.price/100:null),minPartySize:c.min_party_size,id:c.id})):null});
      }
      for(const p of local_job.chunk) if(!local_seen.has(p)) absent++;
    }
    done++;
    if(done%40===0) process.stderr.write("progress "+done+" reqs, "+errs+" err\n");
    await sleep(60);
  }
}
(async()=>{
  const local_total=JOBS.length;
  process.stderr.write("jobs: "+local_total+"\n");
  await Promise.all(Array.from({length:8},()=>worker()));
  fs.writeFileSync(SP+"/readings.json",JSON.stringify({BASE,DATES,readings}));
  console.log(JSON.stringify({jobs:local_total,requests:reqs,errors:errs,dateHit,dateMiss,absentSlots:absent,
    rowsWithAnyReading:Object.values(readings).filter(a=>a.length).length,rows:pop.length},null,1));
})();
