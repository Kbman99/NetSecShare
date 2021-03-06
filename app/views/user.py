from flask import (Blueprint, render_template, redirect, url_for,
                   abort, flash, send_from_directory, jsonify, request)
from flask.ext.login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer
from app import app, models, db
from app.forms import user as user_forms
from app.logger_setup import logger
from app.toolbox import email
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
import os
import random

# Serializer for generating random tokens
ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Create a user blueprint
userbp = Blueprint('userbp', __name__, url_prefix='/user')

# Define ldap server to connect with
s = Server(app.config['LDAP_SERVER'], get_info=ALL)


@userbp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = user_forms.SignUp()
    if form.validate_on_submit():
        # Create a user who hasn't validated his email address
        user = models.User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            #            phone=form.phone.data,
            email=form.email.data,
            confirmation=False,
            password=form.password.data
        )

        # Create a ldap_user 
        ldap_user = {
            'objectClass': ['inetOrgPerson', 'posixAccount', 'top'],
            'givenName': user.first_name,
            'sn': user.last_name,
            'gidNumber': 500,
            'uidNumber': random.randint(1000, 1000000),
            'uid': user.email.split('@', 1)[0],
            'homeDirectory': '/home/users/' + user.email.split('@', 1)[0],
            'userPassword': form.password.data
        }

        user_ldap_dn = 'cn=' + ldap_user['uid'] + ',ou=Users,dc=ldap,dc=com'
        # Insert the user in the database
        db.session.add(user)
        # Add user in LDAP
        try:
            c = Connection(s, user=app.config['LDAP_SERVICE_USERNAME'], password=app.config['LDAP_SERVICE_PASSWORD'])
            c.open()
            c.start_tls()
            c.bind()
            c.add(user_ldap_dn, attributes=ldap_user)
        except Exception as e:
            # remove the user from the db session
            print(e)
            db.session.rollback()
            db.session.commit()
            logger.error('User account creation failed', user=user.get_id())
            flash('There was an error in creating your account, if the issue persists, '
                  'please contact and administrator.', 'negative')
            return redirect(url_for('index'))
        logger.info('User account created successfully', user=user.get_id())
        # If there was no error in adding user via LDAP we will commit the session to the database
        c.unbind()
        db.session.commit()
        # Subject of the confirmation email
        subject = 'Please confirm your email address.'
        # Generate a random token
        token = ts.dumps(user.email, salt='email-confirm-key')
        # Build a confirm link with token
        confirmUrl = url_for('userbp.confirm', token=token, _external=True)
        # Render an HTML template to send by email
        html = render_template('email/confirm.html',
                               confirm_url=confirmUrl)
        # Send the email to user
        email.send(user.email, subject, html)
        # Send back to the home page
        flash('Check your emails to confirm your email address.', 'positive')
        return redirect(url_for('index'))
    return render_template('user/signup.html', form=form, title='Sign up')


@userbp.route('/confirm/<token>', methods=['GET', 'POST'])
def confirm(token):
    try:
        email = ts.loads(token, salt='email-confirm-key', max_age=86400)
    # The token can either expire or be invalid
    except:
        abort(404)
    # Get the user from the database
    user = models.User.query.filter_by(email=email).first()
    # The user has confirmed his or her email address
    user.confirmation = True
    # Update the database with the user
    db.session.commit()
    # Send to the signin page
    flash('Your email address has been confirmed, you can sign in.', 'positive')
    return redirect(url_for('userbp.signin'))


