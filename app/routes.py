from itertools import chain

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import desc
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User, System
from datetime import datetime, date, time, timedelta
from app.forms import EditProfileForm
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_svg import FigureCanvasSVG
# from matplotlib.figure import Figure
import matplotlib.pyplot as pyplot, mpld3
from mpld3 import plugins
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

import io
import base64
session = db.session

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/')
@app.route('/index', methods=['GET'])
@login_required
def index():
    systems = session.query(System.system_id, System.os, System.cpu_cores_phys, System.memory_total,System.memory_percent,
                               System.cpu_freq_max, System.cpu_usage, System.timestamp, System.disk_free).all()


    return render_template('index.html', title='Home', systems=systems)


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

    systems = session.query(System.system_id).all()

    system_list = []
    # for loop to add the va
    # appends values from the db to mylist
    for lists in systems:
        system_list.append(*lists._asdict().values())

    uniqueList = list(set(system_list))
    system1, system2 = uniqueList
    print(system1)
    return render_template('user.html', user=user, systems=uniqueList )


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


@app.route('/cpu', methods=['GET', 'POST'])
@login_required
def cpu():
    css = """
       table
       {
         border-collapse: collapse;
       }
       th
       {
         color: #ffffff;
         background-color: #000000;
       }
       td
       {
         background-color: #cccccc;
       }
       table, th, td
       {
         font-family:Arial, Helvetica, sans-serif;
         border: 1px solid black;
         text-align: right;
       }
       """

    systemSelection = request.form.get("system")

    # Prevents error when first opening the page. Effectively makes 'ubuntu' the default selection.
    if systemSelection is None:
        # Query cpu_usage
        query = session.query(System.cpu_usage).filter_by(system_id='ubuntu').all()
        # query Timestamps
        query2 = session.query(System.timestamp).filter_by(system_id='ubuntu').all()
        systemSelection = 'ubuntu'
    else:
        query2 = session.query(System.timestamp).filter_by(system_id=systemSelection).all()
        query = session.query(System.cpu_usage).filter_by(system_id=systemSelection).all()

    cpu_list = []
    timestamp_list = []
    # add cpu usage to x
    for row in query:
        cpu_list.append(row)

    # add timestamp to y
    for row2 in query2:
        timestamp_list.append(row2)

    def flatten(listOfLists):
        "Flatten one level of nesting"
        return chain.from_iterable(listOfLists)

    # draw the graph
    figure = pyplot.figure(figsize=(15, 5))
    figure.autofmt_xdate()
    ax = pyplot.axes()
    cpu_list = list(flatten(cpu_list))
    time_list = list(flatten(timestamp_list))
    hour = []
    minute = []
    for time, cpu in zip(time_list, cpu_list):
        timehour = [
            "cpu " + str(cpu) + " time " + " " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second)]
        hour.append(timehour)


    labels = hour
    lines = ax.plot(time_list, cpu_list, marker='o', ls='-', ms=5)
    ax.fill_between(time_list, cpu_list)
    ax.set_title(str(systemSelection))
    ax.set_xlabel("Hours")
    ax.set_ylabel("CPU usage %")
    ax.grid()
    # query db for all system_id's
    systems = session.query(System.system_id).all()
    system_list = []
    # for loop to add the va
    # appends values from the db to mylist
    for lists in systems:
        system_list.append(*lists._asdict().values())

    tooltip = plugins.PointHTMLTooltip(lines[0], labels,
                                       voffset=10, hoffset=10, css=css)
    plugins.connect(figure, tooltip)
    html_text = mpld3.fig_to_html(figure)

    # make the list contain only distinct items by converting it to a set and back
    uniqueList = list(set(system_list))

    return render_template('cpu.html', plot=html_text, systems=uniqueList)


