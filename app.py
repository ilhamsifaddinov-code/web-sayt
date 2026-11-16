import os
import time
import base64
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)

DEFAULT_DATABASE_URL = "postgresql://neondb_owner:npg_kvnVEr0zLgN6@ep-empty-term-bd9lpjlr-pooler.c-8.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def _database_uri():
    uri = os.environ.get('DATABASE_URL')
    if not uri or uri.strip() == '' or uri.startswith('sqlite'):
        uri = DEFAULT_DATABASE_URL
    if '://' in uri:
        scheme, rest = uri.split('://', 1)
        if scheme.split('+', 1)[0] in ('postgres', 'postgresql'):
            uri = 'postgresql+psycopg://' + rest
            if 'connect_timeout' not in uri:
                uri += ('&' if '?' in uri else '?') + 'connect_timeout=10'
    return uri

_secret = os.environ.get('SECRET_KEY')
if not _secret:
    _secret = 'logoped-nukus-secure-2026-key'

app.config['SECRET_KEY'] = _secret
app.config['SQLALCHEMY_DATABASE_URI'] = _database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True, 'pool_recycle': 280}
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
except OSError:
    pass

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'svg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_specialist_image(file_obj, url_str, fallback='https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=600'):
    if file_obj and file_obj.filename and allowed_file(file_obj.filename):
        filename = secure_filename(file_obj.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        mime_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'webp': 'image/webp',
            'gif': 'image/gif',
            'svg': 'image/svg+xml'
        }
        mime = mime_map.get(ext, 'image/jpeg')
        file_bytes = file_obj.read()
        
        try:
            unique_name = f"{int(time.time())}_{filename}"
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            with open(upload_path, 'wb') as f:
                f.write(file_bytes)
        except Exception as e:
            app.logger.warning('Failed to save to local uploads: %s', e)

        b64_str = base64.b64encode(file_bytes).decode('utf-8')
        return f"data:{mime};base64,{b64_str}"

    if url_str and url_str.strip():
        return url_str.strip()

    return fallback

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Bul betke kiriw ushın dáslep dizimnen ótiń!"
login_manager.login_message_category = "warning"

# ==================== MODELLER ====================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    role = db.Column(db.String(20), default='user')
    specialist_id = db.Column(db.Integer, db.ForeignKey('specialist.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Specialist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    experience = db.Column(db.String(50), nullable=False)
    success_rate = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.Text, default='https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=600')
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    specialist_id = db.Column(db.Integer, db.ForeignKey('specialist.id'), nullable=False)
    child_name = db.Column(db.String(120), nullable=False)
    child_age = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    date_str = db.Column(db.String(20), nullable=False)
    time_str = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(100), default='Aktiv')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='appointments', foreign_keys=[user_id])
    specialist = db.relationship('Specialist', backref='appointments')

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    specialist_id = db.Column(db.Integer, db.ForeignKey('specialist.id'), nullable=False)
    child_name = db.Column(db.String(120), nullable=False)
    note = db.Column(db.Text, nullable=False)
    homework = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', foreign_keys=[user_id])
    specialist = db.relationship('Specialist', foreign_keys=[specialist_id])

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author_name = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Integer, default=5)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(50), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except Exception:
        db.session.rollback()
        return None

STANDARD_SLOTS = ["09:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00", "14:00 - 15:00", "15:00 - 16:00", "16:00 - 17:00", "17:00 - 18:00"]

