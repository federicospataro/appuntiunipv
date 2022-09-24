from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from importlib_metadata import files
import mysql.connector
import time
import secrets
import hashlib
import random
from operator import attrgetter

from .forms import Login, AddApp, CorsiForm, ImpostaApp, Cambiopassword

global sessioni
global utenti
global filess
global corsi
global possessofile
global img

class Sessioni(object):
    def __init__(self,codice,codiceutente,timestamp):
        self.codice=codice
        self.codiceutente=codiceutente
        self.timestamp=timestamp

class Utenti(object):
    def __init__(self,codice,nomeutente,password,pex):
        self.codice=codice
        self.nomeutente=nomeutente
        self.password=password
        self.pex=pex

class Files(object):
    def __init__(self,codice,nome,etichetta,pagine,prezzo,anno,corso,info):
        self.codice=codice
        self.nome=nome
        self.etichetta=etichetta
        self.pagine=pagine
        self.prezzo=prezzo
        self.anno=anno
        self.corso=corso
        self.info=info #contatti, metodi di pagamento, prof, altre info, max 100 caratteri

class Corsi(object):
    def __init__(self,codice,nome):
        self.codice=codice
        self.nome=nome

class Possessofile(object):
    def __init__(self,codicefile,codiceutente,tipo):
        self.codicefile=codicefile
        self.codiceutente=codiceutente
        self.tipo=tipo

class Image(object):
    def __init__(self,codice,etichetta,pagina):
        self.codice=codice
        self.etichetta=etichetta
        self.pagina=pagina

def database():
    global mydb

    mydb = mysql.connector.connect(
      host="g4yltwdo6z0izlm6.chr7pe7iynqr.eu-west-1.rds.amazonaws.com",
      user="jz1u976ib94rhddq",
      passwd="m59m6z0mc0l6ko4r",
      database="gpf7ryl7vno85w8x"
    )

sessioni=[]
utenti=[]
filess=[]
corsi=[]
possessofile=[]
img=[]

database()
mydb.commit()
mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM sessioniappunti")
myresult = mycursor.fetchall()
i=0
for i in range(len(myresult)):
    sessioni.append(Sessioni(myresult[i][0],myresult[i][1],0))

mycursor.execute("SELECT * FROM utentiappunti")
myresult = mycursor.fetchall()
i=0
for i in range(len(myresult)):
    utenti.append(Utenti(myresult[i][0],myresult[i][1],myresult[i][2],myresult[i][3]))

mycursor.execute("SELECT * FROM filesappunti")
myresult = mycursor.fetchall()
i=0
for i in range(len(myresult)):
    filess.append(Files(myresult[i][0],myresult[i][1],myresult[i][2],myresult[i][3],myresult[i][4],myresult[i][5],myresult[i][6],myresult[i][7]))

mycursor.execute("SELECT * FROM corsiappunti")
myresult = mycursor.fetchall()
i=0
for i in range(len(myresult)):
    corsi.append(Corsi(myresult[i][0],myresult[i][1]))

mycursor.execute("SELECT * FROM possessofileappunti")
myresult = mycursor.fetchall()
i=0
for i in range(len(myresult)):
    possessofile.append(Possessofile(myresult[i][0],myresult[i][1],myresult[i][2]))

def cookies(request):
    if request.COOKIES.get('sessione'):
        c=request.COOKIES.get('sessione')

        pp=-1
        i=0
        for i in range(len(sessioni)):
            if sessioni[i].codice==c:
                pp=sessioni[i].codiceutente
                break
        if pp==0:
            return 0 #non loggato ma ha la sessione
        elif pp==-1:
            return -2 #ha una sessione che non esiste
        
        i=0
        pp2=-1
        for i in range(len(utenti)):
            if utenti[i].codice==pp:
                pp2=utenti[i].pex
                break

        if pp2==1:
            return 1 #loggato utente normale
        elif pp2==2:
            return 2 #loggato utente admin
        elif pp2==3:
            return 3 #loggato utente founder (serve per add appunti)
        elif pp2==-1:
            return -2 #loggato a un account che non esiste
        
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

