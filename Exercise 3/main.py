import os
import json
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog

# the marks file needs to be in the same folder as this program
folder = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = os.path.join(folder, "studentMarks.json")

# pastel colour theme
PAGE_COLOUR = "#fff5f8"      # page background
HEADER_COLOUR = "#f6b8c8"    # header, table heading, form buttons
SIDE_COLOUR = "#fde6ec"      # left menu panel
BUTTON_COLOUR = "#f9d3dd"    # menu buttons
TEXT_COLOUR = "#5b3b46"      # dark plum, easier to read than black
WHITE = "#ffffff"

# each grade gets its own pastel row colour in the table
GRADE_COLOURS = {
    "A": "#d9f2e4",   # mint
    "B": "#dcebfa",   # light blue
    "C": "#fff3cc",   # light yellow
    "D": "#ffe3d1",   # peach
    "F": "#f8d4dc",   # pink
}

# all the students live in this list
# each student is a dictionary like:
# {"number": "1345", "name": "John Curry", "coursework": [8, 15, 7], "exam": 45}
students = []

# reading and saving the file

def load_students():
    students.clear()
    try:
        with open(FILE_NAME, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        return False

    for s in data["students"]:
        student = {
            "number": s["number"],
            "name": s["name"],
            "coursework": s["coursework"],
            "exam": s["exam"],
        }
        students.append(student)

    return True

def save_students():
    # Save the updated student records
    data = {
        "students": students
    }

    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4)

# calculations

def get_coursework_total(student):
    return sum(student["coursework"])        # out of 60

def get_total_mark(student):
    return get_coursework_total(student) + student["exam"]    # out of 160

def get_percentage(student):
    return get_total_mark(student) / 160 * 100

def grade_for(percentage):
    if percentage >= 70:
        return "A"
    elif percentage >= 60:
        return "B"
    elif percentage >= 50:
        return "C"
    elif percentage >= 40:
        return "D"
    else:
        return "F"

def get_grade(student):
    return grade_for(get_percentage(student))

def get_average():
    total = 0
    for s in students:
        total = total + get_percentage(s)
    return total / len(students)


# helper functions 

def find_student(search_text):
    # looks for a match on student number or name (ignores capital letters)
    search_text = search_text.strip().lower()
    for s in students:
        if s["number"].lower() == search_text or s["name"].lower() == search_text:
            return s
    return None

def students_with_total(total):
    # gets every student with this exact total, in case two students tie
    matches = []
    for s in students:
        if get_total_mark(s) == total:
            matches.append(s)
    return matches

def make_summary():
    # the text shown under the table for options 1 and 5
    if len(students) == 0:
        return ""

    best = max(students, key=get_total_mark)
    worst = min(students, key=get_total_mark)
    average = get_average()

    # count how many students passed (40% or more, so anything except an F)
    passed = 0
    for s in students:
        if get_percentage(s) >= 40:
            passed = passed + 1
    pass_rate = passed / len(students) * 100

    return (f"TOTAL STUDENTS: {len(students)}\n"
            f"CLASS AVERAGE: {average:.2f}%  (Grade {grade_for(average)})\n"
            f"HIGHEST SCORE: {get_percentage(best):.2f}%  -  {best['name']}\n"
            f"LOWEST SCORE: {get_percentage(worst):.2f}%  -  {worst['name']}\n"
            f"PASS RATE: {pass_rate:.0f}%  ({passed} of {len(students)} passed)")

def read_one_mark(text, maximum):
    # turns the typed text into a whole number between 0 and maximum
    # gives back None if it isn't a valid mark
    try:
        mark = int(text)
    except ValueError:
        return None
    if mark < 0 or mark > maximum:
        return None
    return mark

def read_marks(entries):
    # reads the four mark boxes on the add form
    # gives back a list [c1, c2, c3, exam] or None if something is wrong
    c1 = read_one_mark(entries["c1"].get(), 20)
    c2 = read_one_mark(entries["c2"].get(), 20)
    c3 = read_one_mark(entries["c3"].get(), 20)
    exam = read_one_mark(entries["exam"].get(), 100)
    if c1 is None or c2 is None or c3 is None or exam is None:
        return None
    return [c1, c2, c3, exam]

MARKS_ERROR = "Marks must be whole numbers (coursework 0-20, exam 0-100)."

# window layout 

root = tk.Tk()
root.title("Student Manager - Academic System")
# make the window fit the screen (some laptop screens are quite short)
screen_height = root.winfo_screenheight()
root.geometry(f"1150x{min(840, screen_height - 80)}")
try:
    root.state("zoomed")        # start maximised on Windows
