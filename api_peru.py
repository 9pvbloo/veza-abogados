import requests

TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6ImZjcHBhYmxvLjAyQGdtYWlsLmNvbSJ9.NUGXuUpiKHn7zLqTt5fS9mPipXr52sk3rJeW2zQh0f8"

def consultar_dni(dni):

    url = f"https://dniruc.apisperu.com/api/v1/dni/{dni}?token={TOKEN}"

    response = requests.get(url)

    print("RESPUESTA RENIEC:", response.text)   # 👈 ver resultado real

    if response.status_code == 200:

        return response.json()

    return None




def consultar_ruc(ruc):

    url = f"https://dniruc.apisperu.com/api/v1/ruc/{ruc}?token={TOKEN}"

    response = requests.get(url)

    if response.status_code == 200:

        return response.json()

    return None