def seed_database():
    db.create_all()
    try:
        db.session.execute(db.text("ALTER TABLE chat_message ADD COLUMN IF NOT EXISTS is_read BOOLEAN DEFAULT FALSE;"))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    try:
        db.session.execute(db.text("ALTER TABLE appointment ALTER COLUMN status TYPE VARCHAR(100);"))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    try:
        db.session.execute(db.text("ALTER TABLE appointment ALTER COLUMN time_str TYPE VARCHAR(50);"))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    if not Setting.query.filter_by(key='reviews_active').first():
        db.session.add(Setting(key='reviews_active', value='true'))
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', full_name='Oray Administratorı', role='admin', phone="+998 90 123 45 67")
        admin.set_password(os.environ.get('ADMIN_PASSWORD', 'admin123'))
        db.session.add(admin)
    if Specialist.query.count() == 0:
        s1 = Specialist(name="Dilnoza Alimbetova", age=32, experience="8 jıl", success_rate=95, price=50000, image="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=600", description="Duduqlanıw hám tutıǵıw yamasa al-analıq waqtındaǵı logopedik xızmet.")
        s2 = Specialist(name="Rustam Joldasbaev", age=38, experience="12 jıl", success_rate=98, price=70000, image="https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=600", description="Keshikken sóylewdi rawajlandırıw, autizm belgileri bar balalar menen islesiw.")
        s3 = Specialist(name="Aygul Turemuratova", age=29, experience="5 jıl", success_rate=92, price=45000, image="https://images.unsplash.com/photo-1594824813682-14066c0d832b?w=600", description="Artikulyaciyalıq gimnastika, 'R' hám 'L' háriplerin anıq aytıwdı úyretiw.")
        s4 = Specialist(name="Zarina Qıdırbaeva", age=35, experience="10 jıl", success_rate=96, price=60000, image="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=600", description="Kishi jastaǵı balalarda sóylew qorqınıshın jeńiw hám logonevrozdi emlew.")
        db.session.add_all([s1, s2, s3, s4])

    for sp in Specialist.query.all():
        if sp.image and 'encrypted-tbn0' in sp.image:
            sp.image = 'https://images.unsplash.com/photo-1594824813682-14066c0d832b?w=600'
        elif sp.image and 'gettyimages' in sp.image:
            sp.image = 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=600'

    if Review.query.count() == 0 and admin:
        r1 = Review(
            user_id=admin.id,
            author_name="Gulbahar Allanazarova",
            rating=5,
            content="Balam 4 jasqa shekem 'R' hám 'L' dawısların ayta almaytuǵın edi. Aygul qániygemiz benen 2 ay shınıǵıwdan soń anıq sóylewdi basladı. Sheksiz minnetdarmız!"
        )
        r2 = Review(
            user_id=admin.id,
            author_name="Azamat Berdimuratov",
            rating=5,
            content="Rustam aǵaǵa kóp raxmet. Balamızdıń keshikken sóylewi boyınsha qızıqlı oyınlar arqalı shınıǵıwlar ótkerildi, házir qatar-quralasları menen erkin sóylesedi."
        )
        r3 = Review(
            user_id=admin.id,
            author_name="Dilfuza Xojamuratova",
            rating=5,
            content="Oray xızmetkerlerine úlken raxmet! Júdá qolaylı orın, zamanagóy pedagogikalıq metodika hám qolaylı jeke kabinet. Hár bir ata-anaǵa usınıs etemen."
        )
        db.session.add_all([r1, r2, r3])

    db.session.commit()

def auto_update_expired_appointments():
    try:
        local_now = datetime.utcnow() + timedelta(hours=5)
        today_date_str = local_now.strftime('%Y-%m-%d')
        current_hm = local_now.strftime('%H:%M')

        active_apps = Appointment.query.filter_by(status='Aktiv').all()
        updated = False
        for a in active_apps:
            if a.date_str < today_date_str:
                a.status = 'Nátiyjeli juwmaqlandı'
                updated = True
            elif a.date_str == today_date_str:
                end_time = a.time_str.split('-')[-1].strip() if '-' in a.time_str else a.time_str.strip()
                if end_time <= current_hm:
                    a.status = 'Nátiyjeli juwmaqlandı'
                    updated = True
        if updated:
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.warning("Auto update expired appointments error: %s", e)

@app.context_processor
def inject_global_data():
    unread_count = 0
    if current_user.is_authenticated:
        try:
            unread_count = ChatMessage.query.filter_by(receiver_id=current_user.id, is_read=False).count()
        except Exception:
            db.session.rollback()
            unread_count = 0
    return {'total_unread_chats': unread_count}

