from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional, Length

# Definición del formulario
class ProductoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
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
