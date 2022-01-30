from gid_tasks.project_info.project import Project
from gid_tasks.hackler.doc_hackler import todo_task
from gid_tasks.hackler.imports_cleaner import clean_imports_task
from rich.console import Console as RichConsole
from invoke import Collection, task, Context, context
import pp


doc_collection = Collection()
doc_collection.add_task(todo_task)
doc_collection.name = "doc"


clean_collection = Collection()
clean_collection.add_task(clean_imports_task)
clean_collection.name = "clean"


update_collection = Collection()
update_collection.name = "update"


@task()
def new_version_patch(c):
    project: Project = c.project
    project.set_version(project.version.increment_patch())


update_collection.add_task(new_version_patch)


@task()
def new_version_minor(c):
    project: Project = c.project
    project.set_version(project.version.increment_minor())


update_collection.add_task(new_version_minor)


@task()
def new_version_major(c):
    project: Project = c.project
    project.set_version(project.version.increment_major())


update_collection.add_task(new_version_major)
