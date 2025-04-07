import tkinter as tk
from tkinter import messagebox, simpledialog
import calendar
import pandas as pd
from datetime import datetime
from functools import partial

class AttendanceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Tracker")
        self.root.geometry("600x400")

        # Initialize data
        self.timetable = {}
        self.holidays = []
        self.attendance = {}  # Format: { "YYYY-MM-DD": { "Subject": "Present/Absent" } }

        # Load saved data
        self.load_data()

        # If timetable is not set, prompt the user to set it
        if not self.timetable:
            self.set_timetable()

        # Create GUI
        self.create_widgets()

    def create_widgets(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Set Timetable", command=self.set_timetable)
        file_menu.add_command(label="Add Holiday", command=self.add_holiday)
        file_menu.add_separator()
        file_menu.add_command(label="Save Data", command=self.save_data)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        attendance_menu = tk.Menu(menubar, tearoff=0)
        attendance_menu.add_command(label="View Attendance Percentage", command=self.view_attendance_percentage)
        menubar.add_cascade(label="Attendance", menu=attendance_menu)

        self.calendar_frame = tk.Frame(self.root)
        self.calendar_frame.pack(pady=20)

        self.display_calendar()

    def display_calendar(self):
        """Displays the monthly calendar with day names as headers and buttons for each day."""
        # Clear the frame
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Get current month and year
        now = datetime.now()
        self.year, self.month = now.year, now.month

        # Generate calendar matrix
        cal = calendar.monthcalendar(self.year, self.month)

        # Define button colors
        colors = {"default": "lightgreen", "holiday": "lightblue"}

        # Add day name headers
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col, day in enumerate(day_names):
            lbl = tk.Label(self.calendar_frame, text=day, font=("Arial", 10, "bold"), padx=10, pady=5, bg="lightgray")
            lbl.grid(row=0, column=col, sticky="nsew")

        # Add day buttons
        for row, week in enumerate(cal, start=1):  # Start from row 1
            for col, day in enumerate(week):
                if day == 0:
                    continue  # Skip empty days

                # Date formatting
                day_str = f"{self.year}-{self.month:02d}-{day:02d}"
                day_name = calendar.day_name[calendar.weekday(self.year, self.month, day)]

                # Choose button color
                bg_color = colors["holiday"] if day_str in self.holidays else colors["default"]

                # Create day button
                btn = tk.Button(
                    self.calendar_frame,
                    text=str(day),
                    width=5,
                    height=2,
                    font=("Arial", 10, "bold"),
                    bg=bg_color,
                    fg="black",
                    relief="raised",
                    command=partial(self.mark_attendance, day_str, day_name),
                )
                btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        # Adjust row/column weights for responsiveness
        for i in range(len(cal) + 1):  # Include header row
            self.calendar_frame.rowconfigure(i, weight=1)
        for j in range(7):  # 7 days a week
            self.calendar_frame.columnconfigure(j, weight=1)

    def set_timetable(self):
        timetable_window = tk.Toplevel(self.root)
        timetable_window.title("Set Timetable")
        timetable_window.geometry("450x400")

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.timetable_entries = {}

        for day in days:
            frame = tk.Frame(timetable_window)
            frame.pack(fill="x", padx=10, pady=5)

            label = tk.Label(frame, text=day, width=10, anchor="w", font=("Arial", 10, "bold"))
            label.pack(side=tk.LEFT, padx=5)

            entry = tk.Entry(frame, width=35)
            entry.pack(side=tk.RIGHT, padx=5)

            if day in self.timetable:
                entry.insert(0, ", ".join(self.timetable[day]))
            else:
                self.timetable[day] = []

            self.timetable_entries[day] = entry

        save_button = tk.Button(timetable_window, text="Save Timetable", command=self.save_timetable, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        save_button.pack(pady=15)

    def save_timetable(self):
        for day, entry in self.timetable_entries.items():
            subjects = entry.get().strip()
            self.timetable[day] = [s.strip() for s in subjects.split(",")] if subjects else []
        messagebox.showinfo("Saved", "Timetable saved successfully!")

    def add_holiday(self):
        holiday = simpledialog.askstring("Add Holiday", "Enter holiday date (YYYY-MM-DD):")
        if holiday:
            self.holidays.append(holiday)
            self.display_calendar()

    def mark_attendance(self, date, day_name):
        if date in self.holidays:
            messagebox.showinfo("Holiday", f"{date} is a holiday!")
            return

        subjects = self.timetable.get(day_name, [])
        if not subjects:
            messagebox.showinfo("No Subjects", f"No subjects found for {day_name}.")
            return

        popup = tk.Toplevel(self.root)
        popup.title(f"Mark Attendance for {date}")
        popup.geometry("300x350")

        attendance_status = {}
        for subject in subjects:
            frame = tk.Frame(popup)
            frame.pack(pady=5)

            label = tk.Label(frame, text=subject)
            label.pack(side=tk.LEFT)

            var = tk.StringVar(value="Present")
            dropdown = tk.OptionMenu(frame, var, "Present", "Absent")
            dropdown.pack(side=tk.RIGHT)

            attendance_status[subject] = var

        save_button = tk.Button(popup, text="Save", command=lambda: self.save_attendance(date, attendance_status, popup))
        save_button.pack(pady=10)

    def save_attendance(self, date, attendance_status, popup):
        self.attendance[date] = {subject: var.get() for subject, var in attendance_status.items()}
        messagebox.showinfo("Saved", f"Attendance saved for {date}.")
        popup.destroy()

    def view_attendance_percentage(self):
        subject_stats = {}
        for subjects in self.attendance.values():
            for subject, status in subjects.items():
                if subject not in subject_stats:
                    subject_stats[subject] = {"Present": 0, "Total": 0}
                subject_stats[subject]["Total"] += 1
                if status == "Present":
                    subject_stats[subject]["Present"] += 1

        percentage_data = [[subject, f"{(stats['Present'] / stats['Total']) * 100:.2f}%"] for subject, stats in subject_stats.items()]

        popup = tk.Toplevel(self.root)
        popup.title("Attendance Percentage")
        popup.geometry("300x200")

        for i, (subject, percentage) in enumerate(percentage_data):
            tk.Label(popup, text=subject).grid(row=i, column=0, padx=10, pady=5)
            tk.Label(popup, text=percentage).grid(row=i, column=1, padx=10, pady=5)

    def save_data(self):
        # Save Timetable
        pd.DataFrame(
            [{"Day": day, "Subjects": ", ".join(subjects)} for day, subjects in self.timetable.items()]
        ).to_csv("timetable.csv", index=False)

        # Save Holidays
        pd.DataFrame(self.holidays, columns=["Holiday"]).to_csv("holidays.csv", index=False)

        # Save Attendance
        attendance_data = []
        for date, subjects in self.attendance.items():
            for subject, status in subjects.items():
                attendance_data.append([date, subject, status])
        pd.DataFrame(attendance_data, columns=["Date", "Subject", "Status"]).to_csv("attendance.csv", index=False)

        messagebox.showinfo("Save", "Data saved successfully!")


    def load_data(self):
        try:
            # Load Timetable
            df_timetable = pd.read_csv("timetable.csv")
            self.timetable = {row["Day"]: row["Subjects"].split(", ") if isinstance(row["Subjects"], str) else [] for _, row in df_timetable.iterrows()}
            
            # Load Holidays
            self.holidays = pd.read_csv("holidays.csv")["Holiday"].tolist()

            # Load Attendance
            df_attendance = pd.read_csv("attendance.csv")
            for _, row in df_attendance.iterrows():
                date = row["Date"]
                subject = row["Subject"]
                status = row["Status"]
                if date not in self.attendance:
                    self.attendance[date] = {}
                self.attendance[date][subject] = status

        except FileNotFoundError:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceTracker(root)
    root.mainloop()