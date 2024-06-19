import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3

days = 5
periods = 6
recess_break_aft = 3  # recess after 3rd Period
section = None
butt_grid = []

period_names = list(map(lambda x: 'Period ' + str(x), range(1, 6 + 1)))
day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

def automatic_schedule():
    cursor = conn.execute("SELECT SUBCODE, FACULTY.INI FROM SUBJECTS, FACULTY WHERE FACULTY.SUBCODE1=SUBJECTS.SUBCODE OR FACULTY.SUBCODE2=SUBJECTS.SUBCODE")
    subject_teacher_pairs = [(row[0], row[1]) for row in cursor]

    for day in range(days):
        for period in range(periods):
            if period < recess_break_aft:
                frame = first_half
            else:
                frame = second_half

            if butt_grid[day][period]['text'] != 'Hello World!':
                continue

            for subject, teacher in subject_teacher_pairs:
                if teacher_is_available(teacher, day, period):
                    butt_grid[day][period]['text'] = f'{subject}\n{teacher}'
                    update_database(day, period, subject, teacher)
                    break
            else:
                butt_grid[day][period]['text'] = 'No Class'

def teacher_is_available(teacher, day, period):
    return True  # You need to implement this function based on your constraints

def update_database(day, period, subject, teacher):
    conn.execute(f"REPLACE INTO SCHEDULE (ID, DAYID, PERIODID, SUBCODE, SECTION, FINI) VALUES \
        ('{section+str((day*periods)+period)}', {day}, {period}, '{subject}', '{section}', '{teacher}')")
    conn.commit()

def update_p(d, p, tree, parent):
    try:
        if len(tree.selection()) > 1:
            messagebox.showerror("Bad Select", "Select one subject at a time!")
            parent.destroy()
            return
        row = tree.item(tree.selection()[0])['values']
        if row[0] == 'NULL' and row[1] == 'NULL':
            conn.execute(f"DELETE FROM SCHEDULE WHERE ID='{section+str((d*periods)+p)}'")
            conn.commit()
            update_table()
            parent.destroy()
            return

        conn.commit()
        conn.execute(f"REPLACE INTO SCHEDULE (ID, DAYID, PERIODID, SUBCODE, SECTION, FINI) VALUES \
            ('{section+str((d*periods)+p)}', {d}, {p}, '{row[1]}', '{section}', '{row[0]}')")
        conn.commit()
        update_table()

    except IndexError:
        messagebox.showerror("Bad Select", "Please select a subject from the list!")
        parent.destroy()
        return

    parent.destroy()

def process_button(d, p):
    add_p = tk.Tk()
    add_p.title('Schedule Period')

    tk.Label(
        add_p,
        text='Select Subject',
        font=('Consolas', 12, 'bold')
    ).pack()

    tk.Label(
        add_p,
        text=f'Day: {day_names[d]}',
        font=('Consolas', 12)
    ).pack()

    tk.Label(
        add_p,
        text=f'Period: {p+1}',
        font=('Consolas', 12)
    ).pack()

    tree = ttk.Treeview(add_p)
    tree['columns'] = ('one', 'two')
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("one", width=70, stretch=tk.NO)
    tree.column("two", width=80, stretch=tk.NO)
    tree.heading('#0', text="")
    tree.heading('one', text="Faculty")
    tree.heading('two', text="Subject Code")

    cursor = conn.execute("SELECT FACULTY.INI, FACULTY.SUBCODE1, FACULTY.SUBCODE2, SUBJECTS.SUBCODE\
        FROM FACULTY, SUBJECTS\
        WHERE FACULTY.SUBCODE1=SUBJECTS.SUBCODE OR FACULTY.SUBCODE2=SUBJECTS.SUBCODE")
    for row in cursor:
        tree.insert(
            "",
            0,
            values=(row[0], row[-1])
        )
    tree.insert("", 0, value=('NULL', 'NULL'))
    tree.pack(pady=10, padx=30)

    tk.Button(
        add_p,
        text="OK",
        padx=15,
        command=lambda x=d, y=p, z=tree, d=add_p: update_p(x, y, z, d)
    ).pack(pady=20)

    add_p.mainloop()

