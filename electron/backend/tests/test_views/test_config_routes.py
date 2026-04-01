import os
from unittest.mock import patch, MagicMock


class TestPanelConfig:
    def test_panel_autenticado(self, auth_client):
        response = auth_client.get('/configuracion', follow_redirects=True)
        assert response.status_code == 200

    def test_panel_no_autenticado(self, client):
        response = client.get('/configuracion', follow_redirects=True)
        assert response.status_code == 200


class TestActualizarJobs:
    def test_actualizar_jobs_valido(self, auth_client):
        with patch('app.views.config_routes.update_env_value'):
            response = auth_client.post('/configuracion/jobs/actualizar', data={
                'JOB_ALERTA_STOCK_HORA': '8',
                'JOB_ALERTA_STOCK_MINUTO': '0',
                'JOB_ALERTA_STOCK_ACTIVO': 'true',
                'JOB_INFORME_MANANA_HORA': '7',
                'JOB_INFORME_MANANA_MINUTO': '0',
                'JOB_INFORME_MANANA_ACTIVO': 'true',
                'JOB_INFORME_TARDE_HORA': '19',
                'JOB_INFORME_TARDE_MINUTO': '0',
                'JOB_INFORME_TARDE_ACTIVO': 'true',
                'JOB_BACKUP_HORA': '23',
                'JOB_BACKUP_MINUTO': '0',
                'JOB_BACKUP_ACTIVO': 'true',
                'tasa_cambio': '0',
                'mail_username': '',
                'mail_password': '',
                'mail_default_sender': ''
            }, follow_redirects=True)
            assert response.status_code == 200
