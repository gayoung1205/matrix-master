from django import template

register = template.Library()

@register.filter(name='range_tag') 
def range_tag(start_val, end_val):
    return range(start_val, end_val)


@register.filter(name='return_input') 
def return_input(mat, num):
    if num == 1:
        return mat.input_a
    elif num == 2:
        return mat.input_b
    elif num == 3:
        return mat.input_c
    elif num == 4:
        return mat.input_d
    elif num == 5:
        return mat.input_e
    elif num == 6:
        return mat.input_f
    elif num == 7:
        return mat.input_g
    elif num == 8:
        return mat.input_h
    else:
        return "X"


def select_color(input):
    if input == "01":
        return "color:red"
    elif input == "02":
        return "color:orange"
    elif input == "03":
        return "color:yellow"
    elif input == "04":
        return "color:green"
    elif input == "05":
        return "color:blue"
    elif input == "06":
        return "color:indigo"
    elif input == "07":
        return "color:violet"
    elif input == "08":
        return "color:red"
    else:
        return "X"


@register.filter(name='return_font_color') 
def return_font_color(mat, num):
    if num == 1:
        return select_color(mat.input_a)
    elif num == 2:
        return select_color(mat.input_b)
    elif num == 3:
        return select_color(mat.input_c)
    elif num == 4:
        return select_color(mat.input_d)
    elif num == 5:
        return select_color(mat.input_e)
    elif num == 6:
        return select_color(mat.input_f)
    elif num == 7:
        return select_color(mat.input_g)
    elif num == 8:
        return select_color(mat.input_h)
    else:
        return "X"

@register.filter(name='list_index') 
def list_index(list, num):
    if num < 5:
        return list[num-1]
    elif num == 5:
        return "전자칠판"
    elif num == 6:
        return "T"
    else:
        return "-"
        
@register.filter
def kvm_index(list, num):
    if num < 10:
        return "PC0"+str(num)
    elif 10 <= num < 21:
        return "PC"+str(num)
    else:
        return "T"


@register.filter(name='option_selected') 
def option_selected(main, num):
    if num == 1:
        return int(main.input_a)
    elif num == 2:
        return int(main.input_b)
    elif num == 3:
        return int(main.input_c)
    elif num == 4:
        return int(main.input_d)
    elif num == 5:
        return int(main.input_e)
    elif num == 6:
        return int(main.input_f)
    elif num == 7:
        return int(main.input_g)
    elif num == 8:
        return int(main.input_h)
    else:
        return "X"

@register.filter
def remainder(target, num):
    return target%num

@register.filter
def group_index(connect: int, num: int):
    if num == 6:
        return "터치테이블"
    elif num == 7:
        return "Main"
    elif num == 8:
        return "-"
    else:
        if (connect-1)*5+num < 10:
            return "PC0"+str((connect-1)*5+num)
        else:
            return "PC"+str((connect-1)*5+num)
