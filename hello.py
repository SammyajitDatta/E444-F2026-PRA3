from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    email = EmailField(
        'What is your UofT Email address?',
        validators=[DataRequired(), Email()]
    )
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()

    if form.validate_on_submit():

        # Check that it is a UofT email
        if 'utoronto' not in form.email.data.lower():
            flash('Please fill in a UofT email address.')
            return redirect(url_for('index'))

        # Save user information
        session['name'] = form.name.data
        session['email'] = form.email.data

        # Go to chatbot page
        return redirect(url_for('chatbot'))

    return render_template(
        'index.html',
        form=form,
        name=session.get('name'),
        email=session.get('email')
    )


@app.route('/chatbot')
def chatbot():
    # Prevent someone from going directly to /chatbot
    # without filling out the form first
    if 'name' not in session or 'email' not in session:
        return redirect(url_for('index'))

    return render_template('chat.html')


@app.route('/chat', methods=['POST'])
def chat():
    message = request.json['message']
    lower_message = message.lower().strip()

    # User tells chatbot their name
    if lower_message.startswith('my name is '):
        remembered_name = message[len('my name is '):].strip()
        remembered_name = remembered_name.rstrip('.!?')

        session['chat_name'] = remembered_name

        reply = f'Nice to meet you, {remembered_name}!'

    # User asks chatbot to remember it
    elif 'what is my name' in lower_message:
        remembered_name = session.get('chat_name')

        if remembered_name:
            reply = f'Your name is {remembered_name}.'
        else:
            reply = "I don't know your name yet."

    # Original starter behavior
    elif 'hello' in lower_message:
        reply = 'Hello!'

    else:
        reply = "I don't understand."

    return {'reply': reply}


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)