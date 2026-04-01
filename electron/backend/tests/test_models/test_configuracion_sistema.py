from app.models import ConfiguracionSistema


def test_create_config(db):
    config = ConfiguracionSistema(clave='ultima_alerta_global', valor='2024-01-01 08:00:00')
    db.session.add(config)
    db.session.commit()
    assert config.id is not None
    assert config.clave == 'ultima_alerta_global'
    assert config.valor == '2024-01-01 08:00:00'


def test_config_clave_unica(db):
    config1 = ConfiguracionSistema(clave='tasa_cambio', valor='50.0')
    config2 = ConfiguracionSistema(clave='tasa_cambio', valor='60.0')
    db.session.add(config1)
    db.session.commit()
    db.session.add(config2)
    try:
        db.session.commit()
        assert False, 'Se esperaba IntegrityError por clave duplicada'
    except Exception:
        db.session.rollback()


def test_config_actualizar_valor(db):
    config = ConfiguracionSistema(clave='ultima_alerta', valor='valor_inicial')
    db.session.add(config)
    db.session.commit()
    config.valor = 'valor_actualizado'
    db.session.commit()
    config_actualizado = ConfiguracionSistema.query.filter_by(clave='ultima_alerta').first()
    assert config_actualizado.valor == 'valor_actualizado'


def test_config_valor_nulo(db):
    config = ConfiguracionSistema(clave='config_vacia')
    db.session.add(config)
    db.session.commit()
    assert config.valor is None


def test_config_consultar_por_clave(db):
    db.session.add(ConfiguracionSistema(clave='alerta_stock', valor='activo'))
    db.session.add(ConfiguracionSistema(clave='informe_diario', valor='activo'))
    db.session.commit()
    config = ConfiguracionSistema.query.filter_by(clave='alerta_stock').first()
    assert config is not None
    assert config.valor == 'activo'


def test_config_eliminar(db):
    config = ConfiguracionSistema(clave='temporal', valor='temp')
    db.session.add(config)
    db.session.commit()
    config_id = config.id
    db.session.delete(config)
    db.session.commit()
    assert ConfiguracionSistema.query.get(config_id) is None
