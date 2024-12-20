from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from importlib_metadata import files
import mysql.connector
import time
import secrets
import hashlib
import random
import sqlite3
from operator import attrgetter

from .forms import Login, AddApp, CorsiForm, ImpostaApp, Cambiopassword

def cookies(request):
    if request.COOKIES.get('sessione'):
        c=request.COOKIES.get('sessione')

        pp=-1

        con = sqlite3.connect('appuntiunipvdb.db')
        cur = con.cursor()
        q=cur.execute("SELECT codiceutente FROM sessioniappunti WHERE codice='"+c+"';")
        r=q.fetchall()
        if len(r)!=0:
            pp=r[0][0]

        if pp==0:
            return 0 #non loggato ma ha la sessione
        elif pp==-1:
            return -2 #ha una sessione che non esiste DA CAMBIARE IN -2
        
        q=cur.execute("SELECT pex FROM utentiappunti WHERE codice="+str(pp)+";")
        r=q.fetchall()

        pp2=-1
        if len(r)!=0:
            pp2=r[0][0]

        if pp2==1:
            return 1 #loggato utente normale
        elif pp2==2:
            return 2 #loggato utente admin
        elif pp2==3:
            return 3 #loggato utente founder (serve per add appunti)
        elif pp2==-1:
            return -2 #loggato a un account che non esiste DA CAMBIARE IN -2
        
    else:
        return -1 #non ha la sessione

def handler404(request, *args, **argv):

    check=cookies(request)
    loggato=False

    if (check==1) or (check==2) or (check==3):
        loggato=True
    elif (check==-2):            #utente con cose che non esistono, cancello il cookie e redirecto home
        response=redirect("/")
        response.set_cookie(key='sessione',value='a',max_age=0)
        return response
    founder=False
    admin=False
    if check==3:
        founder=True
        admin=True
    if check==2:
        admin=True

    response = render(request, "404.html",{'loggato':loggato,'founder':founder,'admin':admin})
    response.status_code = 404
    return response

def getimage(request,id):

    con = sqlite3.connect('appuntiunipvdb.db')
    cur = con.cursor()
    q=cur.execute("SELECT * FROM immaginiappunti;")
    r=q.fetchall()
    imgr=r

    i=0
    pg=-1
    for i in range(len(imgr)):
        if imgr[i][0]==int(id):
            et=imgr[i][1]
            pg=imgr[i][2]
            break

    if pg==-1:
        return redirect("/")

    cur.execute("""DELETE FROM immaginiappunti WHERE codice="""+str(id)+""";""")
    con.commit()

    pathi="filesappunti/"+et+"/"+str(pg)+".jpg"
    image_data = open(pathi, "rb").read()

    #img.pop(i)

    return HttpResponse(image_data, content_type="image/png")

def getlinkimage(id,npagina):
    et=""
    con = sqlite3.connect('appuntiunipvdb.db')
    cur = con.cursor()
    q=cur.execute("SELECT etichetta FROM filesappunti WHERE codice="+str(id)+";")
    r=q.fetchall()
    if len(r)!=0:
        et=r[0][0]

    if et=="":
        return ""

    q=cur.execute("SELECT * FROM immaginiappunti;")
    r=q.fetchall()
    imgr=r

    while True:
        nr=random.randint(10000,99999)
        i=0
        checknr=0
        for i in range(len(imgr)):
            if imgr[i][0]==nr:
                checknr=1
                break
        if checknr==0:
            break

    cur.execute("""INSERT INTO immaginiappunti (codice,etichetta,pagina)
VALUES ("""+str(nr)+""",  '"""+et+"""', """+str(npagina)+""")""")
    con.commit()

    return "/getimage/"+str(nr)



