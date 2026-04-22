import io
import zipfile
import random
import string
import qrcode
from flask import Flask, render_template, request, send_file, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'qr_sifre_anahtari'

ADMIN_PASSWORD = "1453" # Giriş şifren

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
    return '''
        <form method="post" style="text-align:center; margin-top:50px;">
            <input type="password" name="password" placeholder="Şifre">
            <button type="submit">Giriş</button>
        </form>
    '''

@app.route('/generate', methods=['POST'])
def generate():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    adet = int(request.form.get('adet', 1))
    
    # Zip dosyasını bellekte oluştur (
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        karakterler = string.ascii_letters + string.digits
        
        for i in range(adet):
            sifre = ''.join(random.choice(karakterler) for _ in range(8))
            
            # QR Kod Oluştur
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(sifre)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Resmi belleğe kaydet
            img_io = io.BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            
            # Zip içine ekle
            zf.writestr(f"sifre_{i+1}.png", img_io.getvalue())
            
    memory_file.seek(0)
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='qr_kodlar.zip'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)