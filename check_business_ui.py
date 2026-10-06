"""Verify consistent business navigation using a temporary database."""
import gc
import tempfile
from pathlib import Path
import database as db
from ui import MicroInternApp, ACCENT


def run():
    original = db.DB_PATH
    with tempfile.TemporaryDirectory() as folder:
        db.DB_PATH = Path(folder) / 'test.db'
        app = MicroInternApp()
        app.withdraw()
        try:
            db.seed_demo_data()
            app.current_user = db.get_user_by_email('abc@media.com')
            expected = ['dashboard', 'tasks', 'post', 'messages', 'applicants', 'payments', 'profile']
            routes = [('dashboard', app.show_business_dashboard), ('tasks', app.show_business_tasks),
                      ('post', app.show_post_task), ('messages', app.show_messages),
                      ('applicants', app.show_business_inbox), ('payments', app.show_business_invoices),
                      ('profile', app.show_business_profile)]
            for key, route in routes:
                route()
                app.update()
                buttons = app._business_nav_buttons
                assert list(buttons) == expected
                assert buttons[key].cget('bg') == ACCENT
                assert sum(button.cget('bg') == ACCENT for button in buttons.values()) == 1
                sidebar = buttons[key].master
                assert sidebar.cget('bg') == '#1e202b' and sidebar.cget('width') == 204
            task_id = db.list_open_tasks()[0]['id']
            app.show_applicants(task_id)
            app.update()
            assert app._business_nav_buttons['applicants'].cget('bg') == ACCENT
            app._business_nav_buttons['tasks'].invoke()
            app.update()
            assert app._active_screen == 'business_tasks'
            app.change_language('English')
            app.update()
            assert app._active_screen == 'business_tasks'
        finally:
            app.destroy()
            db.DB_PATH = original
            gc.collect()
    print('All business pages share the same sidebar, menu order, and correct active selection.')


if __name__ == '__main__':
    run()
