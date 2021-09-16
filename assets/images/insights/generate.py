import os
readme=open('README.md','w')
filenames=os.listdir()
text='# Insights from Data\n<table>\n<tr><th>Metric</th><th>Image</th></tr>\n'
for filename in filenames:
    if 'jpg' in filename or 'png' in filename or 'PNG' in filename or 'gif' in filename:
        text += '<tr><td>{}</td><td><img src="{}"/></td></tr>\n'.format(filename.split('.')[0],filename)
text+='</table>'
readme.write(text)
readme.close()
#print(text)
