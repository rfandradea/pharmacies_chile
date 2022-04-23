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