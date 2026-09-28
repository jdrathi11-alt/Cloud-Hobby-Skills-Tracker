import React,{useEffect,useState} from 'react'; import {createRoot} from 'react-dom/client'; import {api,auth} from './services/api'; import {LineChart,Line,XAxis,YAxis,Tooltip,BarChart,Bar,CartesianGrid,ResponsiveContainer} from 'recharts'; import './style.css';
const demoSkills=['Photography','Guitar','Coding','Painting','Cooking','Chess'];
function App(){const [user,setUser]=useState(JSON.parse(localStorage.getItem('user')||'null')); const [tab,setTab]=useState(user?'dashboard':'login'); const [skills,setSkills]=useState([]),[goals,setGoals]=useState([]),[feed,setFeed]=useState([]),[stats,setStats]=useState(null),[msg,setMsg]=useState('');
const refresh=async()=>{if(!user)return; try{const [s,g,a,f]=await Promise.all([api('/skills'),api('/goals'),api('/analytics/dashboard'),api('/feed?per_page=20')]);setSkills(s);setGoals(g);setStats(a);setFeed(f.items)}catch(e){setMsg(e.message)}}; useEffect(()=>{refresh()},[user]);
function loggedIn(data){localStorage.setItem('token',data.token);localStorage.setItem('user',JSON.stringify(data.user));setUser(data.user);setTab('dashboard')}
if(!user) return <Auth onDone={loggedIn} mode={tab} setMode={setTab}/>;
return <div><header><b>☁️ SkillCloud</b><nav>{['dashboard','skills','practice','goals','community','profile'].map(x=><button className={tab===x?'active':''} onClick={()=>setTab(x)}>{x}</button>)}<button onClick={()=>{localStorage.clear();setUser(null)}}>Logout</button></nav></header><main>{msg&&<div className="notice">{msg}</div>}{tab==='dashboard'&&<Dashboard stats={stats} goals={goals} skills={skills}/>} {tab==='skills'&&<Skills skills={skills} refresh={refresh}/>} {tab==='practice'&&<Practice skills={skills} refresh={refresh}/>} {tab==='goals'&&<Goals skills={skills} goals={goals} refresh={refresh}/>} {tab==='community'&&<Community feed={feed} refresh={refresh}/>} {tab==='profile'&&<Profile user={user} setUser={setUser}/>}</main></div>}
function Auth({onDone,mode,setMode}){const [form,setForm]=useState({name:'Demo User',username:'demo_user',email:'demo@example.com',password:'password123'}); const submit=async e=>{e.preventDefault();try{const d=mode==='login'?await auth.login({email:form.email,password:form.password}):await auth.register(form);onDone(d)}catch(e){alert(e.message)}};return <div className="auth"><h1>SkillCloud</h1><p>Cloud-based hobby, skill, practice and community tracker.</p><form onSubmit={submit}>{mode==='register'&&<><input placeholder="Name" value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/><input placeholder="Username" value={form.username} onChange={e=>setForm({...form,username:e.target.value})}/></>}<input placeholder="Email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/><input type="password" placeholder="Password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/><button>{mode==='login'?'Login':'Create account'}</button></form><button className="link" onClick={()=>setMode(mode==='login'?'register':'login')}>{mode==='login'?'New user? Register':'Already registered? Login'}</button></div>}
function Dashboard({stats,goals,skills}){if(!stats)return <p>Loading...</p>; const data=stats.practice_by_skill||[];return <><h2>Welcome 👋</h2><div className="cards">{[['Practice hours',stats.total_practice_hours],['Weekly',stats.weekly_practice_hours],['Current streak',`${stats.current_streak} days`],['Goals completed',stats.goals_completed],['Milestones',stats.milestones_achieved],['Likes received',stats.likes_received]].map(x=><div className="card"><small>{x[0]}</small><strong>{x[1]}</strong></div>)}</div><div className="grid"><section className="panel"><h3>Practice by skill</h3><ResponsiveContainer width="100%" height={280}><BarChart data={data}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="skill"/><YAxis/><Tooltip/><Bar dataKey="hours"/></BarChart></ResponsiveContainer></section><section className="panel"><h3>Active skills</h3>{skills.map(s=><div className="row"><span>{s.skill_name}</span><span>{s.current_level}</span></div>)}</section></div></>}
function Skills({skills,refresh}){const [f,setF]=useState({skill_name:'Photography',category:'Art',current_level:'BEGINNER',target_level:'INTERMEDIATE',description:''});const add=async()=>{try{await api('/skills',{method:'POST',body:JSON.stringify(f)});refresh()}catch(e){alert(e.message)}};return <><h2>Skills</h2><div className="panel formgrid">{Object.entries(f).map(([k,v])=><input placeholder={k} value={v} onChange={e=>setF({...f,[k]:e.target.value})}/>)}<button onClick={add}>Add Skill</button></div>{skills.map(s=><div className="panel"><b>{s.skill_name}</b> · {s.category} · {s.current_level} → {s.target_level}<p>{s.description}</p><button onClick={async()=>{await api(`/skills/${s.id}`,{method:'DELETE'});refresh()}}>Delete</button></div>)}</>}
function Practice({skills,refresh}){const [f,setF]=useState({skill_id:'',duration_minutes:60,activity:'Practice session',notes:''});return <><h2>Log practice</h2><div className="panel formgrid"><select value={f.skill_id} onChange={e=>setF({...f,skill_id:e.target.value})}><option value="">Select skill</option>{skills.map(s=><option value={s.id}>{s.skill_name}</option>)}</select><input type="number" value={f.duration_minutes} onChange={e=>setF({...f,duration_minutes:e.target.value})}/><input value={f.activity} onChange={e=>setF({...f,activity:e.target.value})}/><textarea value={f.notes} onChange={e=>setF({...f,notes:e.target.value})}/><button onClick={async()=>{try{await api('/practice',{method:'POST',body:JSON.stringify(f)});refresh();alert('Practice logged')}catch(e){alert(e.message)}}}>Save session</button></div></>}
function Goals({skills,goals,refresh}){const [f,setF]=useState({skill_id:'',title:'Practice 20 hours',target_value:20,unit:'hours',milestones:[5,10,20]});return <><h2>Goals & milestones</h2><div className="panel formgrid"><select value={f.skill_id} onChange={e=>setF({...f,skill_id:e.target.value})}><option value="">Select skill</option>{skills.map(s=><option value={s.id}>{s.skill_name}</option>)}</select><input value={f.title} onChange={e=>setF({...f,title:e.target.value})}/><input type="number" value={f.target_value} onChange={e=>setF({...f,target_value:e.target.value})}/><button onClick={async()=>{try{await api('/goals',{method:'POST',body:JSON.stringify(f)});refresh()}catch(e){alert(e.message)}}}>Create goal</button></div>{goals.map(g=><div className="panel"><b>{g.title}</b><div className="progress"><i style={{width:`${g.progress}%`}}/></div><p>{g.current_value.toFixed(1)} / {g.target_value} {g.unit} ({g.progress}%)</p>{g.milestones.map(m=><span className="pill">{m.achieved?'✓':'○'} {m.title}</span>)}</div>)}</>}
function Community({feed,refresh}){
const [content,setContent]=useState('');
const [file,setFile]=useState(null);
const [posting,setPosting]=useState(false);

const post=async()=>{
if(!content.trim()&&!file){
alert('Write something or attach a file');
return;
}

```
try{
  setPosting(true);

  const formData=new FormData();
  formData.append('content',content);

  if(file){
    formData.append('file',file);
  }

  await api('/posts',{
    method:'POST',
    body:formData
  });

  setContent('');
  setFile(null);

  const input=document.getElementById('post-file');
  if(input) input.value='';

  refresh();
}catch(e){
  alert(e.message);
}finally{
  setPosting(false);
}
```

};

return <> <h2>Community</h2>

```
<div className="panel">
  <textarea
    placeholder="Share an achievement..."
    value={content}
    onChange={e=>setContent(e.target.value)}
  />

  <input
    id="post-file"
    type="file"
    accept="image/jpeg,image/png,image/webp,application/pdf"
    onChange={e=>setFile(e.target.files?.[0]||null)}
  />

  {file&&(
    <p>
      Selected file: <b>{file.name}</b>
    </p>
  )}

  <button onClick={post} disabled={posting}>
    {posting?'Posting...':'Post'}
  </button>
</div>

{feed.map(p=>
  <article className="panel" key={p.id}>
    <b>@{p.user.username}</b>
    <small> · {new Date(p.created_at).toLocaleString()}</small>

    <p>{p.content}</p>

    {p.media_url&&(
      <div style={{margin:'12px 0'}}>
        {/\.(jpg|jpeg|png|webp)$/i.test(p.media_url)?(
          <img
            src={`http://127.0.0.1:5000${p.media_url}`}
            alt="Post attachment"
            style={{
              maxWidth:'100%',
              maxHeight:'400px',
              borderRadius:'10px'
            }}
          />
        ):(
          <a
            href={`http://127.0.0.1:5000${p.media_url}`}
            target="_blank"
            rel="noreferrer"
          >
            📎 View attachment
          </a>
        )}
      </div>
    )}

    <button
      onClick={async()=>{
        await api(`/posts/${p.id}/like`,{method:'POST'});
        refresh();
      }}
    >
      ♥ {p.likes}
    </button>

    <button
      onClick={async()=>{
        const c=prompt('Comment');
        if(c){
          await api(`/posts/${p.id}/comments`,{
            method:'POST',
            body:JSON.stringify({content:c})
          });
          refresh();
        }
      }}
    >
      Comment ({p.comments})
    </button>
  </article>
)}
```

</>;
}

function Profile({user,setUser}){
const [f,setF]=useState(user);
const [file,setFile]=useState(null);
const [uploading,setUploading]=useState(false);

const save=async()=>{
try{
const d=await api('/profile',{
method:'PUT',
body:JSON.stringify(f)
});
localStorage.setItem('user',JSON.stringify(d));
setUser(d);
alert('Profile saved');
}catch(e){
alert(e.message);
}
};

const uploadAvatar=async()=>{
if(!file)return;

```
try{
  setUploading(true);

  const formData=new FormData();
  formData.append('file',file);

  const d=await api('/profile/avatar',{
    method:'POST',
    body:formData
  });

  const updated={...f,profile_picture:d.profile_picture};
  setF(updated);
  localStorage.setItem('user',JSON.stringify(updated));
  setUser(updated);
  setFile(null);

  alert('Profile picture uploaded');
}catch(e){
  alert(e.message);
}finally{
  setUploading(false);
}
```

};

return <> <h2>Profile</h2>

```
<div className="panel formgrid">
  {f.profile_picture&&(
    <img
      src={`http://127.0.0.1:5000${f.profile_picture}`}
      alt="Profile"
      style={{
        width:'120px',
        height:'120px',
        borderRadius:'50%',
        objectFit:'cover'
      }}
    />
  )}

  <input
    type="file"
    accept="image/jpeg,image/png,image/webp"
    onChange={e=>setFile(e.target.files?.[0]||null)}
  />

  <button onClick={uploadAvatar} disabled={!file||uploading}>
    {uploading?'Uploading...':'Upload profile picture'}
  </button>

  <input
    value={f.name}
    onChange={e=>setF({...f,name:e.target.value})}
    placeholder="Name"
  />

  <input
    value={f.bio||''}
    placeholder="Bio"
    onChange={e=>setF({...f,bio:e.target.value})}
  />

  <input
    value={f.interests||''}
    placeholder="Interests"
    onChange={e=>setF({...f,interests:e.target.value})}
  />

  <button onClick={save}>Save</button>
</div>
```

</>;
}

createRoot(document.getElementById('root')).render(<App/>);
