"""Tkinter desktop UI: login, tab navigation, CRUD, rental flows and reporting."""
from datetime import date, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
from movie_app import auth, movies, customers, rentals, reports

class ManagementPage(ttk.Frame):
    def __init__(self, parent, columns, labels, on_search, on_add, on_update, on_delete):
        super().__init__(parent, padding=12)
        self.columns = columns
        self.labels = labels
        self.fields = {}
        for index, field in enumerate(labels):
            ttk.Label(self, text=field).grid(row=index, column=0, sticky="w", pady=3)
            entry = ttk.Entry(self, width=34)
            entry.grid(row=index, column=1, sticky="ew", padx=6)
            self.fields[field] = entry
        button_row = len(labels)
        for col, (text, callback) in enumerate([("Add",on_add),("Update",on_update),("Delete",on_delete)]):
            ttk.Button(self, text=text, command=lambda cb=callback: self.safe(cb)).grid(
                row=button_row,column=col,sticky="ew",padx=3,pady=8)
        ttk.Label(self, text="Search (title/genre/producer or customer name/ID)").grid(row=button_row+1,column=0,columnspan=3,sticky="w")
        self.query = ttk.Entry(self)
        self.query.grid(row=button_row+2,column=0,columnspan=2,sticky="ew")
        ttk.Button(self,text="Search / Refresh",command=lambda: self.safe(on_search)).grid(row=button_row+2,column=2)
        self.tree = ttk.Treeview(self,columns=columns,show="headings",height=12)
        for col in columns:
            self.tree.heading(col,text=col.replace("_"," ").title())
            self.tree.column(col,width=130,anchor="w")
        self.tree.grid(row=button_row+3,column=0,columnspan=3,sticky="nsew",pady=8)
        self.tree.bind("<<TreeviewSelect>>", self.select_row)
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(button_row+3,weight=1)
        ttk.Button(self,text="Export Excel reports",command=lambda: self.safe(self.export)).grid(
            row=button_row+4,column=0,columnspan=3,sticky="ew")
    def values(self):
        return [self.fields[label].get().strip() for label in self.labels]
    def selected_id(self):
        selection = self.tree.selection()
        if not selection:
            raise ValueError("Please select a row first")
        return int(self.tree.item(selection[0],"values")[0])
    def select_row(self, _):
        selection = self.tree.selection()
        if selection:
            values = self.tree.item(selection[0],"values")
            for label,value in zip(self.labels,values[1:]):
                field = self.fields[label]
                field.delete(0,"end")
                field.insert(0,str(value))
    def populate(self,records):
        self.tree.delete(*self.tree.get_children())
        for record in records:
            self.tree.insert("", "end", values=[record.get(k, "") for k in self.columns])
    def safe(self,action):
        try:
            action()
        except Exception as exc:
            messagebox.showerror("Operation failed",str(exc))
    def export(self):
        path=reports.export_excel()
        messagebox.showinfo("Report saved",f"Excel workbook saved to:\n{path.resolve()}")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Movie Rental Management System")
        self.geometry("1050x720")
        self.minsize(850,580)
        self.show_login()
    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()
    def show_login(self):
        self.clear()
        frame=ttk.Frame(self,padding=35)
        frame.pack(expand=True)
        ttk.Label(frame,text="Employee Login",font=("Segoe UI",20,"bold")).pack(pady=12)
        ttk.Label(frame,text="Username").pack(anchor="w")
        user=ttk.Entry(frame,width=35)
        user.pack(pady=5)
        ttk.Label(frame,text="Password").pack(anchor="w")
        password=ttk.Entry(frame,show="*",width=35)
        password.pack(pady=5)
        def login():
            try:
                if auth.authenticate(user.get(),password.get()):
                    self.show_main()
                else:
                    messagebox.showerror("Login failed","Invalid credentials")
            except Exception as exc:
                messagebox.showerror("Login failed",str(exc))
        ttk.Button(frame,text="Login",command=login).pack(pady=15)
        password.bind("<Return>",lambda _: login())
    def show_main(self):
        self.clear()
        top=ttk.Frame(self,padding=8)
        top.pack(fill="x")
        ttk.Label(top,text="Movie Rental Management System",font=("Segoe UI",16,"bold")).pack(side="left")
        ttk.Button(top,text="Logout",command=self.show_login).pack(side="right")
        tabs=ttk.Notebook(self)
        tabs.pack(fill="both",expand=True)
        self.movie_page=ManagementPage(tabs,
            ("movie_id","title","genre","release_year","rental_price","producer"),
            ("Title","Genre","Release Year","Rental Price","Producer"),
            self.refresh_movies,self.add_movie,self.update_movie,self.delete_movie)
        self.customer_page=ManagementPage(tabs,
            ("customer_id","name","contact"),("Name","Contact"),
            self.refresh_customers,self.add_customer,self.update_customer,self.delete_customer)
        self.rental_page=ttk.Frame(tabs,padding=12)
        tabs.add(self.movie_page,text="Movie Management")
        tabs.add(self.customer_page,text="Customer Management")
        tabs.add(self.rental_page,text="Rental Management")
        self.build_rentals()
        self.refresh_movies()
        self.refresh_customers()
        self.refresh_rentals()
    def confirm(self,fn):
        if messagebox.askyesno("Confirm deletion","Delete this record? Historical rentals prevent deletion."):
            fn()
    def refresh_movies(self):
        self.movie_page.populate(movies.search(self.movie_page.query.get()))
    def add_movie(self):
        movies.add(*self.movie_page.values()); self.refresh_movies()
    def update_movie(self):
        movies.update(self.movie_page.selected_id(),*self.movie_page.values()); self.refresh_movies()
    def delete_movie(self):
        self.confirm(lambda: (movies.delete(self.movie_page.selected_id()),self.refresh_movies()))
    def refresh_customers(self):
        self.customer_page.populate(customers.search(self.customer_page.query.get()))
    def add_customer(self):
        customers.add(*self.customer_page.values()); self.refresh_customers()
    def update_customer(self):
        customers.update(self.customer_page.selected_id(),*self.customer_page.values()); self.refresh_customers()
    def delete_customer(self):
        self.confirm(lambda: (customers.delete(self.customer_page.selected_id()),self.refresh_customers()))
    def build_rentals(self):
        p=self.rental_page
        self.rent_entries={}
        defaults={"Movie ID":"","Customer ID":"","Rental Date":str(date.today()),
                  "Due Date":str(date.today()+timedelta(days=7)),"Rental ID":"","Return Date":str(date.today())}
        for i,(label,default) in enumerate(defaults.items()):
            ttk.Label(p,text=label).grid(row=i,column=0,sticky="w",pady=3)
            widget=ttk.Entry(p,width=30)
            widget.insert(0,default)
            widget.grid(row=i,column=1,sticky="ew",padx=6)
            self.rent_entries[label]=widget
        actions=[("View Rentals",self.refresh_rentals),
                 ("Rent a Movie",self.issue_rental),("Return a Movie",self.return_rental),
                 ("Excel Reports",self.export_reports),("Rentals by Genre Chart",self.chart)]
        for i,(label,callback) in enumerate(actions):
            ttk.Button(p,text=label,command=lambda cb=callback: self.safe(cb)).grid(row=i,column=2,sticky="ew",padx=6,pady=3)
        ttk.Label(p,text="Search movie or customer").grid(row=6,column=0,sticky="w")
        self.rental_query=ttk.Entry(p)
        self.rental_query.grid(row=6,column=1,sticky="ew")
        ttk.Button(p,text="Search",command=lambda: self.safe(self.refresh_rentals)).grid(row=6,column=2,sticky="ew")
        columns=("rental_id","movie_id","title","customer_id","name","rental_date","due_date","return_date","late_fee")
        self.rental_tree=ttk.Treeview(p,columns=columns,show="headings",height=11)
        for col in columns:
            self.rental_tree.heading(col,text=col.replace("_"," ").title())
            self.rental_tree.column(col,width=105)
        self.rental_tree.grid(row=7,column=0,columnspan=3,sticky="nsew",pady=8)
        self.rental_tree.bind("<<TreeviewSelect>>",self.select_rental)
        p.grid_columnconfigure(1,weight=1)
        p.grid_rowconfigure(7,weight=1)
    def select_rental(self,_):
        selected=self.rental_tree.selection()
        if selected:
            val=self.rental_tree.item(selected[0],"values")
            for label,index in (("Rental ID",0),("Movie ID",1),("Customer ID",3)):
                entry=self.rent_entries[label];entry.delete(0,"end");entry.insert(0,val[index])
    def refresh_rentals(self):
        items=rentals.search(self.rental_query.get())
        self.rental_tree.delete(*self.rental_tree.get_children())
        keys=("rental_id","movie_id","title","customer_id","name","rental_date","due_date","return_date","late_fee")
        for rec in items:
            self.rental_tree.insert("","end",values=[str(rec.get(k) if rec.get(k) is not None else "") for k in keys])
    def issue_rental(self):
        e=self.rent_entries
        rentals.rent(e["Movie ID"].get(),e["Customer ID"].get(),e["Rental Date"].get(),e["Due Date"].get())
        self.refresh_rentals();messagebox.showinfo("Success","Movie issued")
    def return_rental(self):
        e=self.rent_entries
        fee=rentals.return_movie(e["Rental ID"].get(),e["Return Date"].get())
        self.refresh_rentals();messagebox.showinfo("Returned",f"Late fee: {fee:.2f}")
    def export_reports(self):
        path=reports.export_excel();messagebox.showinfo("Report saved",str(path.resolve()))
    def chart(self):
        reports.show_chart()
    def safe(self,action):
        try:action()
        except Exception as exc:messagebox.showerror("Operation failed",str(exc))