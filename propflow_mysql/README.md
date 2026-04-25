# 🏠 PropFlow — Real Estate Management System (MySQL Edition)

A clean, full-stack property management web app built with **Python Flask + PyMySQL + MySQL**.

---

## ⚙️ Setup in 4 Steps

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Configure your MySQL credentials
Open `config.py` and update:
```python
DB_CONFIG = {
    'host'    : 'localhost',
    'port'    : 3306,
    'user'    : 'root',
    'password': 'YOUR_PASSWORD_HERE',  # ← change this
    'database': 'propflow',
}
```

### Step 3 — Create database & seed data (run ONCE)
```bash
python init_db.py
```
This will:
- Create the `propflow` database
- Create the `properties` table
- Insert 5 demo properties

### Step 4 — Run the app
```bash
python app.py
```
Open: **http://127.0.0.1:5000**

---

## 📁 Project Structure

```
propflow_mysql/
├── app.py          # Flask app — all routes, DB helpers
├── config.py       # MySQL credentials (edit this!)
├── init_db.py      # One-time DB setup & seed script
├── requirements.txt
└── templates/
    ├── base.html       # Layout, navbar, CSS
    ├── index.html      # Dashboard with stats
    ├── properties.html # List with search & filters
    ├── form.html       # Add / Edit form
    └── detail.html     # Single property detail
```

---

## ✨ Features

| Feature | Details |
|---|---|
| Dashboard | Live stats — total, available, sold, rented |
| Add Property | House / Apartment / Land with full details |
| Edit Property | Update any field |
| Delete Property | With confirmation |
| Search & Filter | By name, city, type, status, price range |
| Detail View | Auto-calculates price per sqft |
| REST API | `/api/properties` + `/api/stats` JSON endpoints |

---

## 🗄️ MySQL Table Schema

```sql
CREATE TABLE properties (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(120)  NOT NULL,
    type        VARCHAR(50)   NOT NULL,       -- House / Apartment / Land
    city        VARCHAR(80)   NOT NULL,
    address     VARCHAR(200)  NOT NULL,
    price       DECIMAL(15,2) NOT NULL,
    bedrooms    INT           DEFAULT 0,
    bathrooms   INT           DEFAULT 0,
    area_sqft   FLOAT         DEFAULT 0,
    status      VARCHAR(30)   DEFAULT 'Available', -- Available / Sold / Rented
    description TEXT,
    created_at  DATETIME      DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔌 REST API

```
GET  /api/properties   →  JSON array of all properties
GET  /api/stats        →  { total, available, sold, rented, avg_price }
```

---

## 🔑 Key Differences vs SQLite version

| | SQLite version | MySQL version |
|---|---|---|
| Driver | Built-in `sqlite3` | `PyMySQL` library |
| Placeholder | `?` | `%s` |
| DB file | Local `.db` file | MySQL server |
| Production-ready | Dev/demo only | ✅ Yes |
| Setup | Zero config | Need MySQL running |

---

## 💬 What to say in the interview

> *"I used Flask with PyMySQL to connect to a MySQL database.
> I separated config from code using config.py, and used parameterized queries
> with %s placeholders throughout — which prevents SQL injection.
> The init_db.py script handles first-time setup cleanly.
> I also added REST API endpoints at /api/stats and /api/properties."*
