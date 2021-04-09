import os
from datetime import datetime ,timedelta
from flask import  render_template, flash,url_for, request, redirect,session
from flask_dropzone import Dropzone
from FlaskWebProject2 import app
import getpass
import pdfplumber
import nltk
import re
import subprocess
import requests


data = {"Dhruv":'test1'}




# before you run please install the above packages


def Sort(lys):

    PHONE_REG = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
    EMAIL_REG = re.compile(r'[a-z0-9\.\-+]+@[a-z0-9\.\-+]+\.[a-z]+')

    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')
    nltk.download('stopwords')

    educational_institutes_keywrds = [
        'school',
        'college',
        'university',
        'academy',
        'faculty',
        'institute',
        'faculdades',
        'Schola',
        'schule',
        'lise',
        'lyceum',
        'lycee',
        'polytechnic',
        'kolej',
        'ünivers',
        'okul',
        'iit',
        'dypiu'
    ]

    SKILLS_DB = lys

    print("Skill Database: ", SKILLS_DB)

    def extract_text_from_pdf(pdffileloc):
        with pdfplumber.open(str(pdffileloc)) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text()
        return text



    def extract_names(txt):  # not so accurate though
        person_names = []

        for sent in nltk.sent_tokenize(txt):
            for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
                if hasattr(chunk, 'label') and chunk.label() == 'PERSON':
                    person_names.append(
                        ' '.join(chunk_leave[0] for chunk_leave in chunk.leaves()))

        return person_names

    def extract_phone_number(resume_text):
        phone = re.findall(PHONE_REG, resume_text)

        if phone:
            number = ''.join(phone[0])

            if resume_text.find(number) >= 0 and len(number) < 16:
                return number
        return None

    def extract_emails(resume_text):
        return re.findall(EMAIL_REG, resume_text)

    def extract_education(input_text):  # not so accurate though
        organizations = []

        # first get all the organization names using nltk
        for sent in nltk.sent_tokenize(input_text):
            for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
                if hasattr(chunk, 'label') and chunk.label() == ('ORGANIZATION' or 'FACILITY'):
                    organizations.append(
                        ' '.join(c[0] for c in chunk.leaves()))

        # we search for each bigram and trigram for reserved words
        # (college, university etc...)
        education = set()
        # print(organizations)
        for org in organizations:
            for word in educational_institutes_keywrds:
                if org.lower().find(word) >= 0:
                    education.add(org)

        return education

    def extract_skills(input_text):
        stop_words = set(nltk.corpus.stopwords.words('english'))
        word_tokens = nltk.tokenize.word_tokenize(input_text)

        # remove the stop words
        filtered_tokens = [w for w in word_tokens if w not in stop_words]

        # remove the punctuation
        filtered_tokens = [w for w in word_tokens if w.isalpha()]

        # generate bigrams and trigrams (such as artificial intelligence)
        bigrams_trigrams = list(
            map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))

        # we create a set to keep the results in.
        found_skills = set()

        # we search for each token in our skills database
        for token in filtered_tokens:
            if token in SKILLS_DB:
                found_skills.add(token.lower())

        # we search for each bigram and trigram in our skills database
        for ngram in bigrams_trigrams:
            if ngram in SKILLS_DB:
                found_skills.add(ngram.lower())

        return found_skills

    # location of all resumes, change accordingly
    common_path = "C:/Users/dhruv/source/repos/FlaskWebProject2/FlaskWebProject2/static/uploads/"
    listOfFiles = os.listdir(common_path)

    chosen_name = []
    chosen_mail = []
    chosen_number = []

    print("\n")
    print("\t\t\t\t\t\t\tDetails of Candidate")
    counter = 1
    for resumes in listOfFiles:

        if resumes.endswith(".pdf") or resumes.endswith(".docx"):
            print("Candidate ", counter)
            current_res = common_path + str(resumes)
            text = extract_text_from_pdf(current_res)
            names = extract_names(text)
            phone_number = extract_phone_number(text)
            emails = extract_emails(text)
            skills = extract_skills(text)
            education_information = extract_education(text)

            if names:
                print("Name: ", names[0])
     
            
            if phone_number:
                print("Phone Number: ", phone_number)
  
            
            if emails:
                print("Email Address: ", emails[0])
            else:
                emails.append('Not Found')
            
            if skills:
                print("Skills: ", skills)
         
            
            if education_information:
                print("Educational Details: ", education_information)
         
            counter += 1

            margin = (len(skills) / len(SKILLS_DB)) * 100
            if margin >= 50:
                chosen_name.append(resumes)
                chosen_mail += [emails[0]]
               
                chosen_number += [phone_number]
                print(f"\t\tCurrent candidate {resumes} selected")

            print(round(margin, 2))
            print("\n")
    return chosen_name, chosen_mail,  chosen_number





basedir= "C:/Users/dhruv/source/repos/FlaskWebProject2/FlaskWebProject2/static/"
app.config.update(
    UPLOADED_PATH= os.path.join(basedir,'uploads'),
    DROPZONE_MAX_FILE_SIZE = 1024,
    DROPZONE_TIMEOUT = 5*60*1000)









@app.route('/')
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/login",methods=["POST","GET"])
def login():
    if request.method == "POST":
        # run login logic 
        userid = request.form["userid"]
        password = request.form["pass"]
        
        if userid in data:
            if data[userid] == password:
                return redirect(url_for("search"))
     
 
        print(data)
    else:
        return render_template("login.html")

        
        

@app.route("/register",methods=["POST","GET"])
def register ():
    if request.method == "POST":
        # run login logic 
        userid =    request.form["reguserid"]
        emailid=    request.form["regemail"]
        password =  request.form["regpass"]
        data.update({userid:password})
        print(data)
        return redirect("/login")
    else:
        return render_template("register.html")

        



@app.route("/contact")
def contact():
    return render_template('contact.html')

        





@app.route("/pricing")
def  pricing():
    return render_template("pricing.html")



@app.route("/privacy")
def  privacy():
    return render_template("privacy.html")


@app.route("/cfghxdrvbghvcjfnt")
def  paywall():
    return f'<h1>404 ERROR</h1>'




dropzone = Dropzone(app)
@app.route('/ui',methods=['POST','GET'])
def upload():
    if request.method == 'POST':

        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'],f.filename))
    
    else :
        return render_template('ui.html')
  
      






     





@app.route('/resume',methods=['POST','GET'])
def search():
    if request.method == 'POST':
      
        skills = str(request.form['skill'])
        skills = skills.split(",")
        names, email,  number = Sort(skills)
        return render_template('resumecompute.html' ,names = names ,email=email ,number = number , len = len(names))
    else:
        return render_template('resume.html')
       
     
    
       
        








