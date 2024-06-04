import os
import requests

def test_authentication(api_address, api_port):
    test_cases = [
        ('alice', 'wonderland', 200),
        ('bob', 'builder', 200),
        ('clementine', 'mandarine', 403)
    ]
    
    results = []
    for username, password, expected_status in test_cases:
        r = requests.get(
            url=f'http://{api_address}:{api_port}/permissions',
            params={'username': username, 'password': password}
        )
        status_code = r.status_code
        test_status = 'SUCCESS' if status_code == expected_status else 'FAILURE'
        results.append((username, password, status_code, test_status))
    
    return results

if __name__ == "__main__":
    api_address = 'api'
    api_port = 8000
    results = test_authentication(api_address, api_port)
    
    log_output = "\n".join([
        f'''
        ============================
            Authentication test
        ============================
        request done at "/permissions"
        | username="{username}"
        | password="{password}"
        expected result = {expected_status}
        actual result = {status_code}
        ==>  {test_status}
        ''' for username, password, status_code, test_status in results
    ])
    
    print(log_output)
    
    if os.environ.get('LOG') == '1':
        with open('/logs/api_test.log', 'a') as file:
            file.write(log_output)
