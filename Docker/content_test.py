import os
import requests

def test_content(api_address, api_port):
    test_cases = [
        ('alice', 'wonderland', 'life is beautiful', 1, 1),
        ('alice', 'wonderland', 'that sucks', -1, -1)
    ]
    
    results = []
    for username, password, sentence, expected_v1, expected_v2 in test_cases:
        for version in ['v1', 'v2']:
            r = requests.post(
                url=f'http://{api_address}:{api_port}/{version}/sentiment',
                params={'username': username, 'password': password, 'sentence': sentence}
            )
            score = r.json().get('score')
            expected_score = expected_v1 if version == 'v1' else expected_v2
            test_status = 'SUCCESS' if score == expected_score else 'FAILURE'
            results.append((username, password, version, sentence, score, expected_score, test_status))
    
    return results

if __name__ == "__main__":
    api_address = 'api'
    api_port = 8000
    results = test_content(api_address, api_port)
    
    log_output = "\n".join([
        f'''
        ============================
            Content test
        ============================
        request done at "/{version}/sentiment"
        | username="{username}"
        | password="{password}"
        | sentence="{sentence}"
        expected result = {expected_score}
        actual result = {score}
        ==>  {test_status}
        ''' for username, password, version, sentence, score, expected_score, test_status in results
    ])
    
    print(log_output)
    
    if os.environ.get('LOG') == '1':
        with open('/logs/api_test.log', 'a') as file:
            file.write(log_output)
