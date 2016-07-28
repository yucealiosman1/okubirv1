# -*- coding: utf-8 -*-
from wtforms import BooleanField, PasswordField, validators, StringField, DateField, ValidationError, SelectField, TextAreaField, IntegerField, FileField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, InputRequired, Optional
from flask_wtf import Form
from models import *
from flask_security.forms import LoginForm


regex_letters = u'^[a-zA-ZçğşıöüÇĞŞİÖÜ]+$'
req_msg = u"Bu alanı boş bırakamazsınız."

def ValidateEmail(model):
    def _val(form, field):
        obj = model.query.filter_by(email=field.data).first()
        if obj:
            raise ValidationError(u'E-posta adresi daha once kayıt olmuş')
    return _val

def ValidateDate():
    def _val(form, field):
        if field.data.year < 1900:
            raise ValidationError(u"1900'den düşük bir yıl giremezsiniz")
    return _val

# Select field that doesn't validate (for dynamically filled fields)
class NVSelectField(SelectField):
    def pre_validate(self, form):
        pass

class UserLoginForm(LoginForm):
    email = StringField("E-posta Adresi")
    password = PasswordField("Parola")
    remember = BooleanField(u"Beni Hatırla")
    submit = SubmitField(u"Giriş Yap")

class UserRegisterForm(Form):
    name = StringField(u'*İsim', validators=[Length(2, 64), DataRequired(message=req_msg), Regexp(regex_letters, 0, u'İsim sadece harflerden oluşmalıdır.' )])
    surname = StringField('*Soyisim', validators=[Length(2, 64), DataRequired(message=req_msg), Regexp(regex_letters, 0, u'Soyisim sadece harflerden oluşmalıdır.' )])
    email = StringField('*E-posta adresi', validators=[Length(6, 255), DataRequired(message=req_msg), Email(message=u"Hatalı e-posta adresi"), ValidateEmail(User)])
    password = PasswordField('*Parola', validators=[Length(6, 25, message=u"Parola 6 ila 25 karakter uzunluğunda olmalıdır"), DataRequired(message=req_msg)])
    confirm = PasswordField('*Parola (tekrar)', validators=[DataRequired(message=req_msg), EqualTo('password', message=u'Parolalar eşleşmeli')])
    birth_date = DateField(u'*Doğum tarihi', validators=[DataRequired(message=u"Doğum tarihi verilen formatta olmalıdır"), ValidateDate()], format='%d/%m/%Y')
    #country = StringField(u'Ülke', validators=[Length(2, 32), DataRequired(message=req_msg), Regexp(regex_letters, 0, u'Ülke ismi sadece harflerden oluşmalıdır' )])
    il = SelectField(u'İl', coerce=int)
    ilce = NVSelectField(u'İlçe', choices=[], coerce=int)
    semt = NVSelectField(u'Semt', choices=[], coerce=int)
    #mahalle = NVSelectField(u'Mahalle', choices=[], coerce=int)
    interests = SelectMultipleField(u'İlgi alanları', coerce=int)
    
    def __init__(self, form):
        super(UserRegisterForm, self).__init__()
        interest_list = InterestArea.query.all()
        l = [''] + [i.name for i in interest_list]
        self.interests.choices = list(enumerate(l))
        il_list = Il.query.all()
        l = [u'-- İl seçebilirsiniz --'] + [i.ad for i in il_list]
        self.il.choices = list(enumerate(l))
    
class BookAddForm(Form):
    name = StringField('Kitap ismi', validators=[Length(2, 128), DataRequired()])
    author = SelectField("Yazar", coerce=int)
    publication_place = StringField(u'Yayım yeri', validators=[Optional(), Length(2, 128)])
    publication_year = IntegerField(u'Yayım yılı', validators=[Optional()])
    publisher = SelectField(u"Yayımcı", coerce=int)
    isbn = StringField('ISBN', validators=[Optional(), Length(10, 13)])
    page_amount = IntegerField(u'Sayfa sayısı', validators=[DataRequired()])
    description = TextAreaField(u"Açıklama", validators=[Optional(), Length(1, 1500)])
    ebook = FileField(u'E-kitap dosyası', validators=[Optional()])
    image = FileField(u'Görsel dosyası', validators=[Optional()])
    
    def __init__(self, form):
        super(BookAddForm, self).__init__()
        authors = Author.query.all()
        publishers = Publisher.query.all()
        self.author.choices = [(n.id, n.get_name()) for n in authors]
        l = [(0, '')] + [(n.id, n.name) for n in publishers]
        self.publisher.choices = l

class WriteSummaryForm(Form):
    summary = TextAreaField(u'Özet', validators=[Length(1, 5000), DataRequired()])

class WriteNoteForm(Form):
    page = IntegerField(u'Sayfa numarası')
    note = TextAreaField('Not', validators=[Length(1, 500), DataRequired()])
    is_public = BooleanField(u'Herkese görünsün')

class WriteCommentForm(Form):
    comment = TextAreaField('Yorum yap', validators=[Length(1, 500), DataRequired()])

class RecommendBookForm(Form):
    book = SelectField("Kitap", coerce=int)
    
    def __init__(self, form):
        super(RecommendBookForm, self).__init__()
        books = Book.query.all()
        l = [''] + books
        self.book.choices = list(enumerate(l))
