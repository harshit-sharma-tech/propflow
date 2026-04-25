import pymysql
import pymysql.cursors
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g
#render_templates=shows html pages
#request =  reads what user sent
#redirect  = send the user to another page
#url_for = used to create url
#jsonify=helps to make the json file of any data which can be mapped in key value format
#flash=used to display a message whether it is an successful , danger,warning,etc...
#g=temporary storage while a request
from config import DB_CONFIG

app = Flask(__name__)
app.config['SECRET_KEY'] = 'propflow-mysql-2024'#with secret key you cannot use session to your code



# DATABASE 

def get_db():#go connect to the database
    """Open ONE MySQL connection per request."""
    if 'db' not in g:#the data is stored in g till the request is not finished
        g.db = pymysql.connect(
            host     = DB_CONFIG['host'],
            port     = DB_CONFIG['port'],
            user     = DB_CONFIG['user'],
            password = DB_CONFIG['password'],
            database = DB_CONFIG['database'],
            cursorclass = pymysql.cursors.DictCursor,   # rows come back as dicts
            autocommit  = False
        )
    return g.db

@app.teardown_appcontext#closing a database
def close_db(error):
    """Close the connection when the request ends."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def query(sql, params=(), one=False):
    """Run a SELECT and return one row or all rows."""
    db  = get_db()
    cur = db.cursor()
    cur.execute(sql, params)
    return cur.fetchone() if one else cur.fetchall()

def execute(sql, params=()):
    """Run INSERT / UPDATE / DELETE and commit."""
    db  = get_db()
    cur = db.cursor()
    cur.execute(sql, params)
    db.commit()
    return cur.lastrowid



# DB INIT & SEED  (run once via: python init_db.py)


def init_db():#creating the database
    """Create the properties table if it doesn't exist."""
    db  = pymysql.connect(**{k: v for k, v in DB_CONFIG.items()}, cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            title       VARCHAR(120) NOT NULL,
            type        VARCHAR(50)  NOT NULL,
            city        VARCHAR(80)  NOT NULL,
            address     VARCHAR(200) NOT NULL,
            price       DECIMAL(15,2) NOT NULL,
            bedrooms    INT          DEFAULT 0,
            bathrooms   INT          DEFAULT 0,
            area_sqft   FLOAT        DEFAULT 0,
            status      VARCHAR(30)  DEFAULT "Available",
            description TEXT,
            created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db.commit()

    # Seed demo rows only if table is empty
    cur.execute('SELECT COUNT(*) as cnt FROM properties')
    if cur.fetchone()['cnt'] == 0:
        demo = [
            ('Sunrise Villa',      'House',     'Mumbai',    '12 Marine Drive, Mumbai',       12500000, 4, 3, 2400,  'Available', 'Stunning sea-facing villa with modern interiors.'),
            ('Green Heights Apt',  'Apartment', 'Pune',      '45 Koregaon Park, Pune',         4800000, 2, 2,  950,  'Available', 'Cozy apartment in a prime gated society.'),
            ('Tech Park Studio',   'Apartment', 'Bengaluru', '7 Whitefield Road, Bengaluru',   3200000, 1, 1,  620,  'Rented',    'Perfect studio near IT corridor.'),
            ('Farm Land Plot',     'Land',      'Nashik',    'NH-60, Nashik Rural',            1500000, 0, 0, 10000, 'Available', 'Fertile agricultural land with road access.'),
            ('City Centre Duplex', 'House',     'Delhi',     '22 Connaught Place, Delhi',     28000000, 5, 4, 3800,  'Sold',      'Luxury duplex in the heart of Delhi.'),
        ]
        cur.executemany(
            'INSERT INTO properties (title,type,city,address,price,bedrooms,bathrooms,area_sqft,status,description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            demo
        )
        db.commit()
        print('✅ Seeded 5 demo properties.')

    db.close()
    print('✅ Database ready.')


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route('/')
def index():
    stats = {
        'total':     query('SELECT COUNT(*) as n FROM properties', one=True)['n'],
        'available': query('SELECT COUNT(*) as n FROM properties WHERE status="Available"', one=True)['n'],
        'sold':      query('SELECT COUNT(*) as n FROM properties WHERE status="Sold"', one=True)['n'],
        'rented':    query('SELECT COUNT(*) as n FROM properties WHERE status="Rented"', one=True)['n'],
    }
    recent = query('SELECT * FROM properties ORDER BY id DESC LIMIT 5')
    return render_template('index.html', stats=stats, recent=recent)


@app.route('/properties')
def properties():
    q      = request.args.get('q', '')
    city   = request.args.get('city', '')
    ptype  = request.args.get('type', '')
    status = request.args.get('status', '')
    min_p  = request.args.get('min_price', '')
    max_p  = request.args.get('max_price', '')

    # Build WHERE clause dynamically
    sql    = 'SELECT * FROM properties WHERE 1=1'
    params = []
    if q:      sql += ' AND title LIKE %s';  params.append(f'%{q}%')
    if city:   sql += ' AND city LIKE %s';   params.append(f'%{city}%')
    if ptype:  sql += ' AND type = %s';      params.append(ptype)
    if status: sql += ' AND status = %s';    params.append(status)
    if min_p:  sql += ' AND price >= %s';    params.append(float(min_p))
    if max_p:  sql += ' AND price <= %s';    params.append(float(max_p))
    sql += ' ORDER BY id DESC'

    props  = query(sql, params)
    cities = [r['city'] for r in query('SELECT DISTINCT city FROM properties ORDER BY city')]
    return render_template('properties.html', props=props, cities=cities)


@app.route('/property/new', methods=['GET', 'POST'])
def new_property():
    if request.method == 'POST':
        execute(
            'INSERT INTO properties (title,type,city,address,price,bedrooms,bathrooms,area_sqft,status,description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (
                request.form['title'],
                request.form['type'],
                request.form['city'],
                request.form['address'],
                float(request.form['price']),
                int(request.form.get('bedrooms', 0)),
                int(request.form.get('bathrooms', 0)),
                float(request.form.get('area_sqft', 0)),
                request.form.get('status', 'Available'),
                request.form.get('description', '')
            )
        )
        flash('Property listed successfully!', 'success')
        return redirect(url_for('properties'))
    return render_template('form.html', prop=None, action='Add')


