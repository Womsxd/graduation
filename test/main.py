import httpx

api_url = "http://127.0.0.1:5000"

with httpx.Client() as client:
    print(client.post(f"{api_url}/auth/login",data={"account":"admin","password":"admin"}).text)
    print(client.get(f"{api_url}/ping").text)
    accountk = "testuser"
    for i in range(1,101):
        userinfo = f"{accountk}{i}"
        print(client.post(f"{api_url}/user/add",data={"account":userinfo,"password":userinfo}).text)