@app.route('/')
def index():
    specialists = Specialist.query.filter_by(is_active=True).all()
    reviews = Review.query.order_by(Review.id.desc()).all()
    reviews_setting = Setting.query.filter_by(key='reviews_active').first()
    reviews_enabled = reviews_setting.value == 'true' if reviews_setting else True
    return render_template('index.html', specialists=specialists, reviews=reviews, reviews_enabled=reviews_enabled)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        full_name = request.form.get('full_name', '').strip()
        country_code = request.form.get('country_code', '+998')
        phone_number = request.form.get('phone_number', '').strip()
        password = request.form.get('password', '').strip()
        phone = f"{country_code} {phone_number}"

        if not username or not password or not full_name:
            flash("Barlıq maydanlardı toltırıń!", "warning")
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash("Bul login bánt! Basqa login tańlań.", "warning")
            return redirect(url_for('register'))

        new_user = User(username=username, full_name=full_name, phone=phone, role='user')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("Tabıslı dizimnen óttińiz!", "success")
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    next_page = request.args.get('next')
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            if user.role == 'admin': return redirect(url_for('admin_panel'))
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        flash("Login yamasa parol nadurıs!", "danger")
    return render_template('login.html')

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.svg')

@app.route('/robots.txt')
def robots():
    content = "User-agent: *\nAllow: /\nSitemap: https://logoped-five.vercel.app/sitemap.xml\n"
    return content, 200, {'Content-Type': 'text/plain'}

@app.route('/sitemap.xml')
def sitemap():
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://logoped-five.vercel.app/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://logoped-five.vercel.app/login</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://logoped-five.vercel.app/register</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>"""
    return content, 200, {'Content-Type': 'application/xml'}

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    auto_update_expired_appointments()
    if current_user.role == 'admin': return redirect(url_for('admin_panel'))
    if current_user.role == 'specialist':
        my_appointments = Appointment.query.filter_by(specialist_id=current_user.specialist_id).order_by(Appointment.date_str.desc()).all()
        unique_clients = list({app.user_id: app for app in my_appointments if app.status in ('Aktiv', 'Nátiyjeli juwmaqlandı')}.values())
        return render_template('dashboard_specialist.html', appointments=my_appointments, clients=unique_clients)
    
    specialists = Specialist.query.filter_by(is_active=True).all()
    user_appointments = Appointment.query.filter_by(user_id=current_user.id).order_by(Appointment.id.desc()).all()
    progress_notes = Progress.query.filter_by(user_id=current_user.id).order_by(Progress.id.desc()).all()
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    selected_sp_id = request.args.get('specialist_id', type=int)
    return render_template(
        'dashboard.html',
        specialists=specialists,
        appointments=user_appointments,
        progress_notes=progress_notes,
        standard_slots=STANDARD_SLOTS,
        current_date=today_str,
        selected_sp_id=selected_sp_id
    )

@app.route('/api/available-slots/<int:specialist_id>/<date_str>')
@login_required
def available_slots(specialist_id, date_str):
    booked = Appointment.query.filter_by(specialist_id=specialist_id, date_str=date_str, status='Aktiv').all()
    booked_times = [a.time_str for a in booked]
    available = [slot for slot in STANDARD_SLOTS if slot not in booked_times]
    return jsonify({"available_slots": available, "booked_slots": booked_times})

