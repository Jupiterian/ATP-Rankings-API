#Import modules
import sys
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
from collections import Counter
import os

# Get the project root directory (parent of scripts/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(project_root, 'rankings.db')

#Connect to Database
conn = sqlite3.connect(db_path)
cur = conn.cursor()

def helpMenu():
    help_text = """
    Usage: analyze.py [OPTION] <first_last> <first2_last2>

    Analyze ATP tennis data and generate visualizations.

    Options:
        -h            Show this help menu with all commands and their usage
        -n            Generate a bar graph using matplotlib of the ATP weeks at number 1
        -p            Generate a plot using matplotlib of a player's point history
        -r            Generate a plot using matplotlib of a player's ranking history
        -f            Show player factile

    Example:
        python analyze.py -p first_last first2_last2
            Generates and displays a plot of the selected player's point history. Supports multiple names.
        python analyze.py -f first_last
            Generates and outputs a player statistics factile of the selected player.
"""
    print(help_text.strip())


#Define Table Gathering function
def getTables() :
    #Get Tables for dates
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cur.fetchall()]
    return tables

#Define Data Gathering Function
#FIX ACCURACY FOR MISSING WEEKS
def playerCareerDataFind (playerName: str, index: int, specialChar: str):
    tables = getTables()
    x = []
    y = []
    data = []
    #Gather Specified Data
    for a in tables:
        cur.execute(f"SELECT * FROM '{a}';")
        data.append(cur.fetchall())
    for b in data:
        for c in b:
            if playerName == c[1]:
                x.append(tables[data.index(b)])
                dataPoint = c[index].replace(specialChar, "")
                try:
                    y.append(int(dataPoint))
                except:
                    continue
    x2 = []
    for d in x:
        x2.append(datetime.strptime(d, f"%Y-%m-%d"))
    return x2, y

#Define Player Name Gathering Function based on sys.argv
def gatherPlayer ():
    argList = list(sys.argv)
    argList.pop(0)
    argList.pop(0)
    playerNames = []
    for x in argList:
        new = x.replace("_", " ")
        playerNames.append(new)
    return playerNames

#Check if help menu called
if len(sys.argv) == 1:
    helpMenu()
    exit(0)
if sys.argv[1] == "-h":
    helpMenu()
    exit(0)

#Rankings Plot
if sys.argv[1] == "-r":
    # Get Supplied Names
    names = gatherPlayer()
    nameList = ""
    for name in names:
        # Gather Data Using Function
        dates, rankings = playerCareerDataFind(name, 0, "T")
        plt.plot(dates, rankings, marker='o', label=name)  # Different line for each player
        nameList = nameList + " " + name

    plt.yticks(range(0, 101, 5))
    plt.gca().invert_yaxis()
    plt.xlabel("Date")
    plt.ylabel("Ranking")
    plt.title(f"{nameList} Top 100 Rankings Over Time")
    plt.legend()  # Show names with their line color
    plt.grid(True)
    plt.gcf().autofmt_xdate()
    plt.show()

#Points Plot
if sys.argv[1] == "-p":
    # Get Supplied Names
    names = gatherPlayer()
    nameList = ""
    for name in names:
        # Gather Data Using Function
        dates, points = playerCareerDataFind(name, 2, ",")
        plt.plot(dates, points, marker='o', label=name)  # Different line for each player
        nameList = nameList + " " + name

    plt.xlabel("Date")
    plt.ylabel("Points")
    plt.title(f"{nameList} Top 100 Points Over Time")
    plt.legend()  # Show names with their line color
    plt.grid(True)
    plt.gcf().autofmt_xdate()
    plt.show()

#Weeks at Number 1 histogram
if sys.argv[1] == "-n":
    #Get Tables
    tables = getTables()
    rank1 = []
    for a in tables:
        cur.execute(f'SELECT * FROM "{a}" WHERE "rank" = "1";')
        rank1.append(cur.fetchall())
    data = []
    for b in rank1:
        row = b[0]
        data.append(row[1])
    
    #Sort Data
    counts = Counter(data)
    sorted_counts = dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))
    names = list(sorted_counts.keys())
    weeks = list(sorted_counts.values())

    #Plot Data
    plt.figure(figsize=(14, 7))
    plt.bar(names, weeks, color='skyblue', edgecolor='black')
    plt.xlabel('Player', fontsize=12)
    plt.ylabel('Weeks at Number 1', fontsize=12)
    plt.title('Total Weeks at Number 1', fontsize=15)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

#Player Factile
if sys.argv[1] == "-f":
    name = sys.argv[2]
    name = name.replace("_", " ")
    #Gather Ranking Data
    week, rank = playerCareerDataFind(name, 0, "T")
    #Career High
    ch = 101
    chWeek=""
    for x in rank:
        if int(x) < ch:
            ch = x
            chWeek = week[rank.index(x)]
    chWeek = str(chWeek).replace(' 00:00:00', '')

    #Gather Points Data
    week, points = playerCareerDataFind(name, 2, ",")
    #Career High Points
    maxPoints = 0
    maxPointsWeek=""
    for x in points:
        if int(x) > maxPoints:
            maxPoints = x
            maxPointsWeek = week[points.index(x)]
    if maxPoints == 0:
        maxPointsWeek = "No Points System"
    maxPointsWeek = str(maxPointsWeek).replace(' 00:00:00', '')
    
    #Weeks in top 100
    top100 = len(rank)
    
    #Weeks in Top 10 & World Num 1
    top10 = 0
    no1 = 0
    for x in rank:
        if int(x) in range(1,11):
            top10+=1
            if int(x) == 1:
                no1+=1
    
    #Print Factile
    # ANSI color codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    BLUE = "\033[36m"
    #Print Code
    print(f"{BOLD}{GREEN}{name} Player Factile{RESET}")
    print(f"     {BLUE}Career High Rank: {ch} ({chWeek}){RESET}")    
    print(f"     {BLUE}Most Points Ever: {maxPoints} ({maxPointsWeek}){RESET}")
    print(f"     {BLUE}Weeks in Top 100: {top100}{RESET}")
    print(f"     {BLUE}Weeks in Top 10: {top10}{RESET}")
    print(f"     {BLUE}Weeks at Number 1: {no1}{RESET}")
