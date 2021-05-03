from mysql import connector as mysql
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import hashlib

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'event_management'

admin_login = ""
user_signup = ""
user_login = ""
login = ""
username="Login"
user_email=""
login_error=""

@app.route('/')
def hello():
    return render_template("index.html",login=username)

@app.route('/login')
def login():
    global username, user_email
    username = "Login"
    user_email = ""
    return render_template("login.html",login="Login")

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/submit',methods=['GET','POST'])
def submit():
    if request.method == "POST":
        details = request.form
        name = details['name']
        email = details['email']
        occupation = details['occupation']
        address = details['address']
        mobile = details['mobile']
        Password = details['password']
        re_Password = details['re-password']
        if(Password == re_Password):
            con = mysql.connect(user='root', password='', host='localhost', database='event_management', port=3306)
            cur = con.cursor()
            if con.is_connected():
                print('Connected to MySQL database')
            cur.execute("INSERT INTO sign_up VALUES ('%s', '%s', '%s', '%s', '%s')" %(name,email,occupation,mobile,address))
            cur.execute("INSERT INTO login VALUES ('%s', '%s')" % (email,Password))
            con.commit()
            return render_template("login.html")
        else:
            user_signup = "Password doesn't Match"
            return render_template("signup.html",user_signup = user_signup)

@app.route('/login_submit',methods=['GET','POST'])
def login_submit():
    if request.method == "POST":
        details = request.form
        email = details['email']
        password = details['password']
        con = mysql.connect(user='root', password='', host='localhost', database='event_management', port=3306)
        cur = con.cursor()
        if con.is_connected():
            print('Connected to MySQL database')
        cur.execute("SELECT Password from login where Email = '%s'" % (email))
        records = cur.fetchall()
        if(records[0][0] == password):
            cur.execute("SELECT Name from sign_up where Email = '%s'" % (email))
            records = cur.fetchall()
            global username,user_email
            username=records[0][0]
            user_email = email
            return render_template("index.html", login=records[0][0])
        else:
            return render_template("login.html",login = login,login_error="Username and Password doesn't Match")


@app.route('/admin_login')
def admin_login():
    return render_template("admin_login.html")

@app.route('/admin_submit',methods=['GET','POST'])
def admin_submit():
    if request.method == "POST":
        details = request.form
        name = details['name']
        password = details['password']
        print(name,password)
        if(name =="admin" and password=="admin@123"):
            return render_template("event_registration.html")
        else:
            admin_login = "Username and Password Doesn't match"
            return render_template("admin_login.html",admin_login=admin_login)

@app.route('/event_registration')
def event_registration():
    return render_template("event_registration.html")

@app.route('/add_event',methods=['GET','POST'])
def add_event():
    if request.method == "POST":
        details = request.form
        name = details['name']
        domain = details['domain']
        city = details['city']
        date_time = details['date_time']
        price = details['price']
        time = date_time[list(date_time).index('T')+1:]
        d = datetime.strptime(time, "%H:%M")
        date = date_time[:list(date_time).index('T')]
        con = mysql.connect(user='root', password='', host='localhost', database='event_management', port=3306)
        cur = con.cursor()
        if con.is_connected():
            print('Connected to MySQL database')
        print("INSERT INTO event_details (Name, Domain,City, Date and Time, Ticket price) VALUES ('%s', '%s', '%s', '%s %s', %d)" % (name, domain, city, date,d, int(price)))
        cur.execute(
            "INSERT INTO event_details (`Name`, `Domain`, `City`, `Date and Time`, `Ticket Price`, `Event_ID`) VALUES ('%s', '%s', '%s','%s %s', %d , NULL)" % (name, domain, city, date,d, int(price)))
        con.commit()
        return render_template("login.html")

@app.route('/events')
def events():
    con = mysql.connect(user='root', password='', host='localhost', database='event_management', port=3306)
    cur = con.cursor()
    if con.is_connected():
        print('Connected to MySQL database')
    cur.execute("SELECT * FROM event_details")
    records = cur.fetchall()
    con.commit()
    return render_template("event.html",records = records,login=username)

@app.route('/event_register',methods=['GET','POST'])
def event_register():
    if(request.method=='POST'):
        if(username == ""):
            return render_template("login.html",login_error = "Please Login to Register")
        con = mysql.connect(user='root', password='', host='localhost', database='event_management', port=3306)
        cur = con.cursor()
        if con.is_connected():
            print('Connected to MySQL database')
        cur.execute("SELECT `Name`, `City`, `Date and Time` FROM event_details where Event_ID = %d" %(int(request.form['register'])))
        records = cur.fetchall()
        return render_template("user_event_register.html",id=request.form['register'],name=records[0][0],email=user_email,city=records[0][1],date_time = records[0][2],login=username)