@app.route('/book-appointment', methods=['POST'])
@login_required
def book_appointment():
    specialist_id = request.form.get('specialist_id')
    child_name = request.form.get('child_name', '').strip()
    child_age = request.form.get('child_age')
    time_str = request.form.get('time_str', '').strip()
    booking_type = request.form.get('booking_type', 'single') # 'single', 'weekly', 'monthly'

    if not specialist_id or not child_name or not time_str:
        flash("Barlıq kerekli maydanlardı toltırıń!", "warning")
        return redirect(url_for('dashboard'))

    try:
        sp_id = int(specialist_id)
        age = int(child_age) if child_age else 4
    except ValueError:
        flash("Nadurıs maǵlıwmat kiritildi!", "danger")
        return redirect(url_for('dashboard'))

    target_specialist = db.session.get(Specialist, sp_id)
    if not target_specialist or not target_specialist.is_active:
        flash("Tańlanǵan qániyge aktiv emes!", "danger")
        return redirect(url_for('dashboard'))

    target_dates = []
    if booking_type == 'single':
        date_str = request.form.get('date_str', '').strip()
        if not date_str:
            flash("Qabıl sánesin tańlań!", "warning")
            return redirect(url_for('dashboard'))
        target_dates = [date_str]
    elif booking_type in ('weekly', 'monthly'):
        start_date_str = request.form.get('start_date', '').strip() or request.form.get('date_str', '').strip()
        selected_days = request.form.getlist('days_of_week')
        if not start_date_str:
            start_date_str = (datetime.utcnow() + timedelta(hours=5)).strftime('%Y-%m-%d')
        if not selected_days:
            flash("Iltimas, hápte kúnlerinen keminde birin tańlań!", "warning")
            return redirect(url_for('dashboard'))

        try:
            start_dt = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            flash("Nadurıs baslanıw sánesi!", "danger")
            return redirect(url_for('dashboard'))

        total_days = 7 if booking_type == 'weekly' else 30
        int_days = [int(x) for x in selected_days if x.isdigit()]
        for i in range(total_days):
            d = start_dt + timedelta(days=i)
            if d.weekday() in int_days:
                target_dates.append(d.strftime('%Y-%m-%d'))

        if not target_dates:
            flash("Tańlanǵan hápte kúnleri boyınsha sáneler tabılmadı!", "warning")
            return redirect(url_for('dashboard'))

    # Conflict check across all target dates for requested specialist
    conflicting_apps = Appointment.query.filter(
        Appointment.specialist_id == sp_id,
        Appointment.time_str == time_str,
        Appointment.status == 'Aktiv',
        Appointment.date_str.in_(target_dates)
    ).all()

    if conflicting_apps:
        conflict_dates = sorted(list(set(a.date_str for a in conflicting_apps)))
        # Search for alternative active specialists who are free on ALL target_dates at time_str
        other_specialists = Specialist.query.filter(
            Specialist.id != sp_id,
            Specialist.is_active == True
        ).all()

        alternative_specialists = []
        for other_sp in other_specialists:
            other_conflict_count = Appointment.query.filter(
                Appointment.specialist_id == other_sp.id,
                Appointment.time_str == time_str,
                Appointment.status == 'Aktiv',
                Appointment.date_str.in_(target_dates)
            ).count()
            if other_conflict_count == 0:
                alternative_specialists.append(other_sp)

        conflict_str = ", ".join(conflict_dates)
        if alternative_specialists:
            alt_list = ", ".join([f"{s.name} ({s.price:,.0f} so'm)" for s in alternative_specialists])
            flash(
                f"Qániyge {target_specialist.name} {time_str} waqtında tómendegi sánelerde bánt: {conflict_str}. "
                f"Ushbu waqıtta bos basqa qániyge(ler): {alt_list}.",
                "warning"
            )
        else:
            flash(
                f"Qániyge {target_specialist.name} {time_str} waqtında tómendegi sánelerde bánt: {conflict_str}. "
                f"Bul waqıtta basqa qániygeler de bánt, iltimas basqa bos waqıt tańlań.",
                "danger"
            )
        return redirect(url_for('dashboard', specialist_id=sp_id))

    new_apps = []
    for d in target_dates:
        app_obj = Appointment(
            user_id=current_user.id,
            specialist_id=sp_id,
            child_name=child_name,
            child_age=age,
            phone=current_user.phone or "Kiritilmegen",
            date_str=d,
            time_str=time_str,
            status='Aktiv'
        )
        new_apps.append(app_obj)

    db.session.add_all(new_apps)
    db.session.commit()
    plan_name = "Bir kúnlik" if booking_type == 'single' else ("Bir háptelik" if booking_type == 'weekly' else "Bir aylıq")
    flash(f"{plan_name} rejesi boyınsha {len(target_dates)} kún ushın qabılǵa tabıslı jazıldıńız ({time_str})!", "success")
    return redirect(url_for('dashboard'))

