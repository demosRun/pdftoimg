import sys, fitz
import json
import os
import datetime
from flask_cors import CORS
from flask import Flask,render_template,request,redirect,url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__, static_url_path='')
CORS(app, supports_credentials=True)

serverUrl = 'http://172.31.36.223:5000/'


@app.route('/', methods=['POST', 'GET'])
def upload():
  if request.method == 'POST':
    f = request.files['file']
    upload_path = os.path.join('./tmp', secure_filename(f.filename))  #注意：没有的文件夹一定要先创建，不然会提示没有该路径
    f.save(upload_path)
    pyMuPDF_fitz(upload_path, './static/' + f.filename.replace('.pdf', ''))
    return redirect(url_for('upload'))
  return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
    <h1>文件上传示例</h1>
    <form action="" enctype='multipart/form-data' method='POST'>
        <input type="file" multiple="multiple" name="file" accept=".pdf">
        <input type="submit" value="上传">
    </form>
</body>
</html>
'''

def pyMuPDF_fitz(pdfPath, imagePath):
    startTime_pdf2img = datetime.datetime.now()#开始时间
    
    print("imagePath="+imagePath)
    returnData = []
    pdfDoc = fitz.open(pdfPath)
    for pg in range(pdfDoc.pageCount):
        page = pdfDoc[pg]
        rotate = int(0)
        # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
        # 此处若是不做设置，默认图片大小为：792X612, dpi=72
        zoom_x = 1.33333333 #(1.33333333-->1056x816)   (2-->1584x1224)
        zoom_y = 1.33333333
        mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pix = page.getPixmap(matrix=mat, alpha=False)
        
        if not os.path.exists(imagePath):#判断存放图片的文件夹是否存在
            os.makedirs(imagePath) # 若图片文件夹不存在就创建
        
        pix.writePNG(imagePath+'/'+'%s.png' % pg)#将图片写入指定的文件夹内
        returnData.append(imagePath+'/'+'%s.png' % pg)
    endTime_pdf2img = datetime.datetime.now()#结束时间
    print('pdf2img时间=',(endTime_pdf2img - startTime_pdf2img).seconds)
    return ''

@app.route('/list', methods=['GET'])
def list():
  # print(os.listdir('./static'))
  return json.dumps({
    "err": 0,
    "data": os.listdir('./static')
  })

@app.route('/file', methods=['GET'])
def file():
  name = request.args.get("name")
  if (name):
    returnData = []
    if (os.path.exists('./static/' + name)):
      for item in os.listdir('./static/' + name):
        returnData.append(serverUrl + name + '/' + item)
      return json.dumps({
        "err": 0,
        "data": returnData
      })
    else:
      return json.dumps({
        "err": 1,
        "data": []
      })

@app.route('/new', methods=['GET'])
def new():
  name = os.listdir('./static')[-1]
  if (name):
    # print(os.listdir('./static'))
    returnData = []
    if (os.path.exists('./static/' + name)):
      for item in os.listdir('./static/' + name):
        returnData.append(serverUrl + name + '/' + item)
      return json.dumps({
        "err": 0,
        "data": returnData
      })
    else:
      return json.dumps({
        "err": 1,
        "data": []
      })


if __name__ == "__main__":
    # pdfPath = './test.pdf'
    # imagePath = './image'
    # pyMuPDF_fitz(pdfPath, imagePath)
    app.run(debug=True, host="0.0.0.0")