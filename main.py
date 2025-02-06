from flask import Flask, render_template, request, redirect, session, flash, jsonify
import os
from datetime import timedelta  # used for setting session timeout
import pandas as pd
import plotly
import plotly.express as px
import json
import warnings
import support

warnings.filterwarnings("ignore")

app = Flask(__name__)
app.secret_key = '\xdb\xb2oo!^x\x1e\x13\xf4P1\xfc\xbe\xa9\x8drY\x87\x97\xd1\xde\xac\xb1'

@app.route('/')
def login():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)
    if 'user_id' in session:  # if logged-in
        flash("Already a user is logged-in!")
        return redirect('/home')
    else:  # if not logged-in
        return render_template("login.html")

@app.route('/login_validation', methods=['POST'])
def login_validation():
    if 'user_id' not in session:  # if user not logged-in
        email = request.form.get('email')
        passwd = request.form.get('password')
        query = """SELECT * FROM user_login WHERE email LIKE '{}' AND password LIKE '{}'""".format(email, passwd)
        users = support.execute_query("search", query)
        if len(users) > 0:  # if user details matched in db
            session['user_id'] = users[0][0]
            return redirect('/home')
        else:  # if user details not matched in db
            flash("Invalid email and password!")
            return redirect('/')
    else:  # if user already logged-in
        flash("Already a user is logged-in!")
        return redirect('/home')

@app.route('/reset', methods=['POST'])
def reset():
    if 'user_id' not in session:
        email = request.form.get('femail')
        pswd = request.form.get('pswd')
        userdata = support.execute_query('search', """select * from user_login where email LIKE '{}'""".format(email))
        if len(userdata) > 0:
            try:
                query = """update user_login set password = '{}' where email = '{}'""".format(pswd, email)
                support.execute_query('insert', query)
                flash("Password has been changed!!")
                return redirect('/')
            except:
                flash("Something went wrong!!")
                return redirect('/')
        else:
            flash("Invalid email address!!")
            return redirect('/')
    else:
        return redirect('/home')

@app.route('/register')
def register():
    if 'user_id' in session:  # if user is logged-in
        flash("Already a user is logged-in!")
        return redirect('/home')
    else:  # if not logged-in
        return render_template("register.html")

@app.route('/registration', methods=['POST'])
def registration():
    if 'user_id' not in session:  # if not logged-in
        name = request.form.get('name')
        email = request.form.get('email')
        passwd = request.form.get('password')
        if len(name) > 5 and len(email) > 10 and len(passwd) > 5:  # if input details satisfy length condition
            try:
                query = """INSERT INTO user_login(username, email, password) VALUES('{}','{}','{}')""".format(name,
                                                                                                              email,
                                                                                                              passwd)
                support.execute_query('insert', query)

                user = support.execute_query('search',
                                             """SELECT * from user_login where email LIKE '{}'""".format(email))
                session['user_id'] = user[0][0]  # set session on successful registration
                flash("Successfully Registered!!")
                return redirect('/home')
            except:
                flash("Email id already exists, use another email!!")
                return redirect('/register')
        else:  # if input condition length not satisfy
            flash("Not enough data to register, try again!!")
            return redirect('/register')
    else:  # if already logged-in
        flash("Already a user is logged-in!")
        return redirect('/home')

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/feedback', methods=['POST'])
def feedback():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    sub = request.form.get("sub")
    message = request.form.get("message")
    flash("Thanks for reaching out to us. We will contact you soon.")
    return redirect('/')

