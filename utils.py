import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))

def validate_username(username: str) -> bool:
    if len(username) < 3 or len(username) > 80:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_]+$', username))

def hash_password(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def format_date(dt: Optional[datetime]) -> str:
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M")

def is_overdue(task: Dict) -> bool:
    if task.get('due_date') is None:
        return False
    if task.get('status') == 'completed':
        return False
    return datetime.utcnow() > task['due_date']

def calculate_completion_percentage(tasks: List[Dict]) -> float:
    if not tasks:
        return 0.0
    completed = sum(1 for t in tasks if t.get('status') == 'completed')
    return (completed / len(tasks)) * 100

def filter_tasks_by_status(tasks: List[Dict], status: str) -> List[Dict]:
    return [t for t in tasks if t.get('status') == status]

def filter_tasks_by_priority(tasks: List[Dict], priority: str) -> List[Dict]:
    return [t for t in tasks if t.get('priority') == priority]

def sort_tasks_by_due_date(tasks: List[Dict]) -> List[Dict]:
    return sorted(tasks, key=lambda x: x.get('due_date') or datetime.max)

def sort_tasks_by_priority(tasks: List[Dict]) -> List[Dict]:
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    return sorted(tasks, key=lambda x: priority_order.get(x.get('priority'), 3))

def group_tasks_by_status(tasks: List[Dict]) -> Dict[str, List[Dict]]:
    groups = {}
    for task in tasks:
        status = task.get('status', 'unknown')
        if status not in groups:
            groups[status] = []
        groups[status].append(task)
    return groups

def get_task_summary(tasks: List[Dict]) -> Dict[str, Any]:
    total = len(tasks)
    completed = len([t for t in tasks if t.get('status') == 'completed'])
    pending = len([t for t in tasks if t.get('status') == 'pending'])
    in_progress = len([t for t in tasks if t.get('status') == 'in_progress'])
    return {
        'total': total,
        'completed': completed,
        'pending': pending,
        'in_progress': in_progress,
        'completion_rate': (completed / total * 100) if total > 0 else 0
    }

def paginate(items: List[Any], page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        'items': items[start:end],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page if total > 0 else 0
    }

def truncate_string(s: str, max_len: int = 50) -> str:
    if len(s) <= max_len:
        return s
    return s[:max_len-3] + '...'

def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    if b == 0:
        return default
    return a / b

def days_between(date1: datetime, date2: datetime) -> int:
    return abs((date2 - date1).days)

def add_days(date: datetime, days: int) -> datetime:
    return date + timedelta(days=days)

def get_week_range(date: datetime) -> tuple:
    start = date - timedelta(days=date.weekday())
    end = start + timedelta(days=6)
    return start, end

def is_weekend(date: datetime) -> bool:
    return date.weekday() >= 5

def get_next_weekday(date: datetime) -> datetime:
    next_day = date + timedelta(days=1)
    while next_day.weekday() >= 5:
        next_day += timedelta(days=1)
    return next_day

def parse_date(date_str: str) -> Optional[datetime]:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

def format_duration(minutes: int) -> str:
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0:
        return f"{hours}h {mins}m"
    return f"{mins}m"

def get_priority_color(priority: str) -> str:
    colors = {'high': 'red', 'medium': 'orange', 'low': 'green'}
    return colors.get(priority, 'gray')

def get_status_color(status: str) -> str:
    colors = {'completed': 'green', 'in_progress': 'blue', 'pending': 'gray'}
    return colors.get(status, 'gray')

def validate_task_data(data: Dict) -> List[str]:
    errors = []
    if not data.get('title'):
        errors.append("Title is required")
    if len(data.get('title', '')) > 200:
        errors.append("Title too long")
    if data.get('status') not in ['pending', 'in_progress', 'completed']:
        errors.append("Invalid status")
    if data.get('priority') not in ['high', 'medium', 'low']:
        errors.append("Invalid priority")
    return errors

def merge_dicts(dicts: List[Dict]) -> Dict:
    result = {}
    for d in dicts:
        result.update(d)
    return result

def flatten_list(nested: List[List[Any]]) -> List[Any]:
    return [item for sublist in nested for item in sublist]

def chunk_list(lst: List[Any], size: int) -> List[List[Any]]:
    return [lst[i:i+size] for i in range(0, len(lst), size)]

def unique_by_key(items: List[Dict], key: str) -> List[Dict]:
    seen = set()
    result = []
    for item in items:
        k = item.get(key)
        if k not in seen:
            seen.add(k)
            result.append(item)
    return result

def sum_by_key(items: List[Dict], key: str) -> float:
    return sum(item.get(key, 0) for item in items)

def average_by_key(items: List[Dict], key: str) -> float:
    if not items:
        return 0.0
    return sum_by_key(items, key) / len(items)

def min_by_key(items: List[Dict], key: str):
    return min(items, key=lambda x: x.get(key, float('inf'))) if items else None

def max_by_key(items: List[Dict], key: str):
    return max(items, key=lambda x: x.get(key, float('-inf'))) if items else None

def sort_by_key(items: List[Dict], key: str, reverse: bool = False) -> List[Dict]:
    return sorted(items, key=lambda x: x.get(key, 0), reverse=reverse)

def filter_by_key(items: List[Dict], key: str, value: Any) -> List[Dict]:
    return [item for item in items if item.get(key) == value]

def count_by_key(items: List[Dict], key: str) -> Dict:
    counts = {}
    for item in items:
        k = item.get(key)
        counts[k] = counts.get(k, 0) + 1
    return counts
