# Examples: ATP Singles Rankings Data Analysis

This document provides practical examples of how to use the analysis scripts in this repository. These examples assume your environment is set up as described in the [README.md](../README.md).

---

## 1. Plot a Multiple Players' Ranking History

**Command Example:**
```bash
python3 analyze.py -r Roger_Federer Rafael_Nadal Novak_Djokovic
```

**Description:**  
Generates a plot showing the provided players ATP singles ranking over time.

**Expected Output:**  
A matplotlib line graph with the y-axis as ATP ranking (lower is better), x-axis as date.

---

## 2. Plot Multiple Players' Points History

**Command Example:**
```bash
python3 analyze.py -p Rafael_Nadal Novak_Djokovic Roger_Federer
```

**Description:**  
Plots the ATP points history for provided players on the same graph for comparison.

**Expected Output:**  
A matplotlib line graph with separate lines for each player, showing their point totals over time.

---

## 3. Generate a Player Factile

**Command Example:**
```bash
python3 analyze.py -f Novak_Djokovic
```

**Description:**  
Outputs a factile (summary statistics) for the provided player, including career high rank, most points, weeks in top 100/10/1, etc.

**Expected Output:**
```
Novak Djokovic Player Factile
    Career High Rank: 1 (YYYY-MM-DD)
    Most Points Ever: 16500 (YYYY-MM-DD)
    Weeks in Top 100: 900
    Weeks in Top 10: 700
    Weeks at Number 1: 450
```

---

## 4. Generate Weeks at Number 1 Histogram

**Command:**
```bash
python3 analyze.py -n
```

**Description:**
Outputs a matplotlib histogram sorting weeks spent at number 1 by player.

**Expected Output:**
Histogram similar to the one shown in WeeksAtNo1Hist.png

---

## 5. Update the Database with New Rankings

**Command:**
```bash
python3 filler.py
```

**Description:**  
Fetches and inserts new rankings data into the SQLite database, extending it to the current week.

---

## 6. Regenerate the Database from Scratch

**Command:**
```bash
python3 generate.py
```

**Description:**  
Completely rebuilds the SQLite database from historical ATP data.
> ⚠️ Only use this if you need a fresh database or have deleted your existing one.

---

## 7. Debug the Database for Anomalies

**Command:**
```bash
python3 debug.py
```

**Description:**  
Identifies tables with only 1 row, which may indicate incomplete or corrupt data. Manually review and delete such tables if needed.

---

## Notes

- Use underscores (`_`) between first and last names when specifying players (e.g., `Rafael_Nadal`).
- For more details on command-line arguments, run:
  ```bash
  python analyze.py -h
  ```
- For troubleshooting, see the [README.md](../README.md).

---

