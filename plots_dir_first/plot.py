import plotly.express as px

file = open("qlen.data", "r")
x, y = [], []
for i in file.readlines():
    i = i.strip().split(" ")
    x.append(i[0])
    y.append(i[1])

fig = px.line(x=x, y=y)
fig.show()