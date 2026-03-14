from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from wtforms import widgets
from app.models import ModeloTelefono

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    descripcion = TextAreaField('Descripción', validators=[Optional(), Length(max=200)])
    categoria = SelectField('Categoría', choices=[
        ('pantalla', 'Pantalla'),
        ('bateria', 'Batería'),
        ('funda', 'Funda'),
        ('cable', 'Cable'),
        ('cargador', 'Cargador'),
        ('otro', 'Otro')
    ], validators=[DataRequired()])
    cantidad_stock = IntegerField('Cantidad en stock', validators=[DataRequired(), NumberRange(min=0)])
    stock_minimo = IntegerField('Stock mínimo', validators=[DataRequired(), NumberRange(min=1)])
    proveedor = StringField('Proveedor', validators=[Optional(), Length(max=100)])
    modelos_compatibles = MultiCheckboxField('Modelos compatibles (solo para pantallas)', coerce=int, validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cargar opciones de modelos desde la BD
        self.modelos_compatibles.choices = [(m.id, m.nombre) for m in ModeloTelefono.query.order_by('nombre').all()]

class ModeloForm(FlaskForm):
    nombre = StringField('Nombre del modelo', validators=[DataRequired(), Length(max=100)])