"""
def reload(request):

    global sessioni
    global utenti
    global filess
    global corsi
    global possessofile

    if cookies(request)!=3:
        return redirect("/")

    sessioni=[]
    utenti=[]
    filess=[]
    corsi=[]
    possessofile=[]

    database()
    mydb.commit()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM sessioniappunti")
    myresult = mycursor.fetchall()
    i=0
    for i in range(len(myresult)):
        sessioni.append(Sessioni(myresult[i][0],myresult[i][1],0))

    mycursor.execute("SELECT * FROM utentiappunti")
    myresult = mycursor.fetchall()
    i=0
    for i in range(len(myresult)):
        utenti.append(Utenti(myresult[i][0],myresult[i][1],myresult[i][2],myresult[i][3]))

    mycursor.execute("SELECT * FROM filesappunti")
    myresult = mycursor.fetchall()
    i=0
    for i in range(len(myresult)):
        filess.append(Files(myresult[i][0],myresult[i][1],myresult[i][2],myresult[i][3],myresult[i][4],myresult[i][5],myresult[i][6],myresult[i][7]))

    mycursor.execute("SELECT * FROM corsiappunti")
    myresult = mycursor.fetchall()
    i=0
    for i in range(len(myresult)):
        corsi.append(Corsi(myresult[i][0],myresult[i][1]))

    mycursor.execute("SELECT * FROM possessofileappunti")
    myresult = mycursor.fetchall()
    i=0
    for i in range(len(myresult)):
        possessofile.append(Possessofile(myresult[i][0],myresult[i][1],myresult[i][2]))

    return redirect("/")
"""

def getimage(request,id):

    i=0
    pg=-1
    for i in range(len(img)):
        if img[i].codice==int(id):
            et=img[i].etichetta
            pg=img[i].pagina
            savei=i
            p=img[i]
            break

    if pg==-1:
        return redirect("/")

    img.remove(p)

    pathi="filesappunti/"+et+"/"+str(pg)+".jpg"
    image_data = open(pathi, "rb").read()

    #img.pop(i)

    return HttpResponse(image_data, content_type="image/png")

