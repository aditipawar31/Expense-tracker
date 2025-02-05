import datetime
import pandas as pd
import sqlite3
import plotly
import plotly.express as px
import json


# Use this function for SQLITE3
def connect_db():
    conn = sqlite3.connect("expense.db")
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS user_login (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR(30) NOT NULL, 
        email VARCHAR(30) NOT NULL UNIQUE, password VARCHAR(20) NOT NULL)''')
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS user_expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, pdate DATE NOT 
        NULL, expense VARCHAR(10) NOT NULL, amount INTEGER NOT NULL, pdescription VARCHAR(50), FOREIGN KEY (user_id) 
        REFERENCES user_login(user_id))''')
    conn.commit()
    return conn, cur


def close_db(connection=None, cursor=None):
    """
    close database connection
    :param connection:
    :param cursor:
    :return: close connection
    """
    cursor.close()
    connection.close()


def execute_query(operation=None, query=None):
    """
    Execute Query
    :param operation:
    :param query:
    :return: data incase search query or write to database
    """
    connection, cursor = connect_db()
    if operation == 'search':
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        return data
    elif operation == 'insert':
        cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()
        return None


def generate_df(df):
    """
    create new features
    :param df:
    :return: df
    """
    df = df
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month_name'] = df['Date'].dt.month_name()
    df['Month'] = df['Date'].dt.month
    df['Day_name'] = df['Date'].dt.day_name()
    df['Day'] = df['Date'].dt.day
    df['Week'] = df['Date'].dt.isocalendar().week
    return df


def num2MB(num):
    """
        num: int, float
        it will return values like thousands(10K), Millions(10M),Billions(1B)
    """
    if num < 1000:
        return int(num)
    if 1000 <= num < 1000000:
        return f'{float("%.2f" % (num / 1000))}K'
    elif 1000000 <= num < 1000000000:
        return f'{float("%.2f" % (num / 1000000))}M'
    else:
        return f'{float("%.2f" % (num / 1000000000))}B'


def top_tiles(df=None):
    """
    Sum of total expenses
    :param df:
    :return: sum
    """
    if df is not None:
        tiles_data = df[['Expense', 'Amount']].groupby('Expense').sum()
        tiles = {'Earning': 0, 'Investment': 0, 'Saving': 0, 'Spend': 0}
        for i in list(tiles_data.index):
            try:
                tiles[i] = num2MB(tiles_data.loc[i][0])
            except:
                pass
        return tiles['Earning'], tiles['Spend'], tiles['Investment'], tiles['Saving']
    return