def index(request):

    check=cookies(request)
    loggato=False

    if (check==1) or (check==2) or (check==3):
        loggato=True
    elif (check==-2):            #utente con cose che non esistono, cancello il cookie e redirecto home
        response=redirect("/")
        response.set_cookie(key='sessione',value='a',max_age=0)
        return response
    founder=False
    admin=False
    if check==3:
        founder=True
        admin=True
    if check==2:
        admin=True

    pp=0
    if request.COOKIES.get('sessione'):
        con = sqlite3.connect('appuntiunipvdb.db')
        cur = con.cursor()
        q=cur.execute("SELECT codiceutente FROM sessioniappunti WHERE codice='"+request.COOKIES.get('sessione')+"';")
        r=q.fetchall()

        if len(r)!=0:
            pp=r[0][0]

    con = sqlite3.connect('appuntiunipvdb.db')
    cur = con.cursor()
    q=cur.execute("SELECT * FROM filesappunti ORDER BY anno;")
    r=q.fetchall()
    filessordine=r

    q=cur.execute("SELECT * FROM corsiappunti;")
    r=q.fetchall()
    corsir=r

    i=0
    listaappunti=[]
    for i in range(len(corsir)):
        listaf=[]
        j=0
        for j in range(len(filessordine)):
            if filessordine[j][6]==corsir[i][0]:
                loho=False
                if pp!=0:
                    q=cur.execute("SELECT codiceutente FROM possessofileappunti WHERE codicefile="+str(filessordine[j][0])+" AND codiceutente="+str(pp)+";")
                    r=q.fetchall()
                    if len(r)!=0:
                        if r[0][0]==pp:
                            loho=True

                info = {
                    "nome": filessordine[j][1],
                    "anno": str(filessordine[j][5]),
                    "pagine": str(filessordine[j][3]),
                    "prezzo": str(filessordine[j][4]),
                    "codice": str(filessordine[j][0]),
                    "loho": loho,
                }
                listaf.append(info)
        
        if len(listaf)!=0:
            info = {
                "nome": corsir[i][1],
                "listaf": listaf,
            }
            listaappunti.append(info)

    return render(request, "index.html",{'loggato':loggato,'founder':founder,'admin':admin,'listaappunti':listaappunti})


def addcorsi(request):
    if cookies(request)!=3:
        return redirect("/")

    if request.method == 'POST':
        form = CorsiForm(request.POST)
        if form.is_valid():

            con = sqlite3.connect('appuntiunipvdb.db')
            cur = con.cursor()
            q=cur.execute("SELECT codice FROM corsiappunti;")
            r=q.fetchall()
            corsir=r

            while True:
                cc=random.randint(10000,99999)
                i=0
                checkcc=0
                for i in range(len(corsir)):
                    if int(corsir[i][0])==cc:
                        checkcc=1
                        break
                if checkcc==0:
                    break
            
            cur.execute("""INSERT INTO corsiappunti (codice,nome)
    VALUES ("""+str(cc)+""",  '"""+form.cleaned_data['nome']+"""')""")
            con.commit()

            messages.success(request, 'Corso aggiunto CORRETTAMENTE')
        else:
            messages.success(request, 'Inserisci tutti i campi richiesti')

    return redirect("/addappunti")