@app.route('/update-appointment-status/<int:app_id>', methods=['POST'])
@login_required
def update_appointment_status(app_id):
    new_status = request.form.get('status', '').strip()
    valid_statuses = ['Aktiv', 'Nátiyjeli juwmaqlandı', 'Kelmadi', 'Biykar etildi']
    if new_status not in valid_statuses:
        flash("Nadurıs status!", "danger")
        return redirect(request.referrer or url_for('dashboard'))

    app_item = db.session.get(Appointment, app_id)
    if not app_item:
        flash("Qabıl tabılmadı!", "warning")
        return redirect(request.referrer or url_for('dashboard'))

    if current_user.role == 'admin':
        app_item.status = new_status
        db.session.commit()
        flash(f"Qabıl #{app_id} statusı '{new_status}' etip belgilendi!", "success")
        return redirect(request.referrer or url_for('admin_panel'))
    elif current_user.role == 'specialist' and app_item.specialist_id == current_user.specialist_id:
        app_item.status = new_status
        db.session.commit()
        flash(f"Qabıl statusı '{new_status}' etip belgilendi!", "success")
        return redirect(request.referrer or url_for('dashboard'))
    else:
        flash("Status ózgertiwge ruxsat joq!", "danger")
        return redirect(url_for('dashboard'))

@app.route('/add-progress', methods=['POST'])
@login_required
def add_progress():
    if current_user.role != 'specialist': return redirect(url_for('index'))
    user_id = request.form.get('user_id')
    child_name = request.form.get('child_name')
    note = request.form.get('note')
    homework = request.form.get('homework')
    prg = Progress(user_id=int(user_id), specialist_id=current_user.specialist_id, child_name=child_name, note=note, homework=homework)
    db.session.add(prg)
    db.session.commit()
    flash("Nátiyje saqlandı!", "success")
    return redirect(url_for('dashboard'))

@app.route('/cancel-my-appointment/<int:app_id>', methods=['POST'])
@login_required
def cancel_my_appointment(app_id):
    app_item = Appointment.query.filter_by(id=app_id, user_id=current_user.id).first_or_404()
    app_item.status = 'Biykar etildi'
    db.session.commit()
    flash("Qabıl biykar etildi.", "info")
    return redirect(url_for('dashboard'))

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    contact_users = []
    if current_user.role == 'admin':
        contact_users = User.query.filter(User.id != current_user.id).all()
    elif current_user.role == 'specialist':
        admin = User.query.filter_by(role='admin').first()
        my_users_ids = [a.user_id for a in Appointment.query.filter_by(specialist_id=current_user.specialist_id).all()]
        my_users = User.query.filter(User.id.in_(my_users_ids)).all() if my_users_ids else []
        contact_users = [admin] + my_users if admin else my_users
    else:
        admin = User.query.filter_by(role='admin').first()
        my_sp_ids = [a.specialist_id for a in Appointment.query.filter_by(user_id=current_user.id).all()]
        my_sp_users = User.query.filter(User.specialist_id.in_(my_sp_ids)).all() if my_sp_ids else []
        contact_users = [admin] + my_sp_users if admin else my_sp_users

    contact_users = list({u.id: u for u in contact_users if u is not None}.values())

    # Attach unread count and latest message for Telegram-style indicators
    for u in contact_users:
        u.unread_from_user = ChatMessage.query.filter_by(
            sender_id=u.id, receiver_id=current_user.id, is_read=False
        ).count()
        last_m = ChatMessage.query.filter(
            ((ChatMessage.sender_id == current_user.id) & (ChatMessage.receiver_id == u.id)) |
            ((ChatMessage.sender_id == u.id) & (ChatMessage.receiver_id == current_user.id))
        ).order_by(ChatMessage.created_at.desc()).first()
        u.last_message = last_m

    if request.method == 'POST':
        msg_text = request.form.get('message', '').strip()
        receiver_id = request.form.get('receiver_id')
        allowed_ids = [u.id for u in contact_users]
        if msg_text and receiver_id and int(receiver_id) in allowed_ids:
            msg = ChatMessage(sender_id=current_user.id, receiver_id=int(receiver_id), message=msg_text, is_read=False)
            db.session.add(msg)
            db.session.commit()
        return redirect(url_for('chat', user_id=receiver_id))

    selected_user_id = request.args.get('user_id')
    active_chat_user = None
    messages = []
    if selected_user_id and int(selected_user_id) in [u.id for u in contact_users]:
        active_chat_user = db.session.get(User, int(selected_user_id))
        # Mark all messages from active_chat_user as read
        ChatMessage.query.filter_by(
            sender_id=active_chat_user.id, receiver_id=current_user.id, is_read=False
        ).update({'is_read': True})
        db.session.commit()

        messages = ChatMessage.query.filter(
            ((ChatMessage.sender_id == current_user.id) & (ChatMessage.receiver_id == active_chat_user.id)) |
            ((ChatMessage.sender_id == active_chat_user.id) & (ChatMessage.receiver_id == current_user.id))
        ).order_by(ChatMessage.created_at.asc()).all()

    return render_template('chat.html', contacts=contact_users, active_user=active_chat_user, messages=messages)

