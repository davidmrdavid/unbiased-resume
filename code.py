from bs4 import BeautifulSoup
import json
import string
import random
from weasyprint import HTML,CSS
import re
from collections import defaultdict
from sys import argv
import subprocess

# GLOBALS
font_sizes = defaultdict(int) 
size2tags = defaultdict(list) 

def count_fontsizes(tag):
    # Use global font_sizes
    global font_sizes
    global size2tags

    # Ignore if text is invalid
    if (tag.text == " " or tag.text == "" or tag.text == "\n"):
        return False
    # Otherwise
    if(u'style' in tag.attrs.keys()):
        match = re.compile('font-size:[\d]+').search(tag[u'style'])
        if (match):
            font_size= int(match.group(0).replace('font-size:',''))
            font_sizes[font_size] += 1 
            size2tags[font_size].append(tag)
    

def font_size_analysis(soup):
    global font_sizes
    soup.findAll(count_fontsizes)
    
    # Find name
    name_font_size = max(x for x in font_sizes.keys()) 
    name_tag =  size2tags[name_font_size] 
    name = name_tag[0].text.replace('\n','')
    name_tag[0].extract()
    del font_sizes[name_font_size]
    del size2tags[name_font_size]

    # Find headers
    header_font_size = max(x for x in font_sizes.keys())
    header_tags = size2tags[header_font_size]
    header_titles = []
    for header in header_tags:
        title = header.text.replace('\n','')
        header_titles.append(title)
    del font_sizes[header_font_size]
    del size2tags[header_font_size]

    name = name.replace(u'\xa0','')
    return (soup,name,header_titles)

def is_email(tag):
    if(len(tag) < 2):
        return False
    match =re.compile("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+").search(tag) 
    if(match):
        tag.extract() #removed from html tree
        return True

def is_school(tag):
    match = re.compile('University+').search(tag)
    if(match):
        university = tag.replace('\n', '')
        tag.extract()
        return True
    return False

def is_gpa(tag):
    match = re.compile('GPA+').search(tag)
    if(match):
        gpa = tag.replace('\n', '')
        tag.extract()
        return True
    return False

def extract_text(soup):
    text = "" 
    for tag in soup():
        if( len(tag.text) == 0 or tag.name == 'br'):
            tag.extract()
        else:
            text += " " + tag.text
        break
    text = text.replace('Page 1','')
    text = text.replace('Page: 1', '')
    return text

def get_resume_obj(titles, resume_text):
    title_indexes = []
    segment_indexes = []
    resume_obj = {}
    for title in titles:
        title_indexes.append((resume_text.find(title), title))
    title_indexes.sort()    
    for index in range(len(title_indexes)):
        (start,title) = title_indexes[index]
        try:
            (end, nextTitle) = title_indexes[index+1]
        except Exception:
            end = len(resume_text)-1
        tupl = (start,end, title)
        segment_indexes.append(tupl)

    for (start,end,title) in segment_indexes:
        segment = resume_text[start:end]
        segment = segment.replace(title,'')
        segment = re.sub('\n', '<br>', segment)
        segment = re.sub(u'\u2022',  u'<br>\t\u2022 ' ,segment)
        title = title.replace('\n','')
        title = title.replace(':','')

        doneFormatting = False
        while(not doneFormatting):
            occurrences =  [m.start() for m in re.finditer('<br>',segment)]
            if(0 in occurrences):
                segment = segment[4:]
                continue
            if(len(segment) - 4 in occurrences):
                segment =  segment[:-4]
                continue
            if(len(segment) - 5  in occurrences):
                segment =  segment[:-5]
                continue
            doneFormatting = True    


        doneFormatting = False
        while(not doneFormatting):
            occurrences =  [m.start() for m in re.finditer('<br>\s+<br>',segment)]
            for index in occurrences:
                segment = segment[index:index+9]
            doneFormatting = True    
        resume_obj[title] = segment
    return resume_obj 

def resume_start():
    return '<html><head></head><body ><center><h2>APPLICANT</h2></center>'

def resume_end():
    return '</body></html>'

def add_segment(title, body):
    return '<div><h3>'+title+'</h3><hr><p style="text-align:justify;">'+body+'</p></div>'

def generate_resume(resume_obj):
    new_resume = resume_start()
    for title in resume_obj.keys():
        text = resume_obj[title]
        new_resume += add_segment(title, text)
    new_resume += resume_end()
    with open('hi.html','wb') as f:
        new_resume = new_resume.encode('utf-16')
        f.write(new_resume)
    name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    name += ".pdf"
    HTML(string=new_resume).write_pdf("./public/new_resume.pdf",
            stylesheets=[CSS(string='h3{ margin: 0px;  }body { font-family: "Times New Roman" !important }')])        
    return name

def main(filepath):
    print "======================================================="
    print "                       CoreX                           "
    print "======================================================="
   
    command = "pdf2txt.py -o temp.html %s" % filepath
    subprocess.call(command, shell=True)

    # Opening file
    print "\n> Opening file: " + filepath + " ..."
    html_doc = open("temp.html").read()
    soup = BeautifulSoup(html_doc, "html.parser")
    print "> Done.\n"

    # Extracting name and headers
    print "> Analyzing fonts sizes..."
    (soup,name, titles) = font_size_analysis(soup)    
    print "> Found name %s, it's been removed." % name
    print "> Found these subheaders %r: " % titles

    # Extract GPA
    gpa = soup.findAll(string=is_gpa)
    print "> Found and deleted this GPA: %s" % gpa 

    # Extract University
    school = soup.findAll(string=is_school)
    school = school[0].replace(u'\xa0',' ')
    print  "> Found and deleted this school: %s" %school

    # Extract email
    email = soup.findAll(string=is_email)
    email = email[0].replace(u'\xa0','')
    email = email.replace(u'\xa0545','')
    email = email.replace(u'\xad8232','')
    print "> Found and deleted this email: %s" % email

    # Create resume segments
    resume_text = extract_text(soup)
    resume_obj = get_resume_obj(titles, resume_text)

    # Create resume
    new_path = generate_resume(resume_obj)

    # Create output json
    output_json = {}
    output_json["name"] = str(name)
    output_json["oldResumePath"] = str(filepath)
    output_json["newResumePath"] = str(new_path)
    output_json["linterScore"] = 7
    output_json["githubUsername"] = "dummy"
    output_json["school"] = str(school)
    output_json["email"] = str(email)

    with open("json_response", "wb") as file:
        j= json.dumps(output_json, ensure_ascii=False)
        json.dump(j,file)
if __name__ == "__main__":
    main(argv[1])