def addappunti(request):
    if cookies(request)!=3:
        return redirect("/")

    error=True

    listacorsi=[]
    con = sqlite3.connect('appuntiunipvdb.db')
    cur = con.cursor()
    q=cur.execute("SELECT * FROM corsiappunti;")
    r=q.fetchall()
    corsir=r

    i=0
    for i in range(len(corsir)):
        listacorsi.append("- "+str(corsir[i][0])+" "+corsir[i][1]+"\n")

    if request.method == 'POST':
        form = AddApp(request.POST)
        if form.is_valid():
            pagine=form.cleaned_data['pagine']
            prezzo=form.cleaned_data['prezzo']
            codicecorso=form.cleaned_data['codicecorso']
            anno=form.cleaned_data['anno']

            checkform=0
            try:
                pagine=int(pagine)
            except:
                checkform=1
                messages.success(request, 'Il campo pagine deve essere solo numerico')

            try:
                prezzo=int(prezzo)
            except:
                checkform=1
                messages.success(request, 'Il campo prezzo deve essere solo numerico')

            try:
                codicecorso=int(codicecorso)
            except:
                checkform=1
                messages.success(request, 'Il campo Codice Corso deve essere solo numerico')
                codicecorso=0

            try:
                anno=int(anno)
            except:
                checkform=1
                messages.success(request, 'Il campo anno deve essere solo numerico')

            trovato=0
            i=0
            for i in range(len(corsir)):
                if int(corsir[i][0])==codicecorso:
                    trovato=1
                    break
            
            if trovato==0:
                messages.success(request, 'Il Codice Corso non corrisponde a nessun corso')
                checkform=1

            if checkform!=1:
                q=cur.execute("SELECT codice FROM filesappunti;")
                r=q.fetchall()
                filessr=r
                while True:
                    cc=random.randint(10000,99999)
                    i=0
                    checkcc=0
                    for i in range(len(filessr)):
                        if int(filessr[i][0])==cc:
                            checkcc=1
                            break
                    if checkcc==0:
                        break


                cur.execute("""INSERT INTO filesappunti (codice,nome,etichetta,pagine,prezzo,anno,corso,info)
        VALUES ("""+str(cc)+""",  '"""+form.cleaned_data['nome']+"""', '"""+form.cleaned_data['etichetta']+"""',"""+str(pagine)+""","""+str(prezzo)+""","""+str(anno)+""","""+str(codicecorso)+""",'"""+form.cleaned_data['info']+"""')""")
                con.commit()
            
                messages.success(request, 'Appunto inserito CORRETTAMENTE')
                error=False
        else:
            messages.success(request, 'Inserisci tutti i campi richiesti')


    return render(request, "addapp.html",{'error':error,'loggato':True,'founder':True,'admin':True,'listacorsi':listacorsi})


def imposta(request):
    coock=cookies(request)
    if (coock!=2) and (coock!=3):
        return redirect("/")

    founder=False
    if coock==3:
        founder=True

    error=True

    con = sqlite3.connect('appuntiunipvdb.db')
    cur = con.cursor()
    q=cur.execute("SELECT codiceutente FROM sessioniappunti WHERE codice='"+request.COOKIES.get('sessione')+"';")
    r=q.fetchall()
    if len(r)!=0:
        pp=r[0][0]

    q=cur.execute("SELECT codice,nome FROM filesappunti;")
    r=q.fetchall()
    filessr=r

    q=cur.execute("SELECT * FROM possessofileappunti;")
    r=q.fetchall()
    possessofiler=r

    listafil=[]
    i=0
    for i in range(len(filessr)):
        if founder==False:
            j=0
            for j in range(len(possessofiler)):
                if (filessr[i][0]==possessofiler[j][0]) and (possessofiler[j][1]==pp) and (possessofiler[j][2]==2):
                    listafil.append("- "+str(filessr[i][0])+" "+filessr[i][1])
                    break
        else:
            listafil.append("- "+str(filessr[i][0])+" "+filessr[i][1])

    #print(listafil)

    if request.method == 'POST':
        form = ImpostaApp(request.POST)
        if form.is_valid():
            nomeutente=form.cleaned_data['nomeutente']
            codicefile=form.cleaned_data['codicefile']

            password=form.cleaned_data['password']

            checkform=0

            try:
                codicefile=int(codicefile)
            except:
                checkform=1
                messages.success(request, 'Il campo Codice File deve essere solo numerico')

            if " " in nomeutente:
                checkform=1
                messages.success(request, 'Il nome utente non deve contenere spazi')

            q=cur.execute("SELECT codice,nomeutente,pex FROM utentiappunti;")
            r=q.fetchall()
            utentir=r

            i=0
            salvaidu=0
            for i in range(len(utentir)):
                if nomeutente==utentir[i][1]:
                    salvaidu=utentir[i][0]
                    break
            
            if (salvaidu==0) and (password==""):
                checkform=1
                messages.success(request, 'Nessun utente corrisponde al nome inserito')
            elif (salvaidu!=0) and (password!=""):
                checkform=1
                messages.success(request, 'Il nome utente inserito è già in uso')

            if founder==True:
                if form.cleaned_data['tipo']=="":
                    checkform=1
                    messages.success(request, 'Tipo Associazione mancante')
                elif (form.cleaned_data['tipo']!="1") and (form.cleaned_data['tipo']!="2"):
                    checkform=1
                    messages.success(request, 'Tipo Associazione può essere solo 1 o 2')
                else:
                    tipo=int(form.cleaned_data['tipo'])
            else:
                tipo=1

            if checkform!=1:
                i=0
                filecheck=0
                for i in range(len(filessr)):
                    if codicefile==filessr[i][0]:
                        filecheck=1
                        break

                if filecheck==0:
                    checkform=1
                    messages.success(request, 'Il Codice File non corrisponde a nessun File')
            
            if (founder==False) and (checkform!=1):
                i=0
                possessocheck=0
                for i in range(len(possessofiler)):
                    if (codicefile==possessofiler[i][0]) and (pp==possessofiler[i][1]) and (possessofiler[i][2]==2):
                        possessocheck=1
                        break
                
                if possessocheck==0:
                    checkform=1
                    messages.success(request, 'Non hai il permesso di assegnare questo File')

            if checkform!=1:

                if password!="":
                    pex=tipo

                    while True:
                        cod=random.randint(10000,99999)
                        i=0
                        checkc=0
                        for i in range(len(utentir)):
                            if cod==utentir[i][0]:
                                checkc=1
                                break
                        if checkc==0:
                            break
                    
                    cur.execute("""INSERT INTO utentiappunti (codice,nomeutente,password,pex)
            VALUES ("""+str(cod)+""",'"""+nomeutente+"""','"""+password+"""',"""+str(pex)+""")""")
                    con.commit()
                    salvaidu=cod

                cur.execute("""INSERT INTO possessofileappunti (codicefile,codiceutente,tipo)
        VALUES ("""+str(codicefile)+""","""+str(salvaidu)+""","""+str(tipo)+""")""")
                con.commit()

                if tipo==2:
                    i=0
                    utcheck=0
                    for i in range(len(utentir)):
                        if salvaidu==utentir[i][0]:
                            if (utentir[i][2]!=2) and (utenti[i][2]!=3):
                                utcheck=1
                                break
                    
                    if utcheck==1:
                        cur.execute("""UPDATE utentiappunti SET pex=2 WHERE codice="""+str(salvaidu)+""";""")
                        con.commit()

                messages.success(request, 'Impostazione inserita CORRETTAMENTE')
                error=False
        else:
            messages.success(request, 'Inserisci tutti i campi richiesti')

    return render(request, "imposta.html",{'error':error,'loggato':True,'founder':founder,'admin':True,'listafil':listafil})