except tk.TclError:
    pass                        # some systems don't support this, so just skip it
root.configure(bg=PAGE_COLOUR)

# style for the table
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background=WHITE, fieldbackground=WHITE,
                foreground=TEXT_COLOUR, rowheight=30, font=("Segoe UI", 10))
style.configure("Treeview.Heading", background=HEADER_COLOUR,
                foreground=TEXT_COLOUR, font=("Segoe UI", 10, "bold"),
                relief="flat", padding=6)
style.map("Treeview.Heading", background=[("active", HEADER_COLOUR)])

# header at the top
header = tk.Frame(root, bg=HEADER_COLOUR, padx=25, pady=8)
header.pack(fill="x", padx=15, pady=(15, 8))
tk.Label(header, text="STUDENT MANAGER", bg=HEADER_COLOUR, fg=TEXT_COLOUR,
         font=("Segoe UI", 24, "bold")).pack(anchor="w")
tk.Label(header, text="Academic Records Management System", bg=HEADER_COLOUR,
         fg=TEXT_COLOUR, font=("Segoe UI", 11)).pack(anchor="w")

# bar at the very bottom for the exit button
bottom_bar = tk.Frame(root, bg=PAGE_COLOUR)
bottom_bar.pack(side="bottom", fill="x", pady=(0, 12))

# left side menu
side_frame = tk.Frame(root, bg=SIDE_COLOUR, padx=15, pady=10)
side_frame.pack(side="left", fill="y", padx=(15, 8), pady=(0, 15))

# main area on the right
main_frame = tk.Frame(root, bg=WHITE, padx=20, pady=15)
main_frame.pack(side="right", fill="both", expand=True, padx=(8, 15), pady=(0, 15))

# title row 
top_bar = tk.Frame(main_frame, bg=WHITE)
top_bar.pack(fill="x")

tk.Frame(top_bar, bg=HEADER_COLOUR, width=6, height=28).pack(side="left", padx=(0, 10))
title_label = tk.Label(top_bar, text="", bg=WHITE, fg=TEXT_COLOUR,
                       font=("Segoe UI", 16, "bold"))
title_label.pack(side="left")
message_label = tk.Label(top_bar, text="", bg=WHITE, fg=TEXT_COLOUR,
                         font=("Segoe UI", 10, "italic"), wraplength=420,
                         justify="right")
message_label.pack(side="right")

# the form area stays empty unless an option needs typing
form_frame = tk.Frame(main_frame, bg=WHITE)
form_frame.pack(fill="x", pady=(10, 0))

# summary text at the bottom 
summary_label = tk.Label(main_frame, text="", bg=WHITE, fg=TEXT_COLOUR,
                         font=("Segoe UI", 11, "bold"), justify="left")
summary_label.pack(side="bottom", anchor="w", pady=(10, 0))

# the table
table_frame = tk.Frame(main_frame, bg=WHITE)
table_frame.pack(fill="both", expand=True, pady=(10, 0))

columns = ("number", "name", "coursework", "exam", "total", "percentage", "grade")
headings = ("STUDENT NO.", "STUDENT NAME", "COURSEWORK", "EXAM", "TOTAL",
            "PERCENTAGE", "GRADE")
widths = (100, 200, 110, 100, 100, 110, 70)

table = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="none")
for i in range(len(columns)):
    table.heading(columns[i], text=headings[i])
    if columns[i] == "name":
        table.column(columns[i], width=widths[i], anchor="w")
    else:
        table.column(columns[i], width=widths[i], anchor="center")

# set up a background colour for each grade
for grade, colour in GRADE_COLOURS.items():
    table.tag_configure(grade, background=colour)

table_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
table.configure(yscrollcommand=table_scroll.set)
table_scroll.pack(side="right", fill="y")
table.pack(side="left", fill="both", expand=True)

# functions that update the screen

def show_table(student_list, title, message="", summary=""):
    # empty the table first
    for row in table.get_children():
        table.delete(row)

    # then add one row for each student
    for s in student_list:
        grade = get_grade(s)
        table.insert("", tk.END, tags=(grade,), values=(
            s["number"],
            s["name"],
            f"{get_coursework_total(s)} / 60",
            f"{s['exam']} / 100",
            f"{get_total_mark(s)} / 160",
            f"{get_percentage(s):.2f}%",
            grade,
        ))

    title_label.config(text=title)
    message_label.config(text=message)
    summary_label.config(text=summary)

def show_message(text):
    message_label.config(text=text)

def clear_form():
    for widget in form_frame.winfo_children():
        widget.destroy()

