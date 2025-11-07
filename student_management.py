import mysql.connector
from datetime import datetime
from db_config import get_connection

class StudentManagementSystem:
    def __init__(self):
        self.current_professor = None

    # ---------- PROFESSOR AUTHENTICATION ----------
    def authenticate(self):
        print("\n" + "="*50)
        print("     PROFESSOR LOGIN")
        print("="*50)
        
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        max_attempts = 3
        for attempt in range(max_attempts):
            username = input("\nUsername: ").strip()
            password = input("Password: ").strip()

            cur.execute("SELECT * FROM professors WHERE username=%s AND password=%s", (username, password))
            professor = cur.fetchone()

            if professor:
                self.current_professor = professor
                print(f"\n✓ Login successful! Welcome {professor['name']}")
                conn.close()
                return True
            else:
                remaining = max_attempts - attempt - 1
                if remaining > 0:
                    print(f"\n✗ Invalid credentials. {remaining} attempt(s) left.")
                else:
                    print("\n✗ Maximum attempts reached.")
        conn.close()
        return False

    # ---------- CGPA CALCULATION ----------
    def calculate_cgpa(self, student_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT AVG(grade) FROM grades WHERE student_id=%s", (student_id,))
        avg = cur.fetchone()[0]
        avg = round(avg, 2) if avg else 0.0
        cur.execute("UPDATE students SET cgpa=%s WHERE student_id=%s", (avg, student_id))
        conn.commit()
        conn.close()
        return avg

    # ---------- MENU ----------
    def display_menu(self):
        print("\n" + "="*50)
        print("     STUDENT MANAGEMENT SYSTEM")
        print("="*50)
        print("\n1. Register new student")
        print("2. View all students")
        print("3. Search student")
        print("4. Edit student")
        print("5. Delete student")
        print("6. Manage student grades")
        print("7. Display student ranking")
        print("8. General statistics")
        print("9. Logout")
        print("0. Exit")
        print("="*50)

    # ---------- ADD STUDENT ----------
    def add_student(self):
        print("\n--- REGISTER NEW STUDENT ---")
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT MAX(id) FROM students")
        last_id = cur.fetchone()[0]
        new_id = 1 if last_id is None else last_id + 1
        student_id = f"STU{new_id:04d}"

        print(f"\nGenerated ID: {student_id}")
        first_name = input("First Name: ").strip()
        last_name = input("Last Name: ").strip()
        email = input("Email: ").strip()
        phone = input("Phone: ").strip()
        department = input("Department: ").strip()

        cur.execute("""
            INSERT INTO students (student_id, first_name, last_name, email, phone, department, date_registered)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (student_id, first_name, last_name, email, phone, department, datetime.now()))

        conn.commit()
        conn.close()
        print(f"\n✓ Student {first_name} {last_name} registered successfully! (ID: {student_id})")

    # ---------- VIEW ALL STUDENTS ----------
    def display_all_students(self):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM students ORDER BY id")
        students = cur.fetchall()
        conn.close()

        if not students:
            print("\n⚠ No students registered.")
            return

        print("\n" + "="*100)
        print(f"{'ID':<10} {'First Name':<15} {'Last Name':<15} {'Department':<15} {'CGPA':<8} {'Email':<25}")
        print("="*100)
        for s in students:
            print(f"{s['student_id']:<10} {s['first_name']:<15} {s['last_name']:<15} {s['department']:<15} {s['cgpa']:<8} {s['email']:<25}")
        print("="*100)
        print(f"\nTotal: {len(students)} student(s)")

    # ---------- SEARCH STUDENT ----------
    def search_student(self):
        print("\n--- SEARCH STUDENT ---")
        print("1. Search by ID")
        print("2. Search by Name")
        choice = input("\nYour choice: ").strip()
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        if choice == "1":
            sid = input("Student ID: ").strip().upper()
            cur.execute("SELECT * FROM students WHERE student_id=%s", (sid,))
            s = cur.fetchone()
            if s:
                self.display_student_details(s)
            else:
                print(f"\n✗ No student found with ID: {sid}")

        elif choice == "2":
            name = input("Name to search: ").strip()
            cur.execute("SELECT * FROM students WHERE first_name LIKE %s OR last_name LIKE %s", (f"%{name}%", f"%{name}%"))
            found = cur.fetchall()
            if found:
                print(f"\n✓ {len(found)} student(s) found:")
                for s in found:
                    self.display_student_details(s)
            else:
                print(f"\n✗ No student found with name: {name}")
        conn.close()

    # ---------- DISPLAY STUDENT DETAILS ----------
    def display_student_details(self, s):
        print("\n" + "-"*50)
        print(f"ID: {s['student_id']}")
        print(f"Full Name: {s['first_name']} {s['last_name']}")
        print(f"Email: {s['email']}")
        print(f"Phone: {s['phone']}")
        print(f"Department: {s['department']}")
        print(f"CGPA: {s['cgpa']}/10")
        print(f"Registered on: {s['date_registered']}")
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT subject, grade FROM grades WHERE student_id=%s", (s['student_id'],))
        grades = cur.fetchall()
        if grades:
            print("\nGrades:")
            for g in grades:
                print(f"  - {g['subject']}: {g['grade']}/10")
        else:
            print("\nNo grades recorded.")
        conn.close()
        print("-"*50)

    # ---------- EDIT STUDENT ----------
    def edit_student(self):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        sid = input("\nStudent ID to edit: ").strip().upper()
        cur.execute("SELECT * FROM students WHERE student_id=%s", (sid,))
        s = cur.fetchone()

        if not s:
            print("\n✗ No student found.")
            conn.close()
            return

        print(f"\nEditing student: {s['first_name']} {s['last_name']}")
        print("Leave blank to keep current value.")

        first_name = input(f"First Name [{s['first_name']}]: ").strip() or s['first_name']
        last_name = input(f"Last Name [{s['last_name']}]: ").strip() or s['last_name']
        email = input(f"Email [{s['email']}]: ").strip() or s['email']
        phone = input(f"Phone [{s['phone']}]: ").strip() or s['phone']
        department = input(f"Department [{s['department']}]: ").strip() or s['department']

        cur.execute("""
            UPDATE students SET first_name=%s, last_name=%s, email=%s, phone=%s, department=%s WHERE student_id=%s
        """, (first_name, last_name, email, phone, department, sid))
        conn.commit()
        conn.close()
        print("\n✓ Student information updated successfully.")

    # ---------- DELETE STUDENT ----------
    def delete_student(self):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        sid = input("\nStudent ID to delete: ").strip().upper()
        cur.execute("SELECT * FROM students WHERE student_id=%s", (sid,))
        s = cur.fetchone()

        if not s:
            print("\n✗ No student found.")
            conn.close()
            return

        confirm = input(f"\n⚠ Are you sure you want to delete {s['first_name']} {s['last_name']}? (yes/no): ").strip().lower()
        if confirm == "yes":
            cur.execute("DELETE FROM students WHERE student_id=%s", (sid,))
            conn.commit()
            print("\n✓ Student deleted successfully.")
        else:
            print("\n✗ Deletion cancelled.")
        conn.close()

    # ---------- MANAGE GRADES ----------
    def manage_grades(self):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        sid = input("\nStudent ID: ").strip().upper()
        cur.execute("SELECT * FROM students WHERE student_id=%s", (sid,))
        s = cur.fetchone()

        if not s:
            print("\n✗ No student found.")
            conn.close()
            return

        print(f"\nManaging grades for: {s['first_name']} {s['last_name']}")
        print("\n1. Add/Edit grade")
        print("2. Delete grade")
        print("3. Show all grades")

        choice = input("\nYour choice: ").strip()

        if choice == "1":
            subject = input("Subject: ").strip()
            try:
                grade = float(input("Grade (0-10): ").strip())
                if 0 <= grade <= 10:
                    cur.execute("SELECT * FROM grades WHERE student_id=%s AND subject=%s", (sid, subject))
                    exists = cur.fetchone()
                    if exists:
                        cur.execute("UPDATE grades SET grade=%s WHERE id=%s", (grade, exists['id']))
                    else:
                        cur.execute("INSERT INTO grades (student_id, subject, grade) VALUES (%s, %s, %s)", (sid, subject, grade))
                    conn.commit()
                    avg = self.calculate_cgpa(sid)
                    print(f"\n✓ Grade saved! Updated CGPA: {avg}/10")
                else:
                    print("\n✗ Grade must be between 0 and 10.")
            except ValueError:
                print("\n✗ Invalid input.")
        
        elif choice == "2":
            subject = input("Subject to delete: ").strip()
            cur.execute("DELETE FROM grades WHERE student_id=%s AND subject=%s", (sid, subject))
            conn.commit()
            avg = self.calculate_cgpa(sid)
            print(f"\n✓ Grade deleted. Updated CGPA: {avg}/10")

        elif choice == "3":
            cur.execute("SELECT * FROM grades WHERE student_id=%s", (sid,))
            grades = cur.fetchall()
            if grades:
                print("\nGrades:")
                for g in grades:
                    print(f"  - {g['subject']}: {g['grade']}/10")
                print(f"\nCGPA: {s['cgpa']}/10")
            else:
                print("\n⚠ No grades recorded.")
        conn.close()

    # ---------- RANKING ----------
    def display_ranking(self):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM students ORDER BY cgpa DESC")
        students = cur.fetchall()
        conn.close()

        if not students:
            print("\n⚠ No students registered.")
            return

        print("\n" + "="*80)
        print("     STUDENT RANKING (BY CGPA)")
        print("="*80)
        print(f"{'Rank':<6} {'ID':<10} {'Name':<25} {'Department':<20} {'CGPA':<8}")
        print("="*80)

        for rank, s in enumerate(students, 1):
            fullname = f"{s['first_name']} {s['last_name']}"
            print(f"{rank:<6} {s['student_id']:<10} {fullname:<25} {s['department']:<20} {s['cgpa']:<8}")
        print("="*80)

    # ---------- STATISTICS ----------
    def display_statistics(self):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) as total FROM students")
        total = cur.fetchone()['total']
        cur.execute("SELECT COUNT(DISTINCT student_id) as with_grades FROM grades")
        with_grades = cur.fetchone()['with_grades']
        cur.execute("SELECT AVG(cgpa) as avg_cgpa, MAX(cgpa) as max_cgpa, MIN(cgpa) as min_cgpa FROM students")
        stats = cur.fetchone()

        print("\n" + "="*50)
        print("     GENERAL STATISTICS")
        print("="*50)
        print(f"Total students: {total}")
        print(f"Students with grades: {with_grades}")
        if stats['avg_cgpa'] is not None:
            print(f"\nAverage CGPA: {stats['avg_cgpa']:.2f}/10")
            print(f"Max CGPA: {stats['max_cgpa']:.2f}/10")
            print(f"Min CGPA: {stats['min_cgpa']:.2f}/10")
        else:
            print("\n⚠ No grades recorded yet.")
        print("="*50)
        conn.close()

    # ---------- MAIN LOOP ----------
    def run(self):
        print("\n" + "*"*50)
        print("   WELCOME TO STUDENT MANAGEMENT SYSTEM")
        print("*"*50)

        if not self.authenticate():
            print("\n✗ Authentication failed. Exiting system.")
            return

        while True:
            self.display_menu()
            choice = input("\nYour choice: ").strip()

            if choice == "1":
                self.add_student()
            elif choice == "2":
                self.display_all_students()
            elif choice == "3":
                self.search_student()
            elif choice == "4":
                self.edit_student()
            elif choice == "5":
                self.delete_student()
            elif choice == "6":
                self.manage_grades()
            elif choice == "7":
                self.display_ranking()
            elif choice == "8":
                self.display_statistics()
            elif choice == "9":
                print(f"\n Logging out, {self.current_professor['username']}!")
                if not self.authenticate():
                    break
            elif choice == "0":
                print("\n Thank you for using the system. Goodbye!")
                break
            else:
                print("\n✗ Invalid choice. Try again.")

            input("\nPress Enter to continue...")

if __name__ == "__main__":
    system = StudentManagementSystem()
    system.run()