def profilo(request):
    
    check=cookies(request)
    loggato=False

    if (check==1) or (check==2) or (check==3):
        loggato=True
    elif (check==-2):            #utente con cose che non esistono, cancello il cookie e redirecto home
        response=redirect("/")
        response.set_cookie(key='sessione',value='a',max_age=0)
        return response
    founder=False
    admin=False
    if check==3:
        founder=True
        admin=True
    if check==2:
        admin=True
    
    if loggato==False:
        return redirect("/")

    error=True

    con = sqlite3.connect('appuntiunipvdb.db')
    cur = con.cursor()
    q=cur.execute("SELECT codiceutente FROM sessioniappunti WHERE codice='"+request.COOKIES.get('sessione')+"';")
    r=q.fetchall()
    pp=0
    if len(r)!=0:
        pp=r[0][0]
    
    q=cur.execute("SELECT nomeutente FROM utentiappunti WHERE codice="+str(pp)+";")
    r=q.fetchall()
    if len(r)!=0:
        nomeutente=r[0][0]

    q=cur.execute("SELECT * FROM possessofileappunti;")
    r=q.fetchall()
    possessofiler=r

    cont=0
    i=0
    for i in range(len(possessofiler)):
        if (pp==possessofiler[i][1]) and (possessofiler[i][2]==1):
            cont=cont+1

    ruolo="Utente"
    if founder==True:
        ruolo="Founder"
    elif admin==True:
        ruolo="Venditore"

    q=cur.execute("SELECT * FROM filesappunti ORDER BY anno;")
    r=q.fetchall()
    filessordine=r

    j=0
    listaf=[]
    for j in range(len(filessordine)):
        loho=False
        if pp!=0:
            k=0
            for k in range(len(possessofiler)):
                if (possessofiler[k][0]==filessordine[j][0]) and (pp==possessofiler[k][1]):
                    loho=True
                    break
        if loho==True:
            info = {
                "nome": filessordine[j][1],
                "anno": str(filessordine[j][5]),
                "pagine": str(filessordine[j][3]),
                "prezzo": str(filessordine[j][4]),
                "codice": str(filessordine[j][0]),
                "loho": loho,
            }
            listaf.append(info)

    if request.method == 'POST':
        form = Cambiopassword(request.POST)
        if form.is_valid():
            vecchia=form.cleaned_data['vecchia']
            nuova=form.cleaned_data['nuova']

            pswcheck=0
            if ("'" in nuova) or ('"' in nuova) or (";" in nuova) or ("select" in nuova.lower()) or ("drop" in nuova.lower()):
                pswcheck==1
                messages.success(request, 'Caratteri non consentiti')

            if pswcheck==0:
                q=cur.execute("SELECT codice,password FROM utentiappunti;")
                r=q.fetchall()
                utentir=r

                i=0
                for i in range(len(utentir)):
                    if utentir[i][0]==pp:
                        if utentir[i][1]!=vecchia:
                            pswcheck=1
                            messages.success(request, 'Password Attuale errata')
                        break
            
            if pswcheck==0:
                cur.execute("""UPDATE utentiappunti SET password='"""+nuova+"""' WHERE codice="""+str(pp)+""";""")
                con.commit()

                error=False
                messages.success(request, 'Password cambiata con Successo')
        else:
            messages.success(request, 'Inserisci tutti i campi richiesti')

    return render(request, "profilo.html",{'error':error,'loggato':True,'founder':founder,'admin':admin,'nomeutente':nomeutente,'contacquisti':cont,'ruolo':ruolo,'listaf':listaf})