def make_button(parent, text, command, colour):
    return tk.Button(parent, text=text, command=command, bg=colour,
                     fg=TEXT_COLOUR, activebackground=HEADER_COLOUR,
                     activeforeground=TEXT_COLOUR, relief="flat",
                     font=("Segoe UI", 10, "bold"), cursor="hand2")

def make_form():
    # builds the six input boxes for the add form, in two rows of three
    fields = [
        ("number", "Student number", 0, 0),
        ("name", "Student name", 0, 2),
        ("exam", "Exam mark (out of 100)", 0, 4),
        ("c1", "Coursework 1 (out of 20)", 1, 0),
        ("c2", "Coursework 2 (out of 20)", 1, 2),
        ("c3", "Coursework 3 (out of 20)", 1, 4),
    ]
    entries = {}
    for key, label_text, row, column in fields:
        tk.Label(form_frame, text=label_text, bg=WHITE, fg=TEXT_COLOUR,
                 font=("Segoe UI", 9)).grid(row=row, column=column,
                                            padx=(0, 5), pady=4, sticky="e")
        box = tk.Entry(form_frame, width=14, font=("Segoe UI", 10))
        box.grid(row=row, column=column + 1, padx=(0, 15), pady=4)
        entries[key] = box

    return entries

# menu options

# option 1
def view_all():
    clear_form()
    if len(students) == 0:
        show_table([], "STUDENT LIST", "There are no student records.")
        return
    show_table(students, "STUDENT LIST", "", make_summary())

# option 2
def view_individual():
    clear_form()
    text = simpledialog.askstring("Individual Student",
                                  "Enter student name or student number:")
    if text is None:            # they pressed Cancel
        return

    student = find_student(text)
    if student is None:
        show_table([], "INDIVIDUAL STUDENT RECORD",
                   "No student found with that name or number.")
    else:
        show_table([student], "INDIVIDUAL STUDENT RECORD")

# option 3
def show_highest():
    clear_form()
    if len(students) == 0:
        show_table([], "HIGHEST TOTAL SCORE", "There are no student records.")
        return
    best = max(students, key=get_total_mark)
    show_table(students_with_total(get_total_mark(best)), "HIGHEST TOTAL SCORE")

# option 4
def show_lowest():
    clear_form()
    if len(students) == 0:
        show_table([], "LOWEST TOTAL SCORE", "There are no student records.")
        return
    worst = min(students, key=get_total_mark)
    show_table(students_with_total(get_total_mark(worst)), "LOWEST TOTAL SCORE")

# option 5 
def sort_students(descending):
    clear_form()
    sorted_list = sorted(students, key=get_percentage, reverse=descending)
    if descending:
        title = "SORTED: HIGHEST TO LOWEST"
    else:
        title = "SORTED: LOWEST TO HIGHEST"
    show_table(sorted_list, title, "Sorted by overall percentage.", make_summary())

def sort_ascending():
    sort_students(False)

def sort_descending():
    sort_students(True)

# option 6
def add_student():
    clear_form()
    entries = make_form()
    show_table(students, "ADD A STUDENT", "Fill in all the boxes and press Add Student.")

    def save_new():
        number = entries["number"].get().strip()
        name = entries["name"].get().strip()

        if number == "" or name == "":
            show_message("Please enter a student number and a name.")
            return
        if "," in number or "," in name:
            show_message("Commas are not allowed in the number or name.")
            return
        for s in students:
            if s["number"] == number:
                show_message("A student with that number already exists.")
                return

        marks = read_marks(entries)
        if marks is None:
            show_message(MARKS_ERROR)
            return

        new_student = {
            "number": number,
            "name": name,
            "coursework": [marks[0], marks[1], marks[2]],
            "exam": marks[3],
        }
        students.append(new_student)
        save_students()

        # empty the boxes so another student can be added
        for box in entries.values():
            box.delete(0, tk.END)
        show_table(students, "ADD A STUDENT", f"Added {name} and saved to the file.")

    make_button(form_frame, "Add Student", save_new,
                HEADER_COLOUR).grid(row=2, column=0, columnspan=2,
                                    pady=(8, 0), sticky="w", ipadx=10)

# option 7
def delete_student():
    clear_form()
    text = simpledialog.askstring("Delete Student",
                                  "Enter the name or number of the student to delete:")
    if text is None:
        return

    student = find_student(text)
    if student is None:
        show_table(students, "STUDENT LIST",
                   "No student found with that name or number.", make_summary())
        return

    students.remove(student)
    save_students()
    show_table(students, "STUDENT LIST",
               f"Deleted {student['name']} ({student['number']}) and saved to the file.",
               make_summary())


