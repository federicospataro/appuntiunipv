import os

l=os.listdir()
un=len(l)

i=0
while(i<un):
    if ".jpg" in l[i]:
        os.rename(l[i],str(i+1)+".jpg")
    i=i+1
