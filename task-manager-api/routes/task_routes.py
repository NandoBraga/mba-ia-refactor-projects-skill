from flask import Blueprint, request, jsonify

from services.task_service import TaskService, ServiceError


task_bp = Blueprint('tasks', __name__)
task_service = TaskService()


def _handle_service(call, *args, **kwargs):
    try:
        return call(*args, **kwargs)
    except ServiceError as error:
        return jsonify({'error': str(error)}), error.status
    except Exception:
        return jsonify({'error': 'Erro interno'}), 500


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    return _handle_service(task_service.list)


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    result = _handle_service(task_service.get, task_id)
    if isinstance(result, tuple):
        return result
    return jsonify(result), 200


@task_bp.route('/tasks', methods=['POST'])
def create_task():
    result = _handle_service(task_service.create, request.get_json(silent=True))
    if isinstance(result, tuple):
        return result
    return jsonify(result), 201


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    result = _handle_service(task_service.update, task_id, request.get_json(silent=True))
    if isinstance(result, tuple):
        return result
    return jsonify(result), 200


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    result = _handle_service(task_service.delete, task_id)
    if isinstance(result, tuple):
        return result
    return jsonify({'message': 'Task deletada com sucesso'}), 200


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    result = _handle_service(
        task_service.search,
        request.args.get('q', ''),
        request.args.get('status', ''),
        request.args.get('priority', ''),
        request.args.get('user_id', ''),
    )
    if isinstance(result, tuple):
        return result
    return jsonify(result), 200


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    result = _handle_service(task_service.stats)
    if isinstance(result, tuple):
        return result
    return jsonify(result), 200
