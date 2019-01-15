from datetime import datetime as dt
import re,os,json,sys,shutil,imp
import pprint


def filterEntry(text,fieldname):
    if text is None:
        return 'N/A'



    if type(text) == 'str':
        text = text.lstrip()

    text = re.sub(r"\\+r\\+n", '<br>', text)
    text = re.sub(r"\\+t", '&nbsp;', text)
    text = re.sub(r"\\+n", '<br>', text)

    if fieldname == 'postcontent':
        text = re.sub(r"\[(playergm|talk|thought|action|ooc|radio)\]", r'<span class="postformatting \1"><span class="formattext formatopen">[\1]</span>', text, flags=re.I)
        text = re.sub(r"\[\/(playergm|talk|thought|action|ooc|radio)\]", r'<span class="formattext formatclose">[/\1]</span></span>', text, flags=re.I)

        copen = text.count("<span class=\"formattext formatopen\">[")
        cclose = text.count("<span class=\"formattext formatclose\">[/")
#        if copen < cclose:
#            print 'detection crash!'
#            print copen,cclose,text
#            sys.exit(1)
        if copen > cclose:
            for r in range(cclose,copen):
                text = text + '</span>'


    if fieldname == "postdate":
        text = re.sub("-\d*$", '', text)
        text = re.sub("\.\d+$", '', text)
        text = re.sub("\s+(?=\d\d\:)", '&nbsp;&nbsp;&nbsp;', text)

    return text