# option 8 (step 1: find the student)
def update_student():
    clear_form()
    text = simpledialog.askstring("Update Student",
                                  "Enter the name or number of the student to update:")
    if text is None:
        return

    student = find_student(text)
    if student is None:
        show_table(students, "STUDENT LIST",
                   "No student found with that name or number.", make_summary())
    else:
        show_update_menu(student)


# option 8 (step 2: sub menu to pick which item to change, then save it)
def show_update_menu(student):
    clear_form()
    show_table([student], "UPDATE A STUDENT", f"Editing {student['name']}.")

    items = [
        ("name", "Name"),
        ("number", "Student number"),
        ("c1", "Coursework 1"),
        ("c2", "Coursework 2"),
        ("c3", "Coursework 3"),
        ("exam", "Exam mark"),
    ]
    choice = tk.StringVar(value="name")      # remembers which radio button is picked

    tk.Label(form_frame, text="Which item do you want to update?", bg=WHITE,
             fg=TEXT_COLOUR, font=("Segoe UI", 10, "bold")).grid(
                 row=0, column=0, columnspan=6, sticky="w", pady=(0, 4))

    # one radio button for each item
    column = 0
    for key, label_text in items:
        tk.Radiobutton(form_frame, text=label_text, variable=choice, value=key,
                       bg=WHITE, fg=TEXT_COLOUR, activebackground=WHITE,
                       font=("Segoe UI", 10)).grid(row=1, column=column,
                                                   padx=(0, 10), sticky="w")
        column = column + 1

    tk.Label(form_frame, text="New value:", bg=WHITE, fg=TEXT_COLOUR,
             font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", pady=(10, 0))
    new_value_box = tk.Entry(form_frame, width=24, font=("Segoe UI", 10))
    new_value_box.grid(row=2, column=1, columnspan=2, padx=5, pady=(10, 0))

    def save_update():
        item = choice.get()
        value = new_value_box.get().strip()

        if value == "":
            show_message("Please type the new value.")
            return

        if item == "name":
            if "," in value:
                show_message("Commas are not allowed in the name.")
                return
            student["name"] = value

        elif item == "number":
            if "," in value:
                show_message("Commas are not allowed in the student number.")
                return
            for s in students:
                if s["number"] == value and s is not student:
                    show_message("Another student already has that number.")
                    return
            student["number"] = value

        elif item == "exam":
            mark = read_one_mark(value, 100)
            if mark is None:
                show_message("Exam mark must be a whole number from 0 to 100.")
                return
            student["exam"] = mark

        else:
            # item is "c1", "c2" or "c3", so the second letter tells us which one
            mark = read_one_mark(value, 20)
            if mark is None:
                show_message("Coursework mark must be a whole number from 0 to 20.")
                return
            position = int(item[1]) - 1        # "c1" -> 0, "c2" -> 1, "c3" -> 2
            student["coursework"][position] = mark

        save_students()
        new_value_box.delete(0, tk.END)
        show_table([student], "UPDATE A STUDENT",
                   f"Updated {student['name']} and saved to the file.")

    make_button(form_frame, "Update", save_update,
                HEADER_COLOUR).grid(row=2, column=3, padx=5, pady=(10, 0), ipadx=10)

# menu buttons

def add_menu_title(text):
    tk.Label(side_frame, text=text, bg=SIDE_COLOUR, fg=TEXT_COLOUR,
             font=("Segoe UI", 11, "bold")).pack(pady=(12, 4))

def add_menu_button(text, command):
    button = make_button(side_frame, text, command, BUTTON_COLOUR)
    button.config(width=24, anchor="w", padx=12, pady=4)
    button.pack(pady=2)

add_menu_title("NAVIGATION")
add_menu_button("All Student Records", view_all)
add_menu_button("Individual Student Record", view_individual)
add_menu_button("Highest Total Score", show_highest)
add_menu_button("Lowest Total Score", show_lowest)

add_menu_title("SORT RECORDS")
add_menu_button("Ascending Order", sort_ascending)
add_menu_button("Descending Order", sort_descending)

add_menu_title("MANAGE STUDENTS")
add_menu_button("Add Student Record", add_student)
add_menu_button("Delete Student Record", delete_student)
add_menu_button("Update Student Record", update_student)

# exit button
exit_button = make_button(bottom_bar, "EXIT APPLICATION", root.destroy, BUTTON_COLOUR)
exit_button.config(padx=25, pady=10)
exit_button.pack()

# start the program

if load_students():
    view_all()
    show_message(f"Loaded {len(students)} students from studentMarks.json")
else:
    show_table([], "STUDENT LIST",
               "Could not find studentMarks.json. Put it in the same folder as this program.")

root.mainloop()
