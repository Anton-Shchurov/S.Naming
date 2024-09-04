import pytest
import pandas as pd
from io import BytesIO
import requests

# Mocked constants for testing
import constants as ct

ct.URL = 'https://globalteamgf-my.sharepoint.com/:x:/g/personal/a_shchurov_glassfordglobal_rs/EVUH6ebvB6pFg4w-8n-x2Y4B3dtIefUJVxjHJ86jmSpisQ?download=1'

# Example DataFrame for testing
data = {
    'Project Name': ['Project1', 'Project1', 'Project2'],
    'Short Name': ['P1', 'P1', 'P2'],
    'Phase': ['1.0', '2.0', '3.0'],
    'Stage': ['1', '2', '3'],
    'Building': ['B1', 'B2', 'B3']
}
df = pd.DataFrame(data)

# Mocking requests.get to return the example DataFrame
def mock_requests_get(url):
    if url == 'https://globalteamgf-my.sharepoint.com/:x:/g/personal/a_shchurov_glassfordglobal_rs/EVUH6ebvB6pFg4w-8n-x2Y4B3dtIefUJVxjHJ86jmSpisQ?download=1':
        excel_file = BytesIO()
        df.to_excel(excel_file, index=False, sheet_name='Summary Table')
        excel_file.seek(0)
        response = requests.Response()
        response.status_code = 200
        response._content = excel_file.read()
        return response
    else:
        raise requests.ConnectionError()

requests.get = mock_requests_get

from project import url_connect, create_phase_stage_name, field_generator

def test_url_connect():
    result = url_connect(ct.URL)
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert 'Project Name' in result.columns
    assert 'Short Name' in result.columns

def test_create_phase_stage_name():
    result = create_phase_stage_name('1.0', ['1', '2'])
    assert result == ['1.1', '1.2']
    result = create_phase_stage_name('nan', ['1', '2'])
    assert result == '00'
    result = create_phase_stage_name('1.0', ['nan', '-'])
    assert result == ['1']

def test_field_generator():
    result = field_generator(['1.1', '1.3', '1.5'])
    assert result == '1.1#1.3#1.5'
    result = field_generator(['1', '2', '3', '4', '5'])
    assert result == '1-5'
    result = field_generator(['1.1', '1.2', '1.3', '1.4', '1.5'])
    assert result == '1.1-1.5'
    result = field_generator(['1.1', '1.2'])
    assert result == '1.1#1.2'
    result = field_generator(['1', '2', '5'])
    assert result == '1#2#5'
    result = field_generator(['1.1', '1.2', '1.3', '1.5', '2', '3', '4', '5.1', '5.2', '5.3', '6', '7', '8', '9', '12'])
    assert result == '1.1-1.3#1.5#2-4#5.1-5.3#6-9#12'
    result = field_generator(['3.1 Паркинг', '3.2 Паркинг', '5.5', '6.6'])
    assert result == '5.5#6.6#3.1 Паркинг#3.2 Паркинг'
    result = field_generator(['1.1', '2.2', '3.3', '1.1 Паркинг', '1.2 Паркинг'])
    assert result == '1.1#2.2#3.3#1.1 Паркинг#1.2 Паркинг'
