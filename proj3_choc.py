import sqlite3
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

# proj3_choc.py
# You can change anything in this file you want as long as you pass the tests
# and meet the project requirements! You will need to implement several new
# functions.

# Part 1: Read data from a database called choc.db
DBNAME = 'choc.sqlite'


# Part 1: Implement logic to process user commands
def process_command(command):
    command = command.strip()
    CMDS = ["bars", "companies", "countries", "regions"]
    REGIONS = ["none", "country=", "region="]
    TYPES_ = ["sell", "source"]
    SORTINGS = ["ratings", "cocoa", "number_of_bars"]
    ORDERS = ["top", "bottom"]
    command_tokens = command.split()
    cmd = "bars"
    location = "none"
    type_ = "sell"
    sorting = "ratings"
    order = "top"
    num = 10

    def isInt(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    for token in command_tokens:
        # print(token)
        if token in CMDS:
            cmd = token
        elif token == "none" or token.startswith("country=") or token.startswith("region="):
            location = token
        elif token in TYPES_:
            type_ = token
        elif token in SORTINGS:
            sorting = token
        elif token in ORDERS:
            order = token
        elif isInt(token):
            num = int(token)
        else:
            # brken
            return None
    query = ""
    if cmd == "bars":
        cond = " "
        if location == "none":
            pass
        elif location.startswith("country="):
            if type_ == "sell":
                country = location.split("=")[1]
                cond = f" WHERE c1.Alpha2='{country}' "
            else:
                country = location.split("=")[1]
                cond = f" WHERE c2.Alpha2='{country}' "
        elif location.startswith("region="):
            if type_ == "sell":
                region = location.split("=")[1]
                cond = f" WHERE c1.Region='{region}' "
            else:
                region = location.split("=")[1]
                cond = f" WHERE c2.Region='{region}' "
        if sorting == "ratings":
            cond += "ORDER BY Bars.Rating "
        elif sorting == "cocoa":
            cond += "ORDER BY Bars.CocoaPercent "
        if order == "top":
            cond += f"DESC LIMIT {num};"
        else:
            cond += f"LIMIT {num};"
        query = f"SELECT Bars.SpecificBeanBarName, Bars.Company, c1.EnglishName, Bars.Rating, Bars.CocoaPercent, " \
                "c2.EnglishName  FROM Bars JOIN Countries c1 ON Bars.CompanyLocationId = c1.id JOIN Countries c2 ON " \
                "Bars.BroadBeanOriginId = c2.id "
        query = query + cond
    elif cmd == "companies":
        cond = " "
        if location == "none":
            pass
        elif location.startswith("country="):
            country = location.split("=")[1]
            cond = f" and c.Alpha2='{country}' "
        elif location.startswith("region="):
            region = location.split("=")[1]
            cond = f" and c.Region='{region}' "
        if sorting == "ratings":
            cond += "ORDER BY AVG(b.Rating) "
        elif sorting == "cocoa":
            cond += "ORDER BY AVG(b.CocoaPercent) "
        elif sorting == "number_of_bars":
            cond += "ORDER BY COUNT(b.id) "
        if order == "top":
            cond += f"DESC LIMIT {num};"
        else:
            cond += f"LIMIT {num}"
        if sorting == "ratings":
            t = "AVG(b.Rating)"
        elif sorting == "cocoa":
            t = "AVG(b.CocoaPercent)"
        else:
            t = "COUNT(b.id)"
        query = f"SELECT b.Company, c.EnglishName, {t} FROM Bars b JOIN Countries c ON  b.CompanyLocationId = c.id GROUP BY b.Company HAVING COUNT(b.Id) > 4 {cond}"
    elif cmd == "countries":
        cond = " "
        if location == "none":
            pass
        elif location.startswith("region="):
            if type_ == "sell":
                region = location.split("=")[1]
                cond = f" and c1.Region='{region}'"
            else:
                region = location.split("=")[1]
                cond = f" and c2.Region='{region}'"
        if sorting == "ratings":
            cond += "ORDER BY AVG(b.Rating) "
        elif sorting == "cocoa":
            cond += "ORDER BY AVG(b.CocoaPercent) "
        elif sorting == "number_of_bars":
            cond += "ORDER BY COUNT(b.id) "
        if order == "top":
            cond += f"DESC LIMIT {num};"
        else:
            cond += f"LIMIT {num};"
        if sorting == "ratings":
            t = "AVG(b.Rating)"
        elif sorting == "cocoa":
            t = "AVG(b.CocoaPercent)"
        else:
            t = "COUNT(b.id)"

        if type_ == "sell":
            query = f"SELECT c1.EnglishName, c1.Region, {t} FROM Bars b JOIN Countries c1 ON b.CompanyLocationId = c1.id JOIN Countries c2 ON b.BroadBeanOriginId = c2.id GROUP BY b.CompanyLocationId HAVING COUNT(b.id) > 4 {cond}"
        else:
            query = f"SELECT c2.EnglishName, c2.Region, {t} FROM Bars b JOIN Countries c1 ON b.CompanyLocationId = c1.id JOIN Countries c2 ON b.BroadBeanOriginId = c2.id GROUP BY b.BroadBeanOriginId HAVING COUNT(b.id) > 4 {cond}"
    elif cmd == "regions":
        cond = " "
        if sorting == "ratings":
            cond += "ORDER BY AVG(b.Rating) "
        elif sorting == "cocoa":
            cond += "ORDER BY AVG(b.CocoaPercent) "
        elif sorting == "number_of_bars":
            cond += "ORDER BY COUNT(b.id) "
        if order == "top":
            cond += f"DESC LIMIT {num};"
        else:
            cond += f"LIMIT {num};"
        if sorting == "ratings":
            t = "AVG(b.Rating)"
        elif sorting == "cocoa":
            t = "AVG(b.CocoaPercent)"
        else:
            t = "COUNT(b.id)"
        if type_ == "sell":
            query = f"SELECT c1.Region, {t} FROM Bars b JOIN Countries c1 ON b.CompanyLocationId = c1.id JOIN Countries c2 ON b.BroadBeanOriginId = c2.id GROUP BY c1.Region HAVING COUNT(b.id) > 4 {cond}"
        else:
            query = f"SELECT c2.Region, {t} FROM Bars b JOIN Countries c1 ON b.CompanyLocationId = c1.id JOIN Countries c2 ON b.BroadBeanOriginId = c2.id GROUP BY c2.Region HAVING COUNT(b.id) > 4 {cond}"

    con = sqlite3.connect("choc.sqlite")
    cur = con.cursor()
    cur.execute(query)
    l = cur.fetchall()
    cur.close()
    con.close()
    return l


def load_help_text():
    with open('help.txt') as f:
        return f.read()


# Part 2 & 3: Implement interactive prompt and plotting. We've started for you!
def interactive_prompt():
    def omit(token, size):
        token = str(token)
        if len(token) > size - 1:
            return token[:size - 3] + "..."
        else:
            return token

    help_text = load_help_text()
    response = ''
    while response != 'exit':
        response = input('Enter a command: ')

        if response == 'help':
            print(help_text)
            continue
        if response == "exit":
            print("bye")
            break
        barplot = False
        if response.endswith("barplot"):
            barplot = True
            response = response[:-len("barplot")].strip()
        itemList = process_command(response)
        # print(itemList)eex
        if itemList is None:
            # broken
            print("Command not recognized:", response)
        elif response.startswith("bars"):
            pattern = "{:<16}{:<16}{:<16}{:.1f}\t\t{:.0%}\t\t{:<16}"
            d = {"Specific Bean Bar Name": [],
                 "Company Name": [],
                 "Company Location": [],
                 "Rating": [],
                 "Cocoa Percent": [],
                 "Broad Bean Origin": []}
            for item in itemList:
                print(pattern.format(omit(item[0], 15), omit(item[1], 15), omit(item[2], 15), item[3], item[4],
                                     omit(item[5], 15)))
                d["Specific Bean Bar Name"].append(item[0])
                d["Company Name"].append(item[1])
                d["Company Location"].append(item[2])
                d["Rating"].append(item[3])
                d["Cocoa Percent"].append(item[4])
                d["Broad Bean Origin"].append(item[5])
            df = pd.DataFrame(d)
            if barplot:
                fig = px.bar(df, x="Specific Bean Bar Name", y="Cocoa Percent")
                fig.show()

        elif response.startswith("companies") or response.startswith("countries"):
            int_pattern = "{:<16}{:<16}{:n}"
            float_pattern = "{:<16}{:<16}{:.1f}"
            value_attr = ""
            if "number_of_bars" in response:
                value_attr = "number of bars"
            elif "ratings" in response:
                value_attr = "Ratings"
            else:
                value_attr = "Cocoa Percent"
            isCompany = False
            if response.startswith("companies"):
                isCompany = True
                d = {"Company Name": [],
                     "Company Location": [],
                     value_attr: []}
            else:
                d = {
                    "Country Name": [],
                    "Region Name": [],
                    value_attr:[]
                }
            for item in itemList:
                if type(item[2]) == float:
                    print(float_pattern.format(omit(item[0], 15), omit(item[1], 15), item[2]))
                else:
                    print(int_pattern.format(omit(item[0], 15), omit(item[1], 15), item[2]))
                if isCompany:
                    d["Company Name"].append(item[0])
                    d["Company Location"].append(item[1])
                    d[value_attr].append(item[2])
                else:
                    d["Country Name"].append(item[0])
                    d["Region Name"].append(item[1])
                    d[value_attr].append(item[2])
            # print(d)
            df = pd.DataFrame(d)
            if barplot:
                if isCompany:
                    name = "Company Name"
                else:
                    name = "Country Name"
                fig = px.bar(df, x=name, y=value_attr)
                fig.show()

        elif response.startswith("regions"):
            int_pattern = "{:<16}{:n}"
            float_pattern = "{:<16}{:.1f}"
            value_attr = ""
            if "number_of_bars" in response:
                value_attr = "number of bars"
            elif "ratings" in response:
                value_attr = "Ratings"
            else:
                value_attr = "Cocoa Percent"
            d = {
                "Region Name":[],
                value_attr: []
            }
            for item in itemList:
                if type(item[1]) == float:
                    print(float_pattern.format(omit(item[0], 15), item[1]))
                else:
                    print(int_pattern.format(omit(item[0], 15), item[1]))
                d["Region Name"].append(item[0])
                d[value_attr].append(item[1])
            df = pd.DataFrame(d)
            if barplot:
                fig = px.bar(df, x="Region Name", y=value_attr)
                fig.show()

        else:
            print("Command not recognized:", response)
        response = None


# Make sure nothing runs or prints out when this file is run as a module/library
if __name__ == "__main__":
    interactive_prompt()
