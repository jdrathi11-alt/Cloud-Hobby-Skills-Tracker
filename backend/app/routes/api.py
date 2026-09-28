from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from sqlalchemy import or_, func
from .. import db
from ..models.models import User, Skill, Goal, Milestone, PracticeSession, Post, Comment, Like, Follow, FileAsset
from ..utils.auth import make_token, login_required
from ..services.analytics import dashboard
from ..services.storage import save_local, delete_local, get_storage

api = Blueprint('api', __name__)

def parse_date(v): return datetime.strptime(v, '%Y-%m-%d').date() if v else None
def user_json(u, public=False):
    d={'id':u.id,'name':u.name,'username':u.username,'bio':u.bio,'interests':u.interests,'profile_picture':u.profile_picture,'created_at':u.created_at.isoformat()}
    if not public: d['email']=u.email
    return d

def skill_json(s): return {'id':s.id,'user_id':s.user_id,'skill_name':s.skill_name,'category':s.category,'current_level':s.current_level,'target_level':s.target_level,'start_date':s.start_date.isoformat() if s.start_date else None,'target_date':s.target_date.isoformat() if s.target_date else None,'status':s.status,'description':s.description}

def post_json(p, me=None):
    likes=Like.query.filter_by(post_id=p.id).count(); liked=bool(me and Like.query.filter_by(post_id=p.id,user_id=me.id).first())
    return {'id':p.id,'content':p.content,'media_url':p.media_url,'created_at':p.created_at.isoformat(),'user':user_json(p.author,True),'skill_id':p.skill_id,'likes':likes,'liked':liked,'comments':Comment.query.filter_by(post_id=p.id).count()}

@api.post('/register')
def register():
    data=request.get_json() or {}; name=data.get('name','').strip(); username=data.get('username','').strip(); email=data.get('email','').strip().lower(); password=data.get('password','')
    if not all([name,username,email,password]) or len(password)<8: return jsonify({'error':'name, username, email and password(8+ chars) are required'}),400
    if User.query.filter(or_(User.username==username,User.email==email)).first(): return jsonify({'error':'Username or email already exists'}),409
    u=User(name=name,username=username,email=email); u.set_password(password); db.session.add(u); db.session.commit(); return jsonify({'token':make_token(u.id),'user':user_json(u)}),201

@api.post('/login')
def login():
    data=request.get_json() or {}; u=User.query.filter_by(email=data.get('email','').lower()).first()
    if not u or not u.check_password(data.get('password','')): return jsonify({'error':'Invalid credentials'}),401
    return jsonify({'token':make_token(u.id),'user':user_json(u)})

@api.post('/logout')
def logout(): return jsonify({'message':'Client should discard its token'})

@api.get('/profile')
@login_required
def profile(user): return jsonify(user_json(user))

@api.put('/profile')
@login_required
def update_profile(user):
    data=request.get_json() or {}
    for field in ['name','bio','interests']:
        if field in data: setattr(user,field,str(data[field]))
    db.session.commit(); return jsonify(user_json(user))


@api.post('/profile/avatar')
@login_required
def profile_avatar(user):
    try: key=save_local(request.files.get('file'),user.id)
    except ValueError as e: return jsonify({'error':str(e)}),400
    old=user.profile_picture
    user.profile_picture=key
    if old: delete_local(old)
    db.session.commit()
    return jsonify({'profile_picture':key})

@api.get('/users/<username>')
def public_profile(username):
    u=User.query.filter_by(username=username).first_or_404(); return jsonify(user_json(u,True))

@api.post('/skills')
@login_required
def create_skill(user):
    d=request.get_json() or {}; required=['skill_name','category']
    if any(not d.get(x) for x in required): return jsonify({'error':'skill_name and category are required'}),400
    s=Skill(user_id=user.id, skill_name=d['skill_name'], category=d['category'], current_level=d.get('current_level','BEGINNER'), target_level=d.get('target_level','INTERMEDIATE'), start_date=parse_date(d.get('start_date')), target_date=parse_date(d.get('target_date')), status=d.get('status','ACTIVE'), description=d.get('description',''))
    db.session.add(s); db.session.commit(); return jsonify(skill_json(s)),201

@api.get('/skills')
@login_required
def get_skills(user): return jsonify([skill_json(s) for s in Skill.query.filter_by(user_id=user.id).order_by(Skill.created_at.desc()).all()])

@api.get('/skills/<int:sid>')
@login_required
def get_skill(user,sid):
    s=Skill.query.filter_by(id=sid,user_id=user.id).first_or_404(); return jsonify(skill_json(s))

@api.put('/skills/<int:sid>')
@login_required
def update_skill(user,sid):
    s=Skill.query.filter_by(id=sid,user_id=user.id).first_or_404(); d=request.get_json() or {}
    for f in ['skill_name','category','current_level','target_level','status','description']:
        if f in d: setattr(s,f,d[f])
    for f in ['start_date','target_date']:
        if f in d: setattr(s,f,parse_date(d[f]))
    db.session.commit(); return jsonify(skill_json(s))

