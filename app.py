import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'logoped-nukus-secure-2026-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///logoped.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 6 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
    image = db.Column(db.String(500), default='default.png')
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
    time_str = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Aktiv')
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(50), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

STANDARD_SLOTS = ["09:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00", "14:00 - 15:00", "15:00 - 16:00", "16:00 - 17:00", "17:00 - 18:00"]

def seed_database():
    db.create_all()
    if not Setting.query.filter_by(key='reviews_active').first():
        db.session.add(Setting(key='reviews_active', value='true'))
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', full_name='Oray Administratorı', role='admin', phone="+998 90 123 45 67")
        admin.set_password('admin123')
        db.session.add(admin)
    if Specialist.query.count() == 0:
        s1 = Specialist(name="Dilnoza Alimbetova", age=32, experience="8 jıl", success_rate=95, price=50000, image="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=600", description="Duduqlanıw hám tutıǵıw yamasa al-analıq waqtındaǵı logopedik xızmet.")
        s2 = Specialist(name="Rustam Joldasbaev", age=38, experience="12 jıl", success_rate=98, price=70000, image="https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=600", description="Keshikken sóylewdi rawajlandırıw, autizm belgileri bar balalar menen islesiw.")
        s3 = Specialist(name="Aygul Turemuratova", age=29, experience="5 jıl", success_rate=92, price=45000, image="https://images.unsplash.com/photo-1594824432258-f446051515bb?w=600", description="Artikulyaciyalıq gimnastika, 'R' hám 'L' háriplerin anıq aytıwdı úyretiw.")
        s4 = Specialist(name="Zarina Qıdırbaeva", age=35, experience="10 jıl", success_rate=96, price=60000, image="https://images.unsplash.com/photo-1527613426496-2287d6b820bb?w=600", description="Kishi jastaǵı balalarda sóylew qorqınıshın jeńiw hám logonevrozdi emlew.")
        db.session.add_all([s1, s2, s3, s4])
    db.session.commit()

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
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            if user.role == 'admin': return redirect(url_for('admin_panel'))
            return redirect(url_for('dashboard'))
        flash("Login yamasa parol nadurıs!", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin': return redirect(url_for('admin_panel'))
    if current_user.role == 'specialist':
        my_appointments = Appointment.query.filter_by(specialist_id=current_user.specialist_id).order_by(Appointment.date_str.desc()).all()
        unique_clients = {app.user_id: app for app in my_appointments if app.status == 'Aktiv'}.values()
        return render_template('dashboard_specialist.html', appointments=my_appointments, clients=unique_clients)
    
    specialists = Specialist.query.filter_by(is_active=True).all()
    user_appointments = Appointment.query.filter_by(user_id=current_user.id).order_by(Appointment.id.desc()).all()
    progress_notes = Progress.query.filter_by(user_id=current_user.id).order_by(Progress.id.desc()).all()
    return render_template('dashboard.html', specialists=specialists, appointments=user_appointments, progress_notes=progress_notes, standard_slots=STANDARD_SLOTS)

@app.route('/api/available-slots/<int:specialist_id>/<date_str>')
@login_required
def available_slots(specialist_id, date_str):
    booked = Appointment.query.filter_by(specialist_id=specialist_id, date_str=date_str, status='Aktiv').all()
    booked_times = [app.time_str for app in booked]
    available = [slot for slot in STANDARD_SLOTS if slot not in booked_times]
    return jsonify({"available_slots": available})

@app.route('/book-appointment', methods=['POST'])
@login_required
def book_appointment():
    specialist_id = request.form.get('specialist_id')
    child_name = request.form.get('child_name')
    child_age = request.form.get('child_age')
    date_str = request.form.get('date_str')
    time_str = request.form.get('time_str')

    if Appointment.query.filter_by(specialist_id=specialist_id, date_str=date_str, time_str=time_str, status='Aktiv').first():
        flash("Bul waqıt bánt!", "warning")
        return redirect(url_for('dashboard'))

    app_obj = Appointment(
        user_id=current_user.id, specialist_id=specialist_id,
        child_name=child_name, child_age=int(child_age) if child_age else 4,
        phone=current_user.phone or "Kiritilmegen",
        date_str=date_str, time_str=time_str, status='Aktiv'
    )
    db.session.add(app_obj)
    db.session.commit()
    flash("Qabılǵa jazıldıńız!", "success")
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
        my_users = User.query.filter(User.id.in_(my_users_ids)).all()
        contact_users = [admin] + my_users if admin else my_users
    else:
        admin = User.query.filter_by(role='admin').first()
        my_sp_ids = [a.specialist_id for a in Appointment.query.filter_by(user_id=current_user.id).all()]
        my_sp_users = User.query.filter(User.specialist_id.in_(my_sp_ids)).all()
        contact_users = [admin] + my_sp_users if admin else my_sp_users

    contact_users = list({u.id: u for u in contact_users if u is not None}.values())

    if request.method == 'POST':
        msg_text = request.form.get('message', '').strip()
        receiver_id = request.form.get('receiver_id')
        allowed_ids = [u.id for u in contact_users]
        if msg_text and receiver_id and int(receiver_id) in allowed_ids:
            msg = ChatMessage(sender_id=current_user.id, receiver_id=int(receiver_id), message=msg_text)
            db.session.add(msg)
            db.session.commit()
        return redirect(url_for('chat', user_id=receiver_id))

    selected_user_id = request.args.get('user_id')
    active_chat_user = None
    messages = []
    if selected_user_id and int(selected_user_id) in [u.id for u in contact_users]:
        active_chat_user = User.query.get(int(selected_user_id))
        messages = ChatMessage.query.filter(
            ((ChatMessage.sender_id == current_user.id) & (ChatMessage.receiver_id == active_chat_user.id)) |
            ((ChatMessage.sender_id == active_chat_user.id) & (ChatMessage.receiver_id == current_user.id))
        ).order_by(ChatMessage.created_at.asc()).all()

    return render_template('chat.html', contacts=contact_users, active_user=active_chat_user, messages=messages)

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
    app_item = Appointment.query.get_or_404(app_id)
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
    sp = Specialist.query.get(sp_id)
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
    
    usr = User.query.get(target_id)
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
    rev = Review.query.get_or_404(rev_id)
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
    sp = Specialist.query.get_or_404(specialist_id)
    sp.price = new_price
    db.session.commit()
    flash("Baha jańalandı!", "success")
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete-specialist/<int:specialist_id>', methods=['POST'])
@login_required
def delete_specialist(specialist_id):
    if current_user.role != 'admin': return redirect(url_for('index'))
    sp = Specialist.query.get_or_404(specialist_id)
    sp.is_active = False
    db.session.commit()
    flash("Vrach óshirildi.", "info")
    return redirect(url_for('admin_panel'))

@app.route('/admin/add-specialist', methods=['POST'])
@login_required
def add_specialist():
    if current_user.role != 'admin': return redirect(url_for('index'))
    name = request.form.get('name')
    age = int(request.form.get('age', 30))
    experience = request.form.get('experience')
    success_rate = int(request.form.get('success_rate', 95))
    price = float(request.form.get('price', 50000))
    image_url = request.form.get('image_url')
    description = request.form.get('description', '')
    new_sp = Specialist(name=name, age=age, experience=experience, success_rate=success_rate, price=price, image=image_url or "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=600", description=description)
    db.session.add(new_sp)
    db.session.commit()
    flash("Jańa qániyge qosıldı!", "success")
    return redirect(url_for('admin_panel'))

with app.app_context():
    seed_database()

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true', host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
