import requests, json

data = {
 "startCord": [8.681495, 49.41461],
 "endCord": [8.687872, 49.420318],
 "targetCount": 2,
}
headers = {}

try :
    """
    res = requests.post("http://localhost:8080/findRouter", json=data, headers=headers)
    # HTTP CODE
    print(res.status_code)
    # HTTP 응답 원문
    print(res.text)
    # HTTP 요청 값
    print(res.request, res.request.body, res.content)
    # HTTP 응답 원문(JSON)을 디코딩하여 Dictionary로 반환
    print(res.json())
    """
    # Define the URL
    url = 'http://localhost:8080/findRouter'
    # Send the GET request
    response = requests.get(url)
    # Handle the response
    data = response.json()
    # Print the data
    print(data)
except ConnectionError:
    print("Error!")