@api.delete('/skills/<int:sid>')
@login_required
def delete_skill(user,sid):
    s=Skill.query.filter_by(id=sid,user_id=user.id).first_or_404(); db.session.delete(s); db.session.commit(); return jsonify({'message':'Skill deleted'})

@api.post('/goals')
@login_required
def create_goal(user):
    d=request.get_json() or {}; s=Skill.query.filter_by(id=d.get('skill_id'),user_id=user.id).first()
    if not s: return jsonify({'error':'Skill not found'}),404
    g=Goal(user_id=user.id,skill_id=s.id,title=d.get('title',''),target_value=float(d.get('target_value',0)),unit=d.get('unit','hours'),deadline=parse_date(d.get('deadline')),status='ACTIVE')
    db.session.add(g); db.session.commit()
    for value in d.get('milestones',[]): db.session.add(Milestone(goal_id=g.id,title=f'{value} {g.unit}',target_value=float(value)))
    db.session.commit(); return jsonify(goal_json(g)),201

def goal_json(g):
    pct=min(100, round((g.current_value/g.target_value*100) if g.target_value else 0,1)); ms=Milestone.query.filter_by(goal_id=g.id).all()
    return {'id':g.id,'skill_id':g.skill_id,'title':g.title,'target_value':g.target_value,'current_value':g.current_value,'unit':g.unit,'deadline':g.deadline.isoformat() if g.deadline else None,'status':g.status,'progress':pct,'milestones':[{'id':m.id,'title':m.title,'target_value':m.target_value,'achieved':m.achieved,'achieved_at':m.achieved_at.isoformat() if m.achieved_at else None} for m in ms]}

@api.get('/goals')
@login_required
def get_goals(user): return jsonify([goal_json(g) for g in Goal.query.filter_by(user_id=user.id).all()])

@api.put('/goals/<int:gid>')
@login_required
def update_goal(user,gid):
    g=Goal.query.filter_by(id=gid,user_id=user.id).first_or_404(); d=request.get_json() or {}
    if 'current_value' in d: g.current_value=float(d['current_value'])
    if 'status' in d: g.status=d['status']
    if g.current_value>=g.target_value: g.status='COMPLETED'
    for m in Milestone.query.filter_by(goal_id=g.id).all():
        if g.current_value>=m.target_value and not m.achieved: m.achieved=True; m.achieved_at=datetime.now(timezone.utc)
    db.session.commit(); return jsonify(goal_json(g))

@api.post('/practice')
@login_required
def practice(user):
    d=request.get_json() or {}; s=Skill.query.filter_by(id=d.get('skill_id'),user_id=user.id).first()
    if not s or int(d.get('duration_minutes',0))<=0: return jsonify({'error':'Valid skill and positive duration required'}),400
    p=PracticeSession(user_id=user.id,skill_id=s.id,duration_minutes=int(d['duration_minutes']),activity=d.get('activity','Practice'),notes=d.get('notes',''),practiced_at=datetime.fromisoformat(d['practiced_at'].replace('Z','+00:00')) if d.get('practiced_at') else datetime.now(timezone.utc))
    db.session.add(p); db.session.flush()
    for g in Goal.query.filter_by(user_id=user.id,skill_id=s.id,status='ACTIVE').all(): g.current_value += p.duration_minutes/60; g.status='COMPLETED' if g.current_value>=g.target_value else g.status
    db.session.commit(); return jsonify({'id':p.id,'message':'Practice logged','dashboard':dashboard(user.id)}),201

@api.get('/practice')
@login_required
def get_practice(user):
    rows=PracticeSession.query.filter_by(user_id=user.id).order_by(PracticeSession.practiced_at.desc()).all(); return jsonify([{'id':r.id,'skill_id':r.skill_id,'duration_minutes':r.duration_minutes,'activity':r.activity,'notes':r.notes,'practiced_at':r.practiced_at.isoformat()} for r in rows])

@api.get('/skills/<int:sid>/practice')
@login_required
def skill_practice(user,sid):
    Skill.query.filter_by(id=sid,user_id=user.id).first_or_404(); rows=PracticeSession.query.filter_by(user_id=user.id,skill_id=sid).all(); return jsonify([{'id':r.id,'duration_minutes':r.duration_minutes,'activity':r.activity,'notes':r.notes,'practiced_at':r.practiced_at.isoformat()} for r in rows])

@api.post('/posts')
@login_required
def create_post(user):
    d=request.form if request.form else (request.get_json() or {}); content=d.get('content','').strip(); skill_id=d.get('skill_id') or None
    if not content: return jsonify({'error':'Content required'}),400
    if skill_id and not Skill.query.filter_by(id=int(skill_id),user_id=user.id).first(): return jsonify({'error':'Skill not found'}),404
    p=Post(user_id=user.id,skill_id=int(skill_id) if skill_id else None,content=content); db.session.add(p); db.session.flush()
    attachment=request.files.get('file') if request.files else None
    if attachment:
        try:
            key=save_local(attachment,user.id); a=FileAsset(user_id=user.id,object_key=key,original_name=attachment.filename,content_type=attachment.content_type,size_bytes=0,visibility='public'); db.session.add(a); db.session.flush(); p.media_url=f'/api/files/{a.id}'
        except ValueError as e:
            db.session.rollback(); return jsonify({'error':str(e)}),400
    db.session.commit(); return jsonify(post_json(p,user)),201

