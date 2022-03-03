from flask import Flask, render_template, request
import requests
from urllib import parse
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from PIL import Image
from io import BytesIO
import base64

UPLOAD_FOLDER = './static/img/in/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def make_finalname_list(fileObj):
    filename_encoded = parse.quote(fileObj.filename)    # 한글 에러나서 ?로 인코딩 해주는 함수
    print('# fileObj.name=', filename_encoded)
    filename_cleaned = secure_filename(filename_encoded)     # 알파벳, 대시, 언더바, 닷 등 제거하고 클린하게 만들어줌
    print('# filename_cleaned=', filename_cleaned)

    now = datetime.now()
    time = now.strftime('%Y-%m-%dT%H-%M-%S')
    print('# time=', time)

    finalname_list = [time+'F'+filename_cleaned, time+'C'+filename_cleaned]

    return finalname_list


@app.route('/')
def index():
    return render_template('index.html')  


@app.route('/result', methods=['POST'])
def result():    
    if request.method == 'POST':
        print('request.files=', request.files)
        fileObj = request.files['filePath']
        # print('# fileObj=', fileObj)
        # print('# type(fileObj)=', type(fileObj))
        # print('# fileObj.file=', fileObj.file)
        # print('# type(fileObj.file)=', type(fileObj.file))

        # 경로 형성
        finalname_list = make_finalname_list(fileObj)        
        in_path = os.path.join(app.config['UPLOAD_FOLDER'], finalname_list[0])
        out_path =os.path.join('./static/img/out/', finalname_list[0]) 
        crop_path = os.path.join('./static/img/out/', finalname_list[1])
        
        # 파일 저장
        fileObj.save(in_path)

        # 파일 전송 & 결과 받기
        data = open(in_path,'rb')
        # print('# data=',data)
        # print('# type(data)=',type(data))
        res = requests.post('http://127.0.0.2:7000/ganarate', files={'img':data})

        # 결과 저장
        # file = open(out_path, 'wb')
        # file.write(res.content)
        
        # print(res.json()['result'][0])
        print(len(res.json()['result']))
        # print(res.content)
        # print(len(res.content))
        cropped_img_bytes = res.json()['result'][0]
        result_img_bytes = res.json()['result'][1]
        print('cropped_img_bytes:', type(cropped_img_bytes))

        cropped_img_data = base64.b64decode(cropped_img_bytes)
        result_img_data = base64.b64decode(result_img_bytes)

        print('cropped_img_data:', type(cropped_img_data))
        
        with open(crop_path, 'wb') as f:
            f.write(cropped_img_data)

        with open(out_path, 'wb') as f:
            f.write(result_img_data)
        
        return render_template('result.html', out_path=out_path, crop_path=crop_path)


if __name__ == '__main__':
    app.run(debug=True)    
    # host 등을 직접 지정하고 싶다면
    # app.run(host="127.0.0.1", port="5000", debug=True)