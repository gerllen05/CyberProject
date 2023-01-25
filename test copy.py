from tkinter import *
root = Tk()
root.geometry('500x500')
def pri(a):
    user = e.get()
    print(user)
e = Entry(root)
e.pack()

a = 0

b = Button(root, text="sybmit", command=pri)
b.pack()
root.mainloop()