@api.get('/feed')
def feed():
    q=request.args.get('q','').strip(); category=request.args.get('category','').strip(); page=max(1,int(request.args.get('page',1))); per=min(30,max(1,int(request.args.get('per_page',10))))
    query=Post.query.join(User).outerjoin(Skill,Post.skill_id==Skill.id)
    if q: query=query.filter(or_(Post.content.ilike(f'%{q}%'),User.username.ilike(f'%{q}%'),Skill.skill_name.ilike(f'%{q}%')))
    if category: query=query.filter(Skill.category==category)
    rows=query.order_by(Post.created_at.desc()).paginate(page=page,per_page=per,error_out=False); return jsonify({'items':[post_json(p) for p in rows.items],'page':page,'pages':rows.pages,'total':rows.total})

@api.delete('/posts/<int:pid>')
@login_required
def delete_post(user,pid):
    p=Post.query.filter_by(id=pid,user_id=user.id).first_or_404(); db.session.delete(p); db.session.commit(); return jsonify({'message':'Post deleted'})

@api.post('/posts/<int:pid>/like')
@login_required
def like(user,pid):
    Post.query.get_or_404(pid)
    if Like.query.filter_by(post_id=pid,user_id=user.id).first(): return jsonify({'message':'Already liked'}),200
    db.session.add(Like(post_id=pid,user_id=user.id)); db.session.commit(); return jsonify({'liked':True})

@api.delete('/posts/<int:pid>/like')
@login_required
def unlike(user,pid):
    x=Like.query.filter_by(post_id=pid,user_id=user.id).first()
    if x: db.session.delete(x); db.session.commit()
    return jsonify({'liked':False})

@api.get('/posts/<int:pid>/comments')
def comments(pid):
    Post.query.get_or_404(pid); rows=Comment.query.filter_by(post_id=pid).order_by(Comment.created_at.asc()).all(); return jsonify([{'id':c.id,'content':c.content,'created_at':c.created_at.isoformat(),'user':user_json(User.query.get(c.user_id),True)} for c in rows])

@api.post('/posts/<int:pid>/comments')
@login_required
def add_comment(user,pid):
    Post.query.get_or_404(pid); content=(request.get_json() or {}).get('content','').strip()
    if not content: return jsonify({'error':'Comment required'}),400
    c=Comment(post_id=pid,user_id=user.id,content=content); db.session.add(c); db.session.commit(); return jsonify({'id':c.id,'content':c.content}),201

@api.delete('/comments/<int:cid>')
@login_required
def delete_comment(user,cid):
    c=Comment.query.get_or_404(cid); p=Post.query.get(c.post_id)
    if c.user_id!=user.id and p.user_id!=user.id: return jsonify({'error':'Forbidden'}),403
    db.session.delete(c); db.session.commit(); return jsonify({'message':'Comment deleted'})

@api.post('/users/<int:uid>/follow')
@login_required
def follow(user,uid):
    if user.id==uid: return jsonify({'error':'Cannot follow yourself'}),400
    User.query.get_or_404(uid)
    if not Follow.query.filter_by(follower_id=user.id,followed_id=uid).first(): db.session.add(Follow(follower_id=user.id,followed_id=uid)); db.session.commit()
    return jsonify({'following':True})

@api.delete('/users/<int:uid>/follow')
@login_required
def unfollow(user,uid):
    x=Follow.query.filter_by(follower_id=user.id,followed_id=uid).first()
    if x: db.session.delete(x); db.session.commit()
    return jsonify({'following':False})

@api.get('/analytics/dashboard')
@login_required
def analytics(user): return jsonify(dashboard(user.id))

@api.post('/files/upload')
@login_required
def upload(user):
    try: key=save_local(request.files.get('file'),user.id)
    except ValueError as e: return jsonify({'error':str(e)}),400
    f=request.files['file']; import os; path=os.path.join(current_app.config['UPLOAD_FOLDER'], key); asset=FileAsset(user_id=user.id,object_key=key,original_name=f.filename,content_type=f.content_type,size_bytes=os.path.getsize(path),visibility=request.form.get('visibility','private')); db.session.add(asset); db.session.commit(); return jsonify({'id':asset.id,'object_key':key,'url':f'/api/files/{asset.id}'}),201

@api.get('/files/<int:fid>')
@login_required
def get_file(user,fid):
    a=FileAsset.query.filter_by(id=fid).first_or_404()
    if a.visibility!='public' and a.user_id!=user.id: return jsonify({'error':'Forbidden'}),403
    import os
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], os.path.dirname(a.object_key), path=os.path.basename(a.object_key), as_attachment=False, mimetype=a.content_type)

@api.delete('/files/<int:fid>')
@login_required
def delete_file(user,fid):
    a=FileAsset.query.filter_by(id=fid,user_id=user.id).first_or_404(); delete_local(a.object_key); db.session.delete(a); db.session.commit(); return jsonify({'message':'File deleted'})