# @userbp.route('/signin', methods=['GET', 'POST'])
# def signin():
#     form = user_forms.Login()
#     if form.validate_on_submit():
#         user = models.User.query.filter_by(email=form.email.data).first()
#         # Check the user exists
#         if user is not None:
#             # Setup a connection between the client and LDAP server
#             user_ldap_dn = 'cn=' + user.email.split('@', 1)[0] + ',ou=Users,dc=ldap,dc=com'
#             print(user_ldap_dn)
#             c = Connection(s, user=user_ldap_dn, password=form.password.data)
#             print(c)
#             # Initialize connection to LDAP server
#             c.open()
#             print(c)
#             # Start TLS to encrypt credentials
#             c.start_tls()
#             print(c)
#             # Check the password is correct
#             print(form.password.data, file=sys.stderr)
#             if user.check_password(form.password.data) and c.bind():
#                 # unbind user from LDAP server and log them in
#                 print(c)
#                 c.unbind()
#                 login_user(user)
#                 logger.info('User logged in successfully', user=current_user.get_id())
#                 # Send back to the home page
#                 flash('Succesfully signed in.', 'positive')
#                 return redirect(url_for('index'))
#             else:
#                 print(c)
#                 logger.info('User login failed', user=user.email)
#                 flash('The password you have entered is wrong.', 'negative')
#                 return redirect(url_for('userbp.signin'))
#         else:
#             flash('Unknown email address.', 'negative')
#             return redirect(url_for('userbp.signin'))
#     return render_template('user/signin.html', form=form, title='Sign in')


@userbp.route('/signin', methods=['GET', 'POST'])
def signin():
    form = user_forms.Login()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data).first()
        # Check the user exists
        if user is not None:
            # Setup a connection between the client and LDAP server
            user_ldap_dn = 'cn=' + user.email.split('@', 1)[0] + ',ou=Users,dc=ldap,dc=com'
            c = Connection(s, user=user_ldap_dn, password=form.password.data)
            # Initialize connection to LDAP server
            c.open()
            # Start TLS to encrypt credentials
            c.start_tls()
            # Check the password is correct
            if user.check_password(form.password.data) and c.bind():
                # unbind user from LDAP server and log them in
                c.unbind()
                login_user(user)
                logger.info('User logged in successfully', user=current_user.get_id())
                # Send back to the home page
                flash('Succesfully signed in.', 'positive')
                return redirect(url_for('index'))
            else:
                print(c)
                logger.info('User login attempt failed failed for user {}'.format(user.get_id()), user="none")
                flash('The password you have entered is wrong.', 'negative')
                return redirect(url_for('userbp.signin'))
        else:
            flash('Unknown email address.', 'negative')
            return redirect(url_for('userbp.signin'))
    return render_template('user/signin.html', form=form, title='Sign in')


@userbp.route('/resend', methods=['GET', 'POST'])
def resend():
    form = user_forms.Resend()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data).first()
        # Check the user exists
        if user is not None:
            subject = 'Please confirm your email address.'
            # Generate a random token
            token = ts.dumps(user.email, salt='email-confirm-key')
            # Build a confirm link with token
            confirmUrl = url_for('userbp.confirm', token=token, _external=True)
            # Render an HTML template to send by email
            html = render_template('email/confirm.html',
                                   confirm_url=confirmUrl)
            # Send the email to user
            email.send(user.email, subject, html)
            # Send back to the home page
            flash('Your confirmation email has been successfully resent. '
                  'Check your emails to confirm your email address.', 'positive')
            return redirect(url_for('index'))
        else:
            flash('Unknown email address.', 'negative')
            return redirect(url_for('index'))
    return render_template('user/resend.html', form=form)


@userbp.route('/signout')
def signout():
    logger.info('User logged out', user=current_user.get_id())
    logout_user()
    flash('Succesfully signed out.', 'positive')
    return redirect(url_for('index'))


@userbp.route('/account')
@login_required
def account():
    return render_template('user/account.html', title='Account')


@userbp.route('/forgot', methods=['GET', 'POST'])
def forgot():
    form = user_forms.Forgot()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data).first()
        # Check the user exists
        if user is not None:
            # Subject of the confirmation email
            subject = 'Reset your password.'
            # Generate a random token
            token = ts.dumps(user.email, salt='password-reset-key')
            # Build a reset link with token
            resetUrl = url_for('userbp.reset', token=token, _external=True)
            # Render an HTML template to send by email
            html = render_template('email/reset.html', reset_url=resetUrl)
            # Send the email to user
            email.send(user.email, subject, html)
            logger.info('User password reset email sent', user=user.get_id())
            # Send back to the home page
            flash('Check your emails to reset your password.', 'positive')
            return redirect(url_for('index'))
        else:
            flash('Unknown email address.', 'negative')
            return redirect(url_for('userbp.forgot'))
    return render_template('user/forgot.html', form=form)


