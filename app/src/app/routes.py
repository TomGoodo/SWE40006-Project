from flask import Blueprint
from .task_model import Task

task_bp = Blueprint("tasks", __name__)