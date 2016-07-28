# -*- coding: utf-8 -*-
from flask import Flask, flash, redirect, session, request, render_template, url_for, jsonify
from flask_login import login_required, current_user, login_user, user_logged_in
from flask_security import logout_user, LoginForm, utils
from flask_security.decorators import anonymous_user_required
from okubir import app
from okubir.forms import UserRegisterForm, WriteSummaryForm, WriteNoteForm, WriteCommentForm
from okubir.models import *
from okubir import dao, ebooks
from datetime import datetime


@app.route('/userpage', methods=['POST', 'GET'])
@login_required
def index():
    rg = current_user.reading_goal
    message = ""
    if rg:
        now = datetime.now()
        #degisebilir
        if rg.last_update.day != now.day:
            rg.last_update = now
            rg.pages_read_today = 0
            dao.commit()
        if rg.pages_read_today >= rg.goal:
            message = u"Günlük okuma hedefinizi tamamladınız!"
        else:
            message = u"Günlük okuma hedefinizi tamamlamanıza %s sayfa kaldı!" % (rg.goal - rg.pages_read_today)
    return render_template('user.html', status_list=list(enumerate(Status.names)), goal_message=message)

@app.route('/set_goal', methods=['POST'])
@login_required
def setGoal():
    try:
        goal = int(request.form.get('goal'))
    except ValueError:
        flash(u"Kutuya geçerli bir değer girmelisiniz!", "warning")
        return redirect(url_for('index'))
    if goal < 1:
        flash(u"Hedef birden küçük olamaz!", "warning")
        return redirect(url_for('index'))
    if current_user.reading_goal is None:
        current_user.reading_goal = ReadingGoal(
            goal = goal,
            pages_read_today = 0,
            last_update = datetime.now(),
            reached = False
        )
        dao.commit()
    else:
        current_user.reading_goal.goal = goal
        current_user.reading_goal.last_update = datetime.now()
        dao.commit()
    return redirect(url_for('index'))

@app.route('/remove_goal')
@login_required
def removeGoal():
    if current_user.reading_goal is not None:
        dao.deleteObject(current_user.reading_goal)
        dao.commit()
    return redirect(url_for('index'))
    
### Account islemleri ###

@user_logged_in.connect_via(app)
def on_user_logged_in(sender, user):
    user.last_login = datetime.now()
    dao.commit()

@app.route('/register_user', methods=['POST', 'GET'])
@anonymous_user_required
def registerUser():
    form = UserRegisterForm(request.form)
    if form.validate_on_submit():
        user = User(
                name = form.name.data,
                surname = form.surname.data,
                email = form.email.data,
                password = utils.encrypt_password(form.password.data),
                birth_date = form.birth_date.data,
                #country = form.country.data,
                il_id = form.il.data if form.il.data > 0 else None,
                ilce_id = form.ilce.data if form.ilce.data > 0 else None,
                semt_id = form.semt.data if form.semt.data > 0 else None,
                confirmed = False,
                active = True
        )
        for i in form.interests.data:
			#dao.addObject(interests_users(interest_id=i, user_id=user.id))
			user.interests.append(dao.getObject(i, InterestArea))
        dao.addObject(user)
        dao.commit()
        login_user(user)
        flash(u'Kayıt oldunuz', 'info')
        return redirect(url_for('index'))
    return render_template('register_user.html', form=form)

@app.route('/ilceler/<int:il_id>', methods=['GET'])
def ilceler(il_id):
    if il_id < 1 or il_id > 81:
        return
    ilce_list = dao.getIlces(il_id)
    ilce_options = [(i.id, i.ad) for i in ilce_list]
    ilce_options.append(('start', ilce_options[1][0]))
    ilce_options.append(('end', ilce_options[-2][0]))
    #print ilce_options
    return jsonify(ilce_options)

@app.route('/semtler/<int:ilce_id>', methods=['GET'])
def semtler(ilce_id):
    if ilce_id < 1:
        return
    semt_list = dao.getSemts(ilce_id)
    semt_options = [(i.id, i.ad) for i in semt_list]
    semt_options.append(('start', semt_options[1][0]))
    semt_options.append(('end', semt_options[-2][0]))
    #print ilce_options
    return jsonify(semt_options)

@app.route('/logout')
@login_required
def logout():
    flash(u'Çıkış yaptınız', 'info')
    logout_user()
    return redirect("/login")


### Liste islemleri ###

