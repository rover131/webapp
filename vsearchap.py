from flask import Flask, render_template, request,escape
import sys
sys.path.append(r"C:\python\project\mymodul")
from vsearch import searchlet
from DBcm import UseDatabase

app = Flask(__name__)
app.config['dbconfig'] = {'host': '127.0.0.1',
                          'user': 'vsearch',
                          'password': 'vsearchpasswd',
                          'database': 'vsearchlogDB', }

def log_request(req: 'flask_request',res: str) -> None:
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

@app.route('/')
@app.route('/entry')
def entry_page() -> str:
    return render_template('entry.html',the_title='Привет')

@app.route('/search', methods=['POST'])
def do_search() -> 'html':
    phrase = request.form['phrase']
    letters = request.form['letters']
    title = 'Результаты:'
    results=str(searchlet(phrase, letters))
    log_request(request, results)
    return render_template('results.html',
                           the_title=title,
                           the_phrase=phrase,
                           the_letters=letters,
                           the_results=results,)

@app.route('/viewlog')
def view_the_log() -> 'html':
    with UseDatabase (app.config['dbconfig']) as cursor:
        _SQL = """select phrase, letters, ip, browser_string, results from log"""
        cursor.execute(_SQL)
        contens = cursor.fetchall()
    titles=('В этом слове','Ищем эти буквы','Адрес','Кто и с чего','Результат')
    return render_template('viewlog.html',
                            the_title='База данных',
                            the_row_titles=titles,
                            the_data=contens,)
if __name__ == '__main__':
    app.run(debug=True)
