from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import datetime
import sqlite3

with sqlite3.connect("noteslogger2.db") as db:
    cur = db.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS user(userid INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT NOT NULL UNIQUE,password TEXT NOT NULL);")
cur.execute("CREATE TABLE IF NOT EXISTS notes (noteid INTEGER PRIMARY KEY AUTOINCREMENT,userid INTEGER NOT NULL,uname TEXT NOT NULL,tags TEXT NOT NULL,memo TEXT NOT NULL,c_time timestamp,FOREIGN KEY(userid) REFERENCES user(userid));")
cur.execute("PRAGMA foreign_keys=ON")
cur.close()
db.commit()
db.close()

class Main():
    def __init__(self, master):
        self.master = master
        self.username = StringVar()
        self.password = StringVar()
        self.n_username = StringVar()
        self.n_password = StringVar()
        self.bullet = "\u2022"                  
        self.tags = StringVar()
        self.currtime = datetime.datetime.now().ctime()
        self.newTag = StringVar()
        self.master.geometry("500x500")
        self.master.title("Notes Manager")
        self.widgetsReg()
        self.widgetsLog()
        
    def login(self):
        with sqlite3.connect("noteslogger2.db") as db:
            cur = db.cursor()
        find_user = ('SELECT * FROM user WHERE username = ? and password = ?')
        cur.execute(find_user,[(self.username.get()),(self.password.get())])
        result = cur.fetchall()
        if result:
            messagebox.showinfo("Congrats","Good to go!")                 
            self.loginFrame.place_forget()
            self.regFrame.place_forget()
            self.widgetMain()
            self.mainframe.place(width=700,height=700)
            cur.close()
        else:
            messagebox.showerror("Error","Credentials not found!!\n\nTry Registering new account!")
            cur.close()

    def newregister(self):
        try:
            with sqlite3.connect('noteslogger2.db') as db:
                cur = db.cursor()
            insert = ('INSERT INTO user(username,password) VALUES(?,?)')
            cur.execute(insert,[(self.n_username.get()),(self.n_password.get())])
            messagebox.showinfo("Success","Account Created")
            self.log()
            cur.close()
            db.commit()
            db.close()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error","Username already taken!!")
            
    def log(self):
        self.username.set('')
        self.password.set('')
        self.regFrame.place_forget()
        self.loginFrame.place(width=500,height=500)
        # register button is disabled
        self.regbtn.config(state=DISABLED)

    def reg(self):
        self.n_username.set('')
        self.n_password.set('')
        self.loginFrame.place_forget()
        self.regFrame.place(width=500,height=500)

    def addnotes(self):
        try:
            with sqlite3.connect("noteslogger2.db") as db:
                cur = db.cursor()
            fquery = ('SELECT userid FROM user WHERE username = ?')
            cur.execute(fquery,[(self.username.get())])
            rows = cur.fetchall()
            usr = [usr[0] for usr in rows]      #global usr
            insert = ('INSERT INTO notes(userid,uname,tags,memo,c_time)VALUES(?,?,?,?,?)')
            params = (usr[0],self.username.get(),self.tags.get(),self.txt.get("1.0","end-1c"),self.currtime)
            cur.execute(insert,params)
            messagebox.showinfo('Success','Note Added!!!')
            cur.close()
            db.commit()
            db.close
        except sqlite3.IntegrityError as e:
            print(e)    # checking the foreign key constraint and rejected the change in table
            # notes can be added of only those users whose userid exists
            messagebox.showerror("Error","ForeignKey Error!")

    def showNotes(self):
        self.showNotesUi()
        self.loginFrame.place_forget()
        self.regFrame.place_forget()
        self.mainframe.place_forget()
        self.showNotesFrame.place(width=500,height=500)
        with sqlite3.connect("noteslogger2.db") as db:
            cur = db.cursor()
        # extracting the notes of particular user to display them on treeview
        findTMC = ('SELECT tags,memo,c_time from notes WHERE uname = ?')
        cur.execute(findTMC,[(self.username.get())])
        rows = cur.fetchall()        
        for tmc in rows:
            # inserting the tags/memo/date/time of user
            self.tree.insert('', 'end',text=str(tmc[0]),values=(tmc[1],tmc[2]))
        cur.close()
        db.commit()
        db.close()
        
    def modifyNotes(self):
        with sqlite3.connect("noteslogger2.db") as db:
            cur = db.cursor()
        update = ('UPDATE notes SET tags = ?,memo = ?,c_time = ? WHERE tags = ? AND memo = ?')
        par = (self.newTag.get(),self.newMemo.get("1.0","end-1c"),self.currtime,self.oldTag,self.oldMemo)
        cur.execute(update,par)
        messagebox.showinfo("Congrats","Note updated succesfully!!")
        db.commit()
        cur.close()
        db.close()
        self.modiWind.destroy()
        self.cleanNotes()     

    def cleanNotes(self):
        with sqlite3.connect("noteslogger2.db") as db:
            cur = db.cursor()
        notes = self.tree.get_children()
        for ele in notes:
            self.tree.delete(ele)
        findTMC = ('SELECT tags,memo,c_time from notes WHERE uname = ?')
        cur.execute(findTMC,[(self.username.get())])
        rows = cur.fetchall()
        for row in rows:
            self.tree.insert('', 'end',text=str(row[0]),values=(row[1],row[2]))
        db.commit()
        cur.close()
        db.close()
    
    def deleteNotes(self):
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            messagebox.showwarning("Error","Please select a note to be Deleted")
            return
        self.selectedTag = self.tree.item(self.tree.selection())['text']
        self.selectedMemo = self.tree.item(self.tree.selection())['values'][0]
        with sqlite3.connect("noteslogger2.db") as db:
            cur = db.cursor()
        dltQuery = ('DELETE FROM notes WHERE tags = ?')
        cur.execute(dltQuery, (self.selectedTag,))
        messagebox.showinfo("Congrats","Selected note deleted!!")
        db.commit()
        cur.close()
        db.close()
        self.cleanNotes()
            
    def widgetsLog(self):
        self.loginFrame = Frame(self.master,width=500,height=500)
        Label(self.loginFrame, text="Notes Manager", width=17, font=("bold", 25), fg="chocolate").place(x=90, y=20)
        Label(self.loginFrame, text="Login", width=18, font=("bold", 20), fg="blue3").place(x=90, y=79)
        Label(self.loginFrame, text="Username :",width=12, font=(15)).place(x=75, y=160)
        Entry(self.loginFrame, textvariable=self.username,width=20, font=("bold", 12)).place(x=200, y=165)
        Label(self.loginFrame, text="Password :",width=12, font=(15)).place(x=75, y=220)
        Entry(self.loginFrame, textvariable=self.password,show=self.bullet, width=20, font=("bold", 12)).place(x=200, y=225)
        Button(self.loginFrame, text="Login", width=11, font=("bold", 11),bg="brown",fg="white",command=self.login).place(x=100, y=280)
        self.regbtn = Button(self.loginFrame, text="Register",width=11,font=("bold", 11),bg="brown", fg="white",command=self.reg)
        self.regbtn.place(x=250, y=280)
        self.loginFrame.place(width=500,height=500)
        
    def widgetsReg(self):
        self.regFrame = Frame(self.master, width=500,height=500)
        Label(self.regFrame, text="Notes Manager", width=17, font=("bold", 25), fg="chocolate").place(x=80, y=20)
        Label(self.regFrame, text="Registeration", width=18, font=("bold", 20), fg="blue3").place(x=92, y=79)
        Label(self.regFrame, text="Username :",width=12, font=(15)).place(x=75, y=160)
        Entry(self.regFrame, textvariable=self.n_username,width=20, font=("bold", 12)).place(x=200, y=165)
        password = Label(self.regFrame, text="Password :",width=12, font=(15)).place(x=75, y=220)
        Entry(self.regFrame, textvariable=self.n_password,show=self.bullet, width=20, font=("bold", 12)).place(x=200, y=225)
        Button(self.regFrame, text="Submit Details", width=11,font=("bold", 11), bg="brown",fg="white",command=self.newregister).place(x=100, y=280)
        Button(self.regFrame, text="Back to Login", width=11,font=("bold", 11), bg="brown",fg="white",command=self.log).place(x=250, y=280)

    def widgetMain(self):
        self.mainframe = Frame(self.master, width=500,height=500)
        Label(self.mainframe, text="Welcome",width=17,font=("bold, 25"), fg="blueviolet").place(x=80,y=20)
        Label(self.mainframe, text="Tags :",width=12,font=(15)).place(x=40,y=100)
        Entry(self.mainframe,textvariable=self.tags,width=23,font=("bold",12)).place(x=144,y=105)
        Label(self.mainframe,text="Memo :",width=12,font=(15)).place(x=38,y=139)
        self.txt = Text(self.mainframe,height=12,width=35,font=("",12))
        self.txt.place(x=144,y=145)
        scroll = Scrollbar(root, command=self.txt.yview)
        scroll.pack(side=RIGHT,fill=Y)
        self.txt.config(yscrollcommand=scroll.set)
        Button(self.mainframe,text="Add Note",width=11,font=("bold", 11), bg="brown",fg="white",command=self.addnotes).place(x=144, y=400)
        Button(self.mainframe,text="Show All Notes",width=11,font=("bold", 11), bg="brown",fg="white",command=self.showNotes).place(x=300, y=400)
        self.mainframe.place(width=700,height=700)

    def showNotesUi(self):
        self.showNotesFrame = Frame(self.master)
        Label(self.showNotesFrame, text="Your Notes",width=17,font=("bold, 25"), fg="blueviolet").place(x=80,y=20)
        self.tree = ttk.Treeview(self.showNotesFrame,height=10,columns=("#0","#1","#2"))
        self.tree.place(x=0,y=100)
        self.tree.heading('#0',text='Tags',anchor = CENTER);self.tree.column("#0",width=95)
        self.tree.heading('#1',text='Memo',anchor = CENTER);self.tree.column("#1",width=255)
        self.tree.heading('#2',text='Date/Time',anchor = CENTER);self.tree.column("#2",width=150)
        Button(self.showNotesFrame,text="Modify Notes",width=11,font=("bold", 11),bg="brown",fg="white",command=self.modifyNotesUi).place(x=80, y=420)
        Button(self.showNotesFrame,text="Delete Notes",width=11,font=("bold", 11),bg="brown",fg="white",command=self.deleteNotes).place(x=290, y=420)

    def modifyNotesUi(self):
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            messagebox.showwarning("Error","Please select a note to be Modified")
            return

        self.oldTag = self.tree.item(self.tree.selection())['text']
        self.oldMemo = self.tree.item(self.tree.selection())['values'][0]
        self.modiWind = Toplevel()
        self.modiWind.title("Modify Window")
        self.modiWind.geometry("500x500")
        Label(self.modiWind, text="Modify",width=17,font=("bold, 21"), fg="blueviolet").place(x=80,y=15)
        Label(self.modiWind,text='Old Tags :',width=12,font=("",12)).place(x=40,y=79)
        Entry(self.modiWind,textvariable=StringVar(self.modiWind,value=self.oldTag),width=23,state='readonly').place(x=144,y=80)
        Label(self.modiWind,text="New Tags :",width=12,font=("",12)).place(x=40,y=111)
        Entry(self.modiWind,textvariable=self.newTag,width=23,font=("bold",12)).place(x=144,y=110)
        Label(self.modiWind,text='Old Memo:',width=12,font=("",12)).place(x=40,y=147)
        Entry(self.modiWind,textvariable=StringVar(self.modiWind,value=self.oldMemo),width=23,state='readonly').place(x=144,y=150)
        Label(self.modiWind,text="New Memo :",width=12,font=("",12)).place(x=38,y=180)
        self.newMemo = Text(self.modiWind,height=12,width=35,font=("",12))
        self.newMemo.place(x=144,y=183)
        Button(self.modiWind,text="Modify",width=11,font=("bold", 11), bg="brown",fg="white",command=self.modifyNotes).place(x=144, y=460)

if __name__ == "__main__":
    root = Tk()
    Main(root)
    root.mainloop()