@app.route('/home')
def home():
    if 'user_id' in session:  # if user is logged-in
        query = """select * from user_login where user_id = {} """.format(session['user_id'])
        userdata = support.execute_query("search", query)

        table_query = """select * from user_expenses where user_id = {} order by pdate desc""".format(
            session['user_id'])
        table_data = support.execute_query("search", table_query)
        df = pd.DataFrame(table_data, columns=['#', 'User_Id', 'Date', 'Expense', 'Amount', 'Note'])

        df = support.generate_df(df)
        try:
            earning, spend, invest, saving = support.top_tiles(df)
        except:
            earning, spend, invest, saving = 0, 0, 0, 0

        try:
            bar, pie, line, stack_bar = support.generate_Graph(df)
        except:
            bar, pie, line, stack_bar = None, None, None, None
        try:
            monthly_data = support.get_monthly_data(df, res=None)
            print("✅ Monthly Data:", monthly_data)
        except Exception as e:
            print("⚠ get_monthly_data() Error:", e)
            monthly_data = []
        try:
            card_data = support.sort_summary(df)
            print("✅ Card Data:", card_data)
        except Exception as e:
            print("⚠ sort_summary() Error:", e)
            card_data = []

        try:
            goals = support.expense_goal(df)
            print("✅ Goals Data:", goals)
        except Exception as e:
            print("⚠ expense_goal() Error:", e)
            goals = []
        try:
            size = 240
            pie11 = support.makePieChart(df, 'Earning', 'Month_name', size=size)
            pie22 = support.makePieChart(df, 'Spend', 'Day_name', size=size)
            pie33 = support.makePieChart(df, 'Investment', 'Year', size=size)
            pie44 = support.makePieChart(df, 'Saving', 'Note', size=size)
            pie55 = support.makePieChart(df, 'Saving', 'Day_name', size=size)
            pie66 = support.makePieChart(df, 'Investment', 'Note', size=size)
        except:
            pie11, pie22, pie33, pie44, pie55, pie66 = None, None, None, None, None, None
        return render_template('home.html',
                               user_name=userdata[0][1],
                               df_size=df.shape[0],
                               df=jsonify(df.to_json()),
                               earning=earning,
                               spend=spend,
                               invest=invest,
                               saving=saving,
                               monthly_data=monthly_data,
                               card_data=card_data,
                               goals=goals,
                               table_data=table_data[:4],
                               bar=bar,
                               line=line,
                               stack_bar=stack_bar,
                               pie1=pie11,
                               pie2=pie22,
                               pie3=pie33,
                               pie4=pie44,
                               pie5=pie55,
                               pie6=pie66,
                               )
    else:  # if not logged-in
        return redirect('/')

@app.route('/home/add_expense', methods=['POST'])
def add_expense():
    if 'user_id' in session:
        user_id = session['user_id']
        if request.method == 'POST':
            date = request.form.get('e_date')
            expense = request.form.get('e_type')
            amount = request.form.get('amount')
            notes = request.form.get('notes')
            try:
                query = """insert into user_expenses (user_id, pdate, expense, amount, pdescription) values 
                ({}, '{}','{}',{},'{}')""".format(user_id, date, expense, amount, notes)
                support.execute_query('insert', query)
                flash("Saved!!")
            except:
                flash("Something went wrong.")
                return redirect("/home")
            return redirect('/home')
    else:
        return redirect('/')

