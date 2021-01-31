from flask import Flask, render_template, request, escape, session, copy_current_request_context
from threading import Thread
#from time import sleep
import sys
sys.path.append(r"C:\python\appweb\module")
from vsearch import searchlet
from DBcm import UseDatabase, ConnectionError, CredentialsError, SQLError
from checker import check_logged_in

app = Flask(__name__)
app.config['dbconfig'] = {'host': '127.0.0.1',
                          'user': 'vsearch',
                          'password': 'vsearchpasswd',
                          'database': 'vsearchlogDB', }

@app.route('/login')
def do_login():
    session['logged_in'] = True
    return 'You are logged in'

@app.route('/logout')
def do_logout():
    session.pop('logged_in')
    return 'You are logged out'

@app.route('/')
@app.route('/entry')
def entry_page() -> str:
    return render_template('entry.html',the_title='Привет')

@app.route('/search', methods=['POST'])
def do_search() -> 'html':

    try:
        @copy_current_request_context
        def log_request(req: 'flask_request',res: str) -> None:
            #sleep(15)
            with UseDatabase(app.config['dbconfig']) as cursor:
                _SQL = """insert into log
                              (phrase, letters, ip, browser_string, results)
                              values
                              (%s, %s, %s, %s, %s)"""
                cursor.execute(_SQL,(req.form['phrase'],
                                     req.form['letters'],
                                     req.remote_addr,
                                     req.user_agent.browser,
                                     res))
            with open ('vsearch.log','a') as log:
                print(req.form,req.remote_addr,req.user_agent,res, file=log, sep='|')
    except Exception as err:
        print('Ошибка в записи результата в БД', str(err))

    phrase = request.form['phrase']
    letters = request.form['letters']
    title = 'Результаты:'
    results = str(searchlet(phrase, letters))

    try:
        t = Thread(target=log_request, args=(request, results))
        t.start()
    except Exception as err:
        print('Ошибка подключения БД ',str(err))
    return render_template('results.html',
                           the_title=title,
                           the_phrase=phrase,
                           the_letters=letters,
                           the_results=results,)

@app.route('/viewlog')
@check_logged_in
def view_the_log() -> 'html':
    try:
        with UseDatabase (app.config['dbconfig']) as cursor:
            _SQL = """select phrase, letters, ip, browser_string, results from log"""
            cursor.execute(_SQL)
            contens = cursor.fetchall()
        titles=('В этом слове','Ищем эти буквы','Адрес','Кто и с чего','Результат')
        return render_template('viewlog.html',
                                the_title='База данных',
                                the_row_titles=titles,
                                the_data=contens)
    except ConnectionError as err:
        print('ошибка конектора БД, ошибка:', str(err))
    except CredentialsError as err:
        print('ошибка имени пользователя или пароля, ошибка:   ', str(err))
    except SQLError as err:
        print('БД недоступна ', str(err))
    except Exception as err:
        print('Что-то случилось ', str(err))
    return 'Error'


app.secret_key = 'password'
if __name__ == '__main__':
    app.run(debug=True)
