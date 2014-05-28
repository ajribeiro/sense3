from flask import Flask, session, request, render_template, redirect, url_for
import MySQLdb
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'zipfiles'
ALLOWED_EXTENSIONS = set(['zip'])



db = MySQLdb.connect(host="localhost", user="user",
                      passwd="pass", db="dbname")
cur = db.cursor()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = open('sk.txt','r').readline()


events = ['Pre-baseline CT',
'Baseline CT/CTP/CTA',
'Baseline MRI',
'DSA',
'12hr CT/CTP/CTA',
'12hr MRI',
'5day MRI',
'Miscellaneous 1',
'Miscellaneous 2',
'Miscellaneous 3',
'Miscellaneous 4',
'Miscellaneous 5',]

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def comp():
    if 'username' not in session: return redirect(url_for('login'))

    cur.execute("SELECT patientid,enrollment_time,update_time FROM events GROUP BY patientid")

    studylist, tlist, ulist = [], [], []
    for row in cur.fetchall() :
        studylist.append(row[0])
        tlist.append(row[1])
        ulist.append(row[2])

    return render_template('ctmrcomp.html',studylist=studylist, \
            tlist=tlist,ulist=ulist)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur.execute("SELECT password FROM login WHERE username='%s'" % username)

        if cur.rowcount < 1 or cur.fetchone()[0] != password:
            return redirect(url_for('login'))
        else:
            session['username'] = username
            return redirect('/')
    else:
        return render_template('login.html')

@app.route('/add_patient')
def add_patient():
    if 'username' not in session: return redirect(url_for('login'))
    return render_template('add_patient.html')

@app.route('/patient_info')
def patient_info():
    if 'username' not in session: return redirect(url_for('login'))

    patid = request.args.get('patid')

    cur.execute("SELECT * FROM events WHERE patientid = '%s'" % patid)

    allrows = cur.fetchall()
    print allrows

    return render_template('patient_info.html', patid=allrows[0][0], info=allrows)



@app.route('/create_patient', methods=['POST'])
def create_patient():
    if 'username' not in session: return redirect(url_for('login'))
    print request

    patientid = request.form['patientid']
    edate = request.form['edate']
    etime = request.form['etime']

    patid = patientid.replace('-','')
    print patientid
    cur.execute("SELECT DISTINCT patientid FROM events WHERE patientid='%s'" % patientid)
    # check for a new patient id
    if cur.rowcount < 1:
        for ev in events:
            cur.execute("INSERT INTO events (patientid, event, enrollment_date, enrollment_time, update_time, zipfile_path) VALUES ('%s', '%s', '%s', '%s', now(), NULL)" % (patientid, ev, edate, etime))
        db.commit()

    cur.execute("SELECT event,zipfile_path FROM events WHERE patientid='%s'" % patientid)
    paths = {}
    for row in cur.fetchall():
        paths[row[0]] = row[1]

    return redirect(url_for('enter_study_data',patientid=patientid,
                events=events, paths=paths))


@app.route('/enter_study_data', methods=['GET','POST'])
def enter_study_data():
    if 'username' not in session: return redirect(url_for('login'))

    print request
    if request.method == 'POST':
        for i in range(1,100):
            # print 'file%d' % i
            fnum = 'file%d' % i
            if fnum not in request.files: break
            file = request.files[fnum]
            event = request.form['picker1']
            patientid = request.form['patientid']
            print file,event,patientid
            if file and event:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                print "UPDATE events SET update_time=now(), zipfile_path='%s' WHERE patientid='%s' and event='%s';" % ('zipfiles/%s' % filename, patientid, event)
                cur.execute("UPDATE events SET update_time=now(), zipfile_path='%s' WHERE patientid='%s' and event='%s';" % ('zipfiles/%s' % filename, patientid, event))
                db.commit()
        return redirect('/')

    else:
        patientid = request.args.get('patientid')
        patientid.replace('-','')
        print patientid
        cur.execute("SELECT DISTINCT patientid FROM events WHERE patientid='%s'" % patientid)
        # check for a new patient id
        if cur.rowcount < 1:
            for ev in events:
                cur.execute("INSERT INTO events (patientid, event, enrollment_time, update_time, zipfile_path) VALUES ('%s', '%s', now(), NULL, NULL)" % (patientid, ev))
            db.commit()

        cur.execute("SELECT event,zipfile_path FROM events WHERE patientid='%s'" % patientid)
        paths = {}
        for row in cur.fetchall():
            paths[row[0]] = row[1]

        return render_template('enter_study_data.html',patientid=patientid,
                    events=events, paths=paths)


if __name__ == '__main__':
    app.debug = True
    app.run()
