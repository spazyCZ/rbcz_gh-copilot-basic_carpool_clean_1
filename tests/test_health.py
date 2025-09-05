from app import create_app
from app.config.settings import TestConfig


def test_health_endpoint():
    app = create_app(TestConfig)
    with app.test_client() as client:
        res = client.get('/api/v1/health')
        assert res.status_code == 200
        assert res.get_json() == {'status': 'ok'}
