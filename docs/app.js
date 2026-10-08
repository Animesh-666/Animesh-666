
(() => {
  const username = 'Animesh-666';
  const set = (key, value) => document.querySelectorAll(`[data-stat="${key}"]`).forEach(el => el.textContent = Number(value).toLocaleString('en-US'));
  const api = async (url) => {
    const res = await fetch(url, {headers: {'Accept':'application/vnd.github+json'}});
    if (!res.ok) throw new Error(`GitHub API responded ${res.status}`);
    return await res.json();
  };
  const colors=['#42edae','#32c9d8','#5b8af6','#a379eb','#39525b'];
  const makeLanguages = (repos) => {
    const counted = {};
    for (const repo of repos) if (repo.language && !repo.fork) counted[repo.language] = (counted[repo.language] || 0) + 1;
    const data = Object.entries(counted).sort((a,b)=>b[1]-a[1]);
    if(!data.length) {document.querySelector('#language-legend').textContent='No repository-language data';return;}
    const top=data.slice(0,4);
    const other=data.slice(4).reduce((s,[_,n])=>s+n,0);
    if(other)top.push(['Other',other]);
    const sum=top.reduce((s,[_,n])=>s+n,0);
    let pct=0,stops=[];
    const legend=document.querySelector('#language-legend');legend.replaceChildren();
    for(let i=0;i<top.length;i++) {
      const [name,n]=top[i];let start=pct;pct+=n/sum*100;
      stops.push(`${colors[i]} ${start.toFixed(2)}% ${pct.toFixed(2)}%`);
      const line=document.createElement('span');const dot=document.createElement('i');dot.style.background=colors[i];
      line.append(dot,document.createTextNode(`${name} · ${n}`));legend.append(line);
    }
    document.querySelector('.donut').style.background=`conic-gradient(${stops.join(',')})`;
  };
  async function load() {
    try {
      const [profile,repos] = await Promise.all([
        api(`https://api.github.com/users/${username}`),
        api(`https://api.github.com/users/${username}/repos?per_page=100&sort=updated`)
      ]);
      set('repos',profile.public_repos);set('followers',profile.followers);set('following',profile.following);set('gists',profile.public_gists);
      set('stars',repos.reduce((sum,repo)=>sum+(repo.stargazers_count||0),0));
      makeLanguages(repos);
      const repoStars = new Map(repos.map(repo=>[repo.full_name.toLowerCase(),repo.stargazers_count]));
      document.querySelectorAll('[data-project-stars]').forEach(el=>{
        const k=el.dataset.projectStars.toLowerCase();
        if(repoStars.has(k))el.textContent=`★ ${repoStars.get(k)}`;
      });
    } catch(e) {
      document.querySelector('#language-legend').textContent='Visit GitHub for live statistics';
      console.warn('Public statistics could not be loaded.',e);
    }
    const team = document.querySelector('[data-project-stars="subhadipmondal99/ReFeed"]');
    if(team) {
      try {const repo=await api('https://api.github.com/repos/subhadipmondal99/ReFeed');team.textContent=`★ ${repo.stargazers_count}`;}catch(_){/* keep neutral placeholder */}
    }
  }
  const chart=document.querySelector('#contrib-chart');
  if(chart)chart.addEventListener('error',()=>{chart.hidden=true;document.querySelector('.contrib-fallback').hidden=false;});
  const year=document.querySelector('#year');if(year)year.textContent=new Date().getFullYear();
  load();
})();