@app.route('/memory', methods=['GET', 'POST'])
@login_required
def memory():
    css = """
       table
       {
         border-collapse: collapse;
       }
       th
       {
         color: #ffffff;
         background-color: #000000;
       }
       td
       {
         background-color: #cccccc;
       }
       table, th, td
       {
         font-family:Arial, Helvetica, sans-serif;
         border: 1px solid black;
         text-align: right;
       }
       """
    session = db.session
    systemSelection = request.form.get("system")

    # Prevents error when first opening the page. Effectively makes 'ubuntu' the default selection.
    if systemSelection is None:
        # Query cpu_usage
        query = session.query(System.memory_percent).filter_by(system_id='ubuntu').all()
        # query Timestamps
        query2 = session.query(System.timestamp).filter_by(system_id='ubuntu').all()
        totalquery = session.query(System.memory_total).filter_by(system_id='ubuntu').first()
        systemSelection = 'ubuntu'
    else:
        query2 = session.query(System.timestamp).filter_by(system_id=systemSelection).all()
        query = session.query(System.memory_percent).filter_by(system_id=systemSelection).all()
        totalquery = session.query(System.memory_total).filter_by(system_id=systemSelection).first()


    cpu_list = []
    timestamp_list = []
    # add cpu usage to x
    for row in query:
        cpu_list.append(row)

    # add timestamp to y
    for row2 in query2:
        timestamp_list.append(row2)

    def flatten(listOfLists):
        "Flatten one level of nesting"
        return chain.from_iterable(listOfLists)

    # draw the graph
    figure = pyplot.figure(figsize=(10, 5))
    figure.autofmt_xdate()
    ax = pyplot.axes()
    cpu_list = list(flatten(cpu_list))
    time_list = list(flatten(timestamp_list))
    hour = []
    minute = []
    for time, cpu in zip(time_list, cpu_list):
        timehour = [
            "memory " + str(cpu) + " time " + " " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second)]
        hour.append(timehour)

    labels = hour
    lines = ax.plot(time_list, cpu_list, marker='o', ls='-', ms=5)
    ax.fill_between(time_list, cpu_list)
    ax.set_title(str("Memory usage for " + systemSelection + " total memory: " + str(totalquery[0])))
    ax.set_xlabel("Hours")
    ax.set_ylabel("Memory usage %")
    ax.grid()
    # query db for all system_id's
    systems = session.query(System.system_id).all()
    system_list = []
    # for loop to add the va
    # appends values from the db to mylist
    for lists in systems:
        system_list.append(*lists._asdict().values())

    tooltip = plugins.PointHTMLTooltip(lines[0], labels,
                                       voffset=10, hoffset=10, css=css)
    plugins.connect(figure, tooltip)
    html_text = mpld3.fig_to_html(figure)

    # make the list contain only distinct items by converting it to a set and back
    uniqueList = list(set(system_list))

    return render_template('memory.html', plot=html_text, systems=uniqueList)


@app.route('/disk', methods=['GET', 'POST'])
@login_required
def disk():

    session = db.session
    systemSelection = 'ubuntu'
    systemSelection = request.form.get("system")

    # Prevents error when first opening the page. Effectively makes 'ubuntu' the default selection.
    if systemSelection is None:
        # Query cpu_usage
        query = session.query(System.disk_free).filter_by(system_id='ubuntu').order_by(-System.timestamp).first()
        query2 = session.query(System.disk_used).filter_by(system_id='ubuntu').order_by(-System.timestamp).first()

        systemSelection = 'ubuntu'
    else:
        query = session.query(System.disk_free).filter_by(system_id=systemSelection).order_by(-System.timestamp).first()
        query2 = session.query(System.disk_used).filter_by(system_id=systemSelection).order_by(
            -System.timestamp).first()

    def get_size(bytes, suffix="B"):
        """
        Scale bytes to its proper format
        e.g:
            1253656 => '1.20MB'
            1253656678 => '1.17GB'
        """
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return f"{bytes:.2f} " + unit
            bytes /= factor


    figure = pyplot.figure(figsize=(5, 5))
    legendlabels = 'Free space ' + str(get_size(query[0])), 'Used space '+ str(get_size(query2[0]))
    labels = 'Free space', 'Used space'
    sizes = [query, query2]
    explode = (0, 0.1)  # only "explode" the 2nd slice

    ax1 = pyplot.axes()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax1.legend(legendlabels)
    ax1.set_title=systemSelection
    system_list = []
    systems = session.query(System.system_id).all()
    for lists in systems:
        system_list.append(*lists._asdict().values())

    uniqueList = list(set(system_list))

    html_text = mpld3.fig_to_html(figure)
    return render_template('disk.html', plot=html_text, systems=uniqueList, systemSelection=systemSelection)
@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html', title = 'About')