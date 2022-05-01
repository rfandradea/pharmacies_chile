from tkinter.messagebox import NO


def options_dropdown(labels, values = None):

    options = []

    if values == None:

        for label in labels:

            options.append(
                {
                    'label' : label,
                    'value' : label
                }
            )
    
    else:

        for label, value in zip(labels, values):
            
            options.append(
                {
                    'label' : label,
                    'value' : value
                }
            )

    return options

def value_to_list(value):

    value_list = []

    if value is None:

        value_list = []

    elif type(value) != list:

        value_list.append(value)

    else:

        value_list = value

    return value_list