def file(request,id):

    check=cookies(request)
    loggato=False

    if (check==1) or (check==2) or (check==3):
        loggato=True
    elif (check==-2):            #utente con cose che non esistono, cancello il cookie e redirecto home
        response=redirect("/")
        response.set_cookie(key='sessione',value='a',max_age=0)
        return response
    founder=False
    admin=False
    if check==3:
        founder=True
        admin=True
    if check==2:
        admin=True

    con = sqlite3.connect('appuntiunipvdb.db')
    cur = con.cursor()
    q=cur.execute("SELECT * FROM filesappunti;")
    r=q.fetchall()
    filessr=r

    q=cur.execute("SELECT * FROM corsiappunti;")
    r=q.fetchall()
    corsir=r

    checkp=0
    i=0
    for j in range(len(filessr)):
        if filessr[j][0]==int(id):
            i=0
            for i in range(len(corsir)):
                if corsir[i][0]==filessr[j][6]:
                    nomecorso=corsir[i][1]
                    break

            info = {
                "nome": filessr[j][1],
                "etichetta": filessr[j][2],
                "anno": str(filessr[j][5]),
                "pagine": str(filessr[j][3]),
                "prezzo": str(filessr[j][4]),
                "codice": str(filessr[j][0]),
                "corso": str(filessr[j][6]),
                "info": filessr[j][7],
                "nomecorso": nomecorso,
            }
            checkp=1
            break
    #codice,nome,etichetta,pagine,prezzo,anno,corso,info

    if checkp==0:
        return redirect("/")

    pp=0
    possiedo=False
    if request.COOKIES.get('sessione'):
        q=cur.execute("SELECT codiceutente FROM sessioniappunti WHERE codice='"+request.COOKIES.get('sessione')+"';")
        r=q.fetchall()
        if len(r)!=0:
            pp=r[0][0]

    q=cur.execute("SELECT * FROM possessofileappunti WHERE codicefile="+str(id)+" AND codiceutente="+str(pp)+";")
    r=q.fetchall()
    if len(r)!=0:
        possiedo=True

    link=[]

    if possiedo==False:
        n=round(((int(info['pagine']))*20)/100)
        link.append(getlinkimage(int(id),n))

        n=round(((int(info['pagine']))*50)/100)
        link.append(getlinkimage(int(id),n))

        n=round(((int(info['pagine']))*80)/100)
        link.append(getlinkimage(int(id),n))
    else:
        i=0
        for i in range(int(info['pagine'])):
            link.append(getlinkimage(int(id),i+1))


    return render(request, "file.html",{'loggato':loggato,'founder':founder,'admin':admin,'info':info,'link':link,'possiedo':possiedo})


