from nocache import nocache
from flask import send_file
from flask import Flask, request
import urllib
import wget
import requests, json
import uuid
import os
import sendgrid
import sys
from PIL import Image
app = Flask(__name__)


@app.route ('/speak', methods=['POST'])
def demo():
    #get email info from SendGrid 
    subject = request.form['subject']
    to = request.form['from']
    sender = "speakemail@kunal.computer"

    #speak sent in subject
    cmd = "osascript -e 'say \""+subject+"\" using \"Junior\"'"
    os.system(cmd)
    
    #send magic message back to user talking about prizes
    sg = sendgrid.SendGridClient('username', 'apikey')
    subject = 're: '+subject
    sendBody = "We are giving laser keyboards for the best use of the SendGrid API. Hope you have a good memory because the next time you open up this email, it might not be there!"
    emailBody=sendBody
    imgAddress = "http://api.img4me.com/?text="+emailBody+"&font=arial&fcolor=000000&size=10&bcolor=FFFFFF&type=png"
    r = requests.get(imgAddress)
    imgUrl = r.text
    filename = wget.download(imgUrl)
    imgName = str(uuid.uuid4()) + '.png'
    os.rename (filename,imgName)
    
    #Construct email from vars and send
    htmlbody = "<img src =\"http://magicmail.ngrok.com/files/"+imgName+"\" width=\"\" height=\"\"/>"
    message = sendgrid.Mail()
    message.add_to(to)
    message.set_subject(subject)
    message.set_html(htmlbody)
    message.set_text(sendBody)
    message.set_from(sender)
    message.add_unique_arg('filename', imgName)
    status, msg = sg.send(message)

    #return OK
    return "OK"


@app.route ('/image.gif', methods=['GET'])
@nocache
def serve():
    sg = sendgrid.SendGridClient('kunal@sendgrid.com', 'm34YgBKxDP9V')
    imgString = request.args.get('bodytext')
    emailBody = urllib.quote(imgString)
    print emailBody
    imgAddress = "http://api.img4me.com/?text="+emailBody+"&font=arial&fcolor=000000&size=14&bcolor=FFFFFF&type=png"
    print imgAddress
    r = requests.get(imgAddress)
    imgUrl = r.text
    filename = wget.download(imgUrl)
    imgName = str(uuid.uuid4()) + '.png'
    os.rename (filename,imgName)

    #send email with image for body
    htmlbody = "<img src =\"http://magicmail.ngrok.com/files/"+imgName+"\" width=\"\" height=\"\"/>"
    message = sendgrid.Mail()
    message.add_to('kunal@sendgrid.com')
    message.set_subject('Magic Mail returned')
    message.set_html(htmlbody)
    message.set_text('Body')
    message.set_from('kunal732@gmail.com')
    message.add_unique_arg('filename', imgName)
    status, msg = sg.send(message)
    
    #return imgAddress
    return send_file(imgName, mimetype='image/png')

@app.route ('/files/<imgName>', methods=['GET'])
@nocache
def show(imgName):
    #return imgName
    return send_file(imgName, mimetype='image/png')

@app.route ('/makewhite', methods=['POST'])
@nocache
def handlewhite():
    data = json.loads(request.data)
    filename = format(data[0]['filename'])
    print "Your filename is: \n"
    print filename

    img = Image.open(filename)
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = []
    for item in datas:
        newData.append((255,255,255,255))
    img.putdata(newData)
    img.save(filename,"PNG")

    return "OK"

if __name__=='__main__':
    app.run(debug=True)
