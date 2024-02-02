import pandas as pd
a = []
print(a.append([]))
print(a.append([[],[]]))

a = range(4)
b=[]
for _ in range(4):
    b.append(a)
# print(b)
# print(b[:,1:])

df_angle = pd.DataFrame(data=b, columns=["frame", "angle_0", "angle_1", "angle_2"])
print(df_angle[:,1:])