@app.route('/submit_register_event',methods=['GET','POST'])
def submit_register_event():
    if request.method == "POST":
        details = request.form
        id = details['id']
        name = details['name']
        print(list(details.keys()))
        email = details['email']

        date_time = details['date_time']
        con = mysql.connect(user='root', password='', host='localhost', database='event_management', port=3306)
        cur = con.cursor()
        cur.execute("SELECT Email FROM registration_details where Event_ID = %d" %(int(id)))
        f = 1
        for i in cur.fetchall():
            if(i[0]==user_email):
                cur.execute("SELECT * FROM event_details")
                return render_template("event.html",flag = 0,records=cur.fetchall(),login=username)

        cur.execute(
            "UPDATE event_details SET `Registered No. of Tickets` = `Registered No. of Tickets` + 1 where Event_ID = %d" % (
                int(id)))
        con.commit()
        cur.execute("SELECT `Ticket Price`, `Registered No. of Tickets` FROM event_details where Event_ID = %d" % (int(id)))
        records = cur.fetchall()
        transaction_id = name[:2]+str(id)+str(records[0][1])+str(hashlib.md5(user_email.encode("utf-8")).hexdigest())[:5]

        if con.is_connected():
            print('Connected to MySQL databases')
        print("INSERT INTO registration_details VALUES ('%s', '%s', '%s', %d, '%s')" % (id, email,date_time, int(records[0][0]), transaction_id))
        cur.execute(
            "INSERT INTO registration_details VALUES (%d, '%s', '%s', %d, '%s')" % (int(id), email,date_time, int(records[0][0]), transaction_id))

        con.commit()
        cur.execute("SELECT * FROM event_details")
        records = cur.fetchall()
        return render_template("event.html",flag = 1,records=records,login=username)

@app.route('/registered_events')
def registered_events():
    con = mysql.connect(user='root', password='', host='localhost', database='event_management', port=3306)
    cur = con.cursor()
    if con.is_connected():
        print('Connected to MySQL database')
    if(user_email==""):
        return render_template("login.html", login_error="Please Login to View Registered Event Details")
    cur.execute("SELECT r.`Event_ID`,r.`Email`,r.`Date and Time`,r.`Ticket Price`,r.`Transaction ID`,e.Name FROM "
                "`registration_details`as r, `event_details` as e "
                "WHERE r.Email = '%s' and r.Event_ID = e.Event_ID" %(user_email))
    records = cur.fetchall()
    con.commit()
    return render_template("Registered Events.html",records = records,login=username)

@app.route('/cancel')
def cancel():
    if request.method == "GET":
        t_id = request.args.get('transaction_id')
        e_id = request.args.get('event_id')
        print(t_id,e_id)
        con = mysql.connect(user='root', password='', host='localhost', database='event_management', port=3306)
        x = str(datetime.now())
        cur = con.cursor()
        cur.execute(
            "SELECT `Date and Time` FROM registration_details where `Transaction ID` = '%s';" % (
            t_id))
        results = cur.fetchall()
        cur.execute("SELECT DATEDIFF( '%s', '%s');" %(results[0][0],x))
        results= cur.fetchall()
        cur.execute("SELECT r.`Event_ID`,r.`Email`,r.`Date and Time`,r.`Ticket Price`,r.`Transaction ID`,e.Name FROM "
                    "`registration_details`as r, `event_details` as e "
                    "WHERE r.Email = '%s' and r.Event_ID = e.Event_ID" % (user_email))
        records = cur.fetchall()
        if(results[0][0] >=1):
            cur.execute("DELETE FROM registration_details WHERE `Transaction ID` = '%s';" % (t_id))
            cur.execute(
                "UPDATE event_details SET `Registered No. of Tickets` = `Registered No. of Tickets` - 1 where Event_ID = %d" % (
                    int(e_id)))
            con.commit()
            cur.execute(
                "SELECT r.`Event_ID`,r.`Email`,r.`Date and Time`,r.`Ticket Price`,r.`Transaction ID`,e.Name FROM "
                "`registration_details`as r, `event_details` as e "
                "WHERE r.Email = '%s' and r.Event_ID = e.Event_ID" % (user_email))
            records = cur.fetchall()
            return render_template("Registered Events.html", flag=1,records=records,login=username)
        else:
            return render_template("Registered Events.html",flag=0,records=records,login=username)

@app.route("/domain_search",methods=['GET','POST'])
def domain_search():
    con = mysql.connect(user='root', password='', host='localhost', database='event_management', port=3306)
    domain = request.form['domain']
    cur = con.cursor()
    if con.is_connected():
        print('Connected to MySQL database')
    cur.execute("SELECT * FROM event_details where domain = '%s'" %(domain))
    records = cur.fetchall()
    con.commit()
    return render_template("admin.html", records=records)

@app.route('/admin_event')
def admin_event():
    con = mysql.connect(user='root', password='', host='localhost', database='event_management', port=3306)
    cur = con.cursor()
    if con.is_connected():
        print('Connected to MySQL database')
    cur.execute("SELECT * FROM event_details")
    records = cur.fetchall()
    con.commit()
    return render_template("admin.html",records = records)

@app.route("/admin_domain_search",methods=['GET','POST'])
def admin_domain_search():
    con = mysql.connect(user='root', password='', host='localhost', database='event_management', port=3306)
    domain = request.form['domain']
    cur = con.cursor()
    if con.is_connected():
        print('Connected to MySQL database')
    cur.execute("SELECT * FROM event_details where domain = '%s'" %(domain))
    records = cur.fetchall()
    con.commit()
    return render_template("admin.html", records=records)

if __name__ == '__main__':
    app.run()
