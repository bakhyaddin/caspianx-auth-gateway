import requests


def send_request(method, url, headers=None, data=None, files=None, service_type="Kong"):
    res_data = {
        "data": None,
        "status_code": None,
        "message": None
    }

    try:
        res = requests.request(method, url, headers=headers,
                               data=data, files=files, verify=False)
        try:
            d = res.json()
        except:
            d = res.content
        res_data["data"] = d
        res_data["status_code"] = res.status_code
        return res_data
    except Exception as e:
        res_data["status_code"] = 500
        res_data["message"] = service_type + ' Server is unreachable ' + str(e)
        return res_data
