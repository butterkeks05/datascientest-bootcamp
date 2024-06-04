import os
import requests

def test_authorization(api_address, api_port):
    test_cases = [
        ('alice', 'wonderland', 'v1', 200),
        ('alice', 'wonderland', 'v2', 200),
        ('bob', 'builder', 'v1', 200),
        ('bob', 'builder', 'v2', 403)
    ]
    
    results = []
    for username, password, version, expected_status in test_cases:
        r = requests.post(
            url=f'http://{api_address}:{api_port}/{version}/sentiment',
            params={'username': username, 'password': password, 'sentence': 'test'}
        )
        status_code = r.status_code
        test_status = 'SUCCESS' if status_code == expected_status else 'FAILURE'
        results.append((username, password, version, status_code, test_status))
    
    return results

if __name__ == "__main__":
    api_address = 'api'
    api_port = 8000
    results = test_authorization(api_address, api_port)
    
    log_output = "\n".join([
        f'''
        ============================
            Authorization test
        ============================
        request done at "/{version}/sentiment"
        | username="{username}"
        | password="{password}"
        expected result = {expected_status}
        actual result = {status_code}
        ==>  {test_status}
        ''' for username, password, version, status_code, test_status in results
    ])
    
    print(log_output)
    
    if os.environ.get('LOG') == '1':
        with open('/logs/api_test.log', 'a') as file:
            file.write(log_output)
