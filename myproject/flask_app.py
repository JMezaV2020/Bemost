from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Usuario de prueba
class User(UserMixin):
    def __init__(self, id):
        self.id = id

users = {'Admin': {'password': '699'}}

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and user['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    try:
        df = pd.read_excel('datos_limpios.xlsx')

        # Cambiar el conteo ESTADO
        pivot_table1 = df.groupby(['ESTADO', 'RESPONSABLE']).size().reset_index(name='CANTIDAD')
        pivot_table1 = pivot_table1[['CANTIDAD', 'RESPONSABLE', 'ESTADO']]  # Mover Cantidad como la primera columna
        pivot_table1 = pivot_table1.sort_values(by='CANTIDAD', ascending=False)  # Ordenar por Cantidad de mayor a menor

        # Agrupar por TEMA y RESPONSABLE y contar la cantidad
        pivot_table2 = df.groupby(['TEMA', 'RESPONSABLE']).size().reset_index(name='CANTIDAD')

        estados = df['ESTADO'].unique()

        table1 = pivot_table1.to_html(classes='table table-striped', index=False)
        table2 = pivot_table2.to_html(classes='table table-striped', index=False)
    except Exception as e:
        import traceback
        error_message = traceback.format_exc()
        table1 = f"<p>Error leyendo el archivo Excel: {str(e)}</p><pre>{error_message}</pre>"
        table2 = ""
    return render_template('table.html', table1=table1, table2=table2, estados=estados)

@app.route('/charts')
@login_required
def charts():
    try:
        df = pd.read_excel('datos_limpios.xlsx')
        estado_counts = df['ESTADO'].value_counts()
        fig1 = px.pie(estado_counts, values=estado_counts.values, names=estado_counts.index, title='Distribución por Estado', labels={'counts': 'Cantidad'})
        fig1.update_traces(textinfo='label+value')  # Mostrar etiquetas y valores en el gráfico
        graph1 = pio.to_html(fig1, full_html=False)

        df['Fecha'] = pd.to_datetime(df['Fecha'])
        estado_fecha_counts = df.groupby(['Fecha', 'ESTADO']).size().reset_index(name='counts')
        fig3 = px.line(estado_fecha_counts, x='Fecha', y='counts', color='ESTADO', title='Conteo de Eventos por Fecha y Estado')
        graph3 = pio.to_html(fig3, full_html=False)
    except Exception as e:
        import traceback
        error_message = traceback.format_exc()
        graph1 = f"<p>Error generando gráficos: {str(e)}</p><pre>{error_message}</pre>"
        graph3 = ""
    return render_template('charts.html', graph1=graph1, graph3=graph3)

if __name__ == '__main__':
    app.run(debug=True)
