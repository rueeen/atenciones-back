from psychopedagogy.services import can_access_psychopedagogy_module


def psychopedagogy_access(request):
    return {
        'can_access_psychopedagogy_module': can_access_psychopedagogy_module(request.user)
        if request.user.is_authenticated else False
    }
