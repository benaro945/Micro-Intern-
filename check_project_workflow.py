import tempfile, gc
from pathlib import Path
import database as db
from ui import MicroInternApp
with tempfile.TemporaryDirectory() as folder:
 db.DB_PATH=Path(folder)/'test.db'
 app=MicroInternApp(); app.withdraw()
 db.seed_demo_data()
 student=db.get_user_by_email('naro@student.com')
 business=db.get_user_by_email('abc@media.com')
 task=db.list_open_tasks()[0]
 db.apply_to_task(task['id'],student['id'],80)
 application=db.list_student_applications(student['id'])[0]
 db.decide_application(application['id'],True)
 app.current_user=student
 app.show_student_applications(); app.update()
 app.show_project_workspace(task['id']); app.update()
 try:
  db.submit_project(task['id'],business['id'],'','https://example.com','')
  raise AssertionError('Unauthorized submission accepted')
 except ValueError: pass
 db.submit_project(task['id'],student['id'],'First delivery','https://example.com','')
 app.show_project_workspace(task['id']); app.update()
 app.current_user=business
 app.show_project_workspace(task['id']); app.update()
 db.review_project(task['id'],business['id'],False,'Please update the title')
 assert db.project_payment(task['id']) is None
 app.current_user=student
 app.show_project_workspace(task['id']); app.update()
 db.submit_project(task['id'],student['id'],'Revised delivery','https://example.com','')
 db.review_project(task['id'],business['id'],True,'Approved')
 assert db.project_payment(task['id'])['student_earnings']==round(task['budget']*.9,2)
 assert db.get_student(student['id'])['jobs_completed']==1
 try:
  db.review_project(task['id'],business['id'],True,'Again')
  raise AssertionError('Duplicate payment allowed')
 except ValueError: pass
 app.show_project_workspace(task['id']); app.update()
 app.destroy(); gc.collect()
print('Project workspace, submission, revision, approval, authorization and duplicate payment checks passed.')
