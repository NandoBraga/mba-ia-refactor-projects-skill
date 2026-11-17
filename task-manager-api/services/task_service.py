from datetime import datetime

from sqlalchemy.orm import joinedload

from database import db
from models.category import Category
from models.task import Task
from models.user import User


class ServiceError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


class TaskService:
    VALID_STATUSES = {'pending', 'in_progress', 'done', 'cancelled'}

    def _overdue(self, task):
        if not task.due_date:
            return False
        return task.status not in {'done', 'cancelled'} and task.due_date < datetime.utcnow()

    def _serialize(self, task):
        data = task.to_dict()
        data['overdue'] = self._overdue(task)
        data['user_name'] = task.user.name if task.user else None
        data['category_name'] = task.category.name if task.category else None
        return data

    def list(self):
        tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
        return [self._serialize(task) for task in tasks]

    def get(self, task_id):
        task = db.session.get(Task, task_id)
        if not task:
            raise ServiceError('Task não encontrada', 404)
        return self._serialize(task)

    def create(self, data):
        if not data:
            raise ServiceError('Dados inválidos')
        title = data.get('title')
        if not title:
            raise ServiceError('Título é obrigatório')
        if len(title) < 3:
            raise ServiceError('Título muito curto')
        if len(title) > 200:
            raise ServiceError('Título muito longo')

        status = data.get('status', 'pending')
        priority = data.get('priority', 3)
        if status not in self.VALID_STATUSES:
            raise ServiceError('Status inválido')
        if not isinstance(priority, int) or priority < 1 or priority > 5:
            raise ServiceError('Prioridade deve ser entre 1 e 5')

        user_id = data.get('user_id')
        category_id = data.get('category_id')
        if user_id and not db.session.get(User, user_id):
            raise ServiceError('Usuário não encontrado', 404)
        if category_id and not db.session.get(Category, category_id):
            raise ServiceError('Categoria não encontrada', 404)

        task = Task(
            title=title,
            description=data.get('description', ''),
            status=status,
            priority=priority,
            user_id=user_id,
            category_id=category_id,
        )
        due_date = data.get('due_date')
        if due_date:
            try:
                task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
            except (TypeError, ValueError):
                raise ServiceError('Formato de data inválido. Use YYYY-MM-DD')

        tags = data.get('tags')
        task.tags = ','.join(tags) if isinstance(tags, list) else tags
        db.session.add(task)
        db.session.commit()
        db.session.refresh(task)
        return self._serialize(task)

    def update(self, task_id, data):
        task = db.session.get(Task, task_id)
        if not task:
            raise ServiceError('Task não encontrada', 404)
        if not data:
            raise ServiceError('Dados inválidos')

        if 'title' in data:
            if len(data['title']) < 3:
                raise ServiceError('Título muito curto')
            if len(data['title']) > 200:
                raise ServiceError('Título muito longo')
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            if data['status'] not in self.VALID_STATUSES:
                raise ServiceError('Status inválido')
            task.status = data['status']
        if 'priority' in data:
            if not isinstance(data['priority'], int) or data['priority'] < 1 or data['priority'] > 5:
                raise ServiceError('Prioridade deve ser entre 1 e 5')
            task.priority = data['priority']
        if 'user_id' in data:
            if data['user_id'] and not db.session.get(User, data['user_id']):
                raise ServiceError('Usuário não encontrado', 404)
            task.user_id = data['user_id']
        if 'category_id' in data:
            if data['category_id'] and not db.session.get(Category, data['category_id']):
                raise ServiceError('Categoria não encontrada', 404)
            task.category_id = data['category_id']
        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
                except (TypeError, ValueError):
                    raise ServiceError('Formato de data inválido')
            else:
                task.due_date = None
        if 'tags' in data:
            task.tags = ','.join(data['tags']) if isinstance(data['tags'], list) else data['tags']

        task.updated_at = datetime.utcnow()
        db.session.commit()
        db.session.refresh(task)
        return self._serialize(task)

    def delete(self, task_id):
        task = db.session.get(Task, task_id)
        if not task:
            raise ServiceError('Task não encontrada', 404)
        db.session.delete(task)
        db.session.commit()

    def search(self, query='', status='', priority='', user_id=''):
        tasks = Task.query
        if query:
            tasks = tasks.filter(db.or_(Task.title.like(f'%{query}%'), Task.description.like(f'%{query}%')))
        if status:
            tasks = tasks.filter(Task.status == status)
        if priority:
            tasks = tasks.filter(Task.priority == int(priority))
        if user_id:
            tasks = tasks.filter(Task.user_id == int(user_id))
        return [self._serialize(task) for task in tasks.all()]

    def stats(self):
        tasks = Task.query.all()
        total = len(tasks)
        counts = {status: sum(task.status == status for task in tasks) for status in self.VALID_STATUSES}
        overdue = sum(self._overdue(task) for task in tasks)
        return {
            'total': total,
            'pending': counts['pending'],
            'in_progress': counts['in_progress'],
            'done': counts['done'],
            'cancelled': counts['cancelled'],
            'overdue': overdue,
            'completion_rate': round((counts['done'] / total) * 100, 2) if total else 0,
        }
