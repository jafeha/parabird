# encoding: utf-8
"""
liest alle configurationen aus und demonstriert auslesen der configuration und ändern
auslesen:
parser.get('section', 'option') gibt den wert der configurationsoption 'option' aus dem bereich 'section' zurück

setzen
parser.set('section', 'option', 'neuer wert')
"""

from ConfigParser import SafeConfigParser
import codecs

parser = SafeConfigParser()
with codecs.open('config.ini', 'r', encoding='utf-8') as f:
    parser.readfp(f)


    
print "Übersicht über alle Configurationsoptionen"
print "#" * 20
for section_name in parser.sections():
    print 'Section:', section_name
    for name, value in parser.items(section_name):
        print "   %s\t=  %s" % (name, value)
    print "-" * 80

print "\n" * 2
print "url from truecrypt:\t", parser.get('truecrypt', 'url')
print "changing version to 10.0"
parser.set('truecrypt', 'version', '10.0')
print 'this updates the url:\t',  parser.get('truecrypt', 'url')