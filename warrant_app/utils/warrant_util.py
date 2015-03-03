def check_if_warrant_item(symbol):
    # use the rule defined since 2010/5/17 ( see http://www.tej.com.tw/webtej/doc/warnt.htm )
    if len(symbol) != 6: 
        return False
    elif symbol[0] == '0' and symbol[1] in ['3', '4', '5', '6', '7', '8']:
        return True
    elif symbol[0] == '7' and symbol[1] in ['0', '1', '2', '3']:
        return True
    else:
        return False
    
    
def to_dict(a_list):
    a_dict={}
    for item in a_list:
        key=item[0]
        value=item[1]
        a_dict[key]=value
    return a_dict