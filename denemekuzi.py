import io
import zipfile
import uuid
from flask import Flask, render_template, request, send_file, session, redirect, url_for
import qrcode

app = Flask(__name__)
app.secret_key = "cok_gizli_bir_key_burasi" # Session güvenliği için

# Şifreni buradan değiştirebilirsin
ADMIN_PASSWORD = "1234" 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return "Hatalı şifre! <a href='/login'>Tekrar dene</a>"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/generate', methods=['POST'])
def generate():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        adet = int(request.form.get('adet', 5))
    except ValueError:
        adet = 5

    # Zip dosyasını bellekte oluştur (Render disk yazmaya izin vermeyebilir)
    memory_file = io.BytesIO()
    sifre_listesi = []

    with zipfile.ZipFile(memory_file, 'w') as zf:
        for i in range(adet):
            # 8 haneli rastgele benzersiz şifre üret
            random_text = str(uuid.uuid4())[:8]
            sifre_listesi.append(random_text)

            # QR Kod oluştur
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(random_text)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # Resmi zip içine ekle
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            zf.writestr(f"qr_kod_{i+1}.png", img_byte_arr.getvalue())

        # İSTEDİĞİN ÖZELLİK: Tüm şifreleri bir metin dosyasına yaz ve zip'e ekle
        sifre_metni = "\n".join(sifre_listesi)
        zf.writestr("sifreler_listesi.txt", sifre_metni)

    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='qr_paketleri.zip'
    )

if __name__ == '__main__':
    app.run(debug=True)