@app.route('/add_book_to_user')
def addBookToUser():
    book_id = request.args.get("book_id")
    status = request.args.get("status")
    assoc = dao.findUserBook(current_user.id, book_id)
    if assoc is not None and assoc.status == Status.removed:
        dao.updateAssocStatus(book_id, current_user.id, None, status)
        dao.commit()
    else:
        if dao.associateBookWithUser(book_id, current_user.id, status):
            dao.commit()
        else:
            flash("Bu kitap zaten listenizde!", 'warning')
    return redirect(url_for('index'))

@app.route('/remove_book_list')
@login_required
def removeBookFromList():
    book_id = request.args.get('book_id')
    dao.removeBookFromUser(book_id, current_user.id)
    dao.commit()
    return redirect(url_for('index'))

@app.route('/update_book_list')
@login_required
def updateBookFromList():
    book_id = request.args.get('book_id')
    status = request.args.get('status')
    pages_read = request.args.get('pages_read')
    is_finished = dao.updateAssocStatus(book_id, current_user.id, pages_read, status)
    dao.commit()
    if is_finished:
        assoc = dao.findUserBook(current_user.id, book_id)
        flash(assoc.book.__repr__()+u""" kitabını bitirdiniz! 
            <button onclick="rateBook(%s, 1)">Beğen</button>
            <button onclick="rateBook(%s, -1)">Beğenme</button>
            <p><a href='book/%s'>Yorum yapmak için kitap sayfasına gidin</a></p>""" % (assoc.id, assoc.id, book_id), 
            "modal")
    return redirect(url_for('index'))

@app.route('/bookread/<int:book_id>', methods=['GET'])
@login_required
def bookRead(book_id):
    assoc = dao.findUserBook(current_user.id, book_id)
    if assoc is None or (assoc.status != Status.reading and assoc.status != Status.have_read):
        flash(u"Bu kitabı okumuyorsunuz", 'warning')
        return redirect(request.referrer or url_for('index'))
    hide = (request.args.get("hide") is None)
    page = request.args.get('start_page') or assoc.pages_read
    return render_template('book_read.html', assoc=assoc, note_form=WriteNoteForm(page=page), comment_form=WriteCommentForm(), hide=hide, start_page=page)

### Note ###

@app.route('/write_note/<int:assoc_id>', methods=['POST'])
@login_required
def writeNote(assoc_id):
    assoc = dao.getObject(assoc_id, UserBook)
    if assoc is None or assoc.status != Status.reading:
        flash(u"Okumakta olmadığınız bir kitaba not alamazsınız", 'warning')
        return redirect(request.referrer or url_for('index'))
    note_form = WriteNoteForm(request.form)
    if note_form.validate_on_submit():
        note = Note(
            text = note_form.note.data,
            page = note_form.page.data,
            is_public = note_form.is_public.data,
            userbook = assoc,
            time_created = datetime.now(),
            time_last_modified = None
        )
        dao.addObject(note)
        dao.commit()
        flash(u'Not yazıldı!', 'info')
        return redirect(url_for('bookRead', book_id=assoc.book.id))
    else:
        flash(u'Not yazımı hatalı!', 'info')
        return redirect(url_for('bookRead', book_id=assoc.book.id, hide=""))



@app.route('/remove_note/<int:note_id>')
@login_required
def removeNote(note_id):
    note = dao.getObject(note_id, Note)
    if note.user != current_user:
        return redirect(request.referrer or url_for('index'))
    dao.deleteObject(note)
    dao.commit()
    flash("Not silindi!", 'info')
    return redirect(request.referrer or url_for('bookPage', book_id=note.book.id))

### Summary ###

@app.route('/write_summary/<int:assoc_id>', methods=['POST', 'GET'])
@login_required
def writeSummary(assoc_id):
    assoc = dao.getObject(assoc_id, UserBook)
    if assoc is None or assoc not in current_user.book_assocs or assoc.status != Status.have_read or assoc.summary != None:
        flash(u'Sadece okumuş olduğunuz kitaplar hakkında birer adet özet yazabilirsiniz!', 'warning')
        return redirect(request.referrer or url_for('index'))
    
    form = WriteSummaryForm(request.form)
    if form.validate_on_submit():
        summary = Summary(
            text = form.summary.data,
            time_created = datetime.now(),
            time_last_modified = None,
            userbook = assoc
        )
        dao.addObject(summary)
        dao.commit()
        flash(u'Özet yazıldı!', 'info')
        return redirect(url_for('bookPage', book_id=assoc.book.id))
    return render_template('write_summary.html', form=form)
    
