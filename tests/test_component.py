import pytest
import json
from unittest.mock import patch, MagicMock
from app import app as test_app
from app import lambda_handler, convert_v2_to_v1

@pytest.fixture()
def app():
    app = test_app
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client

@pytest.fixture
def lambda_context():
    context = MagicMock()
    context.function_name = "population_api"
    context.function_version = "$LATEST"
    context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:population_api"
    return context

@patch('app.retrieval.population')
def test_population_success(client):
    response = client.get(
        "/population/v1",
        query_string={
            "suburb": "Albury",
            "startYear": "2025",
            "endYear": "2027"
        }
    )
    # Assert status code
    assert response.status_code == 200



@patch('app.retrieval.population')
def test_population_error(mock_population, client):
    # Make request
    response = client.get(
        "/population/v1",
        query_string={
            "suburb": "Albury",
            "startYear": "1800",
            "endYear": "2024"
        }
    )

    assert response.status_code == 400

# def test_population_route_missing_params(client):
#     """Test population endpoint with missing parameters"""
#     response = client.get("/population/v1")
#     assert response.status_code == 400
#     assert b"Missing parameters" in response.data