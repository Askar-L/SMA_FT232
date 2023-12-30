
from tkinter import *
from tkinter import messagebox

def get_height():
    # 获取身高数据(cm)
    height = float(ENTRY2.get())
    return height

def get_weight():
    # 获取体重数据(kg)
    weight = float(ENTRY1.get())
    return weight

def calculate_bmi():
    # 计算BMI系数
    try:
        height = get_height()
        weight = get_weight()
        height = height / 100.0
        bmi = weight / (height ** 2)
    except ZeroDivisionError:
        messagebox.showinfo("提示", "请输入有效的身高数据!!")
    except ValueError:
        messagebox.showinfo("提示", "请输入有效的数据!")
    else:
        messagebox.showinfo("你的BMI系数是: ", bmi)

if __name__ == '__main__':
    # 实例化object，建立窗口TOP
    TOP = Tk()
    TOP.bind("<Return>", calculate_bmi)
    # 设定窗口的大小(长 * 宽)
    TOP.geometry("400x400")
    # 窗口背景颜色
    TOP.configure(background="#ffffff")
    # 窗口标题
    TOP.title("BMI 计算器")
    TOP.resizable(width=False, height=False)
    LABLE = Label(TOP, bg="#8c52ff", fg="#ffffff", text="欢迎使用 BMI 计算器", font=("Helvetica", 20, "bold"), pady=10)
    LABLE.place(x=55, y=0)
    LABLE1 = Label(TOP, bg="#ffffff", text="输入体重(单位：kg):", bd=6,
                   font=("Helvetica", 10, "bold"), pady=5)
    LABLE1.place(x=55, y=60)
    ENTRY1 = Entry(TOP, bd=8, width=10, font="Roboto 11")
    ENTRY1.place(x=240, y=60)
    LABLE2 = Label(TOP, bg="#ffffff", text="输入身高(单位：cm):", bd=6,
                   font=("Helvetica", 10, "bold"), pady=5)
    LABLE2.place(x=55, y=121)
    ENTRY2 = Entry(TOP, bd=8, width=10, font="Roboto 11")
    ENTRY2.place(x=240, y=121)
    BUTTON = Button(bg="#000000", fg='#ffffff', bd=12, text="BMI", padx=33, pady=10, command=calculate_bmi,
                    font=("Helvetica", 20, "bold"))
    BUTTON.grid(row=5, column=0, sticky=W)
    BUTTON.place(x=115, y=250)
    TOP.mainloop()