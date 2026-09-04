const COLDEF = {
  rank:{label:"Rank",type:"rank"},
  name:{label:"Team",type:"team"},
  wl:{label:"W&ndash;L",type:"wl"},
  kpi:{label:"KPI",type:"num"},
  ppi:{label:"PPI",type:"dec"},
  six:{label:"S-Ix",type:"num"},
  wpi:{label:"WPI",type:"num"},
  prank:{label:"P",type:"num"},
  wrank:{label:"W",type:"num"},
  sos:{label:"SOS",type:"dec"},
  kpirank:{label:"Rk",type:"num"}
};

(function(){
  const TABS = window.KPI_TABS || [];
  const DATA = window.KPI_DATA || {};
  if(!TABS.length) return;

  let state = { tab: TABS[0].id, sortKey:"rank", sortDir:"asc", query:"" };

  function currentTab(){ return TABS.find(t=>t.id===state.tab); }
  function rowsFor(tab){ return DATA[tab.id] || []; }

  function fmt(v,type){
    if(type==="dec") return (v>0?"+":"") + v.toFixed(2);
    return String(v);
  }

  function renderStats(){
    const rows = rowsFor(TABS[0]);
    const total = rows.length;
    const played = rows.filter(r=>r.wl.split("-").some(p=>Number(p)>0)).length;
    const unbeaten = rows.filter(r=>{
      const parts = r.wl.split("-");
      return Number(parts[0])>0 && Number(parts[parts.length-1])===0;
    }).length;
    const topRank = rows.length ? Math.min(...rows.map(r=>r.rank)) : null;
    const leaders = rows.filter(r=>r.rank===topRank).map(r=>r.name).join(" & ");

    const items = [
      {label:"Teams Tracked", value: total},
      {label:"Games Played", value: played},
      {label:"Unbeaten", value: unbeaten, accent:true},
      {label:"Top Ranked", value: leaders || "&mdash;", accent:true}
    ];
    document.getElementById("stats").innerHTML = items.map(i=>
      `<div class="stat"><span class="stat-label">${i.label}</span><span class="stat-value${i.accent?" accent":""}">${i.value}</span></div>`
    ).join("");
  }

  function renderTabs(){
    const wrap = document.getElementById("tabs");
    if(TABS.length < 2){
      wrap.style.display = "none";
      return;
    }
    wrap.style.display = "";
    wrap.innerHTML = TABS.map(t=>
      `<button class="tab-btn" role="tab" aria-selected="${t.id===state.tab}" data-tab="${t.id}">${t.label}</button>`
    ).join("");
  }

  function renderHead(){
    const t = currentTab();
    document.getElementById("thead-row").innerHTML = t.cols.map(key=>{
      const def = COLDEF[key];
      const arrow = state.sortKey===key
        ? (state.sortDir==="asc" ? "&#9650;" : "&#9660;")
        : "&#9660;";
      const ariaSort = state.sortKey===key ? (state.sortDir==="asc"?"ascending":"descending") : "none";
      return `<th data-key="${key}" aria-sort="${ariaSort}">${def.label}<span class="arrow">${arrow}</span></th>`;
    }).join("");
  }

  function cellHTML(row,key){
    const def = COLDEF[key];
    const v = row[key];
    if(def.type==="rank") return `<td class="rank">${v}</td>`;
    if(def.type==="team") return `<td class="team">${v}</td>`;
    if(def.type==="wl"){
      const parts = v.split("-");
      const w = parts[0], l = parts[parts.length-1];
      const mid = parts.length===3 ? `<b>${parts[1]}</b>&ndash;` : "";
      return `<td class="wl"><b class="w">${w}</b>&ndash;${mid}<b class="l">${l}</b></td>`;
    }
    return `<td>${fmt(v,def.type)}</td>`;
  }

  function renderBody(){
    const t = currentTab();
    let rows = rowsFor(t).slice();

    if(state.query){
      const q = state.query.toLowerCase();
      rows = rows.filter(r=>r.name.toLowerCase().includes(q));
    }

    rows.sort((a,b)=>{
      const k = state.sortKey in a ? state.sortKey : "rank";
      let av=a[k], bv=b[k];
      if(typeof av==="string") { av=av.toLowerCase(); bv=bv.toLowerCase(); }
      if(av<bv) return state.sortDir==="asc" ? -1 : 1;
      if(av>bv) return state.sortDir==="asc" ? 1 : -1;
      return a.rank-b.rank;
    });

    const body = document.getElementById("tbody");

    if(rows.length===0){
      body.innerHTML = `<tr class="empty-row"><td colspan="${t.cols.length}">No teams match &ldquo;${state.query}&rdquo;.</td></tr>`;
      return;
    }

    body.innerHTML = rows.map(r=>`<tr>${t.cols.map(key=>cellHTML(r,key)).join("")}</tr>`).join("");
  }

  function renderAll(){
    renderTabs();
    renderHead();
    renderBody();
  }

  document.getElementById("tabs").addEventListener("click",e=>{
    const btn = e.target.closest(".tab-btn");
    if(!btn) return;
    state.tab = btn.dataset.tab;
    state.sortKey = "rank";
    state.sortDir = "asc";
    renderAll();
  });

  document.getElementById("thead-row").addEventListener("click",e=>{
    const th = e.target.closest("th");
    if(!th) return;
    const key = th.dataset.key;
    if(state.sortKey===key){
      state.sortDir = state.sortDir==="asc" ? "desc" : "asc";
    } else {
      state.sortKey = key;
      state.sortDir = (key==="rank") ? "asc" : "desc";
    }
    renderHead();
    renderBody();
  });

  document.getElementById("search").addEventListener("input",e=>{
    state.query = e.target.value.trim();
    renderBody();
  });

  renderStats();
  renderAll();
})();
