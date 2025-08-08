import datetime
from unittest.mock import patch, MagicMock
from fastapi import status


class TestMongoDBRoutes:
    def _mock_client(self):
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_client.get_database.return_value = mock_db
        mock_db.get_collection.return_value = mock_collection
        return mock_client, mock_db, mock_collection

    def test_mongodb_success(self, test_client):
        mock_client, mock_db, mock_collection = self._mock_client()
        # insert_one returns an object with inserted_id attribute
        mock_collection.insert_one.return_value = type('obj', (), {'inserted_id': 'id123'})
        # find returns list of docs
        now = datetime.datetime.utcnow()
        mock_collection.find.return_value = [
            {"_id": "id1", "timestamp": now, "source": "testclient"},
            {"_id": "id2", "timestamp": now, "source": "testclient"},
        ]

        with patch('app.routes.mongodb._get_mongo_client', return_value=mock_client):
            response = test_client.get('/mongodb?limit=2')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['connected'] is True
        assert data['writable'] is True
        assert isinstance(data['data'], list)
        assert len(data['data']) <= 2
        assert all('id' in d and 'timestamp' in d and 'source' in d for d in data['data'])

    def test_mongodb_write_error(self, test_client):
        mock_client, mock_db, mock_collection = self._mock_client()
        mock_collection.insert_one.side_effect = Exception('write error')
        mock_collection.find.return_value = []

        with patch('app.routes.mongodb._get_mongo_client', return_value=mock_client):
            response = test_client.get('/mongodb')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['writable'] is False
        assert data['connected'] is True
        assert 'Write error' in data['exception']

    def test_mongodb_read_error(self, test_client):
        mock_client, mock_db, mock_collection = self._mock_client()
        mock_collection.insert_one.return_value = type('obj', (), {'inserted_id': 'id123'})
        mock_collection.find.side_effect = Exception('read error')

        with patch('app.routes.mongodb._get_mongo_client', return_value=mock_client):
            response = test_client.get('/mongodb')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['connected'] is False
        assert data['writable'] is True
        assert 'Read error' in data['exception']

    def test_mongodb_missing_driver(self, test_client):
        with patch('app.routes.mongodb._get_mongo_client', side_effect=RuntimeError('pymongo is required')):
            response = test_client.get('/mongodb')

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert 'pymongo is required' in response.json()['detail']


