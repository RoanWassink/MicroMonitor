from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User, System, CPU, Systemtest
from datetime import datetime, date, time, timedelta
from app.forms import EditProfileForm
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#from matplotlib.figure import Figure
import matplotlib.pyplot as pyplot
import matplotlib.dates as mdates
import matplotlib
import io
import base64

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index', methods=['GET'])
@login_required
def index():



    systems = db.session.query(System.system_id, System.cpu_usage, System.timestamp).all()

    sortparams = {'sortby': 'column_name', 'sortdir': 'asc'}
    return render_template('index.html', title='Home', systems=systems, sortparams=sortparams)




@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'System 1'},
        {'author': user, 'body': 'System 2'}
    ]
    return render_template('user.html', user=user, posts=posts)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
@app.route('/monitoring', methods=['GET', 'POST'])
@login_required
def monitoring():
    session = db.session
    systemSelection = request.form.get("system")


    if systemSelection is None:
        #Query cpu_usage
        query= session.query(System.cpu_usage).filter_by(system_id = 'ubuntu').all()
        #query Timestamps
        query2 = session.query(System.timestamp).filter_by(system_id='ubuntu').all()
        systemSelection = 'ubuntu'
    else:
        query2 = session.query(System.timestamp).filter_by(system_id=systemSelection).all()
        query = session.query(System.cpu_usage).filter_by(system_id=systemSelection).all()








    x = []
    y = []
    #add cpu usage to x
    for row in query:
        x.append(row)


    #add timestamp to y
    for row2 in query2:
        y.append(row2)

    datenow = datetime.now()
    dstart = datenow - timedelta(days=1)
    days= mdates.DateFormatter('%d')
    hours_fmt = mdates.DateFormatter('%H')
    hours = mdates.HourLocator()
    #draw the graph
    figure = pyplot.figure(figsize=(10, 10))
    figure.autofmt_xdate()
    ax = pyplot.axes()
    ax.plot(y, x)
    ax.set_title(str(systemSelection))
    ax.set_xlabel("Hours")
    ax.format_xdata = mdates.DateFormatter('%h:%m')
    ax.set_xlim(dstart, datenow)
    ax.set_ylim([0, 100])

    #ax.xaxis.set_major_locator(hours)

    ax.xaxis.set_major_formatter(hours_fmt)
    ax.xaxis.set_minor_formatter(days)
    ax.set_ylabel("CPU usage %")
    ax.grid()


    # Convert plot to PNG image
    pngImage = io.BytesIO()
    FigureCanvas(figure).print_png(pngImage)

    # Encode PNG image to base64 string
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')

    #query db for all system_id's
    systems = session.query(System.system_id).all()
    mylist= []
    #for loop to add the values from the db to a list
    for lists in systems:
        mylist.append(*lists._asdict().values())

    #make the list contain only distinct items by converting it to a set and back
    uniqueList = list(set(mylist))

    return render_template("image.html", image=pngImageB64String, systems=uniqueList)