def select_sec():
    global section
    section = str(combo1.get())
    update_table()

def update_table():
    for i in range(days):
        for j in range(periods):
            cursor = conn.execute(f"SELECT SUBCODE, FINI FROM SCHEDULE\
                WHERE DAYID={i} AND PERIODID={j} AND SECTION='{section}'")
            cursor = list(cursor)
            if len(cursor) != 0:
                butt_grid[i][j]['text'] = f'{cursor[0][0]}\n{cursor[0][1]}'
                butt_grid[i][j].update()
            else:
                butt_grid[i][j]['text'] = "No Class"
                butt_grid[i][j].update()

conn = sqlite3.connect(r'files/timetable.db')

conn.execute('CREATE TABLE IF NOT EXISTS SCHEDULE\
(ID CHAR(10) NOT NULL PRIMARY KEY,\
DAYID INT NOT NULL,\
PERIODID INT NOT NULL,\
SUBCODE CHAR(10) NOT NULL,\
SECTION CHAR(5) NOT NULL,\
FINI CHAR(10) NOT NULL)')

tt = tk.Tk()
tt.title('Scheduler')

title_lab = tk.Label(
    tt,
    text='T  I  M  E  T  A  B  L  E',
    font=('Consolas', 20, 'bold'),
    pady=5
)
title_lab.pack()

table = tk.Frame(tt)
table.pack()

first_half = tk.Frame(table)
first_half.pack(side='left')

recess_frame = tk.Frame(table)
recess_frame.pack(side='left')

second_half = tk.Frame(table)
second_half.pack(side='left')

recess = tk.Label(
    recess_frame,
    text='R\n\nE\n\nC\n\nE\n\nS\n\nS',
    font=('Consolas', 18, 'italic'),
    width=3,
    relief='sunken'
)
recess.pack()

for i in range(days):
    b = tk.Label(
        first_half,
        text=day_names[i],
        font=('Consolas', 12, 'bold'),
        width=9,
        height=2,
        bd=5,
        relief='raised'
    )
    b.grid(row=i + 1, column=0)

for i in range(periods):
    if i < recess_break_aft:
        b = tk.Label(first_half)
        b.grid(row=0, column=i + 1)
    else:
        b = tk.Label(second_half)
        b.grid(row=0, column=i)

    b.config(
        text=period_names[i],
        font=('Consolas', 12, 'bold'),
        width=9,
        height=1,
        bd=5,
        relief='raised'
    )

for i in range(days):
    b = []
    for j in range(periods):
        if j < recess_break_aft:
            bb = tk.Button(first_half)
            bb.grid(row=i + 1, column=j + 1)
        else:
            bb = tk.Button(second_half)
            bb.grid(row=i + 1, column=j)

        bb.config(
            text='Hello World!',
            font=('Consolas', 10),
            width=13,
            height=3,
            bd=5,
            relief='raised',
            wraplength=80,
            justify='center',
            command=lambda x=i, y=j: process_button(x, y)
        )
        b.append(bb)

    butt_grid.append(b)

sec_select_f = tk.Frame(tt, pady=15)
sec_select_f.pack()

tk.Label(
    sec_select_f,
    text='Select section:  ',
    font=('Consolas', 12, 'bold')
).pack(side=tk.LEFT)

cursor = conn.execute("SELECT DISTINCT SECTION FROM STUDENT")
sec_li = [row[0] for row in cursor]
combo1 = ttk.Combobox(
    sec_select_f,
    values=sec_li,
)
combo1.pack(side=tk.LEFT)
combo1.current(0)

b = tk.Button(
    sec_select_f,
    text="OK",
    font=('Consolas', 12, 'bold'),
    padx=10,
    command=select_sec
)
b.pack(side=tk.LEFT, padx=10)
b.invoke()

automatic_schedule()

quit_button = tk.Button(
    tt,
    text="Quit",
    font=('Consolas', 12, 'bold'),
    padx=10,
    command=tt.quit
)
quit_button.pack(pady=10)

tt.mainloop()