@app.route('/analysis')
def analysis():
    if 'user_id' in session:  # If user is logged in
        query = """SELECT * FROM user_login WHERE user_id = {}""".format(session['user_id'])
        userdata = support.execute_query('search', query)

        query2 = """SELECT pdate, expense, pdescription, amount FROM user_expenses WHERE user_id = {}""".format(
            session['user_id'])
        data = support.execute_query('search', query2)
        
        df = pd.DataFrame(data, columns=['Date', 'Expense', 'Note', 'Amount(₹)'])
        df = support.generate_df(df)  # Process DataFrame

        print("Analysis User Data:", userdata)  # Debugging line
        print("Analysis Data:", data)  # Debugging line
        
        pie, bar, line, scatter, heat, month_bar, sun = None, None, None, None, None, None, None

        if df.shape[0] > 0:  # Check if DataFrame is not empty
            # 🟢 Generate Graphs with Error Handling
            try:
                pie = support.meraPie(df=df, names='Expense', values='Amount(₹)', hole=0.7)
                print("✅ Pie Chart Generated")
            except Exception as e:
                print("⚠ Error in Pie Chart:", e)
                pie = json.dumps({})

            try:
                bar = support.meraBarChart(df=df.groupby(['Note', "Expense"], as_index=False).agg({'Amount(₹)': 'sum'}),
                                           x='Note', y='Amount(₹)', color="Expense")
                print("✅ Bar Chart Generated")
            except Exception as e:
                print("⚠ Error in Bar Chart:", e)
                bar = json.dumps({})

            try:
                line = support.meraLine(df=df, x='Date', y='Amount(₹)', color='Expense')
                print("✅ Line Chart Generated")
            except Exception as e:
                print("⚠ Error in Line Chart:", e)
                line = json.dumps({})

            try:
                scatter = support.meraScatter(df, 'Date', 'Amount(₹)', 'Expense', 'Amount(₹)')
                print("✅ Scatter Chart Generated")
            except Exception as e:
                print("⚠ Error in Scatter Chart:", e)
                scatter = json.dumps({})

            try:
                if 'Day_name' not in df.columns or 'Month_name' not in df.columns:
                    print("⚠ Warning: Heatmap columns missing")
                    heat = json.dumps({})
                else:
                    heat = support.meraHeatmap(df, 'Day_name', 'Month_name')
                    print("✅ Heatmap Generated")
            except Exception as e:
                print("⚠ Error in Heatmap:", e)
                heat = json.dumps({})

            try:
                month_bar = support.month_bar(df, 280)
                print("✅ Month Bar JSON:", month_bar)
                print("✅ Monthly Bar Chart Generated")
            except Exception as e:
                print("⚠ Error in Monthly Bar Chart:", e)
                month_bar = json.dumps({})

            try:
                sun = support.meraSunburst(df, 280)
                print("✅ Sunburst JSON:", sun)  
                print("✅ Sunburst Chart Generated")
            except Exception as e:
                print("⚠ Error in Sunburst Chart:", e)
                sun = json.dumps({})

            return render_template('analysis.html',
                                   user_name=userdata[0][1],
                                   pie=pie,
                                   bar=bar,
                                   line=line,
                                   scatter=scatter,
                                   heat=heat,
                                   month_bar=month_bar,
                                   sun=sun
                                   )
        else:
            print("⚠ No data available for analysis.")
            flash("No data records to analyze.")
            return redirect('/home')

    else:  # If not logged in
        return redirect('/')

@app.route('/profile')
def profile():
    if 'user_id' in session:  # if logged-in
        query = """select * from user_login where user_id = {} """.format(session['user_id'])
        userdata = support.execute_query('search', query)
        return render_template('profile.html', user_name=userdata[0][1], email=userdata[0][2])
    else:  # if not logged-in
        return redirect('/')

@app.route("/updateprofile", methods=['POST'])
def update_profile():
    name = request.form.get('name')
    email = request.form.get("email")
    query = """select * from user_login where user_id = {} """.format(session['user_id'])
    userdata = support.execute_query('search', query)
    query = """select * from user_login where email = "{}" """.format(email)
    email_list = support.execute_query('search', query)
    if name != userdata[0][1] and email != userdata[0][2] and len(email_list) == 0:
        query = """update user_login set username = '{}', email = '{}' where user_id = '{}'""".format(name, email,
                                                                                                      session[
                                                                                                          'user_id'])
        support.execute_query('insert', query)
        flash("Name and Email updated!!")
        return redirect('/profile')
    elif name != userdata[0][1] and email != userdata[0][2] and len(email_list) > 0:
        flash("Email already exists, try another!!")
        return redirect('/profile')
    elif name == userdata[0][1] and email != userdata[0][2] and len(email_list) == 0:
        query = """update user_login set email = '{}' where user_id = '{}'""".format(email, session['user_id'])
        support.execute_query('insert', query)
        flash("Email updated!!")
        return redirect('/profile')
    elif name == userdata[0][1] and email != userdata[0][2] and len(email_list) > 0:
        flash("Email already exists, try another!!")
        return redirect('/profile')

    elif name != userdata[0][1] and email == userdata[0][2]:
        query = """update user_login set username = '{}' where user_id = '{}'""".format(name, session['user_id'])
        support.execute_query('insert', query)
        flash("Name updated!!")
        return redirect("/profile")
    else:
        flash("No Change!!")
        return redirect("/profile")

@app.route('/logout')
def logout():
    try:
        session.pop("user_id")  # delete the user_id in session (deleting session)
        return redirect('/')
    except:  # if already logged-out but in another tab still logged-in
        return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