@app.route('/property/<int:id>')
def view_property(id):
    prop = query('SELECT * FROM properties WHERE id=%s', (id,), one=True)
    if not prop:
        flash('Property not found.', 'error')
        return redirect(url_for('properties'))
    return render_template('detail.html', prop=prop)


@app.route('/property/<int:id>/edit', methods=['GET', 'POST'])
def edit_property(id):
    prop = query('SELECT * FROM properties WHERE id=%s', (id,), one=True)
    if not prop:
        flash('Property not found.', 'error')
        return redirect(url_for('properties'))

    if request.method == 'POST':
        execute(
            '''UPDATE properties SET title=%s, type=%s, city=%s, address=%s, price=%s,
               bedrooms=%s, bathrooms=%s, area_sqft=%s, status=%s, description=%s
               WHERE id=%s''',
            (
                request.form['title'],
                request.form['type'],
                request.form['city'],
                request.form['address'],
                float(request.form['price']),
                int(request.form.get('bedrooms', 0)),
                int(request.form.get('bathrooms', 0)),
                float(request.form.get('area_sqft', 0)),
                request.form.get('status', 'Available'),
                request.form.get('description', ''),
                id
            )
        )
        flash('Property updated!', 'success')
        return redirect(url_for('view_property', id=id))
    return render_template('form.html', prop=prop, action='Edit')


@app.route('/property/<int:id>/delete', methods=['POST'])
def delete_property(id):
    execute('DELETE FROM properties WHERE id=%s', (id,))
    flash('Property removed.', 'info')
    return redirect(url_for('properties'))


# ─────────────────────────────────────────────
# REST API ENDPOINTS
# ─────────────────────────────────────────────

@app.route('/api/properties')
def api_properties():
    rows = query('SELECT * FROM properties ORDER BY id DESC')
    # Convert Decimal to float for JSON
    result = []
    for r in rows:
        d = dict(r)
        d['price'] = float(d['price'])
        d['created_at'] = str(d['created_at'])
        result.append(d)
    return jsonify(result)

@app.route('/api/stats')
def api_stats():
    avg = query('SELECT AVG(price) as a FROM properties', one=True)['a']
    return jsonify({
        'total':     query('SELECT COUNT(*) as n FROM properties', one=True)['n'],
        'available': query('SELECT COUNT(*) as n FROM properties WHERE status="Available"', one=True)['n'],
        'sold':      query('SELECT COUNT(*) as n FROM properties WHERE status="Sold"', one=True)['n'],
        'rented':    query('SELECT COUNT(*) as n FROM properties WHERE status="Rented"', one=True)['n'],
        'avg_price': float(avg) if avg else 0,
    })


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True)
