# MicroIntern

MicroIntern is a Python desktop MVP that connects students with small paid projects posted by businesses.

## Main features
- Student and Business registration/login
- Student skill, availability, minimum budget, experience and rating profiles
- Business task posting
- Public task browsing
- Weighted student-task matching
- Student applications
- Applicant ranking
- Accept/reject workflow
- Task lifecycle: Open -> Assigned -> In Progress -> Completed
- Simulated 10% platform fee
- Student earnings and business/platform analytics
- Business sales dashboard with task payment analytics, recent payments, search, and CSV export
- Student profile and portfolio editor with skill proficiency, resume/avatar paths, and project cards
- Shared dark student sidebar across dashboard, task browsing, task details, applications, and profile
- Responsive task marketplace with getting-started banners, category filters, search, and clickable opportunity cards
- Task details with business contact email, optional deliverables, applicant totals, and the fee/earnings breakdown
- Blue dashboard theme and top-right account dropdown with avatar and logout
- SQLite persistent storage
- Input validation and error handling
- Demo data generator

## Technology
- Python 3.10+
- Tkinter (built into standard Python on most Windows installations)
- SQLite3 (built into Python)
- No external packages required

## How to run
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Run:
   python main.py
4. On first launch you can click **Load Demo Data** on the welcome screen.

## Demo accounts
After loading demo data:
- Student: naro@student.com / student123
- Business: abc@media.com / business123

## Profile photos
Open **Profile** from the sidebar or the top-right account menu. Click **Add photo** or
**Edit photo** to select and preview a PNG or GIF image, then click **Save Changes**.
Saved photos are copied into `profile_photos` beside the database and appear next to
your username in the account menu. Logout is available in that menu.

To check student navigation and photo saving using a temporary database, run
`python check_student_ui.py` on a system with Tkinter available.

Browse Tasks cards use category artwork and company initials. Verification and
business reviews are not recorded by this MVP, so cards show **Unverified** and
**No reviews yet**. Businesses can specify deliverables when posting a task;
older tasks show a prompt to confirm deliverables with the business.

## Submit work and track earnings
Students can also open **My Projects** directly from the sidebar to see all
accepted projects and open their delivery workspace.
Students open **Applications**, select an accepted application, and click
**Open Project / Submit Work**. The workspace shows the brief, deadline,
deliverables, business contact, feedback, and payment status. Attach a file or
provide a project link, add delivery notes, and click **Submit for Review**.
Files are copied into `project_submissions` beside the database.

Businesses select a project in **My Tasks** and click **Review Submission**.
They can save the attachment, open the project link, request changes with
feedback, or approve the work. Approval records one simulated payment, deducts
the 10% platform fee, and updates the student's earnings and completed jobs.
This MVP does not transfer real money. Students can resubmit after changes are
requested. Run `python check_project_workflow.py` for an isolated workflow check.

## In-app messages
Choose **Message Business** on a task or project to discuss the project within
MicroIntern. Both account types have a **Messages** inbox with saved conversations,
timestamps, unread counts, and automatic refresh every three seconds. Project
workspaces also link directly to the conversation. Only the business owning the
task and the student in the conversation can read or send its messages.

Messages currently use the app's SQLite database. Accounts must use the same
database; separate computers do not synchronize automatically. A shared server
is required for messaging across separate installations. No email service is used.
Run `python check_messages.py` for an isolated messaging check.

## Matching algorithm
The app calculates a weighted score:
- Skills: 50%
- Budget: 20%
- Availability: 15%
- Experience: 10%
- Rating: 5%

The score is stored with each application so the business can rank applicants.

## Files
- `main.py` - starts the app
- `database.py` - database schema and queries
- `matching.py` - match-score algorithm
- `security.py` - password hashing/verification
- `ui.py` - Tkinter screens and user workflows

## Suggested final presentation demo
1. Load demo data
2. Log in as a student and browse recommended tasks
3. Apply for a task
4. Log out and log in as the business
5. Open applicants, inspect match scores, and accept one
6. Move the task to In Progress, then Complete it
7. Show the analytics and platform fee calculation
8. Open the business Sales Overview and export completed project payments
9. Sign in as a student to update the profile, skill levels, and portfolio projects

## Important
This is an educational MVP. Payment is simulated; it does not connect to a real payment processor.