def logout(request):
    if (cookies(request))<=0:
        return redirect("/")

    con = sqlite3.connect('appuntiunipvdb.db')
    cur = con.cursor()
    q=cur.execute("SELECT * FROM sessioniappunti;")
    r=q.fetchall()
    sessionir=r

    s=request.COOKIES.get('sessione')
    test1=0
    i=0
    for i in range(len(sessionir)):
        if sessionir[i][0]==s:
            test1=1
            break
    if test1==1:
        cur.execute("UPDATE sessioniappunti SET codiceutente=0 WHERE codice='"+s+"';")
        con.commit()

    messages.success(request, 'Logout effettuato Correttamente!')
    return redirect("/")

def login(request):

    check=cookies(request)

    con = sqlite3.connect('appuntiunipvdb.db')
    cur = con.cursor()
    q=cur.execute("SELECT * FROM sessioniappunti;")
    r=q.fetchall()
    sessionir=r
    
    if (check==1) or (check==2) or (check==3):    #utente loggato normale o admin o founder
        return redirect("/")
    elif (check==-2):            #utente con cose che non esistono, cancello il cookie e redirecto home
        response=redirect("/")
        response.set_cookie(key='sessione',value='a',max_age=0)
        return response
    elif (check==-1):               #utente senza sessione, allora gli do una sessione
        while True:
            cod=secrets.token_hex(8)
            t=0
            i=0
            for i in range(len(sessionir)):
                if sessionir[i][0]==cod:
                    t=1
                    break
            if t==0:
                break

        cur.execute("""INSERT INTO sessioniappunti (codice,codiceutente,timestamp)
VALUES ('"""+cod+"""', 0, 0)""")
        con.commit()

        response=render(request, "login.html")
        response.set_cookie(key='sessione',value=cod,max_age=365*24*60*60)
        return response


    if request.method == 'POST':
        s=request.COOKIES.get('sessione')
        times=time.time()
        i=0
        for i in range(len(sessionir)):
            if s==sessionir[i][0]:
                suotimes=float(sessionir[i][2])
                break

        oktempo=0
        calc=times-suotimes
        minuti=int(int(calc)/60)
        if minuti<1:
            oktempo=1
            messages.success(request, "Devi attendere 1 minuto tra un tentativo e l'altro")

        q=cur.execute("SELECT * FROM utentiappunti;")
        r=q.fetchall()
        utentir=r

        if oktempo==0:
            form = Login(request.POST)
            if form.is_valid():
                nomeutente=form.cleaned_data['nomeutente']
                password=form.cleaned_data['password']
                i=0
                cc=0
                for i in range(len(utentir)):
                    if (utentir[i][1]==nomeutente) and (utentir[i][2]==password):
                        cc=utentir[i][0]
                        break
                
                if cc==0:
                    cur.execute("UPDATE sessioniappunti SET timestamp="+str(times)+" WHERE codice='"+s+"';")
                    con.commit()
                    messages.success(request, 'Nome utente o Password Errati')
                else:
                    test1=0
                    i=0
                    for i in range(len(sessionir)):
                        if sessionir[i][1]==cc:
                            soff=sessionir[i][0]
                            test1=1
                            break
                    if test1==1:
                        cur.execute("UPDATE sessioniappunti SET codiceutente=0 WHERE codice='"+soff+"';")
                        con.commit()

                    cur.execute("UPDATE sessioniappunti SET codiceutente="+str(cc)+" WHERE codice='"+s+"';")
                    con.commit()

                    messages.success(request, 'Login Effettuato Correttamente!')
                    return redirect("/")
            else:
                messages.success(request, 'Inserisci tutti i campi richiesti')

    return render(request, "login.html")