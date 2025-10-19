from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, IntegerField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    
    # Account type
    account_type = SelectField('Tipo de Conta', choices=[
        ('', 'Selecione o tipo de conta'),
        ('profissional', 'Conta Profissional'),
        ('universitaria', 'Conta Universitária'),
        ('estudante', 'Conta Estudante')
    ], validators=[DataRequired()])
    
    # Academic information (conditional - for students and university accounts)
    university = SelectField('Faculdade', choices=[
        ('', 'Selecione a faculdade'),
        ('Brasil', [
            ('USP', 'USP - Universidade de São Paulo'),
            ('UNICAMP', 'UNICAMP - Universidade Estadual de Campinas'),
            ('UFRJ', 'UFRJ - Universidade Federal do Rio de Janeiro'),
            ('UnB', 'UnB - Universidade de Brasília'),
            ('UFMG', 'UFMG - Universidade Federal de Minas Gerais'),
            ('UFPA', 'UFPA - Universidade Federal do Pará'),
            ('UFSCar', 'UFSCar - Universidade Federal de São Carlos'),
            ('UFRGS', 'UFRGS - Universidade Federal do Rio Grande do Sul'),
            ('PUC-SP', 'PUC-SP - Pontifícia Universidade Católica de São Paulo'),
            ('PUC-Rio', 'PUC-Rio - Pontifícia Universidade Católica do Rio de Janeiro'),
            ('UFPE', 'UFPE - Universidade Federal de Pernambuco'),
            ('UFBA', 'UFBA - Universidade Federal da Bahia')
        ]),
        ('EUA', [
            ('Harvard', 'Harvard University'),
            ('Stanford', 'Stanford University'),
            ('UC Berkeley', 'University of California – Berkeley'),
            ('UChicago', 'University of Chicago')
        ]),
        ('Reino Unido', [
            ('Oxford', 'University of Oxford'),
            ('Cambridge', 'University of Cambridge'),
            ('UCL', 'University College London')
        ]),
        ('Canadá', [
            ('Toronto', 'University of Toronto'),
            ('McGill', 'McGill University')
        ]),
        ('Espanha', [
            ('Complutense', 'Universidad Complutense de Madrid'),
            ('Barcelona', 'Universidad de Barcelona')
        ]),
        ('França', [
            ('Sorbonne', 'Sorbonne Université'),
            ('EHESS', 'École des Hautes Études en Sciences Sociales')
        ]),
        ('México', [
            ('UNAM', 'UNAM - Universidad Nacional Autónoma de México'),
            ('Tec Monterrey', 'Tecnológico de Monterrey')
        ]),
        ('custom', 'Outra (digitar manualmente)')
    ], validators=[Optional()])
    
    university_custom = StringField('Digite o nome da faculdade', validators=[Optional(), Length(max=200)])
    course = StringField('Curso/Área de estudo', validators=[Optional(), Length(max=200)])
    entry_year = IntegerField('Ano de entrada', validators=[Optional()])
    institution_type = SelectField('Tipo de instituição', choices=[
        ('', 'Selecione'),
        ('publica', 'Pública'),
        ('privada', 'Privada')
    ], validators=[Optional()])
    city = StringField('Cidade', validators=[Optional(), Length(max=100)])
    state = StringField('Estado', validators=[Optional(), Length(max=100)])
    country = StringField('País', validators=[Optional(), Length(max=100)])

class ArtifactForm(FlaskForm):
    name = StringField('Nome do Artefato', validators=[DataRequired(), Length(max=200)])
    code = StringField('Código do Artefato', validators=[Length(max=50)])
    discovery_date = DateField('Data de Descoberta', validators=[Optional()])
    origin_location = StringField('Local de Origem', validators=[Length(max=300)])
    artifact_type = SelectField('Tipo de Artefato', choices=[
        ('ceramica', 'Cerâmica'),
        ('litico', 'Lítico'),
        ('metal', 'Metal'),
        ('osso', 'Osso'),
        ('madeira', 'Madeira'),
        ('textil', 'Têxtil'),
        ('vidro', 'Vidro'),
        ('outro', 'Outro')
    ])
    conservation_state = SelectField('Estado de Conservação', choices=[
        ('excelente', 'Excelente'),
        ('bom', 'Bom'),
        ('regular', 'Regular'),
        ('ruim', 'Ruim'),
        ('pessimo', 'Péssimo')
    ])
    observations = TextAreaField('Observações')
    photo = FileField('Foto', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Apenas imagens são permitidas!')])
    model_3d = FileField('Modelo 3D', validators=[FileAllowed(['obj', 'ply', 'stl', 'fbx'], 'Apenas modelos 3D são permitidos!')])

class ProfessionalForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(max=100)])
    age = IntegerField('Idade', validators=[Optional()])
    specialization = StringField('Especialização', validators=[Length(max=200)])
    description = TextAreaField('Descrição')
    experience = TextAreaField('Experiência')
    profile_photo = FileField('Foto de Perfil', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Apenas imagens são permitidas!')])

class TransportForm(FlaskForm):
    artifact_id = SelectField('Artefato', coerce=int, validators=[DataRequired()])
    origin_location = StringField('Local de Origem', validators=[DataRequired(), Length(max=300)])
    destination_location = StringField('Local de Destino', validators=[DataRequired(), Length(max=300)])
    transport_date = DateField('Data de Transporte', validators=[Optional()])
    responsible_person = StringField('Responsável', validators=[Length(max=100)])
    status = SelectField('Status', choices=[
        ('pendente', 'Pendente'),
        ('em_transito', 'Em Trânsito'),
        ('concluido', 'Concluído')
    ])
    notes = TextAreaField('Observações')

class Scanner3DForm(FlaskForm):
    artifact_id = SelectField('Artefato', coerce=int, validators=[DataRequired()])
    scanner_type = StringField('Tipo de Scanner', validators=[Length(max=100)])
    resolution = StringField('Resolução', validators=[Length(max=50)])
    scan_file = FileField('Arquivo do Scan', validators=[FileAllowed(['obj', 'ply', 'stl', 'fbx'], 'Apenas arquivos 3D são permitidos!')])
    notes = TextAreaField('Observações')

class AdminUserForm(FlaskForm):
    user_id = SelectField('Usuário', coerce=int, validators=[DataRequired()])
    is_active = BooleanField('Usuário Ativo')
    is_admin = BooleanField('Administrador')

class PhotoGalleryForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Descrição')
    category = SelectField('Categoria', choices=[
        ('geral', 'Foto Geral'),
        ('equipe', 'Foto da Equipe'),
        ('evento', 'Foto de Evento')
    ], default='geral')
    event_name = StringField('Nome do Evento', validators=[Length(max=200)])
    image = FileField('Imagem', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Apenas imagens são permitidas!')])
    is_published = BooleanField('Publicar no Mural')
