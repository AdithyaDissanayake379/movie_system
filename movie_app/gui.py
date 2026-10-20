"""Tkinter desktop UI for movie rental management."""
from datetime import date, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
from movie_app import auth, movies, customers, rentals, reports


class ManagementPage(ttk.Frame):
    def __init__(self, parent, columns, labels, on_search, on_add, on_update, on_delete, search_hint):
        super().__init__(parent, padding=14)
        self.columns = columns
        self.labels = labels
        self.fields = {}
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        form = ttk.LabelFrame(self, text="Record details", padding=12)
        form.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        # Never stretch Entry widgets across the entire application.
        for index, field in enumerate(labels):
            r, c = divmod(index, 2)
            block = ttk.Frame(form)
            block.grid(row=r, column=c, sticky="w", padx=(0, 28), pady=5)
            ttk.Label(block, text=field, width=14).pack(side="left")
            entry = ttk.Entry(block, width=32)
            entry.pack(side="left", padx=(6, 0))
            self.fields[field] = entry

        buttons = ttk.Frame(self)
        buttons.grid(row=1, column=0, sticky="w", pady=(0, 10))
        for text, callback in (
            ("Add", on_add), ("Update", on_update), ("Delete", on_delete),
            ("Clear Fields", self.clear_fields),
        ):
            # Fixed-width buttons, no sticky='ew'.
            ttk.Button(buttons, text=text, width=16,
                       command=lambda cb=callback: self.safe(cb)).pack(side="left", padx=(0, 9))

        search = ttk.Frame(self)
        search.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(search, text=search_hint).pack(side="left", padx=(0, 10))
        self.query = ttk.Entry(search, width=34)
        self.query.pack(side="left", padx=(0, 9))
        ttk.Button(search, text="Search / Refresh", width=19,
                   command=lambda: self.safe(on_search)).pack(side="left")
        self.query.bind("<Return>", lambda _event: self.safe(on_search))

        table_frame = ttk.Frame(self)
        table_frame.grid(row=3, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=13)
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=155, minwidth=95, anchor="w", stretch=False)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vs = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hs = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        vs.grid(row=0, column=1, sticky="ns")
        hs.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        self.tree.bind("<<TreeviewSelect>>", self.select_row)

        ttk.Button(self, text="Export Excel Reports", width=23,
                   command=lambda: self.safe(self.export)).grid(row=4, column=0, sticky="w", pady=(11, 0))

    def values(self):
        return [self.fields[label].get().strip() for label in self.labels]

    def clear_fields(self):
        for entry in self.fields.values():
            entry.delete(0, tk.END)
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        if self.labels:
            self.fields[self.labels[0]].focus_set()

    def selected_id(self):
        selection = self.tree.selection()
        if not selection:
            raise ValueError("Please select a row first")
        return int(self.tree.item(selection[0], "values")[0])

    def select_row(self, _event):
        selection = self.tree.selection()
        if selection:
            values = self.tree.item(selection[0], "values")
            for label, value in zip(self.labels, values[1:]):
                field = self.fields[label]
                field.delete(0, tk.END)
                field.insert(0, str(value))

    def populate(self, records):
        self.tree.delete(*self.tree.get_children())
        for record in records:
            self.tree.insert("", "end", values=[record.get(k, "") for k in self.columns])

    def safe(self, action):
        try:
            action()
        except Exception as exc:
            messagebox.showerror("Operation failed", str(exc))

    def export(self):
        path = reports.export_excel()
        messagebox.showinfo("Report saved", f"Excel workbook saved to:\n{path.resolve()}")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Movie Rental Management System")
        self.geometry("1150x750")
        self.minsize(940, 600)
        self.show_login()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear()
        frame = ttk.Frame(self, padding=35)
        frame.pack(expand=True)
        ttk.Label(frame, text="Employee Login", font=("Segoe UI", 20, "bold")).pack(pady=12)
        ttk.Label(frame, text="Username").pack(anchor="w")
        user = ttk.Entry(frame, width=35)
        user.pack(pady=5)
        ttk.Label(frame, text="Password").pack(anchor="w")
        password = ttk.Entry(frame, show="*", width=35)
        password.pack(pady=5)

        def login():
            try:
                if auth.authenticate(user.get(), password.get()):
                    self.show_main()
                else:
                    messagebox.showerror("Login failed", "Invalid credentials")
            except Exception as exc:
                messagebox.showerror("Login failed", str(exc))

        ttk.Button(frame, text="Login", width=18, command=login).pack(pady=15)
        password.bind("<Return>", lambda _event: login())
        user.focus_set()

    def show_main(self):
        self.clear()
        top = ttk.Frame(self, padding=12)
        top.pack(fill="x")
        ttk.Label(top, text="Movie Rental Management System",
                  font=("Segoe UI", 17, "bold")).pack(side="left")
        ttk.Button(top, text="Logout", width=12, command=self.show_login).pack(side="right")
        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.movie_page = ManagementPage(
            tabs, ("movie_id", "title", "genre", "release_year", "rental_price", "producer"),
            ("Title", "Genre", "Release Year", "Rental Price", "Producer"),
            self.refresh_movies, self.add_movie, self.update_movie, self.delete_movie,
            "Search movies (title / genre / producer):")
        self.customer_page = ManagementPage(
            tabs, ("customer_id", "name", "contact"), ("Name", "Contact"),
            self.refresh_customers, self.add_customer, self.update_customer,
            self.delete_customer, "Search customers (name / ID):")
        self.rental_page = ttk.Frame(tabs, padding=14)
        tabs.add(self.movie_page, text="Movie Management")
        tabs.add(self.customer_page, text="Customer Management")
        tabs.add(self.rental_page, text="Rental Management")
        self.build_rentals()
        self.refresh_movies()
        self.refresh_customers()
        self.refresh_rentals()

    def confirm(self, fn):
        if messagebox.askyesno("Confirm deletion", "Delete this record? Historical rentals prevent deletion."):
            fn()

    def refresh_movies(self):
        self.movie_page.populate(movies.search(self.movie_page.query.get()))

    def add_movie(self):
        movies.add(*self.movie_page.values())
        self.movie_page.query.delete(0, tk.END)
        self.refresh_movies()
        self.movie_page.clear_fields()
        messagebox.showinfo("Success", "Movie added successfully")

    def update_movie(self):
        movie_id = self.movie_page.selected_id()
        movies.update(movie_id, *self.movie_page.values())
        self.movie_page.query.delete(0, tk.END)
        self.refresh_movies()
        self.movie_page.clear_fields()
        messagebox.showinfo("Success", "Movie updated successfully")

    def delete_movie(self):
        movie_id = self.movie_page.selected_id()
        def delete_confirmed():
            movies.delete(movie_id)
            self.movie_page.query.delete(0, tk.END)
            self.refresh_movies()
            self.movie_page.clear_fields()
            messagebox.showinfo("Success", "Movie deleted successfully")
        self.confirm(delete_confirmed)

    def refresh_customers(self):
        self.customer_page.populate(customers.search(self.customer_page.query.get()))

    def add_customer(self):
        customers.add(*self.customer_page.values())
        self.customer_page.query.delete(0, tk.END)
        self.refresh_customers()
        self.customer_page.clear_fields()
        messagebox.showinfo("Success", "Customer added successfully")

    def update_customer(self):
        customer_id = self.customer_page.selected_id()
        customers.update(customer_id, *self.customer_page.values())
        self.customer_page.query.delete(0, tk.END)
        self.refresh_customers()
        self.customer_page.clear_fields()
        messagebox.showinfo("Success", "Customer updated successfully")

    def delete_customer(self):
        customer_id = self.customer_page.selected_id()
        def delete_confirmed():
            customers.delete(customer_id)
            self.customer_page.query.delete(0, tk.END)
            self.refresh_customers()
            self.customer_page.clear_fields()
            messagebox.showinfo("Success", "Customer deleted successfully")
        self.confirm(delete_confirmed)

    def build_rentals(self):
        p = self.rental_page
        p.columnconfigure(0, weight=1)
        p.rowconfigure(3, weight=1)
        self.rent_entries = {}
        defaults = {
            "Movie ID": "", "Customer ID": "",
            "Rental Date": str(date.today()),
            "Due Date": str(date.today() + timedelta(days=7)),
            "Rental ID": "", "Return Date": str(date.today()),
        }
        form = ttk.LabelFrame(p, text="Rental details", padding=12)
        form.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        for i, (label, default) in enumerate(defaults.items()):
            row, col = divmod(i, 3)
            cell = ttk.Frame(form)
            cell.grid(row=row, column=col, sticky="w", padx=(0, 22), pady=5)
            ttk.Label(cell, text=label, width=13).pack(side="left")
            widget = ttk.Entry(cell, width=17)
            widget.insert(0, default)
            widget.pack(side="left", padx=(5, 0))
            self.rent_entries[label] = widget
        actions_frame = ttk.Frame(p)
        actions_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        actions = [
            ("View Rentals", self.refresh_rentals),
            ("Rent a Movie", self.issue_rental),
            ("Return a Movie", self.return_rental),
            ("Excel Reports", self.export_reports),
            ("Rentals by Genre Chart", self.chart),
            ("Clear Fields", self.clear_rental_fields),
        ]
        for index, (label, callback) in enumerate(actions):
            row, col = divmod(index, 3)
            ttk.Button(actions_frame, text=label, width=23,
                       command=lambda cb=callback: self.safe(cb)).grid(
                           row=row, column=col, padx=(0, 10), pady=3, sticky="w")
        search = ttk.Frame(p)
        search.grid(row=2, column=0, sticky="nw")
        # Search stays above table; arrange table separately beneath it.
        ttk.Label(search, text="Search movie or customer").pack(side="left", padx=(0, 8))
        self.rental_query = ttk.Entry(search, width=32)
        self.rental_query.pack(side="left", padx=(0, 8))
        ttk.Button(search, text="Search", width=12,
                   command=lambda: self.safe(self.refresh_rentals)).pack(side="left")
        self.rental_query.bind("<Return>", lambda _event: self.safe(self.refresh_rentals))
        table_frame = ttk.Frame(p)
        table_frame.grid(row=3, column=0, sticky="nsew", pady=(10, 0))
        p.rowconfigure(3, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        columns = ("rental_id", "movie_id", "title", "customer_id", "name",
                   "rental_date", "due_date", "return_date", "late_fee")
        self.rental_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=11)
        for col in columns:
            self.rental_tree.heading(col, text=col.replace("_", " ").title())
            self.rental_tree.column(col, width=135, minwidth=90, stretch=False)
        self.rental_tree.grid(row=0, column=0, sticky="nsew")
        vs = ttk.Scrollbar(table_frame, orient="vertical", command=self.rental_tree.yview)
        hs = ttk.Scrollbar(table_frame, orient="horizontal", command=self.rental_tree.xview)
        vs.grid(row=0, column=1, sticky="ns")
        hs.grid(row=1, column=0, sticky="ew")
        self.rental_tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        self.rental_tree.bind("<<TreeviewSelect>>", self.select_rental)

    def clear_rental_fields(self):
        defaults = {
            "Movie ID": "", "Customer ID": "", "Rental Date": str(date.today()),
            "Due Date": str(date.today() + timedelta(days=7)),
            "Rental ID": "", "Return Date": str(date.today()),
        }
        for label, value in defaults.items():
            entry = self.rent_entries[label]
            entry.delete(0, tk.END)
            entry.insert(0, value)
        for item in self.rental_tree.selection():
            self.rental_tree.selection_remove(item)
        self.rent_entries["Movie ID"].focus_set()

    def select_rental(self, _event):
        selected = self.rental_tree.selection()
        if selected:
            values = self.rental_tree.item(selected[0], "values")
            for label, index in (("Rental ID", 0), ("Movie ID", 1), ("Customer ID", 3)):
                entry = self.rent_entries[label]
                entry.delete(0, tk.END)
                entry.insert(0, values[index])

    def refresh_rentals(self):
        items = rentals.search(self.rental_query.get())
        self.rental_tree.delete(*self.rental_tree.get_children())
        keys = ("rental_id", "movie_id", "title", "customer_id", "name",
                "rental_date", "due_date", "return_date", "late_fee")
        for rec in items:
            self.rental_tree.insert("", "end", values=[
                str(rec.get(k) if rec.get(k) is not None else "") for k in keys])

    def issue_rental(self):
        e = self.rent_entries
        rentals.rent(e["Movie ID"].get(), e["Customer ID"].get(),
                     e["Rental Date"].get(), e["Due Date"].get())
        self.rental_query.delete(0, tk.END)
        self.refresh_rentals()
        self.clear_rental_fields()
        messagebox.showinfo("Success", "Movie issued successfully")

    def return_rental(self):
        e = self.rent_entries
        fee = rentals.return_movie(e["Rental ID"].get(), e["Return Date"].get())
        self.rental_query.delete(0, tk.END)
        self.refresh_rentals()
        self.clear_rental_fields()
        messagebox.showinfo("Returned", f"Late fee: {fee:.2f}")

    def export_reports(self):
        path = reports.export_excel()
        messagebox.showinfo("Report saved", str(path.resolve()))

    def chart(self):
        reports.show_chart()

    def safe(self, action):
        try:
            action()
        except Exception as exc:
            messagebox.showerror("Operation failed", str(exc))