@app.route('/api/chat/messages/<int:target_user_id>')
@login_required
def api_chat_messages(target_user_id):
    target = db.session.get(User, target_user_id)
    if not target:
        return jsonify({'messages': []})

    ChatMessage.query.filter_by(
        sender_id=target.id, receiver_id=current_user.id, is_read=False
    ).update({'is_read': True})
    db.session.commit()

    msgs = ChatMessage.query.filter(
        ((ChatMessage.sender_id == current_user.id) & (ChatMessage.receiver_id == target.id)) |
        ((ChatMessage.sender_id == target.id) & (ChatMessage.receiver_id == current_user.id))
    ).order_by(ChatMessage.created_at.asc()).all()

    result = [{
        'id': m.id,
        'sender_id': m.sender_id,
        'is_me': m.sender_id == current_user.id,
        'message': m.message,
        'time': m.created_at.strftime('%H:%M')
    } for m in msgs]
    return jsonify({'messages': result})

@app.route('/add-review', methods=['POST'])
@login_required
def add_review():
    content = request.form.get('content', '').strip()
    rating = int(request.form.get('rating', 5))
    rev = Review(user_id=current_user.id, author_name=current_user.full_name, rating=rating, content=content)
    db.session.add(rev)
    db.session.commit()
    flash("Pikir qaldırıldı!", "success")
    return redirect(url_for('index') + '#reviews')

@app.route('/admin')
@login_required
def admin_panel():
    auto_update_expired_appointments()
    if current_user.role != 'admin': return redirect(url_for('index'))
    appointments = Appointment.query.order_by(Appointment.id.desc()).all()
    specialists = Specialist.query.all()
    users = User.query.all() # Barlıq userlar admin ushın
    users_count = User.query.filter_by(role='user').count()
    active_apps_count = Appointment.query.filter_by(status='Aktiv').count()
    reviews = Review.query.order_by(Review.id.desc()).all()
    reviews_setting = Setting.query.filter_by(key='reviews_active').first()
    reviews_enabled = reviews_setting.value == 'true' if reviews_setting else True

    return render_template('admin.html', appointments=appointments, specialists=specialists, users=users, users_count=users_count, active_apps_count=active_apps_count, reviews=reviews, reviews_enabled=reviews_enabled)

@app.route('/admin/cancel-appointment/<int:app_id>', methods=['POST'])
@login_required
def admin_cancel_appointment(app_id):
    if current_user.role != 'admin': return redirect(url_for('index'))
    app_item = db.get_or_404(Appointment, app_id)
    app_item.status = 'Biykar etildi'
    db.session.commit()
    flash("Qabıl biykar etildi.", "info")
    return redirect(url_for('admin_panel'))

@app.route('/admin/create-specialist-account', methods=['POST'])
@login_required
def create_specialist_account():
    if current_user.role != 'admin': return redirect(url_for('index'))
    sp_id = request.form.get('specialist_id')
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    sp = db.session.get(Specialist, int(sp_id)) if sp_id else None
    if not sp:
        flash("Qániyge tabılmadı!", "warning")
        return redirect(url_for('admin_panel'))
    if User.query.filter_by(username=username).first():
        flash("Login bánt!", "warning")
        return redirect(url_for('admin_panel'))
    new_user = User(username=username, full_name=sp.name, role='specialist', specialist_id=sp.id)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    flash("Kabinet ashıldı!", "success")
    return redirect(url_for('admin_panel'))

