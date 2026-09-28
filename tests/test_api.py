def register(c,email='a@example.com',username='alice'):
    r=c.post('/api/register',json={'name':'Alice','username':username,'email':email,'password':'password123'}); assert r.status_code==201; return r.json['token']
def auth(token): return {'Authorization':f'Bearer {token}'}

def test_registration_and_duplicate(client):
    register(client); r=client.post('/api/register',json={'name':'A','username':'alice','email':'a@example.com','password':'password123'}); assert r.status_code==409

def test_skill_goal_practice_progress(client):
    t=register(client); h=auth(t)
    s=client.post('/api/skills',json={'skill_name':'Photography','category':'Art'},headers=h).json
    g=client.post('/api/goals',json={'skill_id':s['id'],'title':'20 hours','target_value':20,'unit':'hours','milestones':[5,10,20]},headers=h); assert g.status_code==201
    r=client.post('/api/practice',json={'skill_id':s['id'],'duration_minutes':60,'activity':'Portraits'},headers=h); assert r.status_code==201
    goals=client.get('/api/goals',headers=h).json; assert goals[0]['current_value']==1

def test_duplicate_like_and_unauthorized_delete(client):
    t1=register(client); h1=auth(t1); client.post('/api/posts',json={'content':'Achievement'},headers=h1)
    post=client.get('/api/feed').json['items'][0]; t2=register(client,'b@example.com','bob'); h2=auth(t2)
    assert client.post(f"/api/posts/{post['id']}/like",headers=h2).status_code==200
    assert client.post(f"/api/posts/{post['id']}/like",headers=h2).status_code==200
    assert client.delete(f"/api/posts/{post['id']}",headers=h2).status_code==404

def test_user_data_isolation(client):
    t1=register(client); h1=auth(t1); client.post('/api/skills',json={'skill_name':'Coding','category':'Tech'},headers=h1)
    t2=register(client,'b@example.com','bob'); h2=auth(t2); assert client.get('/api/skills',headers=h2).json==[]
