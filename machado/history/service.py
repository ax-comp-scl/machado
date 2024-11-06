from machado.history.models import History

def createAndSaveHistory(user, method, description):
    """
    Create and save a history object for a given user.
    """
    history = History.objects.create(
        user=user,
        method=method,
        description=description
    )
    return history