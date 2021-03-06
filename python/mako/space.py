
# Describes available spaces and their wrapper implementation.
# Most of the characteristics (barycentric, dual...) are guessed later on.
# However, these characteristics can be specified here. The characteristics
# will be used in the actual space factories by the users.
# The default implementation is 'grid_only', eg a single constructor that takes
# a grid as its only argument.
spaces = {
    'PiecewiseConstantScalarSpace':
    { 'doc':
       'Space of discontinuous, piecewise constant scalar functions',
       'implementation': 'grid_only'
    },
    'PiecewiseLinearContinuousScalarSpace':
    { 'doc':
       'Space of continuous, piecewise linear scalar functions',
       'implementation': 'grid_only'
    },
    'PiecewisePolynomialContinuousScalarSpace': {
        'doc':
        'Space of continuous, piecewise polynomial scalar functions',
        'implementation': 'polynomial'
    },
    'PiecewisePolynomialDiscontinuousScalarSpace': {
        'doc':
        'Space of discontinuous, piecewise polynomial scalar functions',
        'implementation': 'polynomial'
    }
}


# Guess implementation from class name
# Mostly means guessing wether space operates on the direct or dual grid,
# whether functions are continuous, whether they are constant, linear, or
# polynomial, etc. These facts are used later on in the actual space factory.
for key, description in spaces.items():
    if 'implementation' not in description:
        description['implementation'] = 'grid_only'

    if 'header' not in description:
        f = lambda x: x if x.islower() else '_' + x.lower()
        description['header'] = 'bempp/space/%s.hpp' \
            % (key[0].lower() + ''.join([f(u) for u in key[1:]]))

    if 'scalar' not in description:
        description['scalar'] = 'scalar' in key.lower()

    if description['scalar'] and 'order' not in description:
        if 'constant' in key.lower():
            description['order'] = 'constant'
        elif 'linear' in key.lower():
            description['order'] = 'linear'
        else:
            description['order'] = 'polynomial'

    if 'continuous' not in description:
        description['continuous'] = 'discontinuous' not in key.lower()

    if 'dual' not in description:
        description['dual'] = 'dual' in key.lower()

    if 'barycentric' not in description:
        description['barycentric'] = 'barycentric' in key.lower()