def getlinkimage(id,npagina):
    i=0
    et=""
    for i in range(len(filess)):
        if filess[i].codice==int(id):
            et=filess[i].etichetta
            break

    if et=="":
        return ""

    while True:
        nr=random.randint(10000,99999)
        i=0
        checknr=0
        for i in range(len(img)):
            if img[i].codice==nr:
                checknr=1
                break
        if checknr==0:
            break

    img.append(Image(nr,et,npagina))

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

    filessordine=sorted(filess, key=attrgetter('anno'))

    pp=0
    if request.COOKIES.get('sessione'):
        i=0
        pp=0
        for i in range(len(sessioni)):
            if sessioni[i].codice==request.COOKIES.get('sessione'):
                pp=sessioni[i].codiceutente
                break

    i=0
    listaappunti=[]
    for i in range(len(corsi)):
        listaf=[]
        j=0
        for j in range(len(filessordine)):
            if filessordine[j].corso==corsi[i].codice:
                loho=False
                if pp!=0:
                    k=0
                    for k in range(len(possessofile)):
                        if (possessofile[k].codicefile==filessordine[j].codice) and (pp==possessofile[k].codiceutente):
                            loho=True
                            break

                info = {
                    "nome": filessordine[j].nome,
                    "anno": str(filessordine[j].anno),
                    "pagine": str(filessordine[j].pagine),
                    "prezzo": str(filessordine[j].prezzo),
                    "codice": str(filessordine[j].codice),
                    "loho": loho,
                }
                listaf.append(info)
        
        if len(listaf)!=0:
            info = {
                "nome": corsi[i].nome,
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
            while True:
                cc=random.randint(10000,99999)
                i=0
                checkcc=0
                for i in range(len(corsi)):
                    if int(corsi[i].codice)==cc:
                        checkcc=1
                        break
                if checkcc==0:
                    break
            
            corsi.append(Corsi(cc,form.cleaned_data['nome']))
            database()
            mycursor = mydb.cursor()
            mycursor.execute("""INSERT INTO corsiappunti (codice,nome)
    VALUES ("""+str(cc)+""",  '"""+form.cleaned_data['nome']+"""')""")
            mydb.commit()
            messages.success(request, 'Corso aggiunto CORRETTAMENTE')
        else:
            messages.success(request, 'Inserisci tutti i campi richiesti')

    return redirect("/addappunti")


def addappunti(request):
    if cookies(request)!=3:
        return redirect("/")

    error=True

    listacorsi=[]
    i=0
    for i in range(len(corsi)):
        listacorsi.append("- "+str(corsi[i].codice)+" "+corsi[i].nome+"\n")

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

            try:
                anno=int(anno)
            except:
                checkform=1
                messages.success(request, 'Il campo anno deve essere solo numerico')

            i=0
            trovato=0
            for i in range(len(corsi)):
                if int(corsi[i].codice)==codicecorso:
                    trovato=1
                    break
            
            if trovato==0:
                messages.success(request, 'Il Codice Corso non corrisponde a nessun corso')
                checkform==1

            if checkform!=1:
                while True:
                    cc=random.randint(10000,99999)
                    i=0
                    checkcc=0
                    for i in range(len(filess)):
                        if int(filess[i].codice)==cc:
                            checkcc=1
                            break
                    if checkcc==0:
                        break

                filess.append(Files(cc,form.cleaned_data['nome'],form.cleaned_data['etichetta'],pagine,prezzo,anno,codicecorso,form.cleaned_data['info']))
                database()
                mycursor = mydb.cursor()
                mycursor.execute("""INSERT INTO filesappunti (codice,nome,etichetta,pagine,prezzo,anno,corso,info)
        VALUES ("""+str(cc)+""",  '"""+form.cleaned_data['nome']+"""', '"""+form.cleaned_data['etichetta']+"""',"""+str(pagine)+""","""+str(prezzo)+""","""+str(anno)+""","""+str(codicecorso)+""",'"""+form.cleaned_data['info']+"""')""")
                mydb.commit()
            
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

    i=0
    for i in range(len(sessioni)):
        if sessioni[i].codice==request.COOKIES.get('sessione'):
            pp=sessioni[i].codiceutente
            break

    listafil=[]
    i=0
    for i in range(len(filess)):
        if founder==False:
            j=0
            for j in range(len(possessofile)):
                if (filess[i].codice==possessofile[j].codicefile) and (possessofile[j].codiceutente==pp) and (possessofile[j].tipo==2):
                    listafil.append("- "+str(filess[i].codice)+" "+filess[i].nome)
                    break
        else:
            listafil.append("- "+str(filess[i].codice)+" "+filess[i].nome)

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

            i=0
            salvaidu=0
            for i in range(len(utenti)):
                if nomeutente==utenti[i].nomeutente:
                    salvaidu=utenti[i].codice
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
                for i in range(len(filess)):
                    if codicefile==filess[i].codice:
                        filecheck=1
                        break

                if filecheck==0:
                    checkform=1
                    messages.success(request, 'Il Codice File non corrisponde a nessun File')
            
            if (founder==False) and (checkform!=1):
                i=0
                possessocheck=0
                for i in range(len(possessofile)):
                    if (codicefile==possessofile[i].codicefile) and (pp==possessofile[i].codiceutente) and (possessofile[i].tipo==2):
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
                        for i in range(len(utenti)):
                            if cod==utenti[i].codice:
                                checkc=1
                                break
                        if checkc==0:
                            break
                    
                    database()
                    mycursor = mydb.cursor()
                    mycursor.execute("""INSERT INTO utentiappunti (codice,nomeutente,password,pex)
            VALUES ("""+str(cod)+""",'"""+nomeutente+"""','"""+password+"""',"""+str(pex)+""")""")
                    mydb.commit()

                    utenti.append(Utenti(cod,nomeutente,password,pex))
                    salvaidu=cod
                
                database()
                mycursor = mydb.cursor()
                mycursor.execute("""INSERT INTO possessofileappunti (codicefile,codiceutente,tipo)
        VALUES ("""+str(codicefile)+""","""+str(salvaidu)+""","""+str(tipo)+""")""")
                mydb.commit()

                possessofile.append(Possessofile(codicefile,salvaidu,tipo))

                if tipo==2:
                    i=0
                    utcheck=0
                    for i in range(len(utenti)):
                        if salvaidu==utenti[i].codice:
                            if (utenti[i].pex!=2) and (utenti[i].pex!=3):
                                utcheck=1
                                utenti[i].pex=2
                                break
                    
                    database()
                    mycursor = mydb.cursor()
                    mycursor.execute("""UPDATE utentiappunti SET pex=2 WHERE codice="""+str(salvaidu)+""";""")
                    mydb.commit()

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

    i=0
    pp=0
    for i in range(len(sessioni)):
        if sessioni[i].codice==request.COOKIES.get('sessione'):
            pp=sessioni[i].codiceutente
            break
    
    i=0
    for i in range(len(utenti)):
        if pp==utenti[i].codice:
            nomeutente=utenti[i].nomeutente
            break

    cont=0
    i=0
    for i in range(len(possessofile)):
        if (pp==possessofile[i].codiceutente) and (possessofile[i].tipo==1):
            cont=cont+1

    ruolo="Utente"
    if founder==True:
        ruolo="Founder"
    elif admin==True:
        ruolo="Venditore"

    j=0
    listaf=[]
    filessordine=sorted(filess, key=attrgetter('anno'))
    for j in range(len(filessordine)):
        loho=False
        if pp!=0:
            k=0
            for k in range(len(possessofile)):
                if (possessofile[k].codicefile==filessordine[j].codice) and (pp==possessofile[k].codiceutente):
                    loho=True
                    break
        if loho==True:
            info = {
                "nome": filessordine[j].nome,
                "anno": str(filessordine[j].anno),
                "pagine": str(filessordine[j].pagine),
                "prezzo": str(filessordine[j].prezzo),
                "codice": str(filessordine[j].codice),
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
                i=0
                for i in range(len(utenti)):
                    if utenti[i].codice==pp:
                        if utenti[i].password==vecchia:
                            utenti[i].password=nuova
                        else:
                            pswcheck=1
                            messages.success(request, 'Password Attuale errata')
                        break
            
            if pswcheck==0:
                database()
                mycursor = mydb.cursor()
                mycursor.execute("""UPDATE utentiappunti SET password='"""+nuova+"""' WHERE codice="""+str(pp)+""";""")
                mydb.commit()

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

    checkp=0
    i=0
    for j in range(len(filess)):
        if filess[j].codice==int(id):
            i=0
            for i in range(len(corsi)):
                if corsi[i].codice==filess[j].corso:
                    nomecorso=corsi[i].nome
                    break

            info = {
                "nome": filess[j].nome,
                "etichetta": filess[j].etichetta,
                "anno": str(filess[j].anno),
                "pagine": str(filess[j].pagine),
                "prezzo": str(filess[j].prezzo),
                "codice": str(filess[j].codice),
                "corso": str(filess[j].corso),
                "info": filess[j].info,
                "nomecorso": nomecorso,
            }
            checkp=1
            break
    #codice,nome,etichetta,pagine,prezzo,anno,corso,info

    if checkp==0:
        return redirect("/")

    possiedo=False
    i=0
    pp=0
    for i in range(len(sessioni)):
        if sessioni[i].codice==request.COOKIES.get('sessione'):
            pp=sessioni[i].codiceutente
            break

    i=0
    for i in range(len(possessofile)):
        if (int(id)==possessofile[i].codicefile) and (possessofile[i].codiceutente==pp):
            possiedo=True
            break

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

    database()
    mycursor = mydb.cursor()
    s=request.COOKIES.get('sessione')
    test1=0
    i=0
    for i in range(len(sessioni)):
        if sessioni[i].codice==s:
            sessioni[i].codiceutente=0
            test1=1
            break
    if test1==1:
        mycursor.execute("UPDATE sessioniappunti SET codiceutente=0 WHERE codice='"+s+"';")
        mydb.commit()

    messages.success(request, 'Logout effettuato Correttamente!')
    return redirect("/")

def login(request):

    check=cookies(request)
    
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
            for i in range(len(sessioni)):
                if sessioni[i].codice==cod:
                    t=1
                    break
            if t==0:
                break
        database()
        mycursor = mydb.cursor()
        mycursor.execute("""INSERT INTO sessioniappunti (codice,codiceutente)
VALUES ('"""+cod+"""', 0)""")
        mydb.commit()
        sessioni.append(Sessioni(cod, 0, 0))

        response=render(request, "login.html")
        response.set_cookie(key='sessione',value=cod,max_age=365*24*60*60)
        return response


    if request.method == 'POST':
        s=request.COOKIES.get('sessione')
        times=time.time()
        i=0
        for i in range(len(sessioni)):
            if s==sessioni[i].codice:
                suotimes=float(sessioni[i].timestamp)
                break

        oktempo=0
        calc=times-suotimes
        minuti=int(int(calc)/60)
        if minuti<1:
            oktempo=1
            messages.success(request, "Devi attendere 1 minuto tra un tentativo e l'altro")

        if oktempo==0:
            form = Login(request.POST)
            if form.is_valid():
                nomeutente=form.cleaned_data['nomeutente']
                password=form.cleaned_data['password']
                i=0
                cc=0
                for i in range(len(utenti)):
                    if (utenti[i].nomeutente==nomeutente) and (utenti[i].password==password):
                        cc=utenti[i].codice
                        break
                
                if cc==0:
                    
                    i=0
                    for i in range(len(sessioni)):
                        if s==sessioni[i].codice:
                            sessioni[i].timestamp=times
                            break
                    messages.success(request, 'Nome utente o Password Errati')
                else:
                    database()
                    mycursor = mydb.cursor()
                    test1=0
                    i=0
                    for i in range(len(sessioni)):
                        if sessioni[i].codiceutente==cc:
                            sessioni[i].codiceutente=0
                            soff=sessioni[i].codice
                            test1=1
                            break
                    if test1==1:
                        mycursor.execute("UPDATE sessioniappunti SET codiceutente=0 WHERE codice='"+soff+"';")
                        mydb.commit()

                    mycursor.execute("UPDATE sessioniappunti SET codiceutente="+str(cc)+" WHERE codice='"+s+"';")
                    mydb.commit()

                    i=0
                    for i in range(len(sessioni)):
                        if s==sessioni[i].codice:
                            sessioni[i].codiceutente=cc
                            break

                    messages.success(request, 'Login Effettuato Correttamente!')
                    return redirect("/")
            else:
                messages.success(request, 'Inserisci tutti i campi richiesti')

    return render(request, "login.html")