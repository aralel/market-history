from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

DATABASE = os.getenv('DATABASE_PATH', 'market_data.db')
APP_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def root_index():
    return send_from_directory(APP_DIR, 'market_app.html')

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS imports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_date TIMESTAMP NOT NULL,
            import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            import_id INTEGER NOT NULL,
            name TEXT,
            current REAL,
            target REAL,
            growth REAL,
            appeal REAL,
            buy REAL,
            hold REAL,
            sell REAL,
            relative_change REAL,
            absolute_change REAL,
            daily_change REAL,
            cap TEXT,
            trend TEXT,
            raw_data TEXT,
            FOREIGN KEY (import_id) REFERENCES imports(id)
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_import_date ON imports(file_date)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_market_name ON market_records(name, import_id)
    ''')
    
    conn.commit()
    conn.close()

@app.route('/api/upload', methods=['POST'])
def upload_data():
    """Receive market data and store it in the database"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        file_date_str = data.get('file_date')
        market_data = data.get('data')
        
        if not file_date_str or not market_data:
            return jsonify({'error': 'Missing file_date or data'}), 400
        
        # Parse the file date
        try:
            file_date = datetime.fromisoformat(file_date_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert import record
        cursor.execute(
            'INSERT INTO imports (file_date, metadata) VALUES (?, ?)',
            (file_date, json.dumps({'count': len(market_data)}))
        )
        import_id = cursor.lastrowid
        
        # Insert market records
        for item in market_data:
            # Calculate computed fields
            trend_text = item.get('trend', '').replace('trTrendArrow -xsmall -', '').replace(' trPerformanceMeter__arrow', '')
            trend = 1 if trend_text == 'positive' else (-1 if trend_text == 'negative' else 0)
            
            current = parse_number(item.get('current'))
            target = parse_number(item.get('target'))
            growth = (target / current * 100) if (current and target and current != 0) else None
            
            relative_val = parse_number(item.get('relative'))
            absolute_val = parse_number(item.get('absolute'))
            
            buy = parse_number(item.get('buy', 0))
            hold = parse_number(item.get('hold', 0))
            sell = parse_number(item.get('sell', 0))
            
            appeal_base = (buy * 3 + hold - sell * 3) * 3 / 700 if (buy or hold or sell) else None
            
            cursor.execute('''
                INSERT INTO market_records (
                    import_id, name, current, target, growth, appeal,
                    buy, hold, sell, relative_change, absolute_change,
                    daily_change, cap, trend, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                import_id,
                item.get('name'),
                current,
                target,
                growth,
                appeal_base,
                buy,
                hold,
                sell,
                relative_val * trend if relative_val else None,
                absolute_val * trend if absolute_val else None,
                parse_number(item.get('daily_change')),
                item.get('cap'),
                trend_text,
                json.dumps(item)
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'import_id': import_id,
            'records_count': len(market_data),
            'file_date': file_date_str
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/timeseries', methods=['GET'])
def get_timeseries():
    """Return time series across all imports for each stock"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT i.file_date AS file_date, m.name, m.current, m.target, m.growth, m.appeal,
                   m.buy, m.hold, m.sell, m.relative_change
            FROM market_records m
            JOIN imports i ON i.id = m.import_id
            WHERE m.name IS NOT NULL
            ORDER BY m.name ASC, i.file_date ASC
        ''')
        rows = cursor.fetchall()

        series = {}
        for row in rows:
            name = row['name']
            if not name:
                continue
            if name not in series:
                series[name] = []
            series[name].append({
                'date': row['file_date'],
                'current': row['current'],
                'target': row['target'],
                'growth': row['growth'],
                'appeal': row['appeal'],
                'buy': row['buy'],
                'hold': row['hold'],
                'sell': row['sell'],
                'relative': row['relative_change']
            })

        out_series = []
        all_dates = set()
        for name, points in series.items():
            prev_current = None
            enriched = []
            for p in points:
                all_dates.add(p['date'])
                curr = p['current']
                change = None
                if prev_current is not None and prev_current != 0 and curr is not None:
                    change = ((curr - prev_current) / prev_current) * 100.0
                enriched.append({
                    'date': p['date'],
                    'current': curr,
                    'target': p['target'],
                    'growth': p['growth'],
                    'appeal': p['appeal'],
                    'buy': p.get('buy'),
                    'hold': p.get('hold'),
                    'sell': p.get('sell'),
                    'relative': p.get('relative'),
                    'change': change
                })
                if curr is not None:
                    prev_current = curr
            out_series.append({'name': name, 'points': enriched})

        conn.close()
        dates_sorted = sorted(all_dates)
        return jsonify({'dates': dates_sorted, 'series': out_series})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/imports', methods=['GET'])
def get_imports():
    """Get list of all imports with their dates"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                i.id,
                i.file_date,
                i.import_date,
                i.metadata,
                COUNT(m.id) as record_count
            FROM imports i
            LEFT JOIN market_records m ON i.id = m.import_id
            GROUP BY i.id
            ORDER BY i.file_date DESC
        ''')
        
        imports = []
        for row in cursor.fetchall():
            imports.append({
                'id': row['id'],
                'file_date': row['file_date'],
                'import_date': row['import_date'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                'record_count': row['record_count']
            })
        
        conn.close()
        return jsonify(imports)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/imports/<int:import_id>', methods=['GET'])
def get_import_data(import_id):
    """Get market data for a specific import"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM imports WHERE id = ?', (import_id,))
        import_row = cursor.fetchone()
        
        if not import_row:
            return jsonify({'error': 'Import not found'}), 404
        
        cursor.execute('''
            SELECT * FROM market_records 
            WHERE import_id = ?
            ORDER BY appeal DESC
        ''', (import_id,))
        
        records = []
        for row in cursor.fetchall():
            records.append({
                'id': row['id'],
                'name': row['name'],
                'current': row['current'],
                'target': row['target'],
                'growth': row['growth'],
                'appeal': row['appeal'],
                'buy': row['buy'],
                'hold': row['hold'],
                'sell': row['sell'],
                'relative_change': row['relative_change'],
                'absolute_change': row['absolute_change'],
                'daily_change': row['daily_change'],
                'cap': row['cap'],
                'trend': row['trend'],
                'raw_data': json.loads(row['raw_data']) if row['raw_data'] else {}
            })
        
        conn.close()
        
        return jsonify({
            'import_info': {
                'id': import_row['id'],
                'file_date': import_row['file_date'],
                'import_date': import_row['import_date'],
                'metadata': json.loads(import_row['metadata']) if import_row['metadata'] else {}
            },
            'records': records
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def compare_imports():
    """Compare market data between two imports"""
    try:
        data = request.json
        import_id1 = data.get('import_id1')
        import_id2 = data.get('import_id2')
        
        if not import_id1 or not import_id2:
            return jsonify({'error': 'Both import_id1 and import_id2 required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get data from first import
        cursor.execute('''
            SELECT name, current, target, growth, appeal, cap
            FROM market_records
            WHERE import_id = ?
        ''', (import_id1,))
        
        data1 = {row['name']: dict(row) for row in cursor.fetchall() if row['name']}
        
        # Get data from second import
        cursor.execute('''
            SELECT name, current, target, growth, appeal, cap
            FROM market_records
            WHERE import_id = ?
        ''', (import_id2,))
        
        data2 = {row['name']: dict(row) for row in cursor.fetchall() if row['name']}
        
        # Compare
        comparison = []
        all_names = set(data1.keys()) | set(data2.keys())
        
        for name in all_names:
            record1 = data1.get(name, {})
            record2 = data2.get(name, {})
            
            comp_record = {
                'name': name,
                'in_both': name in data1 and name in data2,
                'only_in_first': name in data1 and name not in data2,
                'only_in_second': name not in data1 and name in data2
            }
            
            if name in data1 and name in data2:
                # Calculate changes
                for field in ['current', 'target', 'growth', 'appeal']:
                    val1 = record1.get(field)
                    val2 = record2.get(field)
                    comp_record[f'{field}_1'] = val1
                    comp_record[f'{field}_2'] = val2
                    if val1 is not None and val2 is not None and val1 != 0:
                        comp_record[f'{field}_change'] = ((val2 - val1) / val1) * 100
                    else:
                        comp_record[f'{field}_change'] = None
            else:
                comp_record['data_1'] = record1
                comp_record['data_2'] = record2
            
            comparison.append(comp_record)
        
        conn.close()
        
        return jsonify({
            'import_id1': import_id1,
            'import_id2': import_id2,
            'comparison': comparison
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def parse_number(val):
    """Parse a number from various formats"""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val) if val == val else None  # Check for NaN
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return None
        # Remove currency symbols and spaces
        s = s.replace('\u00A0', ' ').replace('€', '').replace('$', '').replace('£', '').replace('%', '').replace(',', '').replace(' ', '')
        if s in ('', '-', '—'):
            return None
        try:
            n = float(s)
            return n if n == n else None  # Check for NaN
        except ValueError:
            return None
    return None

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    app.run(debug=True, port=5000)