@userbp.route('/reset/<token>', methods=['GET', 'POST'])
def reset(token):
    try:
        email = ts.loads(token, salt='password-reset-key', max_age=86400)
    # The token can either expire or be invalid
    except:
        abort(404)
    form = user_forms.Reset()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=email).first()
        # Check the user exists
        if user is not None:
            # Connect to the LDAP server with the 
            c = Connection(s, user=app.config['LDAP_SERVICE_USERNAME'], password=app.config['LDAP_SERVICE_PASSWORD'])
            # Open up the connection between the client and server
            c.open()
            # Raise the security level and start TLS
            c.start_tls()
            # Bind the user to the server now that the connection is secure
            c.bind()

            user_ldap_dn = 'cn=' + user.email.split('@', 1)[0] + ',ou=Users,dc=ldap,dc=com'

            # Modify the user password and the LDAP user password
            user.password = form.password.data
            c.modify(user_ldap_dn,
                     {
                         'userPassword': [(MODIFY_REPLACE, [form.password.data])]
                     })
            # Modify the LDAP user profile with the new password
            c.unbind()
            # Update the database with the user
            db.session.commit()
            logger.info('User password reset successfully', user=user.get_id())
            # Send to the signin page
            flash('Your password has been reset, you can sign in.', 'positive')
            return redirect(url_for('userbp.signin'))
        else:
            flash('Unknown email address.', 'negative')
            return redirect(url_for('userbp.forgot'))
    return render_template('user/reset.html', form=form, token=token)


@app.route('/files')
@login_required
def files():
    users = []
    # Store all users in a list to pass to the javascript
    for user in models.User.query.all():
        users.append(user.email)
    # We don't want a user sharing a file with himself
    users.remove(current_user.email)
    return render_template('user/files.html', users=users, title='Files')


@app.route('/download_file/<path:filename>', methods=['GET', 'POST'])
@login_required
def download(filename):
    uploads = os.path.join(app.root_path, app.config['UPLOADS_DIR'])
    logger.info("File with name {} downloaded".format(filename), user=current_user.get_id())
    return send_from_directory(directory=uploads, filename=filename, as_attachment=True)


@app.route('/files/share', methods=['POST'])
@login_required
def share():
    data = request.get_json()
    user_email = data["email"]
    file_id = data["file"]
    target_user = models.User.query.filter_by(email=user_email).first()
    response = None
    if target_user:
        try:
            target_file = models.File.query.filter_by(id=file_id).first()
            target_file.share_file(target_user)
            db.session.commit()
            flash("You successfully shared your file with {}".format(user_email), "positive")
            logger.info("File shared by {} to {}".format(current_user.get_id(), target_user.get_id()),
                        user=current_user.get_id())
            return jsonify(dict(success=True, message='File shared!'))
        except Exception as e:
            flash("Error encountered while sharing file, contact an admin or try again", "negative")
            logger.error("Exception encountered {}".format(e), user=current_user.get_id())
            response = {"message": "error"}
            pass
    if response is None:
        response = {"status": 200}
    return jsonify(result=response)


@app.route('/files/delete', methods=['POST'])
@login_required
def delete_file():
    data = request.get_json()
    file_id = data["file"]
    target_file = models.File.query.filter_by(id=file_id).first()
    for item in current_user.files:
        if item.file is target_file:
            db.session.delete(item)
            db.session.commit()
            logger.info("User {} no longer can access file {}".format(current_user.get_id(), file_id),
                        user=current_user.get_id())
            return jsonify(dict(success=True, message="File deleted"))
    return jsonify(dict(success=False, message="Unable to delete file"))
