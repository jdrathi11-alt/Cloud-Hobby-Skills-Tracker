from datetime import datetime, timedelta, timezone
from collections import defaultdict
from ..models.models import PracticeSession, Goal, Milestone, Post, Like, Comment, Skill

def _sessions(user_id): return PracticeSession.query.filter_by(user_id=user_id).all()
def _streaks(sessions):
    days = sorted({s.practiced_at.date() for s in sessions}, reverse=True)
    if not days: return 0, 0
    longest = cur = 1
    for i in range(1, len(days)):
        if days[i-1] - days[i] == timedelta(days=1): cur += 1; longest = max(longest, cur)
        else: cur = 1
    today = datetime.now(timezone.utc).date()
    current = 0
    for d in days:
        expected = today - timedelta(days=current)
        if d == expected: current += 1
        elif d < expected: break
    return current, longest

def dashboard(user_id):
    sessions = _sessions(user_id)
    now = datetime.now(timezone.utc)
    week_start = (now - timedelta(days=now.weekday())).date()
    month_start = now.date().replace(day=1)
    total = sum(s.duration_minutes for s in sessions) / 60
    weekly = sum(s.duration_minutes for s in sessions if s.practiced_at.date() >= week_start) / 60
    monthly = sum(s.duration_minutes for s in sessions if s.practiced_at.date() >= month_start) / 60
    by_skill = defaultdict(float)
    for s in sessions: by_skill[s.skill_id] += s.duration_minutes / 60
    skill_names = {x.id: x.skill_name for x in Skill.query.filter(Skill.id.in_(by_skill.keys())).all()} if by_skill else {}
    current, longest = _streaks(sessions)
    goals = Goal.query.filter_by(user_id=user_id).all()
    completed = sum(1 for g in goals if g.status == 'COMPLETED' or g.current_value >= g.target_value)
    posts = Post.query.filter_by(user_id=user_id).all()
    post_ids = [p.id for p in posts]
    likes = Like.query.filter(Like.post_id.in_(post_ids)).count() if post_ids else 0
    comments = Comment.query.filter(Comment.post_id.in_(post_ids)).count() if post_ids else 0
    milestones = Milestone.query.join(Goal, Milestone.goal_id == Goal.id).filter(Goal.user_id == user_id).all()
    return {'total_practice_hours': round(total,2), 'weekly_practice_hours': round(weekly,2), 'monthly_practice_hours': round(monthly,2), 'most_practiced_skill': max(by_skill, key=by_skill.get) if by_skill else None, 'most_practiced_skill_name': skill_names.get(max(by_skill, key=by_skill.get)) if by_skill else None, 'current_streak': current, 'longest_streak': longest, 'goals_completed': completed, 'active_goals': len(goals)-completed, 'milestones_achieved': sum(1 for m in milestones if m.achieved), 'posts': len(posts), 'likes_received': likes, 'comments_received': comments, 'practice_by_skill': [{'skill': skill_names.get(k, str(k)), 'hours': round(v,2)} for k,v in by_skill.items()]}