def generate_Graph(df=None):
    print("Input DataFrame for Graph Generation:", df)  # Debugging line
    
    if df is not None and df.shape[0] > 0:
        # ✅ Debug: Columns Exist or Not?
        print("DataFrame Columns:", df.columns)

        # 🟢 Bar Chart
        try:
            bar_data = df[['Expense', 'Amount']].groupby('Expense').sum().reset_index()
            print("Bar Data for Chart:", bar_data)  # Debugging line

            if not bar_data.empty:
                bar = px.bar(x=bar_data['Expense'], y=bar_data['Amount'], color=bar_data['Expense'], template="plotly_dark",
                             labels={'x': 'Expense Type', 'y': 'Balance (₹)'}, height=287)
                bar.update(layout_showlegend=False)
                bar.update_layout(margin=dict(l=2, r=2, t=40, b=2),
                                  paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                bar = json.dumps(bar, cls=plotly.utils.PlotlyJSONEncoder)
            else:
                bar = None
        except Exception as e:
            print("⚠ Bar Chart Error:", e)
            bar = None

        # 🟢 Stacked Bar Chart
        try:
            if 'Note' in df.columns and 'Expense' in df.columns:
                s = df.groupby(['Note', 'Expense'])[['Amount']].sum().reset_index()
                print("Stacked Data for Chart:", s)  # Debugging line

                if not s.empty:
                    stack = px.bar(x=s['Note'], y=s['Amount'], color=s['Expense'], barmode="stack", template="plotly_dark",
                                   labels={'x': 'Category', 'y': 'Balance (₹)'}, height=290)
                    stack.update(layout_showlegend=False)
                    stack.update_xaxes(tickangle=45)
                    stack.update_layout(margin=dict(l=2, r=2, t=30, b=2),
                                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    stack = json.dumps(stack, cls=plotly.utils.PlotlyJSONEncoder)
                else:
                    stack = None
            else:
                print("⚠ Error: 'Note' or 'Expense' column missing in DataFrame")
                stack = None
        except Exception as e:
            print("⚠ Stack Chart Error:", e)
            stack = None

        # 🟢 Line Chart
        try:
            line = px.line(df, x='Date', y='Amount', color='Expense', template="plotly_dark")
            line.update_xaxes(rangeslider_visible=True)
            line.update_layout(title_text='Track Record', title_x=0.,
                               legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                               margin=dict(l=2, r=2, t=30, b=2),
                               paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            line = json.dumps(line, cls=plotly.utils.PlotlyJSONEncoder)
        except Exception as e:
            print("⚠ Line Chart Error:", e)
            line = None

        # 🟢 Sunburst Pie Chart
        try:
            pie = px.sunburst(df, path=['Expense', 'Note'], values='Amount', height=280, template="plotly_dark")
            pie.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            pie = json.dumps(pie, cls=plotly.utils.PlotlyJSONEncoder)
        except Exception as e:
            print("⚠ Sunburst Pie Chart Error:", e)
            pie = None

        print("✅ Bar Graph JSON:", bar)
        print("✅ Pie Graph JSON:", pie)
        print("✅ Line Graph JSON:", line)
        print("✅ Stack Bar Graph JSON:", stack)
        
        return bar, pie, line, stack

    print("⚠ No data available for graph generation.")
    return None, None, None, None


def makePieChart(df=None, expense='Earning', names='Note', values='Amount', hole=0.5,
                 color_discrete_sequence=px.colors.sequential.RdBu, size=300, textposition='inside',
                 textinfo='percent+label', margin=2):
    fig = px.pie(df[df['Expense'] == expense], names=names, values=values, hole=hole,
                 color_discrete_sequence=color_discrete_sequence, height=size, width=size)
    fig.update_traces(textposition=textposition, textinfo=textinfo)
    fig.update_layout(annotations=[dict(text=expense, y=0.5, font_size=20, font_color='white', showarrow=False)])
    fig.update_layout(margin=dict(l=margin, r=margin, t=margin, b=margin),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update(layout_showlegend=False)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def meraBarChart(df=None, x=None, y=None, color=None, x_label=None, y_label=None, height=None, width=None,
                 show_legend=False, show_xtick=True, show_ytick=True, x_tickangle=0, y_tickangle=0, barmode='relative'):
    bar = px.bar(data_frame=df, x=x, y=y, color=color, template="plotly_dark", barmode=barmode,
                 labels={'x': x_label, 'y': y_label}, height=height, width=width)
    bar.update(layout_showlegend=show_legend)
    bar.update_layout(
        margin=dict(l=2, r=2, t=2, b=2),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)')
    bar.update_layout(xaxis=dict(showticklabels=show_xtick, tickangle=x_tickangle),
                      yaxis=dict(showticklabels=show_ytick, tickangle=y_tickangle))

    return json.dumps(bar, cls=plotly.utils.PlotlyJSONEncoder)


def get_monthly_data(df, year=datetime.datetime.today().year, res='int'):
    if 'Year' not in df.columns or 'Month' not in df.columns:
        print("⚠ Error: 'Year' or 'Month' column missing in DataFrame")
        return []

    df['Month'] = pd.to_numeric(df['Month'], errors='coerce')  # Ensure Month is numeric
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')  # Ensure Year is numeric

    if df['Year'].isna().sum() > 0 or df['Month'].isna().sum() > 0:
        print("⚠ Error: NaN values found in Year or Month column")
        return []

    temp = pd.DataFrame()
    d_year = df[df['Year'] == year][['Expense', 'Amount', 'Month']]

    if d_year.empty:
        print(f"⚠ No data available for year {year}")
        return []

    d_month = d_year.groupby("Month")
    for month in list(d_month.groups.keys())[::-1][:3]:
        dexp = d_month.get_group(month).groupby('Expense').sum().reset_index()

        temp = pd.concat([temp, pd.DataFrame({"Expense": dexp["Expense"], "Amount": dexp["Amount"], "Month": month})], ignore_index=True)

    month_name = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: "July", 8: 'August',
                  9: "September", 10: "October", 11: "November", 12: "December"}

    ls = []
    for month in list(d_month.groups.keys())[::-1][:3]:
        m = {}
        s = temp[temp['Month'] == month]
        m['Month'] = month_name.get(month, "Unknown")
        for i in range(s.shape[0]):
            if res == 'int':
                m[s.iloc[i]['Expense']] = int(s.iloc[i]['Amount'])
            else:
                m[s.iloc[i]['Expense']] = num2MB(int(s.iloc[i]['Amount']))
        ls.append(m)

    return ls


def sort_summary(df):
    """
    Generate summary data for dashboard cards.
    :param df: Dataframe
    :return: list of dictionaries
    """
    # ✅ Ensure required columns exist
    if not {'Year', 'Month_name', 'Expense', 'Amount', 'Date', 'Week', 'Day'}.issubset(df.columns):
        print("⚠ Error: Required columns missing in DataFrame")
        return []

    df['Month_name'] = df['Month_name'].astype(str)  # Ensure Month_name is string
    
    datas = []

    # 🟢 1. **Highest income month**
    h_month, h_year, h_amount = [], [], []

    try:
        for year in df['Year'].unique():
            yearly_data = df[df['Year'] == year]
            if yearly_data.empty:
                continue

            earning_data = yearly_data[yearly_data['Expense'] == 'Earning']
            if earning_data.empty:
                print(f"⚠ No Earning data for year {year}")
                continue

            top_earning_month = earning_data.groupby("Month_name")['Amount'].sum().reset_index().sort_values("Amount", ascending=False)

            if not top_earning_month.empty:
                h_month.append(top_earning_month.iloc[0]['Month_name'])
                h_year.append(year)
                h_amount.append(top_earning_month.iloc[0]['Amount'])

        if h_amount:
            max_amount = max(h_amount)
            best_month = h_month[h_amount.index(max_amount)]
            best_year = h_year[h_amount.index(max_amount)]
            datas.append({'head': f"₹{num2MB(max_amount)}", 'main': f"{best_month}'{str(best_year)[2:]}", 'msg': "Highest income in a month"})

    except Exception as e:
        print("⚠ Error in calculating highest income month:", e)

    # 🟢 2. **Per Day Average Income**
    try:
        per_day_income = df[df['Expense'] == 'Earning']['Amount'].sum() / df['Date'].nunique()
        datas.append({'head': 'Income', 'main': f"₹{num2MB(per_day_income)}", 'msg': "You earn every day"})
    except Exception as e:
        print("⚠ Error in calculating per day income:", e)

    # 🟢 3. **Per Week Average Saving**
    try:
        per_week_saving = df[df['Expense'] == 'Saving'].groupby('Week')['Amount'].sum().mean()
        datas.append({'head': 'Saving', 'main': f"₹{num2MB(per_week_saving)}", 'msg': "You save every week"})
    except Exception as e:
        print("⚠ Error in calculating weekly saving:", e)

    # 🟢 4. **Per Month Income & Spend**
    try:
        monthly_earning = df[df['Expense'] == 'Earning'].groupby('Month')['Amount'].sum().reset_index()['Amount'].mean()
        monthly_spending = df[df['Expense'] == 'Spend'].groupby('Month')['Amount'].sum().reset_index()['Amount'].mean()
        
        # 🟢 5. **Per Month Spend % of Income**
        monthly_spend_percentage = (monthly_spending / monthly_earning) * 100 if monthly_earning != 0 else 0
        datas.append({'head': 'Spend', 'main': f"{round(monthly_spend_percentage, 2)}%", 'msg': "You spend every month"})
    except Exception as e:
        print("⚠ Error in calculating monthly spend percentage:", e)

    # 🟢 6. **Every Minute Investment**
    try:
        every_minute_investment = df[df['Expense'] == 'Investment'].groupby('Day')['Amount'].sum().mean() / (24 * 60)
        datas.append({'head': 'Invest', 'main': f"₹{round(every_minute_investment, 2)}", 'msg': "You invest every minute"})
    except Exception as e:
        print("⚠ Error in calculating investment per minute:", e)

    return datas



def expense_goal(df):
    if 'Expense' not in df.columns:
        print("⚠ Error: 'Expense' column missing in DataFrame")
        return []

    goal_ls = []
    monthly_data = get_monthly_data(df, res='int')

    if not monthly_data:
        print("⚠ Error: No monthly data available for expense goal calculation.")
        return []

    for expense in df['Expense'].unique():
        dic = {'type': expense}
        x = []

        try:
            for i in monthly_data[:2]:
                if expense in i:
                    x.append(i[expense])
                else:
                    x.append(0)  # Default to 0 if expense is missing

            if len(x) < 2:
                print(f"⚠ Warning: Not enough data for {expense}")
                continue

            first, second = x[0], x[1]
            diff = int(first) - int(second)
            percent = round((diff / second) * 100, 1) if second != 0 else 0

            dic['status'] = 'increased' if percent > 0 else 'decreased'
            dic['percent'] = abs(percent)
            dic['value'] = "₹" + num2MB(x[0])

            goal_ls.append(dic)

        except Exception as e:
            print(f"⚠ Error in processing {expense}:", e)

    return goal_ls


# --------------- Analysis -----------------
def meraPie(df=None, names=None, values=None, color=None, width=None, height=None, hole=None, hole_text=None,
            margin=None, hole_font=10):
    fig = px.pie(data_frame=df, names=names, values=values, color=color, hole=hole, width=width, height=height)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(annotations=[dict(text=hole_text, y=0.5, font_size=hole_font, showarrow=False)])
    fig.update_layout(margin=margin, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update(layout_showlegend=False)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def meraLine(df=None, x=None, y=None, color=None, slider=True, title=None, height=180, width=None, show_legend=True):
    # Line Chart
    line = px.line(data_frame=df, x=x, y=y, color=color, template="plotly_dark", height=height, width=width)
    line.update_xaxes(rangeslider_visible=slider)
    line.update(layout_showlegend=show_legend)
    line.update_layout(title_text=title, title_x=0.,
                       legend=dict(
                           orientation="h",
                           yanchor="bottom",
                           y=1.02,
                           xanchor="right",
                           x=1
                       ),
                       margin=dict(l=2, r=2, t=2, b=2),
                       paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
                       )
    return json.dumps(line, cls=plotly.utils.PlotlyJSONEncoder)


def meraScatter(df=None, x=None, y=None, color=None, size=None, slider=True, title=None, height=180, width=None,
                legend=False):
    if df is None or df.empty:
        print("⚠ Warning: Empty DataFrame in meraScatter()")
        return json.dumps({})

    if x not in df.columns or y not in df.columns or color not in df.columns:
        print(f"⚠ Error: Columns {x}, {y}, or {color} missing in DataFrame for Scatter Chart")
        return json.dumps({})

    # ✅ Check if size exists, else use a default
    if size not in df.columns:
        print(f"⚠ Warning: Column '{size}' missing, using default size")
        df['size'] = 10  # Assign a default size
        size = 'size'

    try:
        scatter = px.scatter(df, x=x, y=y, color=color, size=size, template="plotly_dark",
                             height=height, width=width)

        scatter.update_xaxes(rangeslider_visible=slider)
        scatter.update(layout_showlegend=legend)

        return json.dumps(scatter, cls=plotly.utils.PlotlyJSONEncoder)

    except Exception as e:
        print("⚠ Error in meraScatter():", e)
        return json.dumps({})


def meraHeatmap(df=None, x=None, y=None, text_auto=True, aspect='auto', height=None, width=None, title=None):
    fig = px.imshow(pd.crosstab(df[x], df[y]), text_auto=text_auto, aspect=aspect, height=height, width=width,
                    template='plotly_dark')
    fig.update(layout_showlegend=False)
    fig.update_layout(xaxis=dict(showticklabels=False),
                      yaxis=dict(showticklabels=False))
    fig.update_layout(title_text=title, title_x=0.5,
                      margin=dict(l=2, r=2, t=30, b=2),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
                      )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def month_bar(df=None, height=None, width=None):
    if df is None or df.empty:
        print("⚠ Warning: Empty DataFrame in month_bar()")
        return json.dumps({})  # Return empty JSON if no data
    
    # ✅ Ensure 'Month' column is numeric
    if 'Month' in df.columns:
        df['Month'] = pd.to_numeric(df['Month'], errors='coerce')

    # ✅ Ensure 'Amount(₹)' column exists
    if 'Amount(₹)' not in df.columns:
        print("⚠ Error: 'Amount(₹)' column missing in DataFrame")
        return json.dumps({})

    try:
        # ✅ Group by Month and Expense
        t = df.groupby(['Month', 'Expense'])[['Amount(₹)']].sum().reset_index()

        # ✅ Sort data by Month
        t = t.sort_values(by=['Month'])

        # ✅ Convert Month numbers to Month names
        month_mapping = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }

        t['Month'] = t['Month'].map(month_mapping)

        # ✅ Create Bar Chart with Proper Stacking
        fig = px.bar(t, x='Month', y='Amount(₹)', color='Expense', text_auto=True, height=height, width=width,
                     template='plotly_dark', barmode="stack")

        fig.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))

        fig.update_layout(margin=dict(l=2, r=2, t=30, b=2),
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    except Exception as e:
        print("⚠ Error in month_bar():", e)
        return json.dumps({})


def meraSunburst(df=None, height=None, width=None):
    if df is None or df.empty:
        print("⚠ Warning: Empty DataFrame in meraSunburst()")
        return json.dumps({})  # Return empty JSON if no data

    if 'Year' not in df.columns or 'Expense' not in df.columns or 'Note' not in df.columns or 'Amount(₹)' not in df.columns:
        print("⚠ Error: Required columns missing in DataFrame for Sunburst")
        return json.dumps({})

    try:
        # ✅ Group by Year, Expense Type, and Category
        fig = px.sunburst(df, path=['Year', 'Expense', 'Note'], values='Amount(₹)', height=height, width=width,
                          template="plotly_dark", color='Expense')

        fig.update_layout(margin=dict(l=1, r=1, t=1, b=1),
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    except Exception as e:
        print("⚠ Error in meraSunburst():", e)
        return json.dumps({})
