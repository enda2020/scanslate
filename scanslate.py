# -*- coding: utf-8 -*-
#!/usr/bin/ python3

from __future__ import print_function
from google.cloud import vision, translate
import io
import os
import json
import logging
import sys
import datetime
from PIL import Image
#import pyinsane2
import subprocess
import smtplib
'''
   :param str output_dir: Location for scan document and translation result text file to be saved
   :param str from_language: Original document of document to be scanned e.g ja
   :param str to_language: Document will be translated TO this language e.g en-US
   :param str gcloud_project_name: project name of your your google cloud api setup e.g gcloudproject-1111111
   :param str gcloud_credential_json: path of your your google cloud api credential file e.g gcloudproject-111111-2243dssdf.json
   :param str mail_recipient: destination for email
   :param str smtp_user: username for smtp server
   :param str smtp_password: password for smtp server    
   :EXAMPLE: python3 scanslate.py  /home/user/scan ja en-US gcloudproject-1111111  /home/user/gcloud.json example@example.com smtp_password 
   
   
   '''
  
# set google  application credential as environment variable  during the running of the script
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] =  sys.argv[5]

PROGRESSION_INDICATOR = ['|', '/', '-', '\\']
#smtp_server =  ('smtp-mail.outlook.com', 587)

def send_mail(to, subject, body):
    
    body = 'Subject:' + subject + ' \n\n' +body + '\n\n'
    #print(body)
    try:
        smtpObj = smtplib.SMTP('smtp-mail.outlook.com', 587)
    except Exception as e:
     
        smtpObj = smtplib.SMTP_SSL('smtp-mail.outlook.com', 465)
    # type(smtpObj)
    smtpObj.ehlo()
    smtpObj.starttls()
  
    smtpObj.login(sys.argv[6], sys.argv[7])
  
    smtpObj.sendmail(sys.argv[6], to, body.encode())  # Or recipient@outlook
 
    pass

def format_result(original, translated):
  result = ''
  for i,  line in enumerate(original.split('\n')):
    #result += line + '\n'
    result += line + '\n' + translated.split('\n')[i] + '\n'
  print(result) 
  return result
    
    





def translate_text(text="YOUR_TEXT_TO_TRANSLATE", project_id="YOUR_PROJECT_ID"):

    """Translating Text."""

    client = translate.TranslationServiceClient()

    parent = client.location_path(project_id, "global")

    # Detail on supported types can be found here:
    # https://cloud.google.com/translate/docs/supported-formats
    response = client.translate_text(
        parent=parent,
        contents=[text],
        mime_type="text/plain",  # mime types: text/plain, text/html
        source_language_code=sys.argv[2],
        target_language_code=sys.argv[3],
    )
    # return the translation for each input text provided
    result=''
    for translation in response.translations:
        #print(u"Translated text: {}".format(translation.translated_text))
        result+=translation.translated_text
    return result


def main():
    
    output_file =  sys.argv[1] +'/' +datetime.datetime.today().strftime('%Y-%m-%d-%H%M%S') + '_original_'+sys.argv[2] +'.jpg'
    #output_file = datetime.datetime.today().strftime('%Y-%m-%d-%H%M%S') + '_original_'+sys.argv[2] +'.jpg'
    print("Output file: %s" % output_file)  
    with open(output_file, "w+") as f:
      cmd = subprocess.run(['scanimage','--format', 'jpeg'], stdout=f)

    
    client = vision.ImageAnnotatorClient()

    
    image_path = f'{output_file}'

    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    # construct an iamge instance
    image = vision.types.Image(content=content)

    """
    # or we can pass the image url
    image = vision.types.Image()
    image.source.image_uri = 'https://edu.pngfacts.com/uploads/1/1/3/2/11320972/grade-10-english_orig.png'
    """

    # annotate Image Response
    response = client.text_detection(image=image,
        image_context={"language_hints": [sys.argv[2]]},  # Japanese
    )  # returns TextAnnotation


    body = ""
    i=0
    texts = response.text_annotations
    #for text in texts:
     # body = body+text.description
      #print(text.description)

    #print(body)
    translated =''
    #only do the translation if text is found  
    if len(texts) > 0:  
      #print(translate_text(texts[0].description,sys.argv[4]))
      # save result as file
      translated = translate_text(texts[0].description,sys.argv[4])
      with open(output_file.replace('original_'+sys.argv[2] +'.jpg', 'translated_'+sys.argv[3]+'.txt'),'w') as f:
        f.writelines(translated) 
      send_mail( sys.argv[6],'Translation', format_result(texts[0].description, translated))
    else: 
      print('No text found!') 


if __name__ == "__main__":


   main()