@app.route('/admin/update-user', methods=['POST'])
@login_required
def admin_update_user():
    if current_user.role != 'admin': return redirect(url_for('index'))
    target_id = request.form.get('target_user_id')
    new_username = request.form.get('new_username', '').strip()
    new_password = request.form.get('new_password', '').strip()
    
    usr = db.session.get(User, int(target_id)) if target_id else None
    if usr:
        if new_username: usr.username = new_username
        if new_password: usr.set_password(new_password)
        db.session.commit()
        flash("Paydalanıwshı logini/paroli jańalandı!", "success")
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete-review/<int:rev_id>', methods=['POST'])
@login_required
def delete_review(rev_id):
    if current_user.role != 'admin': return redirect(url_for('index'))
    rev = db.get_or_404(Review, rev_id)
    db.session.delete(rev)
    db.session.commit()
    flash("Pikir óshirildi.", "info")
    return redirect(url_for('admin_panel'))

@app.route('/admin/toggle-reviews', methods=['POST'])
@login_required
def toggle_reviews():
    if current_user.role != 'admin': return redirect(url_for('index'))
    setting = Setting.query.filter_by(key='reviews_active').first()
    setting.value = 'false' if setting.value == 'true' else 'true'
    db.session.commit()
    flash("Pikirler bólimi jańalandı!", "info")
    return redirect(url_for('admin_panel'))

@app.route('/admin/update-price/<int:specialist_id>', methods=['POST'])
@login_required
def update_price(specialist_id):
    if current_user.role != 'admin': return redirect(url_for('index'))
    new_price = float(request.form.get('price', 50000))
    sp = db.get_or_404(Specialist, specialist_id)
    sp.price = new_price
    db.session.commit()
    flash("Baha jańalandı!", "success")
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete-specialist/<int:specialist_id>', methods=['POST'])
@login_required
def delete_specialist(specialist_id):
    if current_user.role != 'admin': return redirect(url_for('index'))
    sp = db.get_or_404(Specialist, specialist_id)
    sp.is_active = False
    db.session.commit()
    flash("Vrach óshirildi.", "info")
    return redirect(url_for('admin_panel'))

@app.route('/admin/add-specialist', methods=['POST'])
@login_required
def add_specialist():
    if current_user.role != 'admin': return redirect(url_for('index'))
    name = request.form.get('name', '').strip()
    age = int(request.form.get('age', 30))
    experience = request.form.get('experience', '').strip()
    success_rate = int(request.form.get('success_rate', 95))
    price = float(request.form.get('price', 50000))
    description = request.form.get('description', '').strip()
    
    image_file = request.files.get('image_file')
    image_url = request.form.get('image_url', '').strip()
    image = process_specialist_image(image_file, image_url)
    
    new_sp = Specialist(
        name=name,
        age=age,
        experience=experience,
        success_rate=success_rate,
        price=price,
        image=image,
        description=description
    )
    db.session.add(new_sp)
    db.session.commit()
    flash("Jańa qániyge qosıldı!", "success")
    return redirect(url_for('admin_panel'))

@app.route('/admin/update-specialist/<int:specialist_id>', methods=['POST'])
@login_required
def update_specialist(specialist_id):
    if current_user.role != 'admin': return redirect(url_for('index'))
    sp = db.get_or_404(Specialist, specialist_id)
    
    name = request.form.get('name', '').strip()
    if name:
        sp.name = name
    
    age = request.form.get('age')
    if age:
        try:
            sp.age = int(age)
        except ValueError:
            pass
        
    experience = request.form.get('experience', '').strip()
    if experience:
        sp.experience = experience
        
    success_rate = request.form.get('success_rate')
    if success_rate:
        try:
            sp.success_rate = int(success_rate)
        except ValueError:
            pass
        
    price = request.form.get('price')
    if price:
        try:
            sp.price = float(price)
        except ValueError:
            pass
        
    description = request.form.get('description')
    if description is not None:
        sp.description = description.strip()
        
    image_file = request.files.get('image_file')
    image_url = request.form.get('image_url', '').strip()
    
    new_image = process_specialist_image(image_file, image_url, fallback=None)
    if new_image:
        sp.image = new_image
        
    db.session.commit()
    flash("Qániyge maǵlıwmatları jańalandı!", "success")
    return redirect(url_for('admin_panel'))

def init_database(retries=5, delay=3):
    for attempt in range(1, retries + 1):
        try:
            with app.app_context():
                seed_database()
            return
        except Exception as exc:
            app.logger.warning('DB init failed (attempt %s/%s): %s', attempt, retries, exc)
            if attempt == retries:
                raise
            time.sleep(delay)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

init_database()

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true', host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