@app.route('/edit_summary/<int:assoc_id>', methods=['POST', 'GET'])
@login_required
def editSummary(assoc_id):
    assoc = dao.getObject(assoc_id, UserBook)
    if assoc is None or assoc not in current_user.book_assocs or assoc.status != Status.have_read or assoc.summary == None:
        flash(u'Var olmayan bir özeti güncelleyemezsiniz!', 'warning')
        return redirect(request.referrer or url_for('index'))
    form = WriteSummaryForm(request.form)
    if form.validate_on_submit():
        assoc.summary.text = form.summary.data
        assoc.summary.time_last_modified = datetime.now()
        dao.commit()
        flash(u'Özet güncellendi!', 'info')
        return redirect(url_for('bookPage', book_id=assoc.book.id))
    elif request.method == 'GET':
        form.summary.data = assoc.summary.text
    return render_template('write_summary.html', form=form)
    
@app.route('/delete_summary/<int:assoc_id>')
@login_required
def deleteSummary(assoc_id):
    assoc = dao.getObject(assoc_id, UserBook)
    if assoc is None or assoc not in current_user.book_assocs or assoc.status != Status.have_read or assoc.summary == None:
        flash(u'Var olmayan bir özeti silemezsiniz!', 'warning')
        return redirect(request.referrer or url_for('index'))
    dao.deleteObject(assoc.summary)
    dao.commit()
    flash(u'Özet silindi!', 'info')
    return redirect(url_for('index'))

### Comment ###

@app.route('/write_comment/<int:book_id>', methods=['POST'])
@login_required
def writeComment(book_id):
    book = dao.getObject(book_id, Book)
    if book is None:
        flash(u'Böyle bir kitap yok!', 'warning')
        return redirect(request.referrer or url_for('index'))
        
    form = WriteCommentForm(request.form)
    if form.validate_on_submit():
        comment = Comment(
            text = form.comment.data,
            user = current_user,
            book = book,
            time_created = datetime.now(),
            time_last_modified = None
        )
        dao.addObject(comment)
        dao.commit()
        flash(u'Yorum yazıldı!', 'info')
    return redirect(request.referrer or url_for('bookPage', book_id=book.id))

@app.route('/edit_comment/<int:comment_id>', methods=['POST'])
@login_required
def editComment(comment_id):
    comment = dao.getObject(comment_id, Comment)
    if comment is None or comment.user != current_user:
        flash(u'Bu yorumu düzenleyemezsiniz!', 'warning')
        return redirect(request.referrer or url_for('index'))
    comment.text = request.form["comment"]
    comment.time_last_modified = datetime.now()
    dao.commit()
    flash(u'Yorum düzenlendi!', 'info')
    return redirect(request.referrer or url_for('bookPage', book_id=comment.book.id))

@app.route('/remove_comment/<int:comment_id>')
@login_required
def removeComment(comment_id):
    comment = dao.getObject(comment_id, Comment)
    if comment.user != current_user:
        return redirect(request.referrer or url_for('index'))
    dao.deleteObject(comment)
    dao.commit()
    flash("Yorum silindi!", 'info')
    return redirect(request.referrer or url_for('bookPage', book_id=comment.book.id))

### Rate ###

@app.route('/ratebook/<int:assoc_id>')
@login_required
def rateBook(assoc_id):
    rate = int(request.args.get("rate"))
    if rate is None or rate not in [-1, 1]:
        return redirect(url_for('home'))
    assoc = dao.getObject(assoc_id, UserBook)
    if assoc.rating == 0:
        assoc.rating = rate
        assoc.book.score_amount += 1
        if rate == 1:
            assoc.book.like_amount += 1
    elif assoc.rating == rate:
        assoc.rating = 0
        assoc.book.score_amount -= 1
        if rate == 1:
            assoc.book.like_amount -= 1
    else:
        assoc.rating = rate
        assoc.book.like_amount += 1 if rate == 1 else -1
    dao.commit()
    return redirect(request.referrer or url_for('index'))
 
 
 
 ###  Samet Was Here  ###
 
@app.route('/iletisim', methods=['POST', 'GET'])
@login_required
def iletisim():
    return render_template('iletisim.html')
    
@app.route('/hakkimizda', methods=['POST', 'GET'])
@login_required
def hakkimizda():
    return render_template('hakkimizda.html')
