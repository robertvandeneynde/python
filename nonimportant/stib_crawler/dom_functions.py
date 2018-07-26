#! /usr/bin/python3
#-*- encoding:utf-8 -*-

import re

def getElementsBySelector(all_selectors, document):
    """ http://www.bin-co.com/python/scripts/getelementsbyselector-html-css-query.php """
    selected = []
    
    all_selectors = re.sub(r'\s*([^\w])\s*',r'\1', all_selectors) #Remove the 'beautification' spaces
    
    # Grab all of the tagName elements within current context    
    def getElements(context,tag):
        if tag == "":
            tag = "*"
        
        # Get elements matching tag, filter them for class selector
        found = []
        for con in context:
            found.extend( con.getElementsByTagName(tag) )
            
        return found

    context = [document]
    inheriters = all_selectors.split()

    # Space
    for element in inheriters:
        #This part is to make sure that it is not part of a CSS3 Selector
        left_bracket = element.find("[")
        right_bracket = element.find("]")
        pos = element.find("#") #ID
        
        if pos+1 and not(pos > left_bracket and pos < right_bracket):
            parts = element.split("#")
            tag = parts[0]
            the_id = parts[1]
            ele = document.getElementById(the_id)
            
            context = [ele]
            continue
        

        pos = element.find(".") #Class
        if pos+1 and not(pos > left_bracket and pos < right_bracket):
            parts = element.split('.')
            tag = parts[0]
            class_name = parts[1]

            reg = r'(^|\s)' + class_name + '(\s|$)'
            context = list(filter(
                lambda fnd: fnd.getAttribute("class") and re.search(reg, fnd.getAttribute("class")),
                getElements(context, tag)
            ))
            
            continue
        

        if element.find('[') + 1:#If the char '[' appears, that means it needs CSS 3 parsing
            # Code to deal with attribute selectors
            m = re.match(r'^(\w*)\[(\w+)([=~\|\^\$\*]?)=?[\'"]?([^\]\'"]*)[\'"]?\]$', element)
            if m:
                tag = m.group(1)
                attr = m.group(2)
                operator = m.group(3)
                value = m.group(4)
            
            found = getElements(context,tag)
            context = []
            for fnd in found:
                if operator == '=' and fnd.getAttribute(attr) != value:
                    continue
                if operator == '~' and not(re.search(r'(^|\\s)'+value+'(\\s|$)',  fnd.getAttribute(attr))):
                    continue
                if operator == '|' and not(re.search(r'^'+value+'-?', fnd.getAttribute(attr))):
                    continue
                if operator == '^' and fnd.getAttribute(attr).find(value) != 0:
                    continue
                if operator == '$' and fnd.getAttribute(attr).rfind(value) != (fnd.getAttribute(attr).length-value.length):
                    continue
                if operator == '*' and not(fnd.getAttribute(attr).find(value) + 1):
                    continue
                
                elif not fnd.getAttribute(attr):
                    continue
                context.append(fnd)

            continue
        
        #Tag selectors - no class or id specified.
        found = getElements(context, element)
        context = found
    
    selected.extend(context)
    return selected
