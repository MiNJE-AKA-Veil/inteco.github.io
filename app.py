import requests
import xml.etree.ElementTree as ET
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# 로그인 요청 XML
soap_request_login = """
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:eds="http://tt.com.pl/eds/">
   <soap:Header/>
   <soap:Body>
      <eds:login>
         <eds:username>admin</eds:username>
         <eds:password>ovation1</eds:password>
         <eds:type>CLIENT-TYPE-DEFAULT</eds:type>
      </eds:login>
   </soap:Body>
</soap:Envelope>
"""

# 로그인 요청 보내기
response_login = requests.post(
    url="http://172.16.31.100:43080",
    headers={"Content-Type": "application/soap+xml"},
    data=soap_request_login
)

# 로그인 응답 처리
root = ET.fromstring(response_login.text)
namespace = {'soap': 'http://www.w3.org/2003/05/soap-envelope', 'eds': 'http://tt.com.pl/eds/'}
auth_string_element = root.find('.//eds:authString', namespace)

if auth_string_element is not None:
    auth_string = auth_string_element.text
else:
    raise Exception('Auth-String을 추출하지 못했습니다. 로그인 요청에 문제가 있습니다.')

# 실시간 데이터를 가져오는 함수
def get_live_value():
    soap_request_get_points = f"""
    <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:eds="http://tt.com.pl/eds/">
       <soap:Header/>
       <soap:Body>
          <eds:getPoints>
             <eds:authString>{auth_string}</eds:authString>
             <eds:filter>
                <eds:iessRe>PIT-4048.UNIT0@OVATION</eds:iessRe>
             </eds:filter>
             <eds:startIdx>0</eds:startIdx>
             <eds:maxCount>1</eds:maxCount>
          </eds:getPoints>
       </soap:Body>
    </soap:Envelope>
    """

    response_get_points = requests.post(
        url="http://172.16.31.100:43080",
        headers={"Content-Type": "application/soap+xml"},
        data=soap_request_get_points
    )

    root = ET.fromstring(response_get_points.text)
    points = root.findall('.//eds:points', namespace)
    
    point_data = {}
    for point in points:
        iess_element = point.find('eds:id/eds:iess', namespace)
        av_element = point.find('eds:value/eds:av', namespace)
        
        if iess_element is not None and av_element is not None:
            iess = iess_element.text
            value = av_element.text
            point_data[iess] = value

    return point_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/live_data')
def live_data():
    data = get_live